# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Generate KMZ Mission – DJI FlightHub 2
 Processing algorithm.

 All five data fields (wp_index, HAE, ASL, angle, pitch) are selectable
 from the input layer's attributes via field-picker parameters.
***************************************************************************/
"""

import copy
import os
import zipfile
import tempfile

try:
    import defusedxml.ElementTree as ET
    from defusedxml.ElementTree import fromstring as _et_fromstring
except ImportError:  # pragma: no cover – defusedxml not installed
    import xml.etree.ElementTree as ET  # nosec B405
    _et_fromstring = ET.fromstring  # nosec B314

from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterVectorLayer,
    QgsProcessingParameterField,
    QgsProcessingParameterFileDestination,
)
from qgis.PyQt.QtGui import QIcon

from .templates import TEMPLATE_KML, TEMPLATE_WPML


class GenerateKmzMission(QgsProcessingAlgorithm):
    """
    Generates a DJI FlightHub 2 .kmz mission file from a QGIS point layer.
    KML and WPML templates are embedded in the plugin – no external files needed.
    All attribute columns are selectable from the layer.
    """

    INPUT_LAYER = "INPUT_LAYER"
    FIELD_INDEX = "FIELD_INDEX"
    FIELD_HAE = "FIELD_HAE"
    FIELD_ASL = "FIELD_ASL"
    FIELD_ANGLE = "FIELD_ANGLE"
    FIELD_PITCH = "FIELD_PITCH"
    OUTPUT_KMZ = "OUTPUT_KMZ"

    NS = {
        "kml": "http://www.opengis.net/kml/2.2",
        "wpml": "http://www.dji.com/wpmz/1.0.6",
    }

    # ----------------------------------------------------------------
    # Boilerplate
    # ----------------------------------------------------------------

    def name(self):
        return "generatekmzmission"

    def displayName(self):
        return "Generate Waypoint Mission KMZ (DJI FlightHub 2)"

    def group(self):
        return "DJI Missions"

    def groupId(self):
        return "djimissions"

    def shortHelpString(self):
        return (
            "<b>Generate Waypoint Mission KMZ for DJI FlightHub 2</b><br><br>"
            "Reads a point layer and produces a <tt>.kmz</tt> file ready for "
            "upload to DJI FlightHub 2.<br><br>"
            "KML and WPML templates are <b>embedded in the plugin</b> – no "
            "external template files are required.<br><br>"
            "<b>Field mapping</b> – select which layer attribute contains each value:<br>"
            "<ul>"
            "<li><b>Waypoint index</b> – integer sort order of waypoints</li>"
            "<li><b>HAE</b> – ellipsoid height (m, WGS84)</li>"
            "<li><b>ASL</b> – height above sea level (m, EGM96)</li>"
            "<li><b>Aircraft Yaw</b> – aircraft heading in degrees</li>"
            "<li><b>Gimbal Tilt</b> – gimbal pitch angle in degrees</li>"
            "</ul>"
            "Default field names match the standard pipeline output "
            "(<tt>wp_index, HAE, ASL, Aircraft Yaw, Gimbal Tilt</tt>)."
        )

    def icon(self):
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        return super().icon()

    def createInstance(self):
        return self.__class__()

    # ----------------------------------------------------------------
    # Parameters
    # ----------------------------------------------------------------

    def initAlgorithm(self, config=None):

        # --- Input layer ---
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INPUT_LAYER,
                "Waypoint point layer",
                [QgsProcessing.TypeVectorPoint],
            )
        )

        # --- Field pickers (all linked to INPUT_LAYER so they auto-populate) ---
        self.addParameter(
            QgsProcessingParameterField(
                self.FIELD_INDEX,
                "Waypoint index field",
                parentLayerParameterName=self.INPUT_LAYER,
                type=QgsProcessingParameterField.Any,
                defaultValue="wp_index",
                optional=False,
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.FIELD_HAE,
                "HAE field (ellipsoid height, m WGS84)",
                parentLayerParameterName=self.INPUT_LAYER,
                type=QgsProcessingParameterField.Numeric,
                defaultValue="HAE",
                optional=False,
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.FIELD_ASL,
                "ASL field (height above sea level, m EGM96)",
                parentLayerParameterName=self.INPUT_LAYER,
                type=QgsProcessingParameterField.Numeric,
                defaultValue="ASL",
                optional=False,
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.FIELD_ANGLE,
                "Aircraft Yaw field (heading, degrees)",
                parentLayerParameterName=self.INPUT_LAYER,
                type=QgsProcessingParameterField.Numeric,
                defaultValue="Aircraft Yaw",
                optional=False,
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.FIELD_PITCH,
                "Gimbal Tilt field (pitch angle, degrees)",
                parentLayerParameterName=self.INPUT_LAYER,
                type=QgsProcessingParameterField.Numeric,
                defaultValue="Gimbal Tilt",
                optional=False,
            )
        )

        # --- Output ---
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT_KMZ,
                "Output KMZ file",
                fileFilter="KMZ files (*.kmz)",
            )
        )

    # ----------------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------------

    def _parse_template_string(self, xml_string, label):
        """Parse an XML template from a string; return (tree, folder_el, template_placemark)."""
        try:
            root = _et_fromstring(xml_string)
        except ET.ParseError as exc:
            raise QgsProcessingException(
                f"Failed to parse embedded {label} template: {exc}"
            ) from exc

        tree = ET.ElementTree(root)
        folder = root.find(".//kml:Folder", self.NS)

        if folder is None:
            raise QgsProcessingException(
                f"<Folder> not found in embedded {label} template"
            )

        placemarks = folder.findall("kml:Placemark", self.NS)
        if not placemarks:
            raise QgsProcessingException(
                f"Embedded {label} template must contain at least ONE <Placemark>"
            )

        template_pm = copy.deepcopy(placemarks[0])
        for pm in placemarks:
            folder.remove(pm)

        return tree, folder, template_pm

    def _set_text(self, element, xpath, value):
        """Find a child element by xpath and set its text; silently skips if missing."""
        el = element.find(xpath, self.NS)
        if el is not None:
            el.text = value

    def _fill_placemark(self, template_pm, lon, lat, idx, hae, asl, angle, pitch):
        """Clone the template placemark and fill in all waypoint-specific values."""
        NS = self.NS
        pm = copy.deepcopy(template_pm)

        self._set_text(pm, ".//kml:coordinates", f"{lon},{lat}")
        self._set_text(pm, ".//wpml:ellipsoidHeight", str(hae))
        self._set_text(pm, ".//wpml:height", str(asl))
        self._set_text(pm, ".//wpml:executeHeight", str(hae))
        self._set_text(pm, ".//wpml:index", str(idx))

        ag_el = pm.find(".//wpml:actionGroup", NS)
        if ag_el is not None:
            self._set_text(ag_el, "wpml:actionGroupId", str(idx))
            self._set_text(ag_el, "wpml:actionGroupStartIndex", str(idx))
            self._set_text(ag_el, "wpml:actionGroupEndIndex", str(idx))

        for action in pm.findall(".//wpml:action", NS):
            func_el = action.find("wpml:actionActuatorFunc", NS)
            if func_el is None:
                continue
            func = func_el.text

            if func == "rotateYaw":
                self._set_text(
                    action,
                    "wpml:actionActuatorFuncParam/wpml:aircraftHeading",
                    str(angle),
                )
            elif func == "gimbalRotate":
                self._set_text(
                    action,
                    "wpml:actionActuatorFuncParam/wpml:gimbalPitchRotateAngle",
                    str(pitch),
                )

        return pm

    # ----------------------------------------------------------------
    # Main processing
    # ----------------------------------------------------------------

    def processAlgorithm(self, parameters, context, feedback):

        ET.register_namespace("", "http://www.opengis.net/kml/2.2")
        ET.register_namespace("wpml", "http://www.dji.com/wpmz/1.0.6")

        # --- Inputs ---
        layer = self.parameterAsVectorLayer(parameters, self.INPUT_LAYER, context)
        kmz_path = self.parameterAsFileOutput(parameters, self.OUTPUT_KMZ, context)

        if layer is None:
            raise QgsProcessingException(
                self.invalidSourceError(parameters, self.INPUT_LAYER)
            )

        # --- CRS check ---
        crs = layer.crs()
        if not crs.isGeographic() or "4326" not in crs.authid():
            feedback.pushWarning(
                f"Layer CRS is '{crs.authid()}', not EPSG:4326. "
                "Coordinates written to the KMZ will be wrong unless the layer "
                "is in WGS 84 geographic (EPSG:4326)."
            )

        # --- Resolve selected field names ---
        f_index = self.parameterAsString(parameters, self.FIELD_INDEX, context)
        f_hae = self.parameterAsString(parameters, self.FIELD_HAE, context)
        f_asl = self.parameterAsString(parameters, self.FIELD_ASL, context)
        f_angle = self.parameterAsString(parameters, self.FIELD_ANGLE, context)
        f_pitch = self.parameterAsString(parameters, self.FIELD_PITCH, context)

        feedback.pushInfo(
            f"Field mapping:  index='{f_index}'  HAE='{f_hae}'  "
            f"ASL='{f_asl}'  angle='{f_angle}'  pitch='{f_pitch}'"
        )

        # --- Load & sort features ---
        features = list(layer.getFeatures())
        if not features:
            raise QgsProcessingException("Point layer contains no features")

        try:
            features.sort(key=lambda f: int(f[f_index]))
        except (KeyError, TypeError, ValueError) as exc:
            raise QgsProcessingException(
                f"Cannot sort by waypoint index field '{f_index}': {exc}"
            ) from exc

        total = len(features)
        feedback.pushInfo(f"Processing {total} waypoints ...")

        # --- Parse embedded templates ---
        tree_kml, folder_kml, tpl_kml = self._parse_template_string(TEMPLATE_KML, "KML")
        tree_wpml, folder_wpml, tpl_wpml = self._parse_template_string(TEMPLATE_WPML, "WPML")

        # --- Generate placemarks ---
        for i, feat in enumerate(features):
            if feedback.isCanceled():
                break

            geom = feat.geometry()
            if geom is None or geom.isEmpty():
                feedback.pushWarning(f"Feature {feat.id()} has no geometry – skipped")
                continue

            pt = geom.asPoint()
            lon, lat = pt.x(), pt.y()

            try:
                idx = int(feat[f_index])
                hae = float(feat[f_hae])
                asl = float(feat[f_asl])
                angle = float(feat[f_angle])
                pitch = float(feat[f_pitch])
            except (KeyError, TypeError, ValueError) as exc:
                raise QgsProcessingException(
                    f"Cannot read attribute values for feature {feat.id()}: {exc}"
                ) from exc

            folder_kml.append(
                self._fill_placemark(tpl_kml, lon, lat, idx, hae, asl, angle, pitch)
            )
            folder_wpml.append(
                self._fill_placemark(tpl_wpml, lon, lat, idx, hae, asl, angle, pitch)
            )

            feedback.setProgress(int((i + 1) / total * 100))

        # --- Write XML to temp files, then pack into KMZ ---
        with tempfile.TemporaryDirectory() as tmp:
            tmp_kml = os.path.join(tmp, "template.kml")
            tmp_wpml = os.path.join(tmp, "waylines.wpml")

            tree_kml.write(tmp_kml, encoding="UTF-8", xml_declaration=True)
            tree_wpml.write(tmp_wpml, encoding="UTF-8", xml_declaration=True)

            out_dir = os.path.dirname(os.path.abspath(kmz_path))
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)

            with zipfile.ZipFile(kmz_path, "w", zipfile.ZIP_DEFLATED) as kmz:
                kmz.write(tmp_kml, arcname="wpmz/template.kml")
                kmz.write(tmp_wpml, arcname="wpmz/waylines.wpml")

        feedback.pushInfo(f"KMZ created successfully: {kmz_path}")
        return {self.OUTPUT_KMZ: kmz_path}

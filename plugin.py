# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Generate KMZ Mission – DJI FlightHub 2
 Main plugin class.
***************************************************************************/
"""

from qgis.core import QgsApplication
from .provider import GenerateKmzMissionProvider


class GenerateKmzMissionPlugin:
    """QGIS plugin wrapper that registers the Processing provider."""

    def __init__(self, iface):
        self.iface = iface
        self.provider = None

    # ------------------------------------------------------------------
    # QGIS plugin lifecycle
    # ------------------------------------------------------------------

    def initProcessing(self):
        """Create and register the provider.  Called by QGIS automatically
        when the Processing framework is ready."""
        self.provider = GenerateKmzMissionProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def initGui(self):
        """Called by QGIS when the plugin is loaded into the GUI."""
        self.initProcessing()

    def unload(self):
        """Called by QGIS when the plugin is unloaded / disabled."""
        if self.provider is not None:
            QgsApplication.processingRegistry().removeProvider(self.provider)
            self.provider = None

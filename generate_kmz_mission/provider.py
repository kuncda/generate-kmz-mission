# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Generate KMZ Mission – DJI FlightHub 2
 Processing provider.
***************************************************************************/
"""

import os

from qgis.core import QgsProcessingProvider
from qgis.PyQt.QtGui import QIcon

from .algorithm import GenerateKmzMission


class GenerateKmzMissionProvider(QgsProcessingProvider):
    """Groups all DJI Mission algorithms under one Processing provider."""

    def id(self) -> str:
        return "djimissions"

    def name(self) -> str:
        return "DJI Missions"

    def longName(self) -> str:
        return "DJI FlightHub 2 Mission Tools"

    def icon(self) -> QIcon:
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        return super().icon()

    def loadAlgorithms(self):
        """Register every algorithm this provider exposes."""
        self.addAlgorithm(GenerateKmzMission())

    def versionInfo(self) -> str:
        return "1.0.0"

# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Generate KMZ Mission – DJI FlightHub 2
 Plugin entry point required by QGIS.
***************************************************************************/
"""


def classFactory(iface):  # noqa: N802
    """Load GenerateKmzMissionPlugin class from plugin.py."""
    from .plugin import GenerateKmzMissionPlugin
    return GenerateKmzMissionPlugin(iface)

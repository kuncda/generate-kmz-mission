# Generate KMZ Mission – DJI FlightHub 2

QGIS plugin that exposes a **Processing algorithm** for generating `.kmz` waypoint mission files ready for upload to **DJI FlightHub 2**.

---

## Installation

### Option A – Install from ZIP (recommended)
1. In QGIS, open **Plugins → Manage and Install Plugins → Install from ZIP**.
2. Browse to `generate_kmz_mission.zip` and click **Install Plugin**.
3. The plugin appears in the Processing Toolbox under **DJI Missions**.

### Option B – Manual installation
1. Unzip the archive into your QGIS plugin profile folder:
   - Windows: `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\`
   - Linux/macOS: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
2. Restart QGIS and enable the plugin via **Plugins → Manage and Install Plugins**.

---

## Usage

1. Open the **Processing Toolbox** (Ctrl+Alt+T).
2. Expand **DJI Missions → Generate Waypoint Mission KMZ (DJI FlightHub 2)**.
3. Fill in the parameters:

| Parameter | Description |
|---|---|
| Waypoint point layer | A point layer in WGS 84 (EPSG:4326). |
| Field Mapping | Map attributes for Index, HAE, ASL, Yaw, and Pitch. |
| Output KMZ file | Destination path for the generated `.kmz`. |

### Required layer fields
[cite_start]The algorithm allows you to select which layer attributes contain the following values[cite: 2]:

| Field | Type | Description |
|---|---|---|
| **Waypoint index** | Integer | Sort order of waypoints (0-based). |
| **HAE** | Numeric | Ellipsoid height (m, WGS84). |
| **ASL** | Numeric | Height above sea level (m, EGM96). |
| **Aircraft Yaw** | Numeric | Aircraft heading in degrees. |
| **Gimbal Tilt** | Numeric | Gimbal pitch angle in degrees. |

---

## Template Files
No external template files are required. [cite_start]The mission structures (KML and WPML) are **embedded within the plugin**[cite: 2]. This ensures that the generated KMZ follows the specific DJI FlightHub 2 requirements automatically.

---

## File structure
```text
generate_kmz_mission/
├── __init__.py       # QGIS plugin entry point
├── plugin.py         # Registers the Processing provider
├── provider.py       # QgsProcessingProvider
├── algorithm.py      # Core logic and field mapping
├── templates.py      # Embedded KML/WPML templates
├── metadata.txt      # Plugin metadata
├── icon.png          # Toolbox icon
└── README.md         # This file

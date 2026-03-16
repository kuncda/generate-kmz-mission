# Generate KMZ Mission – DJI FlightHub 2

QGIS plugin that exposes a **Processing algorithm** for generating `.kmz` waypoint mission files ready for upload to **DJI FlightHub 2**.

---

## Installation

### Option A – QGIS Plugin Repository (recommended)
1. In QGIS, open **Plugins → Manage and Install Plugins**.
2. Search for **Generate KMZ Mission**.
3. Click **Install Plugin**.
4. The plugin appears in the Processing Toolbox under **DJI Missions**.

### Option B – Install from ZIP
1. Download the latest `generate_kmz_mission.zip` from the [Releases](https://github.com/kuncda/generate-kmz-mission/releases) page.
2. In QGIS, open **Plugins → Manage and Install Plugins → Install from ZIP**.
3. Browse to the downloaded zip and click **Install Plugin**.

### Option C – Manual installation
1. In QGIS, open **Settings → User Profiles → Open Active Profile Folder**.
2. Navigate to the `python/plugins/` subfolder inside that folder (create it if it does not exist).
3. Unzip the archive there so the result is `…/python/plugins/generate_kmz_mission/`.
4. Restart QGIS and enable the plugin via **Plugins → Manage and Install Plugins**.

### External dependency – defusedxml
The plugin requires [`defusedxml`](https://pypi.org/project/defusedxml/) for safe XML parsing.
QGIS will prompt you to install it automatically on first use. If it does not, install it manually:

```bash
# Windows – run inside the OSGeo4W Shell
python -m pip install defusedxml

# Linux / macOS
pip install defusedxml --break-system-packages
```

---

## Usage

1. Open the **Processing Toolbox** (`Ctrl+Alt+T`).
2. Expand **DJI Missions → Generate Waypoint Mission KMZ (DJI FlightHub 2)**.
3. Fill in the parameters:

| Parameter | Description |
|---|---|
| Waypoint point layer | A point layer in **WGS 84 (EPSG:4326)**. |
| Field mapping | Map attributes for Index, HAE, ASL, Yaw, and Pitch. |
| Output KMZ file | Destination path for the generated `.kmz`. |

> **Note:** The input layer must be in **EPSG:4326** (WGS 84 geographic). If it is not, the plugin will display a warning and the coordinates written to the KMZ will be incorrect. Reproject your layer first using **Vector → Data Management Tools → Reproject Layer**.

### Required layer fields

Select which layer attributes contain the following values:

| Field | Type | Description |
|---|---|---|
| **Waypoint index** | Integer | Sort order of waypoints (0-based). |
| **HAE** | Numeric | Ellipsoid height (m, WGS84). |
| **ASL** | Numeric | Height above sea level (m, EGM96). |
| **Aircraft Yaw** | Numeric | Aircraft heading in degrees. |
| **Gimbal Tilt** | Numeric | Gimbal pitch angle in degrees. |

Default field names match the standard pipeline output: `wp_index`, `HAE`, `ASL`, `Aircraft Yaw`, `Gimbal Tilt`.

---

## Template files

No external template files are required. The mission structures (KML and WPML) are **embedded within the plugin**. This ensures that the generated KMZ follows the specific DJI FlightHub 2 format automatically.

---

## File structure

```
generate_kmz_mission/
├── __init__.py       # QGIS plugin entry point
├── plugin.py         # Registers the Processing provider
├── provider.py       # QgsProcessingProvider
├── algorithm.py      # Core logic and field mapping
├── templates.py      # Embedded KML/WPML templates
├── metadata.txt      # Plugin metadata
├── icon.png          # Toolbox icon
└── README.md         # This file
```

---

## Changelog

### 1.0.1
- Replace `xml.etree.ElementTree.fromstring` with `defusedxml` equivalent (fixes Bandit B314)
- Remove unused imports (`uuid`, `Any`, `Optional`, `QgsProcessingContext`, `QgsProcessingFeedback`)
- Add CRS warning when input layer is not EPSG:4326
- Remove dead `action_uuid` parameter from `_fill_placemark`
- Add `external_dependencies` and `changelog` fields to `metadata.txt`

### 1.0.0
- Initial release

---

## Issues and contributions

Bug reports and feature requests are welcome at the [issue tracker](https://github.com/kuncda/generate-kmz-mission/issues).

---

## License

[GPL-3.0](LICENSE)

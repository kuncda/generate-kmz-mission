# Generate KMZ Mission – DJI FlightHub 2

QGIS plugin that exposes a **Processing algorithm** for generating `.kmz`
waypoint mission files ready for upload to **DJI FlightHub 2**.

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
2. Expand **DJI Missions → Generate KMZ Mission (DJI FlightHub 2)**.
3. Fill in the parameters:

| Parameter | Description |
|---|---|
| Waypoint point layer | A point layer in WGS 84 (EPSG:4326) |
| KML template file | Path to your `template.kml` base file |
| WPML template file | Path to your `waylines.wpml` base file |
| Output KMZ file | Destination path for the generated `.kmz` |

### Required layer fields

| Field | Type | Description |
|---|---|---|
| `wp_index` | Integer | Waypoint order index (0-based) |
| `HAE` | Float | Ellipsoid height (metres) |
| `ASL` | Float | Height above sea level (metres) |
| `angle` | Float | Aircraft heading / yaw (degrees, 0–360) |
| `pitch` | Float | Gimbal pitch angle (degrees, negative = down) |

---

## Template files

The plugin reads two XML template files that define the mission structure:

- **`template.kml`** – KML placemarks (used by FlightHub 2 for display)
- **`waylines.wpml`** – WPML placemarks (used by the drone for execution)

Each file must contain a `<Folder>` with at least one `<Placemark>`.
The first placemark is used as a template; all others are ignored.

Default template paths (editable in the algorithm dialog):
```
\\Aerovision2\aerovision group 2\Sloupy\vzor\template.kml
\\Aerovision2\aerovision group 2\Sloupy\vzor\waylines.wpml
```

---

## File structure

```
generate_kmz_mission/
├── __init__.py       # QGIS plugin entry point
├── plugin.py         # Plugin class (registers the Processing provider)
├── provider.py       # QgsProcessingProvider
├── algorithm.py      # QgsProcessingAlgorithm (core logic)
├── metadata.txt      # Plugin metadata
├── icon.png          # Toolbar icon
└── README.md         # This file
```

---

## Changelog

### 1.0.0
- Initial release
- Template file paths now configurable via algorithm parameters
- Added field validation before processing
- Packaged as a proper installable QGIS plugin

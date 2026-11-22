# CAD Models

SolidCraft designs (`.sc`) and fabrication exports. One folder per shade.

## Access
The SolidCraft MCP server (`.mcp.json` at the repository root) has write access to this folder and to `solar_tube_cooker/cad/`.
Start Claude Code from the repository root. The server resolves the paths relative to the working directory.

## Conventions
- Take dimensions from the parameters in `../docs/overview.md`. Do not hard-code values that have a parameter.
- Name exports `<part>_x<count>.<ext>`, for example `panel_x12.dxf`.
- Generated exports (`*.stl`, `*.3mf`, `*.step`, `*.dxf`) are not committed. Regenerate them from the designs.

## Contents
| Folder | Design | Exports |
|---|---|---|
| `dodecahedron/` | `dodecahedron_kit.sc`: 11 panels (bottom plain, 5 upper and 5 lower ring panels with the Marrakech patterns; target is the Penrose pattern, see `../docs/light_patterns.md`), 50 keys, 10 lug keys, top plate, reference solid and reference bodies for socket, nipple and bulb | `panel_x1.dxf` (sketch `PanelLaser`: plain panel, bottom), `upper_panel_x5.dxf`, `lower_panel_x5.dxf` (from `../tools/panel_pattern.py`: `panel_x1.dxf` + kerf cutouts), `key_x50.dxf` (sketch `KeyLaser`), `lug_key_x10.dxf` (sketch `LugKeyLaser`), `top_plate_x1.dxf` (sketch `TopPlateLaser`) |
| `dodecahedron/` | `joint_test.sc`: wooden joint test, 2 plates and 2 cross-section keys (see `../docs/joinery.md`) | `joint_test_x1.dxf` (from `../tools/joint_keys.py`) |

Export the DXFs with `sketch.export_dxf {"sketch": ..., "path": ..., "layers": "roles"}`: outline on layer `OUTLINE`, holes on layer `CUT`. With the app connected (mode `app`), give an absolute path: the app refuses a relative one. After each export the Claude Code hook runs `dxf_check.py` on the file; run `just lamp-check` for all files.

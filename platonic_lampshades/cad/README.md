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
| `dodecahedron/` | `dodecahedron_kit.sc`: panels, upper panels with pattern, brackets, top brackets, top plate, reference solid and reference bodies for socket, nipple and bulb | `panel_x6.dxf` (sketch `PanelLaser`), `upper_panel_x5.dxf` (sketch `UpperPanelLaser`), `top_plate_x1.dxf` (sketch `TopPlateLaser`), `fit_test_x1.dxf` (sketch `FitTestLaser`), `bracket_x25.stl` (body `Bracket`), `top_bracket_x5.stl` (body `TopBracket`) |

Export the DXFs with `sketch.export_dxf {"sketch": ..., "path": ..., "layers": "roles"}`: outline on layer `OUTLINE`, holes on layer `CUT`.
Export the STLs with `file.export {"path": ..., "bodies": [...], "lay_on_print_faces": true}`: each bracket is laid on its end face.

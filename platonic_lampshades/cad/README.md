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
| `dodecahedron/` | `dodecahedron_kit.sc`: panels, brackets and a reference solid in one design | `panel_x12.dxf` (sketch `PanelLaser`), `bracket_x30.stl` (body `Bracket`) |

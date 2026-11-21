# CAD Models

SolidCraft designs (`.sc`) and fabrication exports.

## Access
The SolidCraft MCP server (`.mcp.json` at the repository root) has write access to this folder and to `platonic_lampshades/cad/`.
Start Claude Code from the repository root. The server resolves the paths relative to the working directory.

## Conventions
- One design per part. Assemblies reference the part designs.
- Take dimensions from the base parameters in `../docs/overview.md`. Do not hard-code values that have a parameter.
- Generated exports (`*.stl`, `*.3mf`, `*.step`, `*.dxf`) are not committed. Regenerate them from the designs.

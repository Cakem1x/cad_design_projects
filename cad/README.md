# CAD Models

SolidCraft designs (`.sc`) and fabrication exports.

## Access
The SolidCraft MCP server (`.mcp.json`) has write access to this folder only.
Start Claude Code from the repository root. The server resolves `cad` relative to the working directory.

## Conventions
- One design per part. Assemblies reference the part designs.
- Take dimensions from the base parameters in `docs/overview.md`. Do not hard-code values that have a parameter.
- Generated meshes (`*.stl`, `*.3mf`) are not committed. Regenerate them from the designs.

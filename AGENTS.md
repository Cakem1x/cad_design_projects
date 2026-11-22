# Agent Instructions for solar_cad

## Repository
This repository contains independent parametric CAD projects. Each project is a top-level directory.

| Directory | Project |
|---|---|
| `solar_tube_cooker/` | 3D-printed and laser-cut parts for an evacuated-tube solar cooker |
| `platonic_lampshades/` | Laser-cut lamp shades shaped as Platonic solids |

Shared at the root: `flake.nix`, `Justfile`, `.mcp.json`, `.gitignore`, `LICENSE`, `fabrication/`.

## Environment
The Nix flake (`flake.nix`) defines the development shell.
- Inside an active direnv shell (`use flake`), run tools directly.
- Otherwise, prefix commands with `nix develop -c`.
- If you need additional tools to work effectively, ask user whether to add it to nix flake devshell.
- The `Justfile` runs the generator scripts. List the recipes with `just --list`.

## Generated Files
- DXF files are generated and not committed (`.gitignore`). Laser DXFs are exports of the SolidCraft designs. Input DXFs (for example panel patterns imported with `sketch.insert_dxf`) come from the scripts in `<project>/tools/`.
- Regenerate input files before you use them, so that no outdated state enters a design: run `just lamp-inputs` for `platonic_lampshades/`.
- After a change to a generator script or to its design values, regenerate its outputs with the matching recipe.
- After a DXF export, run `just <prefix>-check` (`lamp-check` for `platonic_lampshades/`). A Claude Code hook runs it after each export through SolidCraft MCP. Fix FAILED results. NOT CHECKED is never a pass.

## Design Values and Checks
- The parameters of the `.sc` designs are the single source of design values. Tools read them with `fabrication/tools/scparams.py`; do not copy values into scripts or docs tables without the check (`just <prefix>-check`).
- Non-geometry values (sheet, provider, rule limits) live in `<project>/fabrication.toml`. Design claims live in `<project>/claims.toml`.
- Before an order, follow the skill `laser-release` (`.claude/skills/laser-release/SKILL.md`).
- Record each mistake a check or test cut finds in `<project>/docs/lessons.md`.
- Activate the git hooks once per clone: `just install-hooks`.

## Documentation Style
Use technical writing for all documentation, including READMEs, comments, and commit messages.
- Use short, declarative sentences.
- State facts. Omit filler, marketing language, and speculation.
- Use the imperative mood for instructions.
- Use consistent terminology. Define a term once and reuse it.
- Specify units for all dimensions (for example, `mm`, `°`).
- Prefer lists and tables over long paragraphs.

## Design Documentation
Read `<project>/docs/overview.md` first. It links to the project's other documents.

## Fabrication
- `fabrication/` holds reference data per fabrication method (limits, operations, design rules). Index: `fabrication/README.md`.
- Read `fabrication/<method>.md` before you design a part for that method.
- Treat its values as rough defaults, not fixed requirements. Adapt them to the machine and material. Project docs take precedence.
- `fabrication/providers/` holds provider-specific data. Read it only at the end of the design process, before export and order.

## CAD Modelling
- Use the SolidCraft MCP server (`.mcp.json`) to create and edit models.
- The SolidCraft app listens for agents on `127.0.0.1:27878` (Preferences › AI). The MCP server bridges to it only while the design has no features. Check with `version` (`mode: app`) before modelling.
- Store designs and exports in `<project>/cad/`. See `<project>/cad/README.md` for conventions.

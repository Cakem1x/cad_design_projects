# CAD Design Projects

Parametric CAD projects for 3D printing and laser cutting.

Heavily AI driven, use with caution.
This repo is a hobby project and somewhat of an experiment on how current AI can be used to interface with software and services to create material stuff via 3D printing and lasercutting.

## Projects

| Directory | Project |
|---|---|
| [`solar_tube_cooker/`](solar_tube_cooker/) | Solar cooker built around an evacuated glass tube |
| [`platonic_lampshades/`](platonic_lampshades/) | Lamp shades shaped as Platonic solids |

Each project has `docs/` (design documentation, start with `docs/overview.md`) and `cad/` (SolidCraft designs).

[`fabrication/`](fabrication/) holds shared reference data for the fabrication methods (for example, laser cutting limits).

## Development environment

The Nix flake provides the development shell. It provides [SolidCraft](https://github.com/tangency-labs/solidcraft) (`solidcraft`, `solidcraft-cli`).

- With direnv: run `direnv allow` once. The shell activates when you enter the directory.
- Without direnv: run `nix develop`.
- Git hooks: run `just install-hooks` once per clone. It sets `core.hooksPath` to `.githooks`. Undo with `git config --unset core.hooksPath`.

## Checks

| Entry point | Checks |
|---|---|
| `just lamp-check` | Parameters (designs, doc tables) and laser DXFs. < 2 s. |
| `just lamp-claims` | Design claims in `<project>/claims.toml`. |
| `just lamp-release` | Strict checks, then copies the order files with `manifest.json`. |
| `.githooks/pre-commit` | Parameter check on commit. |
| `.claude/hooks/dxf_check.sh` | DXF check after each export through SolidCraft MCP. |

Scripts: [`fabrication/tools/`](fabrication/README.md#tools). Settings: `<project>/fabrication.toml`. Tiers and triggers: [`platonic_lampshades/docs/overview.md`](platonic_lampshades/docs/overview.md#checks).

## License

BSD 3-Clause. See [LICENSE](LICENSE).

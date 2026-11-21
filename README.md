# solar_cad

Parametric CAD projects for 3D printing and laser cutting.

## Projects

| Directory | Project |
|---|---|
| [`solar_tube_cooker/`](solar_tube_cooker/) | Solar cooker built around an evacuated glass tube |
| [`platonic_lampshades/`](platonic_lampshades/) | Lamp shades shaped as Platonic solids |

Each project has `docs/` (design documentation, start with `docs/overview.md`) and `cad/` (SolidCraft designs).

## Development environment

The Nix flake provides the development shell. It provides [SolidCraft](https://github.com/tangency-labs/solidcraft) (`solidcraft`, `solidcraft-cli`).

- With direnv: run `direnv allow` once. The shell activates when you enter the directory.
- Without direnv: run `nix develop`.

## License

BSD 3-Clause. See [LICENSE](LICENSE).

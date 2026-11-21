# Agent Instructions for solar_cad

## Project
This repository contains parametric CAD models of 3D-printable parts for a solar cooker.

## Environment
The Nix flake (`flake.nix`) defines the development shell.
- Inside an active direnv shell (`use flake`), run tools directly.
- Otherwise, prefix commands with `nix develop -c`.

## Documentation Style
Use technical writing for all documentation, including READMEs, comments, and commit messages.
- Use short, declarative sentences.
- State facts. Omit filler, marketing language, and speculation.
- Use the imperative mood for instructions.
- Use consistent terminology. Define a term once and reuse it.
- Specify units for all dimensions (for example, `mm`, `°`).
- Prefer lists and tables over long paragraphs.

## Design Documentation
Read `docs/overview.md` first. It links to the optics and component documents.

## CAD Modelling
- Use the SolidCraft MCP server (`.mcp.json`) to create and edit models.
- The SolidCraft app listens for agents on `127.0.0.1:27878` (Preferences › AI). The MCP server bridges to it only while the design has no features. Check with `version` (`mode: app`) before modelling.
- Store designs and exports in `cad/`. See `cad/README.md` for conventions.

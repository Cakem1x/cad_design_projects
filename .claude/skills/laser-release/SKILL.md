---
name: laser-release
description: Prepare laser-cut parts of a project in this repository for an order - regenerate inputs, export the DXFs from SolidCraft, run the checks (just <project>-check, claims), compare the reference render, check the provider limits and write the release with its manifest. Use before ordering laser-cut parts or when asked to release, export for order or preflight laser files.
---

# Laser release

The steps only. Reference data: `fabrication/laser_cutting.md`, `fabrication/providers/`, `<project>/fabrication.toml`, `<project>/docs/overview.md` (BOM, Checks). Project prefix for `platonic_lampshades/`: `lamp`.

1. **Inputs.** Run `just lamp-inputs`. The tools read the design values from the saved `.sc` files: save the designs in SolidCraft first.
2. **Export.** Check `version` (mode `app`). Export each sketch in the Contents table of `<project>/cad/README.md` with `sketch.export_dxf {"sketch": ..., "path": <absolute path>, "layers": "roles"}`. The Claude Code hook checks each export; fix a FAILED result before you continue.
3. **Fast check.** Run `just lamp-check`. Fix every error. Resolve every warning (stale exports, files not in the BOM). Explain each NOT CHECKED to the user: it is never a pass.
4. **Claims.** Run `just lamp-claims`. Run the `APP` claims in the open app: expand the `bodies` globs with `inspect_design {"bodies": "names"}`. K1 takes > 10 min: tell the user before you start it. A result with `pairs_not_checked` > 0 is not a pass. Record each result with the date in the Claims table of `docs/joinery.md`.
5. **Reference render.** Take a `screenshot` of the kit from the same view as `docs/img/shade_render.png` (`camera {"target": [0, 0, 120], "yaw": 0.6, "pitch": 0.4, "distance": 470}`, 610 × 540 px, `grid: false`, `axes: false`) and compare it with `compare_picture`. Report differences to the user. Replace the reference only with the user's approval.
6. **Provider.** Read `fabrication/providers/<provider>.md`. Check the sheet size, the cut colour or layer and the file format. Set `[sheet] provider`, `size` and `measured_thickness` in `fabrication.toml` (ask the user for the measured thickness).
7. **Release.** Run `just lamp-release`. It refuses on any failed check. Report the release folder. Commit `manifest.json` only when the user asks.
8. **Lessons.** Add each mistake found during the release to `docs/lessons.md`.

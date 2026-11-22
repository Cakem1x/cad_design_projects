# Lessons

Mistakes found in the design, by an agent, a check or a test cut, and the rule that now prevents each one. Add an entry when a mistake is found. Move a rule that applies to all laser projects to [laser_cutting.md](../../fabrication/laser_cutting.md).

| Date | What went wrong | Found by | Rule that prevents it |
|---|---|---|---|
| 2026-11 | Keys of adjacent edges came within 19.5 mm of each other at a vertex with `ek` = 50 mm. | Vertex interference test in the model | `ek` = 45 mm. Claim K3 checks "key to edge end" in `joint_keys.py`. |
| 2026-11 | Narrow top plate notches (5 mm, turned 36°) came within 5° of the next lock slot and needed an exact bayonet turn. | Bayonet sweep (claim K4) | Lobes instead of notches; 4.5° play on each side of the 15° turn. |
| 2026-11-22 | `tools/joint_keys.py` used a hard-coded panel inradius `RP` = 71.074 mm after the design changed to 74.164 mm. The "key to edge end" check reported 27.64 mm instead of 29.88 mm. | Parameter refactor | The tools read the design values from the `.sc` files (`tools/design.py`). No copied values. |
| 2026-11-22 | A stale export `panel_x11.dxf` lay next to `panel_x1.dxf`. Either could have been ordered. | `just lamp-check` (rule `bom`) | Laser files must appear in the BOM of [overview.md](overview.md) or in `[dxf.sources]`. `just lamp-release` fails on the warning. |
| 2026-11-22 | The assembled interference check (claim K1) did not finish in the 240 s default budget after the patterns were added: 122 of 165 pairs unchecked. | Claim K1 run | K1 uses `budget_s` = 1800 and runs only before an order. A result with unchecked pairs is not a pass. |

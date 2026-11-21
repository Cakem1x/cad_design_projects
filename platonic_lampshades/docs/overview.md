# Project Overview

## Goal
Design lamp shades shaped as Platonic solids.
Fabrication methods: laser cutting (plywood panels) and FDM 3D printing (connectors).
AI agents build the models in SolidCraft through its MCP server.

The dodecahedron is the first shade. It tests the construction concept.

## Construction
| Term | Definition |
|---|---|
| Panel | Laser-cut plywood plate. One per face of the solid. All panels of a shade are identical. |
| Bracket | 3D-printed angle bracket on the inside of one edge. Bolted to the two panels it joins. One per edge. |
| Inset `s` | Distance each panel edge moves inward from the solid's edge, so that panels with square-cut edges do not collide. `s = t · cot(δ/2)`, with `δ` the dihedral angle. |

- Laser cuts are square to the sheet. Panels touch along their inner corners. Each outer seam is a V-groove.
- The DXF is kerf-compensated: the outline is offset outward and the holes inward by `kerf/2`.

## Dodecahedron prototype
Design: `cad/dodecahedron/dodecahedron_kit.sc`.

| Parameter | Value | Meaning |
|---|---|---|
| `a` | 100 mm | Edge length of the solid (outer panel faces) |
| `t` | 3 mm | Plywood thickness |
| `kerf` | 0.15 mm | Laser kerf width |
| `delta` | 116.565° | Dihedral angle |
| `s` | 1.854 mm | Edge inset (`0.618 · t`) |
| `rp` | 66.965 mm | Panel inradius |
| `Lf` | 16 mm | Bracket flange width |
| `tb` | 4 mm | Bracket wall thickness |
| `Lb` | 30 mm | Bracket length |
| `h` | 9 mm | Hole centre distance from the panel edge |
| `dh` | 3.4 mm | Hole diameter (M3 clearance) |

Derived values:
- Panel: regular pentagon, edge 97.31 mm, 5 holes. Outer V-groove width: 3.2 mm.
- Height of the assembled solid: 222.7 mm.

Bill of materials:
| Item | Count | Source |
|---|---|---|
| Panel, 3 mm plywood | 12 | `panel_x12.dxf` |
| Bracket | 30 | `bracket_x30.stl`, print on one flange, no supports |
| M3 × 10 bolt | 60 | — |
| M3 nut | 60 | — |

## Open points
- Closing the solid: the nuts of the last panel are not reachable from inside. Use heat-set inserts or nut traps in the brackets.
- Light exit: the panels are closed. Define cut-out patterns.
- Lamp fitting: define the socket mount, the cable entry and the suspension.
- Heat: define the lamp type and the maximum power for plywood.

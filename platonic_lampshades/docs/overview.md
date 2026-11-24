# Project Overview

## Goal
Design lamp shades shaped as Platonic solids.
Fabrication method: laser cutting (plywood), see [laser_cutting.md](../../fabrication/laser_cutting.md). No 3D-printed parts.
AI agents build the models in SolidCraft through its MCP server.

The dodecahedron is the first shade. It tests the construction concept.

## Construction
| Term | Definition |
|---|---|
| Panel | Laser-cut plywood plate. One per face of the solid: 12 panels with identical outlines and key slots. |
| Shade | The 12 panels and the 60 keys, joined permanently. The top panel has a central hole `H` for the hub. |
| Key | Laser-cut plywood part in the plane perpendicular to an edge. Its two tabs pass through slots in the two panels it joins and set the dihedral angle. 2 per edge, 50 in total. See [joinery.md](joinery.md). |
| Top panel | The panel in the top face. Penrose P3 pattern of the lower ring with a central hole `H`: round core, 5 rhombus petals towards the vertices, 5 smaller rhombus petals towards the edges. |
| Hub | Two glued plywood layers on the nipple, clamped between the nut and the spacer. Lower layer `L`: carries the shade under the top panel. Upper layer `U`: sits in `H` and locks the turn. Carries the shade through a bayonet. |
| Spacer | 3 laser-cut plywood rings (Ø `Dsp`) between the hub and the socket, `Hsp` high. |
| Inset `s` | Distance each panel edge moves inward from the solid's edge, so that panels with square-cut edges do not collide. `s = t · cot(δ/2)`, with `δ` the dihedral angle. |

- Laser cuts are square to the sheet. Panels touch along their inner corners. Each outer seam is a V-groove.
- The DXFs are kerf-compensated: outlines are offset outward and holes inward by `kerf/2`.
- Joint concept, assembly order and the test coupon: [joinery.md](joinery.md).
- Design values: the parameters of the `.sc` designs are the single source. The tools read them (`tools/design.py`). The parameter tables in the docs are checked against them (`just lamp-check`).
- Checks before export and order: [Checks](#checks). Mistakes found so far and the rules that prevent them: [lessons.md](lessons.md).

### Lamp fitting
The lamp hangs from its cable. The hub is clamped to the socket. The shade hangs on the hub.

Stack from the top, along the axis of the solid:

| Part | Type |
|---|---|
| Strain relief (Zugentlastung) or M10x1 nut with washer | Standard lamp part, on top of the hub. Use a washer of Ø 30 mm. |
| Hub, upper layer `U` | Laser-cut, `t`, in the hole `H` of the top panel |
| Hub, lower layer `L` | Laser-cut, `tp`, under the top panel |
| Spacer | 3 laser-cut rings, `Hsp` |
| E27 socket | Thermoplastic, M10x1 internal thread at the top, screwed onto the nipple and tightened against the spacer |
| A60 bulb | E27 |

- The nipple (Gewindenippel or Gewinderohr M10x1, ≥ `Ln`) runs through the hub and the spacer. The cable runs through the nipple.
- Ceiling attachment: a standard ceiling canopy (Baldachin) holds the cable. It is not part of the shade.
- The cable load passes through the socket, the nipple and the nut into the hub. The shade rests on the points of `L`.

### Bulb change (bayonet)
The shade is a closed body. The hub sits in the top panel: `U` in the hole `H`, `L` under the panel.

- `H`: round core (R 34 mm), 5 rhombus petals to R 68 mm towards the vertices, 5 rhombus petals to R 48 mm towards the edges. The petal sides run parallel to the tile edges.
- `L`: the part of `H` turned by 36° that stays inside it for every turn from 32° to 40°, shrunk by 1.5 mm, and within the inner ends of the keys (r ≤ 57.0 mm). Its 5 points lie under the panel, between the 2 keys of each top edge, and carry the shade. It turns under the panel without touching the keys.
- `U`: the part of `H` that stays inside `H` both at 0° ± 4° and at 36° ± 4°, shrunk by 1.5 mm. Seated, its 10 teeth sit in the petals of `H` and stop the turn (play ±6.6°).
- Play: the hub passes `H` from 30.1° to 41.9° (±5.9°) and drops into its seat from −6.7° to +6.7°. Clearance 1.5 mm all round. No force, no friction: weight holds the shade.
- Generator and checks: `tools/top_panel.py` (part of `just lamp-patterns`).

Remove the shade:
1. Lift the shade by more than `t` (3 mm). `U` leaves `H`.
2. Turn the shade by 36° in either direction. The points of `L` move under the 5 large petals of `H`.
3. Lower the shade. The hub passes up through `H`. The socket and the bulb follow (`H` passes Ø 68 mm).
4. Change the bulb.

Fit the shade:
1. Lift the shade from below over the bulb, turned by about 36° against its seat. The hub passes down through `H`.
2. Lift the shade until `L` is clear of the panel, more than `t + tp` (6 mm) above the seat. Turn the shade back by 36°.
3. Lower the shade. The panel lands on the points of `L`. Turn it until `U` drops into `H` (±6.7°).

### Lamp position
The edge length follows from the socket, so that the bulb centre sits at the centre of the solid:

`ri = t + tp + Hsp + Hs + Lc`, `a = ri / (½·√((25 + 11√5)/10)) = ri / 1.11352`

- `t + tp + Hsp`: the socket top lies below the top panel (`t`), the lower hub layer (`tp`) and the spacer (`Hsp`).
- Measure the socket and the bulb before cutting. Set `Hs` and `Lc`. The shade, the keys and the DXFs follow.
- `Hs`: socket height from its top face to its rim.
- `Lc`: distance from the socket rim to the bulb centre, with the bulb screwed in.

## Dodecahedron prototype
Design: `cad/dodecahedron/dodecahedron_kit.sc`.

| Parameter | Value | Meaning |
|---|---|---|
| `a` | 110.46 mm | Edge length of the solid (outer panel faces). Derived, see Lamp position. |
| `ri` | 123.0 mm | Inradius of the solid |
| `t` | 3 mm | Plywood thickness |
| `kerf` | 0.15 mm | Laser kerf width |
| `delta` | 116.565° | Dihedral angle |
| `s` | 1.854 mm | Edge inset (`0.618 · t`) |
| `rp` | 74.164 mm | Panel inradius |
| `tk` | 3 mm | Key thickness (plywood) |
| `Larm` | 18 mm | Key arm length on the inner face |
| `Dkey` | 9 mm | Key depth, normal to the inner face |
| `htab` | 10 mm | Tab / slot centre from the panel edge |
| `wtab` | 6 mm | Tab width = slot length across the edge |
| `tabout` | 0.3 mm | Tab length beyond the outer face (sand flush) |
| `rrel` | 1.2 mm | Key relief at the inner corner |
| `ek` | 36 mm | Distance between the 2 keys of an edge. Each key arm lies on a tile edge of the panel pattern (see [light_patterns.md](light_patterns.md#key-alignment)). |
| `fitt`, `fitw` | 0 mm | Slot minus key thickness / tab width. Tune with the test coupon. |
| `Hs` | 60 mm | E27 socket height (assumed, measure) |
| `Ds` | 40 mm | E27 socket diameter (reference body only) |
| `Lc` | 48 mm | Socket rim to bulb centre, A60 bulb (assumed, measure) |
| `Db` | 60 mm | Bulb diameter (reference body only) |
| `tp` | 3 mm | Hub layer thickness (`t`) |
| `Hsp` | 9 mm | Spacer height between hub and socket (`3·t`, 3 plywood rings) |
| `Dsp` | 34 mm | Spacer ring diameter |
| `zpl` | 243 mm | Hub seat: inner face of the top panel, top face of `L` (`2·ri − t`) |
| `dn` | 10.5 mm | Nipple hole (M10 clearance) |
| `Ln` | 30 mm | Minimum nipple length: 8 mm in the socket, `Hsp`, `tp`, `t`, 7 mm for nut and washer |

Derived values:
- Panel: regular pentagon, edge 107.77 mm, 10 key slots 3 mm × 6 mm. Outer V-groove width: 3.2 mm.
- Key: 30.6 mm × 16.5 mm. The 10 keys of the top edges are normal keys (`TopKey` bodies).
- Top panel: hole `H` with round core Ø 68 mm, petals to Ø 136 mm (vertices) and Ø 96 mm (edges). Hub: `L` 104.5 mm × 109.7 mm, `U` 82.0 mm × 78.1 mm, 5 rhombus holes, Ø 10.5 mm centre hole. Values from `tools/top_panel.py`.
- Height of the solid: 246.0 mm.
- Clearance from the bulb (Ø 60 mm) to each panel: 93 mm.

Checks in the design: claims J1 to K4 in [joinery.md](joinery.md#claims).

The design contains reference bodies for the socket, the nipple and the bulb. They are not exported. The bodies `HubLower`, `HubUpper` and `Spacer` are laser parts (`hub_x1.dxf`, written by `tools/top_panel.py`).

Bill of materials:
| Item | Count | Source |
|---|---|---|
| Bottom panel, 3 mm plywood, Penrose P3 rim with open core | 1 | `bottom_panel_x1.dxf` |
| Upper ring panel, 3 mm plywood, Penrose P3 pattern | 5 | `upper_panel_x5.dxf` |
| Lower ring panel, 3 mm plywood, Penrose P3 pattern | 5 | `lower_panel_x5.dxf` |
| Top panel, 3 mm plywood, Penrose P3 pattern with hub hole | 1 | `top_panel_x1.dxf` |
| Key, 3 mm plywood | 60 | `key_x60.dxf` |
| Hub (`L`, `U`) and 3 spacer rings, 3 mm plywood | 1 set | `hub_x1.dxf` |
| Wood glue | — | For the keys of the shade and to glue `U` onto `L` |
| M10x1 nipple, ≥ 30 mm | 1 | Lamp parts |
| M10x1 nut and washer Ø 30 mm, or M10x1 strain relief | 1 | Lamp parts |
| E27 socket, thermoplastic, M10x1 internal thread | 1 | Lamp parts |
| Pendant cable and ceiling canopy | 1 | Lamp parts |

## Open points
- Test cut: joint coupon (`joint_test_x1.dxf`) for `fitt`, `fitw`, together with pattern test pieces once the first pattern version is final.
- Bayonet test: cut the top panel and the hub. Check the 36° turn, the ±5.9° pass window and the seat of `U` in `H`.
- Top opening: 26 % of the top is open (pattern, petals of `H`). Light and heat escape upward. Check the heat on the ceiling.
- Socket and bulb dimensions: `Hs` and `Lc` are typical values. Measure the purchased parts.
- Light exit: the panels are closed. Requirements for cutout patterns: [light_patterns.md](light_patterns.md).
- Heat: use LED bulbs only. Define the maximum power for plywood.
- Load: shade mass is about 0.5 kg (plywood 0.65 g/cm³, without pattern cutouts). Check the rating of the cable strain relief.

## Checks
| Tier | Command | Time | Trigger | Checks |
|---|---|---|---|---|
| 0 Generator | `just lamp-patterns`, `just lamp-joint-coupon` | with the generator | each run | pattern bridges and keep-outs, key cross-section rules |
| 1 Fast | `just lamp-check [file.dxf] [--json]` | < 2 s | Claude Code hook after each DXF export through SolidCraft MCP; git pre-commit (parameters only) | parameters: designs agree, doc tables match the designs; laser DXFs: closed contours, duplicates, webs, hole size, islands, layers, sheet fit, BOM, staleness |
| 2 Claims | `just lamp-claims` | headless < 1 s, kit in the app > 10 min | before an order, after a change to joints, bayonet or parameters | [joinery.md](joinery.md#claims) |
| 3 Release | `just lamp-release` | seconds | order | tier 1 strict (warnings fail), headless claims, copy of the BOM files and `manifest.json` to `cad/dodecahedron/release/<date>/` |

Settings (sheet, provider, rule limits, file sources): [../fabrication.toml](../fabrication.toml). Rules: [laser_cutting.md](../../fabrication/laser_cutting.md). Order steps: skill `laser-release` (`.claude/skills/laser-release/SKILL.md`).

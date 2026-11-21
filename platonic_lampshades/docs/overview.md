# Project Overview

## Goal
Design lamp shades shaped as Platonic solids.
Fabrication methods: laser cutting (plywood panels) and FDM 3D printing (connectors).
AI agents build the models in SolidCraft through its MCP server.

The dodecahedron is the first shade. It tests the construction concept.

## Construction
| Term | Definition |
|---|---|
| Panel | Laser-cut plywood plate. One per face of the solid. All panels are identical except the top panel. |
| Top panel | Panel with a centre hole for the lamp nipple and 3 holes for the hub pins. Carries the lamp and the suspension. |
| Bracket | 3D-printed angle bracket on the inside of one edge. Its pins press into the two panels it joins. One per edge. |
| Hub | 3D-printed disc under the top panel, held by its pins. Spaces the socket and spreads its load. |
| Pin | Cylindrical peg printed on a bracket or the hub. Presses into a laser-cut panel hole. |
| Inset `s` | Distance each panel edge moves inward from the solid's edge, so that panels with square-cut edges do not collide. `s = t · cot(δ/2)`, with `δ` the dihedral angle. |

- Laser cuts are square to the sheet. Panels touch along their inner corners. Each outer seam is a V-groove.
- The DXFs are kerf-compensated: the outline is offset outward and the holes inward by `kerf/2`.

### Pins
Pins replace the M3 bolts. They are printed as part of the brackets and the hub.

- Each bracket flange carries 2 pins, Ø `dp` = 4 mm, spaced `ep` along the edge. The bracket has 4 pins.
- The hub carries 3 pins on the circle `rhp`.
- Pin length `Lp = t − 0.3 mm`. The tip stays 0.3 mm below the outer panel face. A 0.4 mm chamfer on the tip guides the pin into the hole.
- Panel hole `dh = dp + fit`. `fit < 0` gives interference (press fit), `fit > 0` gives clearance.
- Press the pins into the panels. Add wood glue between flange and panel for a permanent joint.
- The last panel closes from outside. Its brackets already sit on the neighbouring panels, with their free pins normal to the opening. Press the panel straight onto them.

Print orientation:
- Bracket: stand it on one end face (the 30 mm length is vertical). All pins are then horizontal, with layer lines along the pin axis. No supports.
- Hub: bottom face on the bed, pins up.

Fit test:
1. Laser-cut `fit_test_x1.dxf` from the panel plywood. It has 7 holes, `dp + fit` −0.15 mm to +0.15 mm in 0.05 mm steps, smallest next to the small marker hole.
2. Print one bracket.
3. Press a pin into each hole. Pick the hole that holds the pin firmly without splitting the plywood.
4. Add that hole's offset to `fit`. Re-export the DXFs.

### Lamp fitting
The lamp hangs from its cable. The cable load passes through the socket, the nipple and the hub into the top panel.

Stack from the top, along the axis of the solid:

| Part | Type |
|---|---|
| Strain relief (Zugentlastung) or M10x1 nut with washer | Standard lamp part, on top of the top panel |
| Top panel | Laser-cut, `t` |
| Hub | Printed, `th` |
| E27 socket | Thermoplastic, M10x1 internal thread at the top, screwed onto the nipple and tightened against the hub |
| A60 bulb | E27 |

- The nipple (Gewindenippel or Gewinderohr M10x1) runs through the top panel and the hub. The cable runs through the nipple.
- Ceiling attachment: a standard ceiling canopy (Baldachin) holds the cable. It is not part of the shade.

### Lamp position
The edge length follows from the socket, so that the bulb centre sits at the centre of the solid:

`ri = t + th + Hs + Lc`, `a = ri / (½·√((25 + 11√5)/10)) = ri / 1.11352`

- Measure the socket and the bulb before cutting. Set `Hs` and `Lc`. The shade, the brackets and the DXFs follow.
- `Hs`: socket height from its top face to its rim.
- `Lc`: distance from the socket rim to the bulb centre, with the bulb screwed in.

## Dodecahedron prototype
Design: `cad/dodecahedron/dodecahedron_kit.sc`.

| Parameter | Value | Meaning |
|---|---|---|
| `a` | 105.07 mm | Edge length of the solid (outer panel faces). Derived, see Lamp position. |
| `ri` | 117.0 mm | Inradius of the solid |
| `t` | 3 mm | Plywood thickness |
| `kerf` | 0.15 mm | Laser kerf width |
| `delta` | 116.565° | Dihedral angle |
| `s` | 1.854 mm | Edge inset (`0.618 · t`) |
| `rp` | 70.456 mm | Panel inradius |
| `Lf` | 16 mm | Bracket flange width |
| `tb` | 4 mm | Bracket wall thickness |
| `Lb` | 30 mm | Bracket length |
| `h` | 9 mm | Pin centre distance from the panel edge |
| `ep` | 16 mm | Pin spacing along the edge |
| `dp` | 4 mm | Pin diameter |
| `Lp` | 2.7 mm | Pin length (`t − 0.3 mm`) |
| `fit` | 0 mm | Panel hole minus pin diameter. Tune with the fit test. |
| `dh` | 4.0 mm | Pin hole in panels (`dp + fit`, nominal) |
| `Hs` | 60 mm | E27 socket height (assumed, measure) |
| `Ds` | 40 mm | E27 socket diameter (reference body only) |
| `Lc` | 48 mm | Socket rim to bulb centre, A60 bulb (assumed, measure) |
| `Db` | 60 mm | Bulb diameter (reference body only) |
| `th` | 6 mm | Hub thickness |
| `Dhub` | 60 mm | Hub diameter |
| `rhp` | 20 mm | Hub pin circle radius |
| `dn` | 10.5 mm | Nipple hole (M10 clearance) |
| `Ln` | 24 mm | Minimum nipple length: 8 mm in the socket, `th`, `t`, 7 mm for nut and washer |

Derived values:
- Panel: regular pentagon, edge 102.38 mm, 10 pin holes. Outer V-groove width: 3.2 mm.
- Top panel: as panel, plus a Ø 10.5 mm centre hole and 3 pin holes on `rhp`.
- Bracket: 4 pins, Ø 4 mm × 2.7 mm.
- Height of the assembled solid: 234.0 mm.
- Clearance from the bulb (Ø 60 mm) to each panel: 87 mm.

The design contains reference bodies for the socket, the nipple and the bulb. They are not exported.

Bill of materials:
| Item | Count | Source |
|---|---|---|
| Panel, 3 mm plywood | 11 | `panel_x11.dxf` |
| Top panel, 3 mm plywood | 1 | `top_panel_x1.dxf` |
| Bracket | 30 | `bracket_x30.stl`, print standing on one end face, no supports |
| Hub | 1 | `hub_x1.stl`, PETG, pins up |
| Fit test strip, 3 mm plywood | 1 | `fit_test_x1.dxf` |
| Wood glue | — | Optional, see Pins |
| M10x1 nipple, ≥ 25 mm | 1 | Lamp parts |
| M10x1 nut and washer, or M10x1 strain relief | 1 | Lamp parts |
| E27 socket, thermoplastic, M10x1 internal thread | 1 | Lamp parts |
| Pendant cable and ceiling canopy | 1 | Lamp parts |

## Open points
- Bulb change: all 12 panels are glued, so the bulb is not reachable. Options: a bottom panel held by magnets, or a bottom panel with an opening of about Ø 95 mm.
- Pin fit: run the fit test before cutting all panels.
- Socket and bulb dimensions: `Hs` and `Lc` are typical values. Measure the purchased parts.
- Light exit: the panels are closed. Define cut-out patterns.
- Heat: use LED bulbs only. Define the maximum power for plywood and for the printed hub.
- Load: shade mass is about 0.6 kg. Check the rating of the cable strain relief.

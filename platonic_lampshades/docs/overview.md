# Project Overview

## Goal
Design lamp shades shaped as Platonic solids.
Fabrication methods: laser cutting (plywood panels) and FDM 3D printing (connectors).
AI agents build the models in SolidCraft through its MCP server.

The dodecahedron is the first shade. It tests the construction concept.

## Construction
| Term | Definition |
|---|---|
| Panel | Laser-cut plywood plate. One per face of the solid except the top face. 11 identical panels. |
| Shade | The 11 panels and the 30 brackets, joined permanently. Open at the top face. |
| Top plate | Laser-cut plywood disc with 5 notches. Bolted to the socket. Carries the shade through a bayonet. Replaces the top panel. |
| Bracket | 3D-printed angle bracket on the inside of one edge. Its pins press into the two panels it joins. 25 brackets. |
| Top bracket | Bracket on one of the 5 edges of the top face. 2 pins into the side panel, 1 lock pin pointing down into the top plate. |
| Pin | Cylindrical peg printed on a bracket. Presses into a laser-cut panel hole. |
| Lock pin | Pin on a top bracket. Sits loose in a clearance hole of the top plate and stops the shade from turning. |
| Inset `s` | Distance each panel edge moves inward from the solid's edge, so that panels with square-cut edges do not collide. `s = t · cot(δ/2)`, with `δ` the dihedral angle. |

- Laser cuts are square to the sheet. Panels touch along their inner corners. Each outer seam is a V-groove.
- The DXFs are kerf-compensated: the outline is offset outward and the holes inward by `kerf/2`.

### Pins
Pins replace the M3 bolts. They are printed as part of the brackets.

- Each bracket flange carries 2 pins, Ø `dp` = 4 mm, spaced `ep` along the edge. The bracket has 4 pins.
- A top bracket has 2 pins on its side-panel flange and 1 lock pin on its top flange. See Bulb change.
- Pin length `Lp = t − 0.3 mm`. The tip stays 0.3 mm below the outer panel face. A 0.4 mm chamfer on the tip guides the pin into the hole.
- Panel hole `dh = dp + fit`. `fit < 0` gives interference (press fit), `fit > 0` gives clearance.
- Press the pins into the panels. Add wood glue between flange and panel for a permanent joint.
- The last panel closes from outside. Its brackets already sit on the neighbouring panels, with their free pins normal to the opening. Press the panel straight onto them.

Print orientation:
- Bracket: stand it on one end face (the 30 mm length is vertical). All pins are then horizontal, with layer lines along the pin axis. No supports.
- Top bracket: the same. The exports are laid on their print face.

Fit test:
1. Laser-cut `fit_test_x1.dxf` from the panel plywood. It has 7 holes, `dp + fit` −0.15 mm to +0.15 mm in 0.05 mm steps, smallest next to the small marker hole.
2. Print one bracket (not a top bracket).
3. Press a pin into each hole. Pick the hole that holds the pin firmly without splitting the plywood.
4. Add that hole's offset to `fit`. Re-export the DXFs.

### Lamp fitting
The lamp hangs from its cable. The top plate is clamped to the socket. The shade hangs on the top plate.

Stack from the top, along the axis of the solid:

| Part | Type |
|---|---|
| Strain relief (Zugentlastung) or M10x1 nut with washer | Standard lamp part, on top of the top plate. Use a large washer (Ø ≥ 30 mm). |
| Top plate | Laser-cut, `tp` |
| E27 socket | Thermoplastic, M10x1 internal thread at the top, screwed onto the nipple and tightened against the top plate |
| A60 bulb | E27 |

- The nipple (Gewindenippel or Gewinderohr M10x1) runs through the top plate. The cable runs through the nipple.
- Ceiling attachment: a standard ceiling canopy (Baldachin) holds the cable. It is not part of the shade.
- The cable load passes through the socket, the nipple and the nut into the top plate.

### Bulb change (bayonet)
The shade is a closed body except for the top face. The top plate sits inside the shade, under the 5 top brackets.

- Top plate: disc of radius `Rpl` with 5 notches. A notch is `2·wn` wide and reaches in to radius `Rn`. A top bracket's top flange fits through a notch.
- Assembled state: the top flanges rest on the plate between the notches. The lock pins sit in the clearance holes `dlock`.
- The plate passes the top opening of the shade with `cb` clearance. The socket (Ø 40 mm) and the bulb (Ø 60 mm) pass too.
- Weight holds the shade on the plate. No glue, no friction at the lock pins.

Remove the shade:
1. Lift the shade by more than `Lpl` (2.5 mm). The lock pins leave their holes.
2. Turn the shade by 36° in either direction. The notches line up with the top brackets.
3. Lower the shade. The plate passes the top brackets and the top opening. The socket and the bulb follow.
4. Change the bulb.

Fit the shade:
1. Lift the shade from below over the bulb. The plate enters the top opening and passes the top brackets through the notches.
2. Turn the shade by 36°.
3. Lower the shade until the top brackets rest on the plate and the lock pins drop into their holes.

### Lamp position
The edge length follows from the socket, so that the bulb centre sits at the centre of the solid:

`ri = t + tb + tp + Hs + Lc`, `a = ri / (½·√((25 + 11√5)/10)) = ri / 1.11352`

- `t + tb`: the top plate sits under the top flange of the top brackets, `t + tb` below the outer top face.
- Measure the socket and the bulb before cutting. Set `Hs` and `Lc`. The shade, the brackets and the DXFs follow.
- `Hs`: socket height from its top face to its rim.
- `Lc`: distance from the socket rim to the bulb centre, with the bulb screwed in.

## Dodecahedron prototype
Design: `cad/dodecahedron/dodecahedron_kit.sc`.

| Parameter | Value | Meaning |
|---|---|---|
| `a` | 105.97 mm | Edge length of the solid (outer panel faces). Derived, see Lamp position. |
| `ri` | 118.0 mm | Inradius of the solid |
| `t` | 3 mm | Plywood thickness |
| `kerf` | 0.15 mm | Laser kerf width |
| `delta` | 116.565° | Dihedral angle |
| `s` | 1.854 mm | Edge inset (`0.618 · t`) |
| `rp` | 71.074 mm | Panel inradius |
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
| `tp` | 3 mm | Top plate thickness (`t`) |
| `cb` | 1 mm | Bayonet clearance |
| `Rpl` | 67.60 mm | Top plate radius (`rp − tb·cot(δ/2) − cb`) |
| `Rn` | 54.07 mm | Notch bottom radius (`rp − Lf − cb`) |
| `wn` | 16 mm | Notch half width (`Lb/2 + cb`) |
| `Lpl` | 2.5 mm | Lock pin length (`tp − 0.5 mm`) |
| `dlock` | 4.5 mm | Lock pin hole in the top plate (`dp + 0.5 mm`, clearance) |
| `zpl` | 229 mm | Height of the top plate's upper face (`2·ri − t − tb`) |
| `dn` | 10.5 mm | Nipple hole (M10 clearance) |
| `Ln` | 18 mm | Minimum nipple length: 8 mm in the socket, `tp`, 7 mm for nut and washer |

Derived values:
- Panel: regular pentagon, edge 103.28 mm, 10 pin holes. Outer V-groove width: 3.2 mm.
- Top plate: Ø 135.2 mm, 5 notches 32 mm wide, Ø 10.5 mm centre hole, 5 lock pin holes Ø 4.5 mm on radius `rp − h`.
- Bracket: 4 pins, Ø 4 mm × 2.7 mm. Top bracket: 2 pins and 1 lock pin, Ø 4 mm × 2.5 mm.
- Height of the solid: 236.0 mm.
- Clearance from the bulb (Ø 60 mm) to each panel: 88 mm.

Checks in the design (interference):
- Assembled: no part overlaps another.
- Plate turned 36° and moved from 3 mm below to 9 mm above its seat: no contact with the shade.
- Negative check: plate not turned, 4.5 mm up, hits the top brackets.

The design contains reference bodies for the socket, the nipple and the bulb. They are not exported.

Bill of materials:
| Item | Count | Source |
|---|---|---|
| Panel, 3 mm plywood | 11 | `panel_x11.dxf` |
| Top plate, 3 mm plywood | 1 | `top_plate_x1.dxf` |
| Bracket | 25 | `bracket_x25.stl`, laid on its end face, no supports |
| Top bracket | 5 | `top_bracket_x5.stl`, laid on its end face, no supports |
| Fit test strip, 3 mm plywood | 1 | `fit_test_x1.dxf` |
| Wood glue | — | Optional, for the shade only, see Pins |
| M10x1 nipple, ≥ 20 mm | 1 | Lamp parts |
| M10x1 nut and washer Ø ≥ 30 mm, or M10x1 strain relief | 1 | Lamp parts |
| E27 socket, thermoplastic, M10x1 internal thread | 1 | Lamp parts |
| Pendant cable and ceiling canopy | 1 | Lamp parts |

## Open points
- Fit test: cut `fit_test_x1.dxf`, print one bracket, set `fit`. Do this before cutting the panels.
- Bayonet test: cut the top plate and print the 5 top brackets early. Check the 36° turn and the seat of the lock pins.
- Top opening: the notches of the top plate are open. Light and heat escape upward. Check the look from below and the heat on the ceiling.
- Socket and bulb dimensions: `Hs` and `Lc` are typical values. Measure the purchased parts.
- Light exit: the panels are closed. Requirements for cutout patterns: [light_patterns.md](light_patterns.md).
- Heat: use LED bulbs only. Define the maximum power for plywood and the printed brackets.
- Load: shade mass is about 0.6 kg. Check the rating of the cable strain relief.

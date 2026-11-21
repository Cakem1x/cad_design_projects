# Project Overview

## Goal
Design lamp shades shaped as Platonic solids.
Fabrication method: laser cutting (plywood). No 3D-printed parts.
AI agents build the models in SolidCraft through its MCP server.

The dodecahedron is the first shade. It tests the construction concept.

## Construction
| Term | Definition |
|---|---|
| Panel | Laser-cut plywood plate. One per face of the solid except the top face. 11 identical panels. |
| Shade | The 11 panels, the 50 keys and the 10 lug keys, joined permanently. Open at the top face. |
| Key | Laser-cut plywood part in the plane perpendicular to an edge. Its two tabs pass through slots in the two panels it joins and set the dihedral angle. 2 per edge, 50 in total. See [joinery.md](joinery.md). |
| Lug key | Key on one of the 5 top edges. One tab into the upper ring panel; its lower edge rests on the top plate; a lock tab drops into a slot of the top plate. 10 in total. |
| Top plate | Laser-cut plywood plate: core disc with 10 lobes and 10 lock slots. Bolted to the socket. Carries the shade through a bayonet. Replaces the top panel. |
| Inset `s` | Distance each panel edge moves inward from the solid's edge, so that panels with square-cut edges do not collide. `s = t · cot(δ/2)`, with `δ` the dihedral angle. |

- Laser cuts are square to the sheet. Panels touch along their inner corners. Each outer seam is a V-groove.
- The DXFs are kerf-compensated: outlines are offset outward and holes inward by `kerf/2`.
- Joint concept, assembly order and the test coupon: [joinery.md](joinery.md).

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
The shade is a closed body except for the top face. The top plate sits inside the shade, under the 10 lug keys.

- Top plate: core disc of radius `Rnk` with 10 lobes, `wlb` wide, out to radius `Rpl`. One lobe sits under each lug key and carries its lock slot. Between the lobes the plate is open down to `Rnk`.
- Assembled state: the lower edges of the lug keys rest on the plate. The lock tabs sit in the lock slots (clearance `clock`).
- The plate passes the top opening of the shade with 2 mm clearance. The socket (Ø 40 mm) and the bulb (Ø 60 mm) pass too.
- Weight holds the shade on the plate. No glue, no friction at the lock tabs.

Remove the shade:
1. Lift the shade by more than `Lpl` (2.5 mm). The lock tabs leave their slots.
2. Turn the shade by `turn` (15°) in either direction. The lobes move into the gaps between the lug keys. The turn has about ±4.5° play (free from about 10.5° to 19.5°).
3. Lower the shade. The plate passes the lug keys and the top opening. The socket and the bulb follow.
4. Change the bulb.

Fit the shade:
1. Lift the shade from below over the bulb, turned by about 15° against its seat. The plate enters the top opening and the lobes pass between the lug keys.
2. Turn the shade back by 15°.
3. Lower the shade until the lug keys rest on the plate and the lock tabs drop into their slots.

### Lamp position
The edge length follows from the socket, so that the bulb centre sits at the centre of the solid:

`ri = t + Dkey + tp + Hs + Lc`, `a = ri / (½·√((25 + 11√5)/10)) = ri / 1.11352`

- `t + Dkey`: the top plate sits under the lug keys, `t + Dkey` below the outer top face.
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
| `ek` | 45 mm | Distance between the 2 keys of an edge. Each key lies on a trellis bar of the panel pattern (see [light_patterns.md](light_patterns.md#pattern)). |
| `fitt`, `fitw` | 0 mm | Slot minus key thickness / tab width. Tune with the test coupon. |
| `hlock` | 14 mm | Lug key lock tab centre from the inner corner |
| `wlock` | 4 mm | Lug key lock tab width |
| `Lpl` | 2.5 mm | Lock tab length (`tp − 0.5 mm`) |
| `clock` | 0.5 mm | Lock tab clearance in the top plate slot |
| `Hs` | 60 mm | E27 socket height (assumed, measure) |
| `Ds` | 40 mm | E27 socket diameter (reference body only) |
| `Lc` | 48 mm | Socket rim to bulb centre, A60 bulb (assumed, measure) |
| `Db` | 60 mm | Bulb diameter (reference body only) |
| `tp` | 3 mm | Top plate thickness (`t`) |
| `cb` | 1 mm | Bayonet clearance |
| `Rpl` | 71.25 mm | Top plate outer radius (lobe ends): `√((rp − Dkey·cot(δ/2) − cb)² + (ek/2)²)`, clears the lug key bodies in their planes |
| `Rnk` | 55.16 mm | Top plate core radius (`rp − Larm − cb`): clears the inner ends of the lug keys |
| `wlb` | 14 mm | Top plate lobe width. 5 mm web on each side of the lock slot. |
| `turn` | 15° | Bayonet turn. Reference value for the checks; no geometry depends on it. |
| `zpl` | 234 mm | Height of the top plate's upper face (`2·ri − t − Dkey`) |
| `dn` | 10.5 mm | Nipple hole (M10 clearance) |
| `Ln` | 18 mm | Minimum nipple length: 8 mm in the socket, `tp`, 7 mm for nut and washer |

Derived values:
- Panel: regular pentagon, edge 107.77 mm, 10 key slots 3 mm × 6 mm. Outer V-groove width: 3.2 mm.
- Key: 30.6 mm × 16.5 mm. Lug key: same outline without the top tab, with a 4 mm × 2.5 mm lock tab.
- Top plate: core Ø 110.3 mm, 10 lobes 14 mm wide to Ø 142.5 mm, 10 lock slots 4 mm × 5 mm, Ø 10.5 mm centre hole.
- Height of the solid: 246.0 mm.
- Clearance from the bulb (Ø 60 mm) to each panel: 93 mm.

Checks in the design:
- Interference, assembled: no overlap between the 11 panels, the 50 keys, the 10 lug keys and the top plate (145 pairs).
- Bayonet: the plate, 3 mm below its seat, turns from 0° to 15° without contact. Turned 15°, it moves from 3 mm below its seat to above the top opening without contact. Play at 6 mm lift: free from 10.5° to 19.5°; 7.5° and 21° hit the lug keys. Negative check: not turned, 5 mm up, it hits all 10 lug keys.
- Parameters: `t`, `tk`, `Dkey`, `ek`, `Hs` changed together rebuild without errors; the bulb centre stays at `ri`.

The design contains reference bodies for the socket, the nipple and the bulb. They are not exported.

Bill of materials:
| Item | Count | Source |
|---|---|---|
| Bottom panel, 3 mm plywood, plain | 1 | `panel_x1.dxf` |
| Upper ring panel, 3 mm plywood, Marrakech pattern | 5 | `upper_panel_x5.dxf` |
| Lower ring panel, 3 mm plywood, Marrakech pattern | 5 | `lower_panel_x5.dxf` |
| Key, 3 mm plywood | 50 | `key_x50.dxf` |
| Lug key, 3 mm plywood | 10 | `lug_key_x10.dxf` |
| Top plate, 3 mm plywood | 1 | `top_plate_x1.dxf` |
| Wood glue | — | For the keys of the shade, not for the lug key lock tabs |
| M10x1 nipple, ≥ 20 mm | 1 | Lamp parts |
| M10x1 nut and washer Ø ≥ 30 mm, or M10x1 strain relief | 1 | Lamp parts |
| E27 socket, thermoplastic, M10x1 internal thread | 1 | Lamp parts |
| Pendant cable and ceiling canopy | 1 | Lamp parts |

## Open points
- Test cut: joint coupon (`joint_test_x1.dxf`) for `fitt`, `fitw`, together with pattern test pieces once the first pattern version is final.
- Bayonet test: cut the top plate and the lug keys. Check the 15° turn and the seat of the lock tabs.
- Top opening: the gaps between the lobes of the top plate are open. Light and heat escape upward. Check the look from below and the heat on the ceiling.
- Top plate shape: functional draft (core disc and 10 lobes). Adapt its look to the Marrakech pattern at the end.
- Socket and bulb dimensions: `Hs` and `Lc` are typical values. Measure the purchased parts.
- Light exit: the panels are closed. Requirements for cutout patterns: [light_patterns.md](light_patterns.md).
- Heat: use LED bulbs only. Define the maximum power for plywood.
- Load: shade mass is about 0.5 kg (plywood 0.65 g/cm³, without pattern cutouts). Check the rating of the cable strain relief.

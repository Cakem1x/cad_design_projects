# Components and Design Options

Status: first outline. Detail decisions are made during CAD modelling.

## C1: Feet
Function: support the tube at two positions, hold the arm pair angle, stand stable on the ground.

Decisions:
- Both feet are identical.
- Each foot sits in a clear end zone (`clear_end`), not necessarily at the very tube end.
- Cradle: a quarter-circle seat below the tube. An elastic band over the tube holds it. The band ends sit in grooves or notches on both sides of the foot.
- The foot does not enclose the tube. The pivot is in the arm pair (see C2).

Constraints:
- A foot below the tube inside the reflector span collides with the cusp region. Keep the foot outside the reflector span, in the clear end zone.
- The cradle holds the tube against rotation (R1). Use a high-friction liner (rubber). The arm pair ring uses a low-friction liner.
- Tube: Ø 125 mm, 2.5 kg plus food. Soft contact on the glass (silicone, EPDM or cork liner).
- The outer glass stays near ambient temperature (vacuum insulation). Parts in the focal region can still get hot from concentrated sunlight.
- The tray end must stay accessible.
- Tube axis height: set by the tilt range (see [optics.md](optics.md)). At 80° tilt (`min_sun_elevation` = 10°), the lowest reflector point is 325 mm below the tube axis. Tube axis height: approx. 350–380 mm.
- Wind: wide footprint, ground pegs or ballast.

Construction options:
| Option | Description | Assessment |
|--------|-------------|------------|
| F1 | Laser-cut plywood frame (A-frame or trestle), slot-and-tab joints. | Large and stiff, flat-packable. Recommended for the structure. |
| F2 | 3D-printed parts. | Limited by 256 mm bed. Use for liners, clamps, knobs, connectors. |
| F3 | Hybrid: plywood structure + printed tube cradle and pivot parts. | Recommended overall. |

## C2: Arms
Function: define the CPC profile. Attach to the foot. Rotate about the tube axis. Lock in position. Carry the ribs.

Layout:
- One arm per CPC branch. Arm length (straight line, cusp to aperture edge): 707 mm. Arc length: 806 mm (θa = 20°, H = 600).
- Arm pair: left and right arm at one foot. Two arm pairs, 4 arms in total.
- The arms of a pair join around the tube, next to the foot, inboard of the foot. The joint separates for transport.
- The arm pair joint fixes the relative geometry of both branches. The arm pair rotates as one rigid unit.
- Pivot: the arm pair ring rotates on the tube (P4). The foot only locks the angle.
- Axial order per end: tube end, foot, arm pair, rib mats. Foot and arm pair ring fit in `clear_end`.

Constraints:
- The tube has no axle. The pivot must be concentric with the tube, outside the glass.
- A ring bearing around the tube occupies the space where the CPC cusp sits close to the glass. A full ring in the arm pair is not possible there.

Pivot options (arm-to-foot joint):
| Option | Description | Assessment |
|--------|-------------|------------|
| P1 | Ring bearing: the arm pair rotates on a collar around the tube. | Compact. Conflicts with the cusp region. Possible only if the collar is axially outside the reflector span. |
| P2 | Arc guide: curved slot in the foot, concentric with the tube axis, at a large radius (approx. 200–300 mm). Bolts in each arm run in the slot. Lock with a wing nut. | No conflict with the cusp. Continuous adjustment. Laser-cuttable. Each arm attaches separately. Recommended starting point. |
| P3 | Rollers: the arm pair has a circular track segment that rests on 2–3 rollers on the foot. | Smooth movement. More parts. |

| P4 | Arm pair ring on the tube: each arm has a ring section around the tube. The two ring sections overlap and lock with a bayonet joint (pins in slots, locked by rotating the arms against each other). The ring rotates on the glass with a low-friction liner (felt, PTFE tape). | Concentric with the tube by construction. No conflict with the cusp: the ring sits in the clear end zone, outside the reflector span. Load on the glass: check contact pressure. Rib channel of the outer arm passes the ring of the inner arm near the cusp: resolve in the layout. Selected starting point. |

Locking options: friction clamp (wing nut), index holes every 5°, or both.

Material: laser-cut plywood. One arm is approx. 420 × 600 mm (bounding box). One piece per arm (`laser_bed` is sufficient).
Rib mounting: see [Rib-to-arm joint](#rib-to-arm-joint).
Optional: end mirrors on the arms to reduce end losses.

## C3: Ribs
Function: reflective surface. All ribs together form the reflector.

- Rectangular plywood strips. Long side parallel to the tube axis. Length ≥ `useful_length` (650 mm) plus the engagement in the arms at both ends.
- Reflective foil glued onto the front face.
- Rib mat: all ribs of one branch, joined on the back by fabric or tape strips. One rib mat per branch, 2 in total. Rolls up about an axis parallel to the tube.
- Each rib spans from one arm pair to the other and attaches to both.
- The ribs approximate the CPC curve with flat facets.

Slope error of facets: a facet of width `w` on a curve with radius of curvature `R` has a slope error up to `w / (2R)`. The reflected ray deviates by up to `w / R`. Keep the deviation well below θa.

Maximum rib width along the profile (θa = 20°, H = 600, `s` = arc length from the cusp):
| `s` | R | `w` for 5° deviation | `w` for 2.5° deviation |
|-----|---|----------------------|------------------------|
| 25 | 61 | 5 | 3 |
| 50 | 81 | 7 | 4 |
| 100 | 206 | 18 | 9 |
| 200 | 372 | 32 | 16 |
| 300 | 593 | 52 | 26 |
| 400 | 876 | 76 | 38 |
| 500 | 1213 | 106 | 53 |
| 600 | 1601 | 140 | 70 |
| 700 | 2034 | 178 | 89 |

All values in mm. Consequences:
- Upper part (`s` > 400 mm): ribs 50–100 mm wide are acceptable.
- Lower part (`s` < 150 mm): ribs must be very narrow. Options: a flexible strip (aluminium, PET) bent into the arm profile, or accept the error near the cusp (part of this region is removed by the gap treatment, see [optics.md](optics.md#gap-between-reflector-and-absorber)).

### Rib-to-arm joint
Loads:
- Gravity. The direction relative to the arm changes with the tilt (26–80°). At large tilt, one rib mat faces partly downwards: gravity pulls the ribs off the arm.
- Wind. Pressure and suction on the rib mat (aperture area approx. 0.55 m²).

Requirements:
- Hold each rib against the arm profile in both directions (towards and away from the arm).
- Attach and detach the rib mat by hand in a few steps, without tools.
- Keep each rib on the profile within the slope-error budget (see table above).

Note: tension alone does not hold the rib mat. The rib mat lies on the concave side of the profile. Tension pulls it straight and lifts it off the arm.

Options:
| Option | Description | Assessment |
|--------|-------------|------------|
| J1 | Guide channel: a curved channel along the profile on the inner face of each arm (two plywood layers with an offset). The rib ends run in the channel. Insert the rib mat at the aperture end and slide it down to the cusp. Lock with one pin per channel at the aperture end. | Principle of a roller shutter guide rail. Holds in both directions. Few steps. Channel clearance adds slope error. Recommended starting point. |
| J2 | Pins or tabs on the rib ends in keyhole slots in the arm. | Positive hold. One action per rib: slow for many ribs. |
| J3 | Magnets in the rib ends and the arm edge. | Fast. Holding force limited. Wind and heat (magnet temperature) are risks. |
| J4 | Elastic straps or hook-and-loop over the rib mat ends. | Simple. Position on the profile less defined. |

## Alternatives to the Overall Concept
| Alternative | Assessment |
|-------------|------------|
| Continuous flexible sheet (0.3–0.8 mm aluminium, PET or polycarbonate) instead of ribs | No facets, best optical quality. Rolls up. Fallback for the lower reflector part if ribs near the cusp are too narrow. |
| Kerf-bent plywood (living hinge) instead of ribs | The foil surface shows the kerf pattern. Not recommended for optics. |
| V-trough (flat mirrors) | Simpler, lower concentration. Fallback if the CPC is too complex. |
| Parabolic trough | Higher concentration but needs precise tracking. Not suitable for manual tracking. |
| Rotate tube and reflector together | Tilts the tray. Violates R1. Rejected. |
| Fixed reflector with wide θa (no elevation adjustment) | Possible with θa ≥ 35°. Lower concentration. Keep as a configuration of the same design. |

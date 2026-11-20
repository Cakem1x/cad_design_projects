# Components and Design Options

Status: first outline. Detail decisions are made during CAD modelling.

## C1: Feet
Function: support the tube at two positions, carry the pivot of the reflector frame, stand stable on the ground.

Constraints:
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

## C2: Reflector Frame (Arms / Ribs)
Function: hold the reflector sheet in the CPC profile. Rotate about the tube axis. Lock in position.

Analysis of the initial concept (separate arms that rotate about the tube centre):
- Both branches must keep their relative geometry. Connect both arms at each end into one rigid rib (U-shaped CPC profile). Two ribs, one per foot, connected by longitudinal members.
- The tube has no axle. The pivot must be concentric with the tube, outside the glass.
- Conflict: a ring bearing around the tube occupies the space where the CPC cusp sits close to the glass. A full ring in the rib is not possible there.

Pivot options:
| Option | Description | Assessment |
|--------|-------------|------------|
| P1 | Ring bearing: rib rotates on a collar around the tube. | Compact. Conflicts with the cusp region. Possible only if the rib is axially outside the reflector span. |
| P2 | Arc guide: curved slot in the foot, concentric with the tube axis, at a large radius (approx. 200–300 mm). Bolts in the rib run in the slot. Lock with a wing nut. | No conflict with the cusp. Continuous adjustment. Laser-cuttable. Recommended starting point. |
| P3 | Rollers: rib has a circular track segment that rests on 2–3 rollers on the foot. | Smooth movement. More parts. |

Locking options: friction clamp (wing nut), index holes every 5°, or both.

Rib material: laser-cut plywood. The profile is planar and approx. 841 × 600 mm (θa = 20°, H = 600). This likely exceeds the laser bed: split each rib into joined segments, or use separate arms per branch (approx. 420 × 600 mm each, straight length 707 mm).
Sheet mounting on the rib: groove along the profile edge, or printed clips.
Optional: a middle rib for stiffness, end mirrors on the ribs to reduce end losses.

## C3: Reflector Sheet
Function: reflective surface in the CPC profile. Rolls up for transport.
Size per branch: approx. 806 mm (arc length, θa = 20°, H = 600) × ≥ 650 mm (tube direction). The two branches meet at the cusp below the tube. Use two separate sheets.

The sheet bends only in the cross-section plane. It rolls up about an axis parallel to the tube.

| Option | Description | Assessment |
|--------|-------------|------------|
| S1 | Continuous flexible sheet (0.3–0.8 mm aluminium, PET or polycarbonate), with foil or pre-mirrored. Pressed into the rib grooves. | No facets, best optical quality, fewest parts. The curved shape stiffens the sheet along the tube. Recommended starting point. |
| S2 | Tambour: rigid slats parallel to the tube axis, joined by a flexible backing (fabric, tape). | Rolls up well. Facets cause slope errors. Error grows near the cusp (small curvature radius). Slats approx. 700 mm long: check laser bed size or use stock strips. |
| S3 | Laser-cut kerf-bent plywood (living hinge). | Flexible plywood. The foil surface shows the kerf pattern. Not recommended for optics. |

Slope error of facets (S2): a facet of width `w` on a curve with radius of curvature `R` has a slope error up to `w / (2R)`. The reflected ray deviates by twice this value. Keep the deviation well below θa.

## Alternatives to the Overall Concept
| Alternative | Assessment |
|-------------|------------|
| V-trough (flat mirrors) | Simpler, lower concentration. Fallback if the CPC is too complex. |
| Parabolic trough | Higher concentration but needs precise tracking. Not suitable for manual tracking. |
| Rotate tube and reflector together | Tilts the tray. Violates R1. Rejected. |
| Fixed reflector with wide θa (no elevation adjustment) | Possible with θa ≥ 35°. Lower concentration. Keep as a configuration of the same design. |

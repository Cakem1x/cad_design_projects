# Laser Cutting and Engraving

Rough defaults for laser-cut and laser-engraved parts. Use them to start a design. Values differ between machines, materials and providers. Adapt them to the machine that makes the part. See [README.md](README.md#how-to-use-these-values).

## Operations

| Operation | Purpose | Typical result |
|---|---|---|
| Cutting | Cut contours through the sheet. | Edge square to the sheet. |
| Line engraving | Mark lines on the surface. No cut through. | Line width ≈ 0.2 mm. |
| Area engraving | Engrave filled regions on the surface. | Depth not controlled precisely. |

## Machine limits
Typical for a CO2 laser at a commercial service.

| Parameter | Default |
|---|---|
| Part size | ≤ 1200 × 600 mm |
| Material thickness | ≤ 12 mm (wood) |

## Design rules

| Parameter | Default | Note |
|---|---|---|
| Cut edge | Square to the sheet | No bevels or chamfers through the thickness. |
| Kerf (total cut width) | 0.1–0.3 mm | Depends on material, thickness and machine. Measure it with a test coupon. |
| Kerf compensation | Done in the design file | Offset outlines outward and holes inward by kerf/2. Most services cut on the drawn line. |
| Narrow web | ≥ material thickness | Narrower webs burn or break. Thinner is possible with care. |
| Gap between parts | ≥ 2 mm | |
| Margin to sheet edge | ≥ 5 mm | |
| Small parts | Edge length ≥ 20 mm | Smaller parts can fall through the cutting table. Hold them with bridges (uncut gaps ≈ 0.5 mm). |

## Birch plywood
Common material for laser-cut structural parts.

| Parameter | Default | Note |
|---|---|---|
| Nominal thickness | 3, 4, 6 mm | Also 1.5, 2, 9, 12 mm. |
| Actual thickness | Nominal ± 0.3 mm | Varies between sheets. Measure the sheet. Size slots and tabs from the measured value. |
| Kerf (total) | 0.15–0.25 mm | For 3–6 mm on a CO2 laser. |
| Cut edge | Dark brown, charred | Soot rubs off. Sand or wipe the edges. |
| Surface | Smoke stains near cuts | Protect visible faces with masking film or choose the better face as the visible face. |
| Glue | Use laser-grade plywood | Some glues stop the laser or cut poorly. |

## File preparation
General rules. The provider file defines the exact format.
- Draw at 1:1 in mm.
- Use closed contours for cuts.
- Remove duplicate and overlapping lines.
- Convert text to paths.
- Assign operations by colour or layer, as the provider specifies.

## Providers
Provider-specific limits, file formats and material data are in [providers/](providers/README.md). Read the provider file at the end of the design process, before you export and order.

| Provider | Document |
|---|---|
| cutcraft | [providers/cutcraft.md](providers/cutcraft.md) |

# Laser Cutting and Engraving

Rough defaults for laser-cut and laser-engraved parts. Values differ between machines and materials. Adapt them to the machine that makes the part. See [README.md](README.md#how-to-use-these-values).

## Operations

| Operation | Purpose | Default limits |
|---|---|---|
| Cutting | Cut contours through the sheet. Simple and complex shapes. | Part size ≤ 1200 × 600 mm. Material thickness ≤ 12 mm. |
| Line engraving | Mark fine lines on the surface. No cut through. | Line width ≈ 0.2 mm. Good contrast on many materials. |
| Area engraving | Engrave filled regions on the surface. | Engraving size ≤ 1230 × 700 mm. Also on parts supplied by the customer. |

Source: provider service description, recorded 2026-11-22. Provider name: not recorded.

## Materials
- Wood (for example, plywood), plastics, paper and many other materials.
- Check the provider's list before you choose a material. Some plastics (for example, PVC) are not laser-safe.

## Design rules
Rules of thumb. Not provider data. Confirm with a test cut.

| Parameter | Default | Note |
|---|---|---|
| Cut edge | Square to the sheet | No bevels or chamfers through the thickness. |
| Kerf | 0.1–0.3 mm | Depends on material, thickness and machine. Measure it with a test coupon. |
| Minimum web width | ≥ material thickness | Narrower webs burn or break. |

## File preparation
Not recorded yet. Ask the provider for:
- File format (for example, DXF or SVG).
- How the file assigns operations (layer, line colour or line weight).
- Whether the provider compensates kerf, or the file must.

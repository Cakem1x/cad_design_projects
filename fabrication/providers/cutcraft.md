# cutcraft

Online laser cutting service. Website: https://cutcraft.de/

Data recorded 2026-11-22 from:
- Homepage: https://cutcraft.de/
- Design rules: https://cutcraft.de/blogs/hilfe/designvorgaben
- Configurator: https://cutcraft.de/pages/konfigurator
- Material pages: https://cutcraft.de/pages/materialien/<material>. Each page loads its values from `https://cutcraft.de/tools/materialien/<material>/data/` (JSON). Find the material handles in https://cutcraft.de/sitemap_metaobject_pages_1.xml.

Values can change. Check the website before you order.

## Services

| Service | Limits |
|---|---|
| Laser cutting | Part size ≤ 1200 × 600 mm. Material thickness ≤ 12 mm. |
| Line engraving | Line width ≈ 0.2 mm. |
| Area engraving | Engraving size ≤ 1230 × 700 mm. Also on parts supplied by the customer. Depth not guaranteed. |

- No 3D printing.
- Materials: wood, plastic, paper and cardboard, textile. More than 50 materials.
- Special requirements: on request.

## Kerf
- The laser cuts centred on the drawn line.
- The kerf value on each material page is **per side** (half the total cut width). Example: listed kerf 0.1 mm → total cut width 0.2 mm.
- The customer compensates kerf. Offset outlines outward and holes inward by the listed value.
- The listed values give a slightly tight fit. Test critical fits first.

Note: this differs from a kerf parameter defined as total cut width. Convert before you use the listed value.

## Design rules

| Parameter | Value |
|---|---|
| Narrow sections (for example, grid bars) | ≥ 0.6 mm. Wider for longer sections. |
| Gap between parts | ≥ 2 mm. More for plastics. |
| Margin to sheet edge | ≥ 5 mm |
| Small parts | Edge length < 20 mm can shift, tilt or fall through the table. Use bridges. |
| Bridges | Break the path. Width ≈ 0.5 mm. ≤ 20 × 20 mm: 1 bridge. ≤ 50 × 50 mm: 2–3 bridges. Larger: more or wider bridges. |
| Minimum part size | Set per material. Birch plywood: 10 × 10 mm. |
| Minimum hole size | Not stated. |

The configurator checks only the overall file size. It does not check individual parts or narrow sections.

## File preparation

| Item | Rule |
|---|---|
| Formats | AI, PDF, EPS, SVG, DXF. No raster images, also not embedded. Upload size ≤ 50 MB. |
| AI | Save as PDF-compatible. One artboard per file. |
| PDF, EPS | One page per file. |
| SVG | Programs read the size differently. Check the dimensions after upload. |
| DXF | Version 2007/2008/2009 or older. Paths without colour read as black: one operation for all paths. |
| Scale | 1:1, unit mm. |
| Content | One file = one material. Delete guides, dimensions and notes. Convert text to paths. |
| Paths | Close contours. Remove duplicate lines (they add cost and reduce accuracy). |
| Overlaps | Covering objects do not hide cut or line-engrave paths. |

### Operation colours (RGB)

| Operation | Colour |
|---|---|
| Cutting | `#FF0000` (255, 0, 0) |
| Line engraving | `#0000FF` (0, 0, 255) |
| Area engraving | `#808080` to `#000000`. Use `#000000`. Lighter greys are set to `#808080`. |
| Do not laser | `#663300` (102, 51, 0). Counts toward the file dimensions. |

- Other colours are possible. Assign their operation in the configurator.
- Area engraving: use a filled shape, or an outline with stroke ≥ 0.35 mm. All other paths must have no fill.

## Materials

### Birch plywood
Source: material data of the product pages, for example https://cutcraft.de/pages/materialien/birkensperrholz-4-mm (data: https://cutcraft.de/tools/materialien/birkensperrholz-4-mm/data/). Recorded 2026-11-22.

| Property | Value |
|---|---|
| Sheet size | 1200 × 600 mm |
| Minimum part size | 10 × 10 mm |
| Grade | B/B |
| Surface | Sanded, natural colour |
| Glue | Interior |
| Density | 700 kg/m³ |
| Grain direction | Horizontal (along the 1200 mm side, assumed) |
| Thickness tolerance | 0.3 mm (all thicknesses) |
| Kerf value | 0.2 mm (all thicknesses). See the note below. |

| Nominal thickness | Plies | Material price per sheet | Per m² (derived) | Cutting speed factor |
|---|---|---|---|---|
| 1 mm | 3 | 25.57 € | 35.51 €/m² | 2.0 |
| 2 mm | 3 | 20.88 € | 29.00 €/m² | 1.95 |
| 3 mm | 4 | 24.28 € | 33.72 €/m² | 2.0 |
| 4 mm | 5 | 29.39 € | 40.82 €/m² | 1.65 |
| 5 mm | 6 | 29.82 € | 41.42 €/m² | 1.1 |
| 6 mm | 7 | 40.99 € | 56.93 €/m² | 0.82 |
| 8 mm | 9 | 42.48 € | 59.00 €/m² | 0.57 |

- Prices are the listed material price per 1200 × 600 mm sheet (field `materialSellingPricePerPlate`). VAT status not stated. Cutting time and setup cost are extra. The configurator gives the binding price.
- Cutting speed factor: relative speed (field `cuttingSpeed`). Lower is slower and costs more laser time.
- Options: smoke protection film (reduces smoke marks; 3 €/m² plus setup cost), double-sided adhesive film (3M 468MP).

Kerf note: the field is labelled "kerf". The help text on the same page calls the listed value a per-side offset, which means a total cut width of 0.4 mm. That is more than a typical CO2 kerf in birch (0.15–0.25 mm), so 0.2 mm may be the total width instead. Cut a test coupon before you fix the kerf compensation of a fitted joint.

## Pricing
The configurator shows the price after upload. cutcraft does not publish its formula. The site data (`globalPricingSettings` in the material data, updated 2026-09-10) names these cost items:

| Item | Value in the site data |
|---|---|
| Laser time | 1.76 €/min base rate, falls towards 1.30 €/min for longer jobs (discount from 5 min) |
| Laser setup | 6 € per job |
| Material setup | 4 € per material plus 1 € per sheet |
| Material | Area used, plus scrap (5 %) and remnant (30 %) rates for birch plywood |
| Margin, safety | 12 %, 3 % |
| Payment fee | 1.9 % |
| VAT | 19 % |
| Shipping (Germany) | 9.95 € per order. Source: https://cutcraft.de/policies/shipping-policy |
| Production priority | FlexPrio to SameDayPrio. Surcharges not published. |

- Use these values only for rough estimates. The configurator price is binding.
- Delivery in Germany: 3–5 working days. Also ships to AT, FR, NL, BE, IT.

## Ordering
1. Upload the file in the configurator. It detects dimensions and operations. Check them.
2. Choose material, options and quantity. The price shows immediately.
3. Order online. Choose the production priority in the cart (FlexPrio, StandardPrio, ExpressPrio, SameDayPrio).

Support: Monday to Friday, 10:00–18:00, by e-mail, phone or chat.

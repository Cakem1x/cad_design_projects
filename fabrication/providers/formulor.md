# formulor

Online laser cutting service. Website: https://www.formulor.de/

Data recorded 2026-11-22 from:
- Plywood: https://www.formulor.de/en/materials/plywood
- How it works and pricing: https://www.formulor.de/en/how-it-works
- File preparation: https://www.formulor.de/en/help/files
- Kerf: https://www.formulor.de/en/knowledge/kerf-allowance
- Material thickness: https://www.formulor.de/en/knowledge/material-thickness
- Terms: https://www.formulor.de/en/terms

Values can change. Check the website before you order. Some knowledge pages are marked "AI-generated" by formulor.

## Services

| Service | Notes |
|---|---|
| Laser cutting | On fixed sheet formats (see below). |
| Vector engraving | Line traced by the beam. Width ≈ beam width. |
| Raster engraving | Filled areas, line by line. |
| Bending | Acrylic ≤ 6 mm, PET-G ≤ 3 mm, polypropylene. Not wood. 9.99 € per bend. |

- No 3D printing.
- Every order is checked by a person before cutting. File problems return a correction link at no cost.
- Browser modeller and parametric products (shape.tools) in addition to file upload.

## Sheet formats
A design must fit on one sheet. Larger objects must be split.

| Format | Size |
|---|---|
| P1 | 181 × 181 mm |
| P2 | 384 × 384 mm |
| P3 | 790 × 384 mm |
| Q | 900 × 450 mm |

Templates (SVG, DXF): https://www.formulor.de/en/help/templates

## Kerf
- The laser cuts centred on the drawn line. No compensation by formulor. Compensate in the file.
- formulor states kerf as the **total cut width**.
- Reference value: birch plywood 3 mm → 0.2 mm. Acrylic 3 mm → 0.3–0.4 mm.
- Test cut recommended for fitted joints. Order a test strip on P1.

## Design rules

| Parameter | Value |
|---|---|
| Webs and slots | < 1 mm not reliable. ≥ 1.5 mm for loaded parts. |
| Small parts | < 15 × 15 mm: add bridges. |
| Bridges | Interrupt the contour by 0.5–0.8 mm. |

## File preparation

| Item | Rule |
|---|---|
| Formats | SVG, DXF, PDF, EPS, AI. SVG and PDF most robust. No CDR. |
| Colour mode | RGB. CMYK shifts the values. |
| Scale | 1:1, unit mm. |
| Content | Vector paths only. Convert text to paths. No raster images, gradients or effects. No duplicate paths. |

### Operation colours (RGB)

| Operation | Colour | Stroke |
|---|---|---|
| Cutting | `#0000FF` (0, 0, 255) | Hairline (0.01 mm) |
| Vector engraving | `#FF0000` (255, 0, 0) | Hairline |
| Raster engraving | `#000000` (0, 0, 0) | Filled areas, or strokes > 0.1 mm |
| Bend line | `rgb(255, angle, B)` | See the files page. |

Warning: cutcraft uses red for cutting. formulor uses red for engraving and blue for cutting. Recolour the file for each provider.

## Materials

### Plywood
Source: https://www.formulor.de/en/materials/plywood

| Property | Value |
|---|---|
| Glue | Tegofilm (phenolic resin film). Weatherproof per DIN 68705, corresponds to AW 100. Not certified. |
| Grade (birch) | B/B. Knotholes ≤ ≈ 8 mm. |
| Thickness tolerance | Up to ± 0.5 mm |
| Bendable | No |

Sheet prices, incl. VAT:

| Wood | Thickness | P1 | P2 | P3 | Q | Q per m² (derived) |
|---|---|---|---|---|---|---|
| Birch | 0.8 mm | 2.80 € | 10.90 € | 18.69 € | 24.95 € | 61.60 €/m² |
| Birch | 3 mm | 4.40 € | 15.80 € | 27.80 € | 37.12 € | 91.65 €/m² |
| Beech | 2 mm | 4.90 € | 18.20 € | 32.90 € | 43.92 € | 108.44 €/m² |
| Poplar | 4 mm | 4.52 € | 16.07 € | 28.32 € | 37.81 € | 93.36 €/m² |
| Poplar | 5 mm | 5.00 € | 17.85 € | 31.54 € | 42.10 € | 103.95 €/m² |

- Birch plywood only in 0.8 mm and 3 mm. No 6 mm plywood.
- The customer receives the cut parts, not the sheet. The sheet price is the basis of the material cost.

## Pricing
Source: https://www.formulor.de/en/how-it-works

| Item | Basis |
|---|---|
| Material | Sheet area the design needs, including offcut |
| Processing | Laser time (cutting and engraving), machine setup, packaging |
| Shipping | Per order. The amount shows in the order process. Not published. |
| VAT | Included in all displayed prices |

- formulor does not publish the rates. The price is fixed and shown live on upload. Same file, same price.
- Thicker material cuts slower. Cutting time rises with thickness and contour length.

## Ordering
1. Upload the file (or model in the browser). The preview shows the operations and the fixed price.
2. Add to cart and order. Payment: PayPal, credit card, bank transfer (prepayment).
3. A person checks the file. Cutting starts after approval.
4. Delivery within a few days.

- No right of withdrawal for custom parts (§ 312g (2) no. 1 BGB).

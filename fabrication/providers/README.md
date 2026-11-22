# Fabrication Providers

One file per provider. A provider can offer several methods (for example, laser cutting and 3D printing). Its file covers all of them.

| Provider | Methods | Document |
|---|---|---|
| cutcraft | Laser cutting, line engraving, area engraving | [cutcraft.md](cutcraft.md) |
| formulor | Laser cutting, vector engraving, raster engraving, bending (plastics) | [formulor.md](formulor.md) |

## When to read
Read a provider file at the end of the design process: before you export files and order parts. Design with the general defaults in the method documents (for example, [../laser_cutting.md](../laser_cutting.md)) until then.

## Laser cutting: birch plywood comparison
Recorded 2026-11-22. Details and sources in the provider files.

| Property | cutcraft | formulor |
|---|---|---|
| Birch thicknesses | 1, 2, 3, 4, 5, 6, 8 mm | 0.8, 3 mm |
| Largest sheet | 1200 × 600 mm | 900 × 450 mm (Q) |
| Thickness tolerance | 0.3 mm | ± 0.5 mm |
| Glue | Interior | Weatherproof (AW 100 equivalent) |
| Kerf as stated | 0.2 mm, per side (unclear, see file) | 0.2 mm total (3 mm) |
| Cut colour | Red `#FF0000` | Blue `#0000FF` |
| Red means | Cut | Vector engraving |
| 3 mm birch, material per m² (derived from sheet price) | 33.72 €/m² | 91.65 €/m² |
| Shipping (Germany) | 9.95 € per order | Per order, amount shown at checkout |
| Human file check | No (automatic) | Yes |

## Compare prices for a part
Neither provider publishes its full price formula. Both show a fixed price after upload, without an order. Compare with the configurators.

Inputs that drive the price:

| Input | Effect |
|---|---|
| Material and thickness | Material price. Thicker cuts slower: more laser time. |
| Area used (nested parts plus offcut) | Material cost |
| Total cut length | Laser time. Often the largest item for detailed patterns. |
| Engraving area and line length | Laser time |
| Number of sheets | Setup cost per sheet |
| Quantity | Setup cost spreads over the parts |
| Shipping, priority | Per order |

Procedure:
1. Export one file per provider from the same geometry. Set the operation colours of that provider (red for cut at cutcraft, blue for cut at formulor).
2. Check that each part fits the sheet format (formulor: ≤ 900 × 450 mm).
3. Upload to each configurator. Choose the same material, thickness and quantity.
4. Record the price including shipping, and the date.
5. Compare also quantities 1 and the planned series. Setup costs dominate small orders.

Rough estimate before export: material ≈ area used × price per m² from the provider file. Laser time needs the total cut length and the provider's cutting speed, which neither provider publishes.

## Add a provider
1. Create `<provider>.md` in this directory. Use [cutcraft.md](cutcraft.md) as a template.
2. Record the source URL and date of each value.
3. Add a row to the table above and to the "Providers" section of each method document it serves.
4. Add a column to the comparison table.

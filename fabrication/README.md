# Fabrication Methods

Reference data for the fabrication methods used in this repository.

| Method | Document | Used by |
|---|---|---|
| Laser cutting and engraving | [laser_cutting.md](laser_cutting.md) | `platonic_lampshades/`, `solar_tube_cooker/` |

## How to use these values
- The values are rough defaults. Use them as a starting point for a design.
- Limits and parameters differ between machines, providers and materials. Check them against the machine that makes the part and adapt them.
- A project's own docs take precedence. Values a design chooses (for example, sheet thickness or kerf) belong in `<project>/docs/`.
- The names in these documents describe the operations. They are not required terms. Use the terms of the project or the provider when they differ.

## Add a method
1. Create `<method>.md` in this directory. Use [laser_cutting.md](laser_cutting.md) as a template.
2. Record the source and date of each value.
3. Add a row to the table above.

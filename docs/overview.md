# Project Overview

## Goal
Design fabrication-ready CAD models for a solar cooker built around an existing evacuated glass tube with a sliding tray.
Fabrication methods: FDM 3D printing and laser cutting (plywood).
AI agents build the models in SolidCraft through its MCP server.

## Components
| ID | Component | Function |
|----|-----------|----------|
| C1 | Feet (2×) | Hold the tube horizontal, one foot near each tube end. Carry the reflector pivot. |
| C2 | Reflector frame (arms/ribs) | Hold the reflector in an involute CPC profile. Rotate about the tube axis to follow the sun elevation. |
| C3 | Reflector sheet | Flexible sheet with reflective foil. Rolls up for transport. Mounts on C2. |

Details and design options: [components.md](components.md).
Optical design: [optics.md](optics.md).

## Requirements
- R1: The tube does not rotate. The tray stays level.
- R2: The reflector rotates about the tube axis. Each set position locks.
- R3: The whole unit rotates on the ground to follow the sun azimuth.
- R4: The unit disassembles for transport. The reflector sheet rolls up.
- R5: The unit is stable in moderate wind (aperture area approx. 0.5 m²).
- R6: All parts fit the available machines (see parameters).
- R7: Parts near the tube and in the sun tolerate the temperature. Use PETG or ASA, not PLA. Plywood is acceptable.

## Base Parameters
All dimensions in mm unless noted. Values marked "TBD" need a measurement or a decision.

| Parameter | Value | Note |
|-----------|-------|------|
| `tube_od` | 125 | Outer glass diameter. |
| `tube_id` | 110 | Manufacturer value. Meaning TBD (see open questions). |
| `absorber_r` | 55–57.5 (TBD) | Radius of the selective coating (outer surface of the inner glass tube). Drives the CPC. |
| `tube_length` | 750 | Including tray handle. |
| `useful_length` | 650 | Heated length. Reflector length ≥ this. |
| `tube_mass` | 2.5 kg | Without food. |
| `accept_half_angle` | 30–35° (to decide in CAD) | See [optics.md](optics.md). |
| `min_sun_elevation` | 10° | Target. Increase if the tilt range causes problems. Lowest sun elevation for cooking. Sets the maximum reflector tilt and the tube axis height. See [optics.md](optics.md#tilt-range). |
| `trunc_height` | approx. 350 (to decide in CAD) | Reflector height, cusp to aperture. |
| `printer_bed` | ≤ 256 × 256 | FDM. |
| `laser_bed` | TBD | Limits rib size. |
| `sheet_thickness` | TBD | Plywood for laser-cut parts. |

## Modelling Workflow
1. Define all parameters in one source of truth (parameter file in the repository).
2. Generate the CPC profile points with a script from the parameters. Store the output as a data file.
3. Build each part as a separate SolidCraft design. Create the reflector curve as a fit spline through the generated points. Check the deviation from the analytic curve.
4. Build an assembly. Check the tilt range, ground clearance and collisions with motion studies.
5. Export STL/3MF for printed parts and DXF for laser-cut parts.

Verify early (spike):
- MCP server: create a parametric sketch, a fit spline from points and an extrusion.
- DXF export of a planar part in a format the laser software accepts.

## Phases
1. Optics: fix `absorber_r`, `accept_half_angle`, `trunc_height`, gap treatment.
2. Visualization model: tube, CPC profile, simple feet, tilt range.
3. Detail design: pivot and lock, foot structure, sheet mounting.
4. Prototype: print and cut one end (foot + rib) and test it with the tube.
5. Full build.

## Open Questions
- Q1: Meaning of `tube_id` = 110 mm. Is it the cooking-chamber diameter (inner surface of the inner tube) or the outer diameter of the inner tube? Measure the diameter of the dark coating, if possible.
- Q2: Laser cutter bed size and available sheet materials and thicknesses.
- Q3: Reflective material: self-adhesive foil on a carrier sheet, or pre-mirrored aluminium sheet.
- Q4: Required tray access: the tray end must stay free. Which end is closed and rounded?

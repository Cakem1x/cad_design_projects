# Project Overview

## Goal
Design fabrication-ready CAD models for a solar cooker built around an existing evacuated glass tube with a sliding tray.
Fabrication methods: FDM 3D printing and laser cutting (plywood).
AI agents build the models in SolidCraft through its MCP server.

## Components
| ID | Component | Function |
|----|-----------|----------|
| C1 | Feet (2×, identical) | Cradle the tube from below, one foot in each clear end zone. Hold the arm pair angle. |
| C2 | Arms (2 pairs, 4×) | Define the CPC profile. Attach to the foot and rotate about the tube axis (pivot). Carry the ribs. |
| C3 | Ribs | Rectangular plywood strips with reflective foil. Parallel to the tube axis. Joined on the back into one rollable rib mat per branch. Attach to the arms. Together they form the reflector. |

Terms:
- Arm: planar part that follows one CPC branch, from the cusp to the aperture edge.
- Arm pair: the left and the right arm at one foot. Joined below the tube. Separable for transport.
- Rib: rectangular plywood strip, long side parallel to the tube axis, foil glued to the front face. Spans from one arm pair to the other.
- Rib mat: all ribs of one branch, joined on the back by fabric or tape strips. Rolls up for transport.
- Reflector: all ribs in their mounted position.

Details and design options: [components.md](components.md).
Optical design: [optics.md](optics.md).

## Requirements
- R1: The tube does not rotate. The tray stays level.
- R2: The reflector rotates about the tube axis. Each set position locks.
- R3: The whole unit rotates on the ground to follow the sun azimuth.
- R4: The unit disassembles for transport. Each arm pair separates into its two arms. Each rib mat rolls up.
- R5: The unit is stable in moderate wind (aperture area approx. 0.55 m²).
- R6: All parts fit the available machines (see parameters).
- R7: Parts near the tube and in the sun tolerate the temperature. Use PETG or ASA, not PLA. Plywood is acceptable.

## Base Parameters
All dimensions in mm unless noted. Values marked "TBD" need a measurement or a decision.

| Parameter | Value | Note |
|-----------|-------|------|
| `tube_od` | 125 | Outer diameter of the transparent glass. |
| `absorber_d` | 110 | Diameter of the glass with the absorber coating. |
| `absorber_r` | 55 | `absorber_d` / 2. Drives the CPC. |
| `tube_length` | 750 | Including tray handle. |
| `useful_length` | 650 | Heated length. Reflector length ≥ this. |
| `clear_end` | approx. 50 | Clear end zone: clear glass without absorber at each tube end. Holds the foot and the arm pair ring. Measure per end. |
| `tube_mass` | 2.5 kg | Without food. |
| `accept_half_angle` | 20° | Selected. See [optics.md](optics.md). |
| `min_sun_elevation` | 10° | Target. Increase if the tilt range causes problems. Lowest sun elevation for cooking. Sets the maximum reflector tilt and the tube axis height. See [optics.md](optics.md#tilt-range). |
| `trunc_height` | 600 | Selected. Reflector height, lowest profile point to aperture. Arm length (straight line, cusp to aperture edge) 707, below the tube length (750) for packing. |
| `printer_bed` | ≤ 256 × 256 | FDM. |
| `laser_bed` | sufficient | Larger than all parts. No segmentation of arms or ribs. |
| `sheet_thickness` | 6 | Plywood for laser-cut parts. |

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
1. Optics: fix gap treatment.
2. Visualization model: tube, CPC profile, simple feet, tilt range.
3. Detail design: pivot and lock (arm-to-foot joint), arm pair joint, foot structure, rib mounting.
4. Prototype: print and cut one end (foot + arm pair) and test it with the tube.
5. Full build.

## Open Questions
- Q1: Resolved. Plywood 6 mm. Laser bed sufficient.
- Q2: Reflective material: self-adhesive foil on a carrier sheet, or pre-mirrored aluminium sheet.
- Q3: Required tray access: the tray end must stay free. Which end is closed and rounded?
- Q4: Resolved. Ribs form a rollable rib mat (fabric or tape strips on the back).
- Q5: Rib width per position on the arm. Narrow near the cusp (see [components.md](components.md#c3-ribs)).

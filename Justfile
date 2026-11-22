# Generated files. Run inside the Nix dev shell (`nix develop -c just <recipe>` otherwise).
# DXF files are not committed; regenerate them before use.

lamp := "platonic_lampshades"

# List the recipes
default:
    @just --list

# platonic_lampshades: all generated SolidCraft inputs (pattern DXFs)
[group('platonic_lampshades')]
lamp-inputs: lamp-patterns

# platonic_lampshades: panel pattern DXFs and previews (upper and lower ring)
[group('platonic_lampshades')]
lamp-patterns:
    python3 {{lamp}}/tools/panel_pattern.py upper
    python3 {{lamp}}/tools/panel_pattern.py lower

# platonic_lampshades: Penrose pattern study (prototypes/img/penrose_*.svg)
[group('platonic_lampshades')]
lamp-penrose:
    python3 {{lamp}}/prototypes/penrose_pattern.py p3 upper
    python3 {{lamp}}/prototypes/penrose_pattern.py p3 upper 18 --rot36
    python3 {{lamp}}/prototypes/penrose_pattern.py p2 upper
    python3 {{lamp}}/prototypes/penrose_pattern.py p2 upper 22 --rot36
    python3 {{lamp}}/prototypes/penrose_pattern.py p3 lower
    python3 {{lamp}}/prototypes/penrose_pattern.py p2 lower

# platonic_lampshades: laser test coupon for the key joint (joint_test_x1.dxf) and the key figure
[group('platonic_lampshades')]
lamp-joint-coupon:
    python3 {{lamp}}/tools/joint_keys.py

# platonic_lampshades: sight-line and design-zone figures
[group('platonic_lampshades')]
lamp-figures:
    python3 {{lamp}}/tools/plot_sight_lines.py

# platonic_lampshades: everything above
[group('platonic_lampshades')]
lamp-all: lamp-inputs lamp-joint-coupon lamp-figures

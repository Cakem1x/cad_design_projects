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

# platonic_lampshades: former Marrakech pattern (prototypes/img/marrakech_*.svg)
[group('platonic_lampshades')]
lamp-marrakech:
    python3 {{lamp}}/prototypes/marrakech_pattern.py upper
    python3 {{lamp}}/prototypes/marrakech_pattern.py lower

# platonic_lampshades: Penrose pattern variants (prototypes/img/penrose_*.svg)
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

# platonic_lampshades: fast check (< 2 s): parameters (designs, docs) and laser DXFs. Args: --json, file.dxf
[group('platonic_lampshades')]
lamp-check *args:
    #!/usr/bin/env bash
    files=(); flags=()
    for a in {{args}}; do [[ $a == --* ]] && flags+=("$a") || files+=("$a"); done
    rc=0
    [[ ${#files[@]} -eq 0 ]] && { python3 fabrication/tools/param_sync.py {{lamp}} "${flags[@]}" || rc=$?; }
    python3 fabrication/tools/dxf_check.py {{lamp}} "${files[@]}" "${flags[@]}" || { r=$?; (( r > rc )) && rc=$r; }
    exit $rc

# platonic_lampshades: design claims (claims.toml): runs the headless ones, lists the app and manual ones
[group('platonic_lampshades')]
lamp-claims *ids:
    python3 fabrication/tools/claims.py {{lamp}} {{ids}}

# platonic_lampshades: checks (strict) and copy of the laser files with manifest.json for an order
[group('platonic_lampshades')]
lamp-release:
    python3 fabrication/tools/release.py {{lamp}}

# Activate the repository git hooks (.githooks/)
install-hooks:
    git config core.hooksPath .githooks

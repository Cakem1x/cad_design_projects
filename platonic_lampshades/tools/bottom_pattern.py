"""Bottom panel pattern: Penrose P3 rim with an open core. Writes DXF and an SVG preview with the
light on the table.

Pattern:
- Tiling: the tiling of the upper ring panel (panel_pattern.PANELS["upper"]: P3, a_t, phase).
  The bottom panel has the same outline and key positions as the ring panels, so the key
  alignment of the upper ring (a tile edge on each key arm) holds here too.
- Open core: the bars of all rhombs whose centre lies within R_CORE are removed. The core outline
  follows the tile edges, so no thin slivers form at the core.
- Bars: BAR mm, the bridge rule next to the core (> 35 mm) + BAR_MARGIN.
- Frame: BORDER_BOTTOM mm with rounded inner corners (smooth minimum, ROUND mm), key nodes as on
  the ring panels (slot margin BAR).
Pipeline, checks, DXF writers: tools/panel_pattern.py. Light on the table: tools/table_light.py.

Outputs (relative to platonic_lampshades/):
  cad/dodecahedron/bottom_pattern.dxf        nominal cutouts (3D cut)
  cad/dodecahedron/bottom_pattern_kerf.dxf   cutouts shrunk by kerf/2
  cad/dodecahedron/bottom_panel_x1.dxf       laser file: panel_x1.dxf + kerf cutouts on CUT
  docs/img/bottom_panel_pattern.svg          panel and light on the table

Usage: python3 platonic_lampshades/tools/bottom_pattern.py [--ek MM] [--svg PATH]
  --ek   key spacing for a study (default: the design value). Writes the preview only.
  --svg  preview path (default: docs/img/bottom_panel_pattern.svg)
"""
import argparse
import cmath
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import panel_pattern as pp  # noqa: E402
import table_light as tl  # noqa: E402

R_CORE = 50.0          # open core: rhombs with the centre within this radius, mm
BORDER_BOTTOM = 8.0    # frame width, mm
ROUND = 6.0            # smooth-minimum radius of the frame corners, mm
BAR = 4.3              # bar width: bridge rule maximum (core hole > 35 mm) + BAR_MARGIN, mm
CFG = dict(ring=0, slot_margin=BAR, title="Bottom panel")


def smin(a, b, k):
    """Smooth minimum (polynomial), blend radius k."""
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b * (1 - h) + a * h - k * h * (1 - h)


def frame_field(xs, ys, border=BORDER_BOTTOM):
    """Frame keep-out (positive inside the frame opening): border with rounded corners,
    key nodes blended in with 3 mm fillets. Uses pp.CFG["slot_margin"]."""
    X, Y = np.meshgrid(xs, ys)
    f = None
    for nx, ny in pp.EDGE_N:
        d = pp.RP - (X * nx + Y * ny) - border
        f = d if f is None else smin(f, d, ROUND)
    return smin(f, pp.key_keepout(X, Y), 3.0)


def core_edges(a_t, rot36, r_core):
    """P3 tile edges (N x 2 x 2, mm). An edge is removed when all rhombs that own it have their
    centre (midpoint of the half-rhomb base) within r_core. r_core None: all edges."""
    n = 0
    while a_t * pp.PHI ** n < (pp.RV + 3 * a_t) / 0.9:
        n += 1
    radius = a_t * pp.PHI ** n
    rot = cmath.rect(1, math.pi / 5) if rot36 else 1
    owners = {}
    for (a, b), (_, c) in pp.p3_tiles(n):
        a, b, c = (z * radius * rot for z in (a, b, c))
        in_core = r_core is not None and abs((b + c) / 2) < r_core
        for p, q in ((a, b), (a, c)):
            if min(abs(p), abs(q)) > pp.RV + 2 * a_t:
                continue
            key = tuple(sorted([(round(p.real, 4), round(p.imag, 4)), (round(q.real, 4), round(q.imag, 4))]))
            owners.setdefault(key, []).append(in_core)
    return np.array([[list(k[0]), list(k[1])] for k, cs in owners.items() if not all(cs)])


def penrose_core_field(a_t, rot36, r_core, bar=BAR, border=BORDER_BOTTOM):
    """Cutout field for pp.build(): Penrose rim with an open core inside the frame."""
    segs = core_edges(a_t, rot36, r_core)

    def field(xs, ys):
        return np.minimum(pp.seg_dist(xs, ys, segs, a_t) - bar / 2, frame_field(xs, ys, border))
    return field, segs


def set_ek(ek):
    """Override the key spacing (study only)."""
    pp.E_KEY = ek
    pp.KEYS[:] = [(k, sgn * ek / 2) for k in range(5) for sgn in (-1, 1)]


def report(holes):
    """Print the checks. Returns True when all pass."""
    bridge, pair, edge, keep, _, _ = pp.check(holes)
    rot_err, mir_err = pp.symmetry(holes)
    sizes = [pp.size(p) for p in holes]
    area = sum(pp.polygon_area(p) for p in holes)
    print(f"{len(holes)} holes, {min(sizes):.1f} mm to {max(sizes):.1f} mm, open area {area:.0f} mm^2 "
          f"({100 * area / pp.PANEL_AREA:.0f} %), {sum(len(p) for p in holes)} segments")
    if pair:
        print(f"check: bridge margin {bridge:+.2f} mm (actual {pair[0]:.2f}, required {pair[1]:.2f}), "
              f"edge margin {edge:+.2f} mm, key margin {keep:+.2f} mm")
    print(f"symmetry: rotation 72 deg {rot_err:.3f} mm, mirror {mir_err:.3f} mm (limit {pp.SYM_TOL} mm)")
    return min(bridge, edge, keep) >= 0 and max(rot_err, mir_err) <= pp.SYM_TOL


def main():
    ap = argparse.ArgumentParser(description="Bottom panel pattern (Penrose P3 rim, open core).")
    ap.add_argument("--ek", type=float, help="key spacing for a study, mm (preview only)")
    ap.add_argument("--svg", default=os.path.join(pp.IMG_DIR, "bottom_panel_pattern.svg"))
    args = ap.parse_args()
    if args.ek is not None:
        set_ek(args.ek)
    up = pp.PANELS["upper"]
    a_t, rot36 = up["a_t"], up["rot36"]
    pp.CFG = dict(CFG)
    field, segs = penrose_core_field(a_t, rot36, R_CORE)
    holes = pp.build(field)
    print(f"bottom: {pp.TILING_NAMES['p3']}{', rot36' if rot36 else ''}, a_t = {a_t:.2f} mm (upper ring), "
          f"core R {R_CORE:g} mm, bar {BAR:.2f} mm, border {BORDER_BOTTOM:g} mm, ek = {pp.E_KEY:.2f} mm")
    if hasattr(pp, "key_alignment"):
        print(f"key arm to nearest tile edge {pp.key_alignment(segs):.2f} mm")
    ok = report(holes)
    area = sum(pp.polygon_area(p) for p in holes)
    title = (f"Bottom panel: Penrose P3, edge {a_t:g} mm{', turned 36°' if rot36 else ''}, open core R {R_CORE:g} mm, "
             f"{len(holes)} holes, open {100 * area / pp.PANEL_AREA:.0f} %, ek {pp.E_KEY:g} mm")
    os.makedirs(os.path.dirname(os.path.abspath(args.svg)), exist_ok=True)
    tl.figure(holes, title, args.svg)
    print(f"written: {os.path.relpath(args.svg)}")
    if not ok:
        print("CHECK FAILED: no DXF written")
        return 1
    if args.ek is not None:
        print("study (--ek): no DXF written")
        return 0
    stem = os.path.join(pp.CAD_DIR, "bottom_pattern")
    pp.dxf(holes, f"{stem}.dxf")
    kerf = [pp.offset_in(p, pp.KERF / 2) for p in holes]
    pp.dxf(kerf, f"{stem}_kerf.dxf")
    print(f"written: {os.path.relpath(stem)}.dxf, {os.path.relpath(stem)}_kerf.dxf")
    out = os.path.join(pp.CAD_DIR, "bottom_panel_x1.dxf")
    if pp.laser_panel(kerf, os.path.join(pp.CAD_DIR, "panel_x1.dxf"), out):
        print(f"written: {os.path.relpath(out)}")
    else:
        print("panel_x1.dxf missing (export sketch PanelLaser): no laser file written")
    return 0


if __name__ == "__main__":
    sys.exit(main())

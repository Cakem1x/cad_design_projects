"""Bottom panel study: frame variants, Marrakech and Penrose P3, with the light on the table.

Every variant: frame 8 mm with rounded corners and the key nodes (tools/bottom_pattern.py),
pipeline and checks of tools/panel_pattern.py, light on the table from tools/table_light.py.
The chosen variant (penrose_core18_50) is the target in tools/bottom_pattern.py, with the tile
size of the upper ring.

Usage: python3 platonic_lampshades/prototypes/bottom_pattern_study.py [KEY ...] [--img-dir DIR]
  KEY: variant keys (default: all). Writes <img-dir>/bottom_<key>.svg (default: prototypes/img/).
"""
import argparse
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
sys.path.insert(0, HERE)
import panel_pattern as pp  # noqa: E402
import bottom_pattern as bp  # noqa: E402
import table_light as tl  # noqa: E402
import marrakech_pattern as mp  # noqa: E402

IMG_DIR = os.path.join(HERE, "img")
SLOT_MARGIN = 4.3     # bridge rule maximum + 0.3 mm (large holes next to the slots)


def window():
    return bp.frame_field


def lace(n_ring, r0, r_core):
    """Marrakech trellis rim (log-polar, n_ring lanterns per ring) around an open circular core."""
    def field(xs, ys):
        X, Y = np.meshgrid(xs, ys)
        cfg = pp.CFG
        pp.CFG = dict(cfg, n_ring=n_ring, r0=r0, r_hub=-1e9)
        try:
            trellis = mp.pattern_field(xs, ys)
        finally:
            pp.CFG = cfg
        return np.minimum(bp.frame_field(xs, ys), np.maximum(r_core - np.hypot(X, Y), trellis))
    return field


def medallion():
    """5 spokes (5 mm) to the vertices and a 5-petal rosette (Ø 35 mm to 41 mm)."""
    def field(xs, ys):
        X, Y = np.meshgrid(xs, ys)
        rho, th = np.hypot(X, Y), np.arctan2(Y, X)
        solid = rho - 17.0 * (1 + 0.22 * np.cos(5 * th))
        for k in range(5):
            a = math.radians(72 * k)
            along = X * math.cos(a) + Y * math.sin(a)
            across = np.abs(-X * math.sin(a) + Y * math.cos(a))
            solid = bp.smin(solid, np.where(along > 0, across, rho) - 2.5, 4.0)
        return bp.smin(bp.frame_field(xs, ys), solid, 3.0)
    return field


def penrose(a_t, rot36, r_core):
    bar = pp.bar_width(a_t) if r_core is None else max(pp.bar_width(a_t), bp.BAR)
    return bp.penrose_core_field(a_t, rot36, r_core, bar=bar)[0]


PHI = pp.PHI
# key: (title, field)
VARIANTS = {
    "window": ("Open window", window()),
    "marrakech_lace10": ("Marrakech lace rim, 10 per ring, core R 49.6 mm", lace(10, 34.0, 49.6)),
    "medallion": ("Medallion: 5 spokes, rosette", medallion()),
    "penrose_full18": ("Penrose P3 18 mm turned 36°, full", penrose(18.0, True, None)),
    "penrose_full29": ("Penrose P3 29.1 mm turned 36°, full", penrose(18.0 * PHI, True, None)),
    "penrose_core18_40": ("Penrose P3 18 mm turned 36°, core R 40 mm", penrose(18.0, True, 40.0)),
    "penrose_core18_50": ("Penrose P3 18 mm turned 36°, core R 50 mm (chosen)", penrose(18.0, True, 50.0)),
    "penrose_core12_45": ("Penrose P3 12 mm, core R 45 mm", penrose(12.0, False, 45.0)),
    "penrose_core12_50": ("Penrose P3 12 mm, core R 50 mm", penrose(12.0, False, 50.0)),
}


def main():
    ap = argparse.ArgumentParser(description="Bottom panel study.")
    ap.add_argument("keys", nargs="*", help=f"variants (default: all): {', '.join(VARIANTS)}")
    ap.add_argument("--img-dir", default=IMG_DIR)
    args = ap.parse_args()
    for k in args.keys:
        if k not in VARIANTS:
            ap.error(f"unknown variant {k!r}")
    os.makedirs(args.img_dir, exist_ok=True)
    pp.CFG = dict(bp.CFG, slot_margin=SLOT_MARGIN)
    for key in args.keys or VARIANTS:
        title, field = VARIANTS[key]
        holes = pp.build(field)
        area = sum(pp.polygon_area(p) for p in holes)
        bridge, _, edge, keep, _, _ = pp.check(holes)
        ok = min(bridge, edge, keep) >= 0 and max(pp.symmetry(holes)) <= pp.SYM_TOL
        bridge_txt = f"{bridge:+.2f} mm" if bridge < 1e8 else "—"
        print(f"{key}: {len(holes)} holes, open {100 * area / pp.PANEL_AREA:.0f} %, bridge {bridge_txt}, "
              f"edge {edge:+.2f} mm, key {keep:+.2f} mm, {'OK' if ok else 'CHECK FAILED'}")
        path = os.path.join(args.img_dir, f"bottom_{key}.svg")
        tl.figure(holes, f"{title}: {len(holes)} holes, open {100 * area / pp.PANEL_AREA:.0f} %", path)
        print(f"written: {os.path.relpath(path)}")


if __name__ == "__main__":
    main()

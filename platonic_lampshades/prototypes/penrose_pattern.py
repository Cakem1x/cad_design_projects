"""Penrose tiling study for the ring panels: variants of the target pattern.

The tilings, the pipeline and the checks are in tools/panel_pattern.py (the target pattern).
This script runs other tilings, tile sizes and phases and writes the outputs to prototypes/img/
and prototypes/dxf/ by default. The target outputs stay unchanged.

Usage: python3 platonic_lampshades/prototypes/penrose_pattern.py [p3|p2] [upper|lower] [A_T] [--rot36]
       [--img-dir DIR] [--dxf-dir DIR]
  A_T: tile edge length, mm (default: P3 upper 18, lower 12; P2 upper 22, lower 14).
Outputs (default directories: prototypes/img/ and prototypes/dxf/):
  <img-dir>/penrose_<tiling>_<panel>[_rot36].svg
  <dxf-dir>/penrose_<tiling>_<panel>[_rot36]_pattern.dxf
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
import panel_pattern as pp  # noqa: E402

A_T_DEFAULT = {("p3", "upper"): 18.0, ("p2", "upper"): 22.0, ("p3", "lower"): 12.0, ("p2", "lower"): 14.0}
IMG_DIR = os.path.join(HERE, "img")
DXF_DIR = os.path.join(HERE, "dxf")


def main():
    parser = argparse.ArgumentParser(description="Penrose tiling study for the ring panels.")
    parser.add_argument("tiling", nargs="?", default="p3", choices=["p3", "p2"])
    parser.add_argument("panel", nargs="?", default="upper", choices=list(pp.PANELS))
    parser.add_argument("a_t", nargs="?", type=float, metavar="A_T",
                        help="tile edge length, mm (default: P3 upper 18, lower 12; P2 upper 22, lower 14)")
    parser.add_argument("--rot36", action="store_true", help="turn the patch by 36 deg")
    parser.add_argument("--img-dir", default=IMG_DIR, help="SVG preview directory (default: %(default)s)")
    parser.add_argument("--dxf-dir", default=DXF_DIR, help="DXF directory (default: %(default)s)")
    args = parser.parse_args()
    a_t = args.a_t if args.a_t is not None else A_T_DEFAULT[args.tiling, args.panel]
    name = f"penrose_{args.tiling}_{args.panel}{'_rot36' if args.rot36 else ''}"
    sys.exit(pp.run(args.panel, tiling=args.tiling, a_t=a_t, rot36=args.rot36,
                    svg_path=os.path.join(os.path.abspath(args.img_dir), f"{name}.svg"),
                    dxf_stem=os.path.join(os.path.abspath(args.dxf_dir), f"{name}_pattern"),
                    kerf_dxf=False, laser=False))


if __name__ == "__main__":
    main()

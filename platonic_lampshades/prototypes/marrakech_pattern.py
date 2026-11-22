"""Polar Marrakech trellis for the ring panels (prototype, replaced by the Penrose pattern).

Pattern: the Moroccan lantern trellis (diamond tiling with S-curved edges) in log-polar
coordinates around the panel centre (conformal map). N lanterns per ring (multiple of 5), the
lanterns point outwards and grow with the radius. The bar width in mm follows the local hole size.

Pipeline, keep-outs, checks and DXF output: tools/panel_pattern.py. Differences:
- Solid hub of radius r_hub at the panel centre.
- Upper ring: a hole that reaches below E_EYE_TOP (top of the viewer envelope) is dropped whole:
  only the lantern at the bottom tip. The check requires all hole points above E_EYE_TOP.
- Key spacing: E_KEY = 45 mm (study value), not the design value.
- Key nodes: SLOT_MARGIN = 4.3 mm around the slot (bridge rule maximum + 0.3 mm).
  Upper ring: ek = 45 mm puts each key on the trellis bar that meets the edge there. Lower ring:
  r0 = 27.4 mm puts a bar and a junction on each key.

Panels (see PANELS):
  upper   10 lanterns per ring, projection zone only.
  lower   20 lanterns per ring, cut over all zones.

Outputs (default directories: prototypes/img/ and prototypes/dxf/):
  <img-dir>/marrakech_<panel>.svg
  <dxf-dir>/marrakech_<panel>_pattern.dxf, marrakech_<panel>_pattern_kerf.dxf

Usage: python3 platonic_lampshades/prototypes/marrakech_pattern.py [upper|lower] [N_RING]
       [--img-dir DIR] [--dxf-dir DIR]
  N_RING overrides the lanterns per ring (multiple of 5).
"""
import argparse
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
import panel_pattern as pp  # noqa: E402
from panel_pattern import plt  # noqa: E402

IMG_DIR = os.path.join(HERE, "img")
DXF_DIR = os.path.join(HERE, "dxf")

# r0 sets the radial phase of the rings. Lower ring: r0 = 27.4 mm puts a bar and a junction on
# each key (E_KEY is fixed by the upper ring); r0 = 34 mm put the keys inside lanterns.
PANELS = {
    "upper": dict(ring=+1, n_ring=10, r0=34.0, r_hub=14.0, glare_keepout=True,
                  title="Upper ring panel", tip="bottom tip on +x"),
    "lower": dict(ring=-1, n_ring=20, r0=27.4, r_hub=16.0, glare_keepout=False,
                  title="Lower ring panel", tip="top tip on +x"),
}
E_KEY = 45.0          # key spacing of this study, mm (the design uses 36 mm for the Penrose pattern)
STRETCH = 1.2         # lantern tile height / width
BULGE = 0.09          # S-curve amplitude / edge length


def glare_line_x():
    """Largest x such that the line x = const lies above E_GLARE_HI inside the upper ring panel."""
    ys = np.linspace(-pp.RP, pp.RP, 81)
    lo, hi = np.full_like(ys, -pp.RP), np.full_like(ys, pp.RV)
    for _ in range(60):
        m = (lo + hi) / 2
        ok = pp.elevation(m, ys, +1) > pp.E_GLARE_HI
        lo, hi = np.where(ok, m, lo), np.where(ok, hi, m)
    return float(lo.min())


def dist_to_points(U, V, P):
    out = np.empty(U.size)
    u, v = U.ravel(), V.ravel()
    for i in range(0, u.size, 4000):
        du = u[i:i + 4000, None] - P[None, :, 0]
        dv = v[i:i + 4000, None] - P[None, :, 1]
        out[i:i + 4000] = np.sqrt((du * du + dv * dv).min(axis=1))
    return out.reshape(U.shape)


def lantern_dist(U, V, p, stretch, bulge):
    """Distance from (U, V) to the lantern trellis: diamond tiling (width p, height p * stretch)
    whose edges are S-curves, point-symmetric about the edge midpoints, so the tiles stay
    congruent. A lantern is centred on the origin, its points along V."""
    hu, hv = p / 2, p / 2 * stretch
    vt, vr, vl = np.array([0, hv]), np.array([hu, 0]), np.array([-hu, 0])
    t = np.linspace(0, 1, 140)

    def s_curve(a, b, inward):
        e = b - a
        L = np.hypot(*e)
        n = np.array([-e[1], e[0]]) / L
        if np.dot(n, inward) < 0:
            n = -n
        off = bulge * L * np.sin(2 * np.pi * t)
        return a[None] + t[:, None] * e[None] + off[:, None] * n[None]

    fam_a = s_curve(vt, vr, -(vt + vr) / 2)
    fam_b = s_curve(vt, vl, -(vt + vl) / 2)
    a1, a2 = np.array([hu, hv]), np.array([hu, -hv])
    M = np.array([a1, a2]).T
    c = np.linalg.inv(M) @ np.vstack([U.ravel(), V.ravel()])
    c -= np.floor(c)
    f = (M @ c).T
    P = np.vstack([fam + i * a1 + j * a2 for i in (-1, 0, 1, 2) for j in (-1, 0, 1, 2) for fam in (fam_a, fam_b)])
    return dist_to_points(f[:, 0], f[:, 1], P).reshape(U.shape)


def pattern_field(xs, ys):
    """Cutout field before keep-outs: positive inside the lantern holes."""
    X, Y = np.meshgrid(xs, ys)
    cfg = pp.CFG
    n = cfg["n_ring"]
    p = 10.0                                   # tile width in map units
    k = n * p / (2 * math.pi)                  # map units per radian
    rho = np.maximum(np.hypot(X, Y), 0.5)
    th = np.arctan2(Y, X)
    S = lantern_dist(k * th, k * np.log(rho / cfg["r0"]), p, STRETCH, BULGE) * rho / k
    hole = 2 * math.pi * rho / n * STRETCH * 0.9           # approximate local hole length
    w = pp.web_req(hole) + pp.BAR_MARGIN
    return np.minimum(S - w / 2, rho - cfg["r_hub"])


def preview(holes, path, open_pct):
    cfg = pp.CFG
    fig, ax = plt.subplots(figsize=(6, 6))
    fig.patch.set_facecolor("#fcfcfb")
    ax.set_facecolor("#fcfcfb")
    pp.draw_panel(ax, holes)
    xs, ys, E = pp.elevation_grid()
    if cfg["glare_keepout"]:
        ax.contour(xs, ys, E, levels=[pp.E_GLARE_HI], colors="#eb6834", linewidths=1, linestyles=[(0, (3, 2))])
        ax.text(glare_line_x() + 4, pp.RP * 0.62, f"glare zone\n(e < {pp.E_GLARE_HI:+.0f}°)", fontsize=7,
                color="#52514e")
    else:
        ax.contour(xs, ys, E, levels=[pp.E_GLARE_LO, pp.E_GLARE_HI], colors="#eb6834", linewidths=1,
                   linestyles=[(0, (3, 2))])
        ax.text(-pp.RP + 3, pp.RP * 0.92, f"table zone\n(e < {pp.E_GLARE_LO:.0f}°)", fontsize=7, color="#52514e")
        ax.text(pp.RV - 22, pp.RP * 0.40, f"projection\n(e > {pp.E_GLARE_HI:+.0f}°)", fontsize=7, color="#52514e")
        ax.text(-8, -pp.RV * 0.88, "glare zone: diffuser", fontsize=7, color="#52514e")
    ax.set_aspect("equal")
    ax.set_xlim(-pp.RP - 4, pp.RV + 4)
    ax.set_ylim(-pp.RV - 4, pp.RV + 4)
    ax.axis("off")
    ax.set_title(f"{cfg['title']}: polar Marrakech trellis, {cfg['n_ring']} lanterns per ring, "
                 f"open {open_pct:.0f} %. {cfg['tip'].capitalize()}.", fontsize=8, color="#0b0b0b", loc="left")
    fig.tight_layout()
    fig.savefig(path, facecolor="#fcfcfb")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description="Polar Marrakech trellis for the ring panels (prototype).")
    parser.add_argument("panel", nargs="?", default="upper", choices=list(PANELS))
    parser.add_argument("n_ring", nargs="?", type=int, metavar="N_RING", help="lanterns per ring (multiple of 5)")
    parser.add_argument("--img-dir", default=IMG_DIR, help="SVG preview directory (default: %(default)s)")
    parser.add_argument("--dxf-dir", default=DXF_DIR, help="DXF directory (default: %(default)s)")
    args = parser.parse_args()
    pp.E_KEY = E_KEY
    pp.KEYS[:] = [(k, sgn * E_KEY / 2) for k in range(5) for sgn in (-1, 1)]
    pp.CFG = dict(PANELS[args.panel])
    if args.n_ring:
        pp.CFG["n_ring"] = args.n_ring
    holes = pp.build(pattern_field)
    bridge, pair, edge, keep, e_cent, emin = pp.check(holes)
    open_area = sum(pp.polygon_area(p) for p in holes)
    sizes = [pp.size(p) for p in holes]
    print(f"a = {pp.A:.2f} mm, rp = {pp.RP:.2f} mm, ek = {pp.E_KEY:.2f} mm")
    print(f"{len(holes)} holes, {min(sizes):.1f} mm to {max(sizes):.1f} mm, open area {open_area:.0f} mm^2 "
          f"({100 * open_area / pp.PANEL_AREA:.0f} %), {sum(len(p) for p in holes)} segments")
    print(f"check: bridge margin {bridge:+.2f} mm (actual {pair[0]:.2f}, required {pair[1]:.2f}), "
          f"edge margin {edge:+.2f} mm, key margin {keep:+.2f} mm")
    print(f"elevation: lowest hole centroid {e_cent:+.2f} deg, lowest hole point {emin:+.2f} deg")
    img_dir, dxf_dir = os.path.abspath(args.img_dir), os.path.abspath(args.dxf_dir)
    os.makedirs(img_dir, exist_ok=True)
    name = f"marrakech_{args.panel}"
    svg = os.path.join(img_dir, f"{name}.svg")
    preview(holes, svg, 100 * open_area / pp.PANEL_AREA)
    print(f"written: {os.path.relpath(svg)}")
    glare_fail = pp.CFG["glare_keepout"] and emin <= pp.E_EYE_TOP
    if bridge < 0 or edge < 0 or keep < 0 or glare_fail:
        print("CHECK FAILED: no DXF written")
        sys.exit(1)
    os.makedirs(dxf_dir, exist_ok=True)
    pp.dxf(holes, os.path.join(dxf_dir, f"{name}_pattern.dxf"))
    pp.dxf([pp.offset_in(p, pp.KERF / 2) for p in holes], os.path.join(dxf_dir, f"{name}_pattern_kerf.dxf"))
    print(f"written: {os.path.relpath(os.path.join(dxf_dir, name))}_pattern.dxf, ..._kerf.dxf")


if __name__ == "__main__":
    main()

"""Alternative panel pattern styles: Marrakech trellis, latticework, geometric floral.

Shared pipeline (same keep-outs and checks as voronoi_pattern.py):
1. Skeleton distance S: distance (mm) from each grid point to the style's line network.
2. Cutout field F = min(S - w/2, border, bracket keep-outs, glare zone), lightly blurred
   (rounds inner corners), on a 0.2 mm grid.
3. Cutouts: closed contours F = 0. Holes thinner than 2 * R_HOLE_MIN or smaller than A_MIN are dropped.
4. Check on the output polylines: the bridge between two holes must be at least
   web_req = 3.0 mm, rising linearly to 4.0 mm when the larger hole measures 15 mm to 35 mm.
   Border and bracket clearance must meet the same rule.

Coordinates: base panel frame (see voronoi_pattern.py). Panel axis: local u = y (horizontal),
v = -x (up an upper ring panel).

Outputs (relative to platonic_lampshades/):
  cad/dodecahedron/upper_pattern_<style>.dxf and ..._kerf.dxf
  docs/img/pattern_<style>.svg
  docs/img/pattern_styles.svg    (comparison, includes the Voronoi pattern)

Usage: python3 platonic_lampshades/tools/pattern_styles.py [style ...]
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import voronoi_pattern as vp  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402  (backend set in voronoi_pattern)
from matplotlib.patches import Polygon as MplPolygon  # noqa: E402

GRID = 0.2
BORDER = 6.0
KEEP_MARGIN = 4.5
GLARE_CLEAR = 3.0
BLUR = 0.5            # sigma, mm: inner corner radius about 1 mm
R_HOLE_MIN = 1.2      # drop holes narrower than 2.4 mm
A_MIN = 15.0          # drop holes smaller than this, mm^2


def web_req(size):
    return 3.0 + float(np.clip((size - 15.0) / 20.0, 0.0, 1.0))


# ---------- skeletons: functions of local (u, v) arrays, return distance in mm ----------
def dist_to_points(U, V, P):
    """Distance from grid (U, V) to sample points P (n, 2), chunked."""
    out = np.empty(U.size)
    u, v = U.ravel(), V.ravel()
    step = 4000
    for i in range(0, u.size, step):
        du = u[i:i + step, None] - P[None, :, 0]
        dv = v[i:i + step, None] - P[None, :, 1]
        out[i:i + step] = np.sqrt((du * du + dv * dv).min(axis=1))
    return out.reshape(U.shape)


def marrakech(X, Y, U, V, p=22.0, stretch=1.5, bulge=0.07, w=4.0):
    """Moroccan lantern trellis: diamond tiling with S-curved edges (point-symmetric about the
    edge midpoints, so the tiles stay congruent). p: tile width, stretch: height / width."""
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
    # fold the grid into the fundamental cell, then compare with the 3x3 neighbours
    M = np.array([a1, a2]).T
    Minv = np.linalg.inv(M)
    c = Minv @ np.vstack([U.ravel(), V.ravel()])
    c -= np.floor(c)
    f = (M @ c).T
    pts = []
    for i in (-1, 0, 1, 2):
        for j in (-1, 0, 1, 2):
            sh = i * a1 + j * a2
            pts.append(fam_a + sh)
            pts.append(fam_b + sh)
    P = np.vstack(pts)
    S = dist_to_points(f[:, 0], f[:, 1], P).reshape(U.shape)
    return S - w / 2, f"lanterns {p:.0f} x {p * stretch:.0f} mm, bars {w} mm"


def lattice(X, Y, U, V, s=17.0, angle=36.0, w=3.6):
    """Rhombic latticework: two families of straight bars at +-angle from the panel axis
    (72 / 108 degree rhombi, like the pentagon corners). A rhombus is centred on the panel."""
    S = np.full(U.shape, np.inf)
    for sgn in (1, -1):
        a = math.radians(90 + sgn * angle)          # bar direction from the u axis
        n = (-math.sin(a), math.cos(a))             # bar normal
        q = (U * n[0] + V * n[1] - s / 2) % s
        S = np.minimum(S, np.minimum(q, s - q))
    return S - w / 2, f"bar spacing {s:.0f} mm, bars {w} mm, rhombus angle {2 * angle:.0f} deg"


def floral(X, Y, U, V, r=26.0, w=3.3, w_out=4.2):
    """Geometric floral, 10-fold flower of life (base frame): 10 circles of radius r through the
    centre, an inner circle of radius r, and a second ring of 10 circles of radius r centred at 2r.
    Bar width grows with the distance from the centre, from w (small inner petals) to w_out
    (next to the large outer holes)."""
    rho = np.hypot(X, Y)
    wf = np.interp(rho, [1.1 * r, 1.6 * r], [w, w_out])
    D = np.abs(rho - r)
    for k in range(10):
        a = math.radians(36 * k)
        for R in (r, 2 * r):
            D = np.minimum(D, np.abs(np.hypot(X - R * math.cos(a), Y - R * math.sin(a)) - r))
    return D - wf / 2, f"flower of life, 10-fold, circle radius {r:.0f} mm, bars {w} to {w_out} mm"


STYLES = {
    "marrakech": ("Marrakech trellis", marrakech),
    "lattice": ("Latticework", lattice),
    "floral": ("Geometric floral", floral),
}


# ---------- pipeline ----------
def build(style):
    name, fn = STYLES[style]
    xs = np.arange(-vp.RP - 2, vp.RV + 2, GRID)
    ys = np.arange(-vp.RV - 2, vp.RV + 2, GRID)
    X, Y = np.meshgrid(xs, ys)
    U, V = Y, -X
    F, w = fn(X, Y, U, V)
    border = np.min(np.stack([vp.RP - (X * nx + Y * ny) for nx, ny in vp.EDGE_N]), axis=0) - BORDER
    keep = np.min(np.stack([vp.rect_sdf(X, Y, k) for k in range(5)]), axis=0) - KEEP_MARGIN
    glare = (vp.X_GLARE - X) - GLARE_CLEAR
    F = np.minimum.reduce([F, border, keep, glare])
    F = vp.blur(F, BLUR / GRID)
    cs = plt.contour(xs, ys, F, levels=[0.0])
    segs = cs.allsegs[0]
    plt.close("all")
    holes = []
    for seg in segs:
        if len(seg) < 6 or np.hypot(*(seg[0] - seg[-1])) > 1e-6:
            continue
        p = seg[:-1]
        if vp.polygon_area(p) < 0:
            p = p[::-1]
        if vp.polygon_area(p) < A_MIN:
            continue
        # thickness: largest field value inside the hole
        x0, y0 = p.min(0)
        x1, y1 = p.max(0)
        ix = (xs >= x0) & (xs <= x1)
        iy = (ys >= y0) & (ys <= y1)
        sub = F[np.ix_(iy, ix)]
        if sub.size == 0 or sub.max() < R_HOLE_MIN:
            continue
        h = len(p) // 2
        q = np.vstack([vp.simplify(p[:h + 1], vp.SIMPLIFY)[:-1], vp.simplify(np.vstack([p[h:], p[:1]]), vp.SIMPLIFY)[:-1]])
        holes.append(q)
    return name, w, holes


def size(p):
    return float(max(p[:, 0].max() - p[:, 0].min(), p[:, 1].max() - p[:, 1].min()))


def check(holes):
    """Worst bridge margin (actual - required) between holes, to the edge and to the keep-outs."""
    sizes = [size(p) for p in holes]
    worst, worst_pair = 1e9, None
    for i in range(len(holes)):
        bi = holes[i]
        for j in range(i + 1, len(holes)):
            bj = holes[j]
            if (bi[:, 0].min() - bj[:, 0].max() > 6 or bj[:, 0].min() - bi[:, 0].max() > 6 or
                    bi[:, 1].min() - bj[:, 1].max() > 6 or bj[:, 1].min() - bi[:, 1].max() > 6):
                continue
            d = vp.seg_point_dist(bi, bj, np.roll(bj, -1, axis=0)).min()
            req = web_req(max(sizes[i], sizes[j]))
            if d - req < worst:
                worst, worst_pair = d - req, (d, req)
    edge_m, keep_m = 1e9, 1e9
    for p, sz in zip(holes, sizes):
        req = web_req(sz)
        e = float(np.min([vp.RP - (p[:, 0] * nx + p[:, 1] * ny) for nx, ny in vp.EDGE_N]))
        edge_m = min(edge_m, e - req)
        for k in range(5):
            rc = np.array(vp.rect_corners(k))
            kd = vp.seg_point_dist(p, rc, np.roll(rc, -1, axis=0)).min()
            keep_m = min(keep_m, kd - req)
    allp = np.vstack(holes)
    emin = float(vp.elevation(allp[:, 0], allp[:, 1]).min())
    return worst, worst_pair, edge_m, keep_m, emin


def draw(ax, holes, title, open_pct):
    ax.set_facecolor("#fcfcfb")
    ax.add_patch(MplPolygon(vp.PANEL, closed=True, facecolor="#d8b07a", edgecolor="#3d3c39", linewidth=1.0))
    for k in range(5):
        ax.add_patch(MplPolygon(vp.rect_corners(k), closed=True, facecolor="#a9a8a2", alpha=0.45, edgecolor="none"))
    for p in holes:
        ax.add_patch(MplPolygon(p, closed=True, facecolor="#fcfcfb", edgecolor="#3d3c39", linewidth=0.4))
    ax.set_aspect("equal")
    ax.set_xlim(-vp.RP - 3, vp.RV + 3)
    ax.set_ylim(-vp.RV - 3, vp.RV + 3)
    ax.axis("off")
    ax.set_title(f"{title}, open {open_pct:.0f} %", fontsize=9, color="#0b0b0b", loc="left")


def panel_area():
    return 5 * vp.RP * vp.RP * math.tan(math.radians(36))


def main():
    styles = sys.argv[1:] or list(STYLES)
    results = {}
    for st in styles:
        name, w, holes = build(st)
        worst, pair, edge_m, keep_m, emin = check(holes)
        open_pct = 100 * sum(vp.polygon_area(p) for p in holes) / panel_area()
        print(f"{st}: {len(holes)} holes, open {open_pct:.0f} %, {w}, "
              f"largest hole {max(size(p) for p in holes):.1f} mm, smallest {min(size(p) for p in holes):.1f} mm")
        print(f"  bridge margin {worst:+.2f} mm (actual {pair[0]:.2f} vs required {pair[1]:.2f}), "
              f"edge margin {edge_m:+.2f}, keep-out margin {keep_m:+.2f}, min elevation {emin:+.2f} deg")
        ok = worst >= 0 and edge_m >= 0 and keep_m >= 0 and emin > vp.E_GLARE_HI
        print("  check OK" if ok else "  CHECK FAILED")
        fig, ax = plt.subplots(figsize=(5, 5))
        fig.patch.set_facecolor("#fcfcfb")
        draw(ax, holes, name, open_pct)
        fig.tight_layout()
        fig.savefig(os.path.join(vp.IMG_DIR, f"pattern_{st}.svg"), facecolor="#fcfcfb")
        plt.close(fig)
        if ok:
            vp.dxf(holes, os.path.join(vp.CAD_DIR, f"upper_pattern_{st}.dxf"))
            vp.dxf([vp.offset_in(p, vp.KERF / 2) for p in holes],
                   os.path.join(vp.CAD_DIR, f"upper_pattern_{st}_kerf.dxf"))
        results[st] = (name, holes, open_pct)
    if set(STYLES) <= set(results):
        xs, ys, F, _ = vp.field(7)
        vholes = vp.contours(xs, ys, F)
        vopen = 100 * sum(vp.polygon_area(p) for p in vholes) / panel_area()
        fig, axs = plt.subplots(2, 2, figsize=(9, 9))
        fig.patch.set_facecolor("#fcfcfb")
        draw(axs[0, 0], vholes, "Organic Voronoi (seed 7)", vopen)
        for ax, st in zip([axs[0, 1], axs[1, 0], axs[1, 1]], STYLES):
            name, holes, op = results[st]
            draw(ax, holes, name, op)
        fig.text(0.01, 0.01, "Upper ring panel, outer face. Bottom tip (glare zone) on the right. "
                 "Grey: bracket footprints.", fontsize=8, color="#52514e")
        fig.tight_layout(rect=(0, 0.02, 1, 1))
        fig.savefig(os.path.join(vp.IMG_DIR, "pattern_styles.svg"), facecolor="#fcfcfb")
        plt.close(fig)


if __name__ == "__main__":
    main()

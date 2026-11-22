"""Penrose tiling study for the ring panels (5-fold symmetric). Writes an SVG preview and a DXF.

Study only: the outputs go to prototypes/img/ and prototypes/dxf/ by default. The current pattern
(tools/panel_pattern.py) and its outputs stay unchanged.

Tilings:
  p3   thick rhombs (72 deg / 108 deg) and thin rhombs (36 deg / 144 deg)
  p2   kites (72 / 72 / 72 / 144 deg) and darts (36 / 72 / 36 / 216 deg)

Method:
1. Robinson-triangle deflation from a D5-symmetric start wheel around the panel centre
   (p3: sun of 10 half-rhombs, p2: sun of 5 kites). Deflation keeps the D5 symmetry.
   One mirror axis lies on +x, like the panel (vertex on +x). --rot36 turns the patch by 36 deg
   (the other symmetric phase, equal to a point reflection).
2. Tile edges (no rhomb diagonals, no kite or dart axes) are the bar centrelines.
   Field S = distance to the edges. Bar width w = web_req(long tile diagonal) + BAR_MARGIN.
3. Border, key keep-outs, blur, contours, hole filter and check: tools/panel_pattern.py.
   No hole is dropped for glare. Holes that reach into the glare zone are coloured in the
   preview (light orange up to 15 mm, red above) and listed.
4. Symmetry check: each hole centroid rotated by 72 deg and mirrored about the x axis must
   match a hole centroid within SYM_TOL. No DXF if it fails.

Usage: python3 platonic_lampshades/prototypes/penrose_pattern.py [p3|p2] [upper|lower] [A_T] [--rot36]
       [--img-dir DIR] [--dxf-dir DIR]
  A_T: tile edge length, mm (default: P3 upper 18, lower 12; P2 upper 22, lower 14).
Outputs (default directories: prototypes/img/ and prototypes/dxf/):
  <img-dir>/penrose_<tiling>_<panel>.svg
  <dxf-dir>/penrose_<tiling>_<panel>_pattern.dxf
"""
import argparse
import cmath
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
import panel_pattern as pp  # noqa: E402
from panel_pattern import plt, MplPolygon  # noqa: E402

PHI = (1 + 5 ** 0.5) / 2
A_T_DEFAULT = {("p3", "upper"): 18.0, ("p2", "upper"): 22.0, ("p3", "lower"): 12.0, ("p2", "lower"): 14.0}
SYM_TOL = 0.2          # centroid mismatch under rotation and mirror, mm
GLARE_BIG = 15.0       # glare holes above this size are marked red, mm
IMG_DIR = os.path.join(HERE, "img")
DXF_DIR = os.path.join(HERE, "dxf")


# ---------- tilings ----------
def p3_tiles(n):
    """P3: half-rhombs (kind, A, B, C), A = apex. kind 0 thin (36 deg), 1 thick (108 deg).
    Edges AB and AC; BC is the rhomb diagonal shared with the mirror half."""
    ts = []
    for i in range(10):
        b, c = cmath.rect(1, (2 * i - 1) * math.pi / 10), cmath.rect(1, (2 * i + 1) * math.pi / 10)
        if i % 2 == 0:
            b, c = c, b
        ts.append((0, 0j, b, c))
    for _ in range(n):
        out = []
        for k, a, b, c in ts:
            if k == 0:
                p = a + (b - a) / PHI
                out += [(0, c, p, b), (1, p, c, a)]
            else:
                q = b + (a - b) / PHI
                r = b + (c - b) / PHI
                out += [(1, r, c, a), (1, q, r, b), (0, r, q, a)]
        ts = out
    # mirror axes of the sun lie at odd multiples of 18 deg: turn one onto +x
    rot = cmath.rect(1, -math.pi / 10)
    return [((a * rot, b * rot), (a * rot, c * rot)) for _, a, b, c in ts]


def p2_tiles(n):
    """P2: half-kites ('K', apex, side, corner) and half-darts ('D', reflex, side, tip).
    Kite edges apex-side (long) and side-corner (short); axis apex-corner.
    Dart edges reflex-side (short) and side-tip (long); axis reflex-tip."""
    ts = []
    for k in range(5):
        c = PHI * cmath.rect(1, math.radians(72 * k))
        for s in (-1, 1):
            ts.append(("K", 0j, PHI * cmath.rect(1, math.radians(72 * k + 36 * s)), c))
    for _ in range(n):
        out = []
        for kind, a, b, c in ts:
            if kind == "K":
                p = a + (b - a) / PHI ** 2
                r = a + (c - a) / PHI
                out += [("D", p, r, a), ("K", b, p, r), ("K", b, c, r)]
            else:
                u = c + (b - c) / PHI
                out += [("K", c, u, a), ("D", u, a, b)]
        ts = out
    scale = 1 / PHI     # start radius 1 (kite edge phi)
    return [((a * scale, b * scale), (b * scale, c * scale)) for _, a, b, c in ts]


def tile_edges(tiling, a_t, rot36):
    """Unique tile edges (N x 2 x 2 array, mm) covering the panel, tile edge a_t."""
    n = 0
    while a_t * PHI ** n < (pp.RV + 3 * a_t) / 0.9:
        n += 1
    gen = p3_tiles if tiling == "p3" else p2_tiles
    radius = a_t * PHI ** n
    rot = cmath.rect(1, math.pi / 5) if rot36 else 1
    seen, segs = set(), []
    for e in (e for tri in gen(n) for e in tri):
        p, q = (z * radius * rot for z in e)
        key = tuple(sorted([(round(p.real, 4), round(p.imag, 4)), (round(q.real, 4), round(q.imag, 4))]))
        if key in seen or min(abs(p), abs(q)) > pp.RV + 2 * a_t:
            continue
        seen.add(key)
        segs.append([[p.real, p.imag], [q.real, q.imag]])
    return np.array(segs)


# ---------- field ----------
def seg_dist(X, Y, segs):
    """Distance from the grid points to the nearest segment."""
    P = np.stack([X.ravel(), Y.ravel()], axis=1)
    A_, B_ = segs[:, 0], segs[:, 1]
    AB = B_ - A_
    L2 = np.maximum((AB ** 2).sum(1), 1e-12)
    out = np.empty(len(P))
    for i in range(0, len(P), 2000):
        Q = P[i:i + 2000]
        AP = Q[:, None, :] - A_[None]
        t = np.clip((AP * AB[None]).sum(2) / L2[None], 0, 1)
        D = AP - t[..., None] * AB[None]
        out[i:i + 2000] = np.sqrt((D ** 2).sum(2).min(1))
    return out.reshape(X.shape)


def make_field(segs, a_t):
    w = pp.web_req(2 * a_t * math.cos(math.radians(18))) + pp.BAR_MARGIN   # long diagonal 1.902 a_t

    def field(X, Y):
        return seg_dist(X, Y, segs) - w / 2
    return field, w


# ---------- checks ----------
def symmetry(holes):
    """Worst centroid mismatch (mm) under rotation by 72 deg and under the x-axis mirror."""
    c = np.array([pp.centroid(p) for p in holes])
    z = c[:, 0] + 1j * c[:, 1]
    worst = []
    for zt in (z * cmath.rect(1, math.radians(72)), np.conj(z)):
        worst.append(float(np.abs(zt[:, None] - z[None, :]).min(1).max()))
    return worst


def glare_holes(holes):
    """Indices of holes that reach into the glare zone; for the upper ring also those below
    E_EYE_TOP (bulb visible to a viewer)."""
    glare, eye = [], []
    for i, p in enumerate(holes):
        e = pp.elevation(p[:, 0], p[:, 1])
        if pp.CFG["ring"] > 0:
            if e.min() < pp.E_GLARE_HI:
                glare.append(i)
            if e.min() < pp.E_EYE_TOP:
                eye.append(i)
        elif np.any((e > pp.E_GLARE_LO) & (e < pp.E_GLARE_HI)):
            glare.append(i)
    return glare, eye


# ---------- preview ----------
def preview(holes, glare, eye, path, title):
    fig, ax = plt.subplots(figsize=(6, 6.3))
    bg = "#fcfcfb"
    fig.patch.set_facecolor(bg)
    ax.set_facecolor(bg)
    ax.add_patch(MplPolygon(pp.PANEL, closed=True, facecolor="#d8b07a", edgecolor="#3d3c39", linewidth=1.2))
    for i in range(len(pp.KEYS)):
        ax.add_patch(MplPolygon(pp.rect_corners(i), closed=True, facecolor="#a9a8a2", alpha=0.6, edgecolor="none"))
        ax.add_patch(MplPolygon(pp.slot_corners(i), closed=True, facecolor=bg, edgecolor="#3d3c39", linewidth=0.5))
    for i, p in enumerate(holes):
        fc = bg
        if i in glare:
            fc = "#e0392b" if pp.size(p) > GLARE_BIG else "#f6c48f"
        ax.add_patch(MplPolygon(p, closed=True, facecolor=fc, edgecolor="#3d3c39", linewidth=0.5,
                                hatch="////" if i in eye else None))
    xs = np.linspace(-pp.RP, pp.RV, 300)
    ys = np.linspace(-pp.RV, pp.RV, 300)
    X, Y = np.meshgrid(xs, ys)
    E = pp.elevation(X, Y)
    inside = np.min(np.stack([pp.RP - (X * nx + Y * ny) for nx, ny in pp.EDGE_N]), axis=0) > 0
    E = np.where(inside, E, np.nan)
    levels = [pp.E_EYE_TOP, pp.E_GLARE_HI] if pp.CFG["ring"] > 0 else [pp.E_GLARE_LO, pp.E_GLARE_HI]
    ax.contour(xs, ys, E, levels=levels, colors="#eb6834", linewidths=1, linestyles=[(0, (3, 2))])
    ax.set_aspect("equal")
    ax.set_xlim(-pp.RP - 4, pp.RV + 4)
    ax.set_ylim(-pp.RV - 4, pp.RV + 4)
    ax.axis("off")
    legend = (f"Glare zone holes: light orange <= {GLARE_BIG:.0f} mm, red > {GLARE_BIG:.0f} mm"
              + (f", hatched: below e = {pp.E_EYE_TOP:+.1f}° (bulb visible)" if pp.CFG["ring"] > 0 else "")
              + f". Dashed: e = {', '.join(f'{v:+.1f}°' for v in levels)}.")
    ax.set_title(title, fontsize=8, color="#0b0b0b", loc="left")
    fig.text(0.02, 0.015, legend, fontsize=6.5, color="#52514e")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(path, facecolor=bg)
    plt.close(fig)


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
    tiling, panel, rot36 = args.tiling, args.panel, args.rot36
    a_t = args.a_t if args.a_t is not None else A_T_DEFAULT[tiling, panel]
    img_dir, dxf_dir = os.path.abspath(args.img_dir), os.path.abspath(args.dxf_dir)
    os.makedirs(img_dir, exist_ok=True)
    pp.CFG = dict(pp.PANELS[panel], glare_keepout=False)
    segs = tile_edges(tiling, a_t, rot36)
    pp.pattern_field, w = make_field(segs, a_t)
    holes = pp.build()
    bridge, pair, edge, keep, _, emin = pp.check(holes)
    rot_err, mir_err = symmetry(holes)
    glare, eye = glare_holes(holes)
    panel_area = 5 * pp.RP * pp.RP * math.tan(math.radians(36))
    open_area = sum(pp.polygon_area(p) for p in holes)
    open_pct = 100 * open_area / panel_area
    sizes = [pp.size(p) for p in holes]
    g_max = max((sizes[i] for i in glare), default=0.0)
    print(f"{tiling} {panel}{' rot36' if rot36 else ''}: a_t = {a_t:.1f} mm, bar {w:.2f} mm, {len(segs)} edges")
    print(f"{len(holes)} holes, {min(sizes):.1f} mm to {max(sizes):.1f} mm, open area {open_area:.0f} mm^2 "
          f"({open_pct:.0f} %)")
    print(f"check: bridge margin {bridge:+.2f} mm (actual {pair[0]:.2f}, required {pair[1]:.2f}), "
          f"edge margin {edge:+.2f} mm, key margin {keep:+.2f} mm")
    print(f"symmetry: rotation 72 deg {rot_err:.3f} mm, mirror {mir_err:.3f} mm (limit {SYM_TOL} mm)")
    print(f"glare zone: {len(glare)} holes, largest {g_max:.1f} mm, "
          f"{sum(sizes[i] > GLARE_BIG for i in glare)} above {GLARE_BIG:.0f} mm"
          + (f"; {len(eye)} holes below e = {pp.E_EYE_TOP:+.1f} deg (lowest point {emin:+.1f} deg)"
             if pp.CFG["ring"] > 0 else ""))
    name = f"penrose_{tiling}_{panel}{'_rot36' if rot36 else ''}"
    tname = {"p3": "Penrose P3 rhombs", "p2": "Penrose P2 kites and darts"}[tiling]
    title = (f"{pp.CFG['title']}: {tname}, edge {a_t:.0f} mm, {len(holes)} holes, open {open_pct:.0f} %. "
             f"{pp.CFG['tip'].capitalize()}.")
    svg = os.path.join(img_dir, f"{name}.svg")
    preview(holes, glare, eye, svg, title)
    print(f"written: {svg}")
    if bridge < 0 or edge < 0 or keep < 0 or max(rot_err, mir_err) > SYM_TOL:
        print("CHECK FAILED: no DXF written")
        sys.exit(1)
    os.makedirs(dxf_dir, exist_ok=True)
    out = os.path.join(dxf_dir, f"{name}_pattern.dxf")
    pp.dxf(holes, out)
    print(f"written: {out}")


if __name__ == "__main__":
    main()

"""Organic cell pattern for a dodecahedron panel. Writes DXF and an SVG preview.

Method (distance field on a 0.25 mm grid):
1. Seeds: random points with a minimum spacing, one Lloyd relaxation step.
2. Web field f = (d2 - d1) / 2, with d1, d2 the distances to the nearest and second-nearest seed,
   evaluated in warped coordinates (smooth sinusoidal warp), so the webs curve.
3. Cutout field F = min(f - w/2, border, bracket keep-outs, glare zone), with w a smooth random
   web width. A Gaussian blur rounds every corner and thickens the web junctions.
4. Cutouts are the closed contours F = 0 (marching squares), simplified to 0.03 mm.
5. Check: minimum web between cutouts, distance to the panel edge and to the bracket footprints,
   minimum elevation (exact, on the output polylines).

Coordinates: the base panel frame of the SolidCraft design (sketch PanelLaser): regular pentagon,
centre at the origin, a vertex on +x, the edge opposite at x = -rp. For an upper ring panel the
+x vertex is the bottom tip (glare zone) and the edge at -x is the top edge.

Outputs (relative to platonic_lampshades/):
  cad/dodecahedron/upper_pattern.dxf        nominal cutouts (3D cut)
  cad/dodecahedron/upper_pattern_kerf.dxf   cutouts shrunk by kerf/2 (laser)
  docs/img/upper_panel_pattern.svg          preview with keep-outs and glare zone

Usage: python3 platonic_lampshades/tools/voronoi_pattern.py [seed]
"""
import math
import os
import sys

import numpy as np
import matplotlib

matplotlib.use("svg")
matplotlib.rcParams["svg.hashsalt"] = "platonic_lampshades"
matplotlib.rcParams["svg.fonttype"] = "path"
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Polygon as MplPolygon  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CAD_DIR = os.path.join(ROOT, "cad", "dodecahedron")
IMG_DIR = os.path.join(ROOT, "docs", "img")

# Design parameters (docs/overview.md), mm
T, TB, TP, HS, LC = 3.0, 4.0, 3.0, 60.0, 48.0
LF, LB = 16.0, 30.0
KERF = 0.15
RI = T + TB + TP + HS + LC
A = RI / (math.sqrt((25 + 11 * math.sqrt(5)) / 10) / 2)
S_INSET = T / math.tan(math.radians(180 - math.degrees(math.atan(2))) / 2)
RP = A / (2 * math.tan(math.radians(36))) - S_INSET
RV = RP / math.cos(math.radians(36))
RING_N = math.degrees(math.atan(0.5))
E_GLARE_HI = 4.0                     # projection zone above this elevation (deg)

# Pattern parameters, mm
N_SEEDS = 19
SEED_SPACING = 0.85   # minimum seed spacing as a fraction of sqrt(area / N)
W_MIN, W_MAX = 4.0, 8.0     # web width range before blur
W_WAVE = 70.0         # wavelength of the web width variation
WARP = 5.0            # max warp displacement
WARP_WAVE = (55.0, 95.0)
WARP_TERMS = 3
BORDER = 6.0          # solid border at the panel edge
KEEP_MARGIN = 3.0     # clearance around bracket footprints
GLARE_CLEAR = 3.0     # clearance to the glare zone line
BLUR = 1.6            # Gaussian blur sigma of the cutout field
GRID = 0.25           # grid step
A_MIN = 60.0          # smallest cutout kept, mm^2
SIMPLIFY = 0.03       # polyline simplification tolerance
WEB_MIN = 3.0         # required: minimum web, mm
KEEP_MIN = 2.0        # required: minimum distance to bracket footprints, mm


def elevation(x, y):
    """Elevation (deg) of a point on an upper ring panel's outer face, base frame."""
    a = math.radians(RING_N)
    u, v = y, -x
    px = RI * np.cos(a) - v * np.sin(a)
    pz = RI * np.sin(a) + v * np.cos(a)
    return np.degrees(np.arctan2(pz, np.hypot(px, u)))


def glare_line_x():
    """Largest x such that the line x = const lies above E_GLARE_HI inside the panel."""
    ys = np.linspace(-RP, RP, 81)
    lo, hi = np.full_like(ys, -RP), np.full_like(ys, RV)
    for _ in range(60):
        m = (lo + hi) / 2
        ok = elevation(m, ys) > E_GLARE_HI
        lo, hi = np.where(ok, m, lo), np.where(ok, hi, m)
    return float(lo.min())


X_GLARE = glare_line_x()
PANEL = [(RV * math.cos(math.radians(72 * k)), RV * math.sin(math.radians(72 * k))) for k in range(5)]
EDGE_N = [(math.cos(math.radians(36 + 72 * k)), math.sin(math.radians(36 + 72 * k))) for k in range(5)]


def rect_corners(k, grow=0.0):
    ux, uy = EDGE_N[k]
    tx, ty = -uy, ux
    hw, d_in, d_out = LB / 2 + grow, RP - LF - grow, RP
    return [(d_in * ux - hw * tx, d_in * uy - hw * ty), (d_in * ux + hw * tx, d_in * uy + hw * ty),
            (d_out * ux + hw * tx, d_out * uy + hw * ty), (d_out * ux - hw * tx, d_out * uy - hw * ty)]


def rect_sdf(X, Y, k):
    """Signed distance to bracket footprint k (positive outside)."""
    ux, uy = EDGE_N[k]
    tx, ty = -uy, ux
    s = X * ux + Y * uy - (RP - LF / 2)        # across, centred on the footprint
    t = X * tx + Y * ty
    qx, qy = np.abs(s) - LF / 2, np.abs(t) - LB / 2
    return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0)


def blur(F, sigma_px):
    r = int(3 * sigma_px) + 1
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma_px) ** 2)
    k /= k.sum()
    Fp = np.pad(F, r, mode="edge")
    Fp = np.apply_along_axis(lambda m: np.convolve(m, k, mode="valid"), 0, Fp)
    Fp = np.apply_along_axis(lambda m: np.convolve(m, k, mode="valid"), 1, Fp)
    return Fp


def sin_field(rng, terms, waves, amp):
    comps = []
    for _ in range(terms):
        lam = rng.uniform(*waves)
        ang = rng.uniform(0, 2 * math.pi)
        kk = 2 * math.pi / lam
        comps.append((kk * math.cos(ang), kk * math.sin(ang), rng.uniform(0, 2 * math.pi)))
    return lambda X, Y: amp / terms * sum(np.sin(kx * X + ky * Y + ph) for kx, ky, ph in comps)


def in_panel(x, y, inset):
    return all(x * nx + y * ny <= RP - inset for nx, ny in EDGE_N)


def seeds(rng):
    area = 2.5 * RP * RP * math.tan(math.radians(36)) * 2
    rmin = SEED_SPACING * math.sqrt(area / N_SEEDS)
    pts = []
    for _ in range(20000):
        if len(pts) == N_SEEDS:
            break
        x, y = rng.uniform(-RP, RV), rng.uniform(-RV, RV)
        if in_panel(x, y, 3.0) and all(math.hypot(x - a, y - b) > rmin for a, b in pts):
            pts.append((x, y))
    pts = np.array(pts)
    # one Lloyd step on a coarse grid
    g = np.linspace(-RV, RV, 200)
    GX, GY = np.meshgrid(g, g)
    inside = np.ones_like(GX, bool)
    for nx, ny in EDGE_N:
        inside &= GX * nx + GY * ny <= RP
    gx, gy = GX[inside], GY[inside]
    idx = np.argmin((gx[:, None] - pts[None, :, 0]) ** 2 + (gy[:, None] - pts[None, :, 1]) ** 2, axis=1)
    for i in range(len(pts)):
        m = idx == i
        if m.any():
            pts[i] = (gx[m].mean(), gy[m].mean())
    return pts


def field(seed):
    rng = np.random.default_rng(seed)
    pyrng = __import__("random").Random(seed)
    pts = seeds(pyrng)
    xs = np.arange(-RP - 2, RV + 2, GRID)
    ys = np.arange(-RV - 2, RV + 2, GRID)
    X, Y = np.meshgrid(xs, ys)
    wx = sin_field(pyrng, WARP_TERMS, WARP_WAVE, WARP / math.sqrt(2))
    wy = sin_field(pyrng, WARP_TERMS, WARP_WAVE, WARP / math.sqrt(2))
    XW, YW = X + wx(X, Y), Y + wy(X, Y)
    d = np.sqrt((XW[..., None] - pts[:, 0]) ** 2 + (YW[..., None] - pts[:, 1]) ** 2)
    d.sort(axis=-1)
    f = (d[..., 1] - d[..., 0]) / 2
    wf = sin_field(pyrng, 3, (W_WAVE * 0.7, W_WAVE * 1.3), 1.0)
    w = W_MIN + (W_MAX - W_MIN) * (0.5 + 0.5 * np.clip(wf(X, Y) * 1.5, -1, 1))
    F = f - w / 2
    border = np.min(np.stack([RP - (X * nx + Y * ny) for nx, ny in EDGE_N]), axis=0) - BORDER
    keep = np.min(np.stack([rect_sdf(X, Y, k) for k in range(5)]), axis=0) - KEEP_MARGIN
    glare = (X_GLARE - X) - GLARE_CLEAR
    F = np.minimum.reduce([F, border, keep, glare])
    F = blur(F, BLUR / GRID)
    del rng
    return xs, ys, F, pts


def polygon_area(p):
    x, y = p[:, 0], p[:, 1]
    return 0.5 * float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


def simplify(p, tol):
    """Douglas-Peucker on an open polyline."""
    if len(p) < 3:
        return p
    a, b = p[0], p[-1]
    ab = b - a
    L = np.hypot(*ab)
    if L < 1e-12:
        dist = np.hypot(*(p - a).T)
    else:
        dist = np.abs(ab[0] * (p[:, 1] - a[1]) - ab[1] * (p[:, 0] - a[0])) / L
    i = int(np.argmax(dist))
    if dist[i] > tol:
        return np.vstack([simplify(p[:i + 1], tol)[:-1], simplify(p[i:], tol)])
    return np.array([a, b])


def contours(xs, ys, F):
    cs = plt.contour(xs, ys, F, levels=[0.0])
    loops = []
    for seg in cs.allsegs[0]:
        if len(seg) < 8 or np.hypot(*(seg[0] - seg[-1])) > 1e-6:
            continue
        p = seg[:-1]
        if polygon_area(p) < 0:
            p = p[::-1]
        if polygon_area(p) < A_MIN:
            continue
        # split the closed loop in two halves for the simplification
        h = len(p) // 2
        q = np.vstack([simplify(np.vstack([p[:h + 1]]), SIMPLIFY)[:-1],
                       simplify(np.vstack([p[h:], p[:1]]), SIMPLIFY)[:-1]])
        loops.append(q)
    plt.close("all")
    return loops


def offset_in(p, d):
    """Offset a CCW smooth loop inward by d (vertex normals)."""
    prv, nxt = np.roll(p, 1, axis=0), np.roll(p, -1, axis=0)
    t = nxt - prv
    t /= np.hypot(t[:, 0], t[:, 1])[:, None]
    n = np.stack([-t[:, 1], t[:, 0]], axis=1)   # left normal = inward for CCW
    return p + d * n


def seg_point_dist(P, A_, B_):
    """Distances from points P (n,2) to segments A_->B_ (m,2): (n,m)."""
    AB = B_ - A_
    L2 = np.maximum((AB ** 2).sum(1), 1e-12)
    AP = P[:, None, :] - A_[None, :, :]
    t = np.clip((AP * AB[None]).sum(2) / L2[None], 0, 1)
    D = AP - t[..., None] * AB[None]
    return np.hypot(D[..., 0], D[..., 1])


def check(loops):
    web = 1e9
    for i in range(len(loops)):
        for j in range(i + 1, len(loops)):
            Bj = loops[j]
            web = min(web, seg_point_dist(loops[i], Bj, np.roll(Bj, -1, axis=0)).min())
    allp = np.vstack(loops)
    edge = float(np.min([RP - (allp[:, 0] * nx + allp[:, 1] * ny) for nx, ny in EDGE_N]))
    keep = 1e9
    for k in range(5):
        rc = np.array(rect_corners(k))
        keep = min(keep, seg_point_dist(allp, rc, np.roll(rc, -1, axis=0)).min())
        inside = np.array([rect_sdf(np.array([x]), np.array([y]), k)[0] < 0 for x, y in allp])
        if inside.any():
            keep = -1.0
    emin = float(elevation(allp[:, 0], allp[:, 1]).min())
    return web, edge, keep, emin


def dxf(loops, path):
    out = ["0", "SECTION", "2", "ENTITIES"]
    for p in loops:
        for i in range(len(p)):
            (x0, y0), (x1, y1) = p[i], p[(i + 1) % len(p)]
            out += ["0", "LINE", "8", "0", "10", f"{x0:.4f}", "20", f"{y0:.4f}", "30", "0",
                    "11", f"{x1:.4f}", "21", f"{y1:.4f}", "31", "0"]
    out += ["0", "ENDSEC", "0", "EOF"]
    with open(path, "w") as f:
        f.write("\n".join(out) + "\n")


def preview(loops, path, seed, open_pct):
    fig, ax = plt.subplots(figsize=(6, 6))
    fig.patch.set_facecolor("#fcfcfb")
    ax.set_facecolor("#fcfcfb")
    ax.add_patch(MplPolygon(PANEL, closed=True, facecolor="#d8b07a", edgecolor="#3d3c39", linewidth=1.2))
    for k in range(5):
        ax.add_patch(MplPolygon(rect_corners(k), closed=True, facecolor="#a9a8a2", alpha=0.5, edgecolor="none"))
    for p in loops:
        ax.add_patch(MplPolygon(p, closed=True, facecolor="#fcfcfb", edgecolor="#3d3c39", linewidth=0.6))
    ax.plot([X_GLARE, X_GLARE], [-RP * 0.75, RP * 0.75], color="#eb6834", linewidth=1, linestyle=(0, (3, 2)))
    ax.text(X_GLARE + 2, RP * 0.62, f"glare zone\n(e < {E_GLARE_HI:+.0f}°)", fontsize=7, color="#52514e")
    ax.set_aspect("equal")
    ax.set_xlim(-RP - 4, RV + 4)
    ax.set_ylim(-RV - 4, RV + 4)
    ax.axis("off")
    ax.set_title(f"Upper ring panel, base frame (bottom tip on +x). Seed {seed}, open area {open_pct:.0f} %.",
                 fontsize=8, color="#0b0b0b", loc="left")
    fig.tight_layout()
    fig.savefig(path, facecolor="#fcfcfb")
    plt.close(fig)


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    xs, ys, F, _ = field(seed)
    loops = contours(xs, ys, F)
    kerf_loops = [offset_in(p, KERF / 2) for p in loops]
    web, edge, keep, emin = check(loops)
    panel_area = 5 * RP * RP * math.tan(math.radians(36))
    open_area = sum(polygon_area(p) for p in loops)
    print(f"a = {A:.2f} mm, rp = {RP:.2f} mm, glare line x = {X_GLARE:.2f} mm")
    print(f"seed {seed}: {len(loops)} cutouts, open area {open_area:.0f} mm^2 "
          f"({100 * open_area / panel_area:.0f} % of panel), {sum(len(p) for p in loops)} segments")
    print(f"check: min web {web:.2f} mm (need {WEB_MIN}), to panel edge {edge:.2f} mm, "
          f"to bracket footprints {keep:.2f} mm (need {KEEP_MIN}), min elevation {emin:+.2f} deg "
          f"(need > {E_GLARE_HI:+.0f})")
    preview(loops, os.path.join(IMG_DIR, "upper_panel_pattern.svg"), seed, 100 * open_area / panel_area)
    if web < WEB_MIN or keep < KEEP_MIN or emin <= E_GLARE_HI:
        print("CHECK FAILED: no DXF written")
        sys.exit(1)
    dxf(loops, os.path.join(CAD_DIR, "upper_pattern.dxf"))
    dxf(kerf_loops, os.path.join(CAD_DIR, "upper_pattern_kerf.dxf"))


if __name__ == "__main__":
    main()

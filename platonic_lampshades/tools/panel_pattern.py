"""Polar Marrakech trellis for the upper ring panels. Writes DXF and an SVG preview.

Pattern: the Moroccan lantern trellis (diamond tiling with S-curved edges) in log-polar
coordinates around the panel centre (conformal map). N lanterns per ring (multiple of 5), the
lanterns point outwards and grow with the radius. The bar width in mm follows the local hole size.

Pipeline (0.2 mm grid):
1. Skeleton distance S in map units, converted to mm with the local scale rho / k of the map.
2. Cutout field F = min(S - w(rho)/2, hub, border, bracket keep-outs, glare zone), blurred
   lightly (inner corner radius about 1 mm).
3. Cutouts: closed contours F = 0; holes thinner than 2.4 mm or smaller than 15 mm^2 are dropped.
4. Check on the output polylines (no DXF if it fails): bridge >= 3.0 mm, rising linearly to
   4.0 mm when the larger adjacent hole measures 15 mm to 35 mm; the same rule to the panel edge
   and the bracket footprints; all cutouts above the glare zone.

Coordinates: base panel frame of the design (sketch PanelLaser): regular pentagon, centre at the
origin, a vertex on +x, the opposite edge at x = -rp. On an upper ring panel the +x vertex is the
bottom tip (glare zone).

Outputs (relative to platonic_lampshades/):
  cad/dodecahedron/upper_pattern.dxf        nominal cutouts (3D cut, sketch UpperPatternSketch)
  cad/dodecahedron/upper_pattern_kerf.dxf   cutouts shrunk by kerf/2 (sketch UpperPanelLaser)
  docs/img/upper_panel_pattern.svg          preview with keep-outs and glare zone

Usage: python3 platonic_lampshades/tools/panel_pattern.py
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

# Design parameters (docs/overview.md), mm. Keep in sync with the design.
T, TB, TP, HS, LC = 3.0, 4.0, 3.0, 60.0, 48.0
LF, LB = 16.0, 30.0
KERF = 0.15
RI = T + TB + TP + HS + LC
A = RI / (math.sqrt((25 + 11 * math.sqrt(5)) / 10) / 2)
S_INSET = T / math.tan(math.radians(180 - math.degrees(math.atan(2))) / 2)
RP = A / (2 * math.tan(math.radians(36))) - S_INSET
RV = RP / math.cos(math.radians(36))
RING_N = math.degrees(math.atan(0.5))
E_GLARE_HI = 4.0                     # projection zone above this elevation, deg

# Pattern parameters
N_RING = 10           # lanterns per ring (multiple of 5)
R0 = 34.0             # radius of the lantern ring centred on the panel axis, mm
STRETCH = 1.2         # lantern tile height / width
BULGE = 0.09          # S-curve amplitude / edge length
BAR_MARGIN = 0.3      # bar width above the bridge rule, mm
R_HUB = 14.0          # solid hub radius, mm
BORDER = 6.0          # solid border at the panel edge, mm
KEEP_MARGIN = 4.5     # clearance around the bracket footprints, mm
GLARE_CLEAR = 3.0     # clearance to the glare zone line, mm
BLUR = 0.5            # Gaussian blur sigma, mm
GRID = 0.2
R_HOLE_MIN = 1.2      # drop holes narrower than 2 * R_HOLE_MIN
A_MIN = 15.0          # drop holes smaller than this, mm^2
SIMPLIFY = 0.03       # polyline simplification tolerance, mm

PANEL = [(RV * math.cos(math.radians(72 * k)), RV * math.sin(math.radians(72 * k))) for k in range(5)]
EDGE_N = [(math.cos(math.radians(36 + 72 * k)), math.sin(math.radians(36 + 72 * k))) for k in range(5)]


def web_req(size):
    """Required bridge (mm) next to a hole of the given size (largest extent, mm)."""
    return 3.0 + np.clip((size - 15.0) / 20.0, 0.0, 1.0)


# ---------- panel geometry ----------
def elevation(x, y):
    """Elevation (deg) of a point on an upper ring panel's outer face, base frame."""
    a = math.radians(RING_N)
    v = -x
    px = RI * np.cos(a) - v * np.sin(a)
    pz = RI * np.sin(a) + v * np.cos(a)
    return np.degrees(np.arctan2(pz, np.hypot(px, y)))


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


def rect_corners(k):
    """Bracket footprint k: flange width LF from edge k, length LB, centred on the edge."""
    ux, uy = EDGE_N[k]
    tx, ty = -uy, ux
    hw, d_in, d_out = LB / 2, RP - LF, RP
    return [(d_in * ux - hw * tx, d_in * uy - hw * ty), (d_in * ux + hw * tx, d_in * uy + hw * ty),
            (d_out * ux + hw * tx, d_out * uy + hw * ty), (d_out * ux - hw * tx, d_out * uy - hw * ty)]


def rect_sdf(X, Y, k):
    """Signed distance to bracket footprint k (positive outside)."""
    ux, uy = EDGE_N[k]
    tx, ty = -uy, ux
    s = X * ux + Y * uy - (RP - LF / 2)
    t = X * tx + Y * ty
    qx, qy = np.abs(s) - LF / 2, np.abs(t) - LB / 2
    return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0)


# ---------- lantern trellis ----------
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


def pattern_field(X, Y):
    """Cutout field before keep-outs: positive inside the lantern holes."""
    p = 10.0                                   # tile width in map units
    k = N_RING * p / (2 * math.pi)             # map units per radian
    rho = np.maximum(np.hypot(X, Y), 0.5)
    th = np.arctan2(Y, X)
    S = lantern_dist(k * th, k * np.log(rho / R0), p, STRETCH, BULGE) * rho / k
    hole = 2 * math.pi * rho / N_RING * STRETCH * 0.9      # approximate local hole length
    w = web_req(hole) + BAR_MARGIN
    return np.minimum(S - w / 2, rho - R_HUB)


# ---------- pipeline ----------
def blur(F, sigma_px):
    r = int(3 * sigma_px) + 1
    kern = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma_px) ** 2)
    kern /= kern.sum()
    Fp = np.pad(F, r, mode="edge")
    Fp = np.apply_along_axis(lambda m: np.convolve(m, kern, mode="valid"), 0, Fp)
    return np.apply_along_axis(lambda m: np.convolve(m, kern, mode="valid"), 1, Fp)


def polygon_area(p):
    return 0.5 * float(np.dot(p[:, 0], np.roll(p[:, 1], -1)) - np.dot(p[:, 1], np.roll(p[:, 0], -1)))


def simplify(p, tol):
    """Douglas-Peucker on an open polyline."""
    if len(p) < 3:
        return p
    a, b = p[0], p[-1]
    ab = b - a
    L = np.hypot(*ab)
    dist = np.hypot(*(p - a).T) if L < 1e-12 else np.abs(ab[0] * (p[:, 1] - a[1]) - ab[1] * (p[:, 0] - a[0])) / L
    i = int(np.argmax(dist))
    if dist[i] > tol:
        return np.vstack([simplify(p[:i + 1], tol)[:-1], simplify(p[i:], tol)])
    return np.array([a, b])


def build():
    xs = np.arange(-RP - 2, RV + 2, GRID)
    ys = np.arange(-RV - 2, RV + 2, GRID)
    X, Y = np.meshgrid(xs, ys)
    border = np.min(np.stack([RP - (X * nx + Y * ny) for nx, ny in EDGE_N]), axis=0) - BORDER
    keep = np.min(np.stack([rect_sdf(X, Y, k) for k in range(5)]), axis=0) - KEEP_MARGIN
    glare = (X_GLARE - X) - GLARE_CLEAR
    F = blur(np.minimum.reduce([pattern_field(X, Y), border, keep, glare]), BLUR / GRID)
    tmp = plt.figure()
    segs = tmp.add_subplot().contour(xs, ys, F, levels=[0.0]).allsegs[0]
    plt.close(tmp)
    holes = []
    for seg in segs:
        if len(seg) < 6 or np.hypot(*(seg[0] - seg[-1])) > 1e-6:
            continue
        p = seg[:-1]
        if polygon_area(p) < 0:
            p = p[::-1]
        if polygon_area(p) < A_MIN:
            continue
        x0, y0 = p.min(0)
        x1, y1 = p.max(0)
        sub = F[np.ix_((ys >= y0) & (ys <= y1), (xs >= x0) & (xs <= x1))]
        if sub.size == 0 or sub.max() < R_HOLE_MIN:
            continue
        h = len(p) // 2
        holes.append(np.vstack([simplify(p[:h + 1], SIMPLIFY)[:-1], simplify(np.vstack([p[h:], p[:1]]), SIMPLIFY)[:-1]]))
    return holes


def offset_in(p, d):
    """Offset a CCW smooth loop inward by d (vertex normals)."""
    t = np.roll(p, -1, axis=0) - np.roll(p, 1, axis=0)
    t /= np.hypot(t[:, 0], t[:, 1])[:, None]
    return p + d * np.stack([-t[:, 1], t[:, 0]], axis=1)


def seg_point_dist(P, A_, B_):
    AB = B_ - A_
    L2 = np.maximum((AB ** 2).sum(1), 1e-12)
    AP = P[:, None, :] - A_[None, :, :]
    t = np.clip((AP * AB[None]).sum(2) / L2[None], 0, 1)
    D = AP - t[..., None] * AB[None]
    return np.hypot(D[..., 0], D[..., 1])


def size(p):
    return float(max(np.ptp(p[:, 0]), np.ptp(p[:, 1])))


def check(holes):
    """Worst margins (actual - required) between holes, to the edge, to the bracket footprints;
    lowest elevation."""
    sizes = [size(p) for p in holes]
    bridge, pair = 1e9, None
    for i in range(len(holes)):
        for j in range(i + 1, len(holes)):
            bi, bj = holes[i], holes[j]
            if (bi[:, 0].min() - bj[:, 0].max() > 6 or bj[:, 0].min() - bi[:, 0].max() > 6 or
                    bi[:, 1].min() - bj[:, 1].max() > 6 or bj[:, 1].min() - bi[:, 1].max() > 6):
                continue
            d = seg_point_dist(bi, bj, np.roll(bj, -1, axis=0)).min()
            req = web_req(max(sizes[i], sizes[j]))
            if d - req < bridge:
                bridge, pair = d - req, (d, req)
    edge, keep = 1e9, 1e9
    for p, sz in zip(holes, sizes):
        req = web_req(sz)
        edge = min(edge, float(np.min([RP - (p[:, 0] * nx + p[:, 1] * ny) for nx, ny in EDGE_N])) - req)
        for k in range(5):
            rc = np.array(rect_corners(k))
            keep = min(keep, seg_point_dist(p, rc, np.roll(rc, -1, axis=0)).min() - req)
    allp = np.vstack(holes)
    return bridge, pair, edge, keep, float(elevation(allp[:, 0], allp[:, 1]).min())


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


def preview(holes, path, open_pct):
    fig, ax = plt.subplots(figsize=(6, 6))
    fig.patch.set_facecolor("#fcfcfb")
    ax.set_facecolor("#fcfcfb")
    ax.add_patch(MplPolygon(PANEL, closed=True, facecolor="#d8b07a", edgecolor="#3d3c39", linewidth=1.2))
    for k in range(5):
        ax.add_patch(MplPolygon(rect_corners(k), closed=True, facecolor="#a9a8a2", alpha=0.5, edgecolor="none"))
    for p in holes:
        ax.add_patch(MplPolygon(p, closed=True, facecolor="#fcfcfb", edgecolor="#3d3c39", linewidth=0.5))
    ax.plot([X_GLARE, X_GLARE], [-RP * 0.75, RP * 0.75], color="#eb6834", linewidth=1, linestyle=(0, (3, 2)))
    ax.text(X_GLARE + 2, RP * 0.62, f"glare zone\n(e < {E_GLARE_HI:+.0f}°)", fontsize=7, color="#52514e")
    ax.set_aspect("equal")
    ax.set_xlim(-RP - 4, RV + 4)
    ax.set_ylim(-RV - 4, RV + 4)
    ax.axis("off")
    ax.set_title(f"Upper ring panel: polar Marrakech trellis, {N_RING} lanterns per ring, open {open_pct:.0f} %. "
                 "Bottom tip on +x.", fontsize=8, color="#0b0b0b", loc="left")
    fig.tight_layout()
    fig.savefig(path, facecolor="#fcfcfb")
    plt.close(fig)


def main():
    holes = build()
    bridge, pair, edge, keep, emin = check(holes)
    panel_area = 5 * RP * RP * math.tan(math.radians(36))
    open_area = sum(polygon_area(p) for p in holes)
    sizes = [size(p) for p in holes]
    print(f"a = {A:.2f} mm, rp = {RP:.2f} mm, glare line x = {X_GLARE:.2f} mm")
    print(f"{len(holes)} holes, {min(sizes):.1f} mm to {max(sizes):.1f} mm, open area {open_area:.0f} mm^2 "
          f"({100 * open_area / panel_area:.0f} %), {sum(len(p) for p in holes)} segments")
    print(f"check: bridge margin {bridge:+.2f} mm (actual {pair[0]:.2f}, required {pair[1]:.2f}), "
          f"edge margin {edge:+.2f} mm, keep-out margin {keep:+.2f} mm, min elevation {emin:+.2f} deg")
    preview(holes, os.path.join(IMG_DIR, "upper_panel_pattern.svg"), 100 * open_area / panel_area)
    if bridge < 0 or edge < 0 or keep < 0 or emin <= E_GLARE_HI:
        print("CHECK FAILED: no DXF written")
        sys.exit(1)
    dxf(holes, os.path.join(CAD_DIR, "upper_pattern.dxf"))
    dxf([offset_in(p, KERF / 2) for p in holes], os.path.join(CAD_DIR, "upper_pattern_kerf.dxf"))
    print("written: upper_pattern.dxf, upper_pattern_kerf.dxf")


if __name__ == "__main__":
    main()

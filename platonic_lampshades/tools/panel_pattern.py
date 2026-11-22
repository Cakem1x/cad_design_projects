"""Penrose tiling patterns for the ring panels. Writes DXF and an SVG preview.

Pattern: a Penrose tiling patch centred on the panel, with exact 5-fold symmetry (D5). The tile
edges are bars of constant width; the tiles are the holes.

Tilings:
  p3   thick rhombs (72 deg / 108 deg) and thin rhombs (36 deg / 144 deg)
  p2   kites (72 / 72 / 72 / 144 deg) and darts (36 / 72 / 36 / 216 deg)

Pipeline (0.2 mm grid):
1. Robinson-triangle deflation from a D5-symmetric start wheel around the panel centre
   (p3: sun of 10 half-rhombs, p2: sun of 5 kites). Deflation keeps the D5 symmetry.
   One mirror axis lies on +x, like the panel. rot36 turns the patch by 36 deg (the other
   symmetric phase, equal to a point reflection).
2. Tile edges (no rhomb diagonals, no kite or dart axes) are the bar centrelines.
   Field S = distance to the edges. Bar width w = web_req(long tile diagonal 1.902 a_t) + BAR_MARGIN.
3. Cutout field F = min(S - w/2, border, key keep-outs), blurred lightly (inner corner radius
   about 1 mm). Cutouts: closed contours F = 0; holes thinner than 2.4 mm or smaller than
   15 mm^2 are dropped. No hole is dropped for glare: the preview marks the design zones and
   colours the holes that reach into the glare zone.
4. Checks on the output polylines (no DXF if one fails): bridge >= 3.0 mm, rising linearly to
   4.0 mm when the larger adjacent hole measures 15 mm to 35 mm; the same rule to the panel edge
   and to the key slots; solid arm footprints; symmetry: each hole centroid rotated by 72 deg and
   mirrored about the x axis matches a hole centroid within SYM_TOL.

Joints: cross-section keys (docs/joinery.md), 2 per edge, 10 per panel. Key footprint on the
inner face: TK along the edge x L_ARM from the edge, centred E_KEY / 2 from the edge centre. It
contains the slot (TK x W_TAB, centred H_TAB from the edge). Keep-out: a rounded node around the
slot (slot margin: bridge rule for the long tile diagonal + BAR_MARGIN) plus ARM_MARGIN around
the arm footprint. The bars widen locally into the node.

Panels (see PANELS):
  upper   upper ring: P3, a_t = 18 mm, rot36.
  lower   lower ring: P3, a_t = 12 mm.
  Both are cut over all zones (status: all open). The preview marks the glare zone.

Coordinates: base panel frame of the design (sketch PanelLaser): regular pentagon, centre at the
origin, a vertex on +x, the opposite edge at x = -rp. On an upper ring panel the +x vertex is the
bottom tip. On a lower ring panel the +x vertex is the top tip.

Outputs (relative to platonic_lampshades/), <panel> = upper or lower:
  cad/dodecahedron/<panel>_pattern.dxf        nominal cutouts (3D cut)
  cad/dodecahedron/<panel>_pattern_kerf.dxf   cutouts shrunk by kerf/2 (laser sketch)
  docs/img/<panel>_panel_pattern.svg          preview with keep-outs and design zones
  cad/dodecahedron/<panel>_panel_x5.dxf       laser file: panel_x1.dxf (outline and key slots,
                                              export of sketch PanelLaser) + kerf cutouts on CUT

Usage: python3 platonic_lampshades/tools/panel_pattern.py [upper|lower]
The prototypes (prototypes/penrose_pattern.py, prototypes/marrakech_pattern.py) import the
pipeline from here.
"""
import cmath
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

# Design parameters, mm: read from the SolidCraft design (tools/design.py, docs/overview.md)
from design import KIT  # noqa: E402

T = KIT["t"]
KERF = KIT["kerf"]
# Key parameters (docs/joinery.md), mm
TK = KIT["tk"]        # key thickness
L_ARM = KIT["Larm"]   # arm length on the inner face, from the panel edge
H_TAB = KIT["htab"]   # slot centre from the panel edge
W_TAB = KIT["wtab"]   # slot length across the edge
E_KEY = KIT["ek"]     # distance between the 2 keys of an edge
RP = KIT["rp"]        # panel inradius (outer face)
RI = KIT["ri"]        # inradius of the solid (outer face)
A = KIT["a"]          # edge length of the solid
RV = RP / math.cos(math.radians(36))
RING_N = math.degrees(math.atan(0.5))
E_GLARE_LO = -46.0                   # table zone below this elevation, deg
E_GLARE_HI = 4.0                     # projection zone above this elevation, deg
E_EYE_TOP = -1.3                     # top of the viewer envelope (no zone margin), deg

# Panel types. ring: +1 upper ring (normal at e = +26.6 deg, +x vertex down),
# -1 lower ring (normal at e = -26.6 deg, +x vertex up). a_t: tile edge length, mm.
PANELS = {
    "upper": dict(ring=+1, tiling="p3", a_t=18.0, rot36=True,
                  title="Upper ring panel", tip="bottom tip on +x"),
    "lower": dict(ring=-1, tiling="p3", a_t=12.0, rot36=False,
                  title="Lower ring panel", tip="top tip on +x"),
}
CFG = PANELS["upper"]  # set by run()
TILING_NAMES = {"p3": "Penrose P3 rhombs", "p2": "Penrose P2 kites and darts"}

# Pattern parameters
PHI = (1 + 5 ** 0.5) / 2
BAR_MARGIN = 0.3      # bar width above the bridge rule, mm
BORDER = 6.0          # solid border at the panel edge, mm
SLOT_MARGIN = 4.3     # default node around the key slot: bridge rule maximum + 0.3 mm
ARM_MARGIN = 1.5      # solid wood around the key arm footprint, mm
BLUR = 0.5            # Gaussian blur sigma, mm
GRID = 0.2
R_HOLE_MIN = 1.2      # drop holes narrower than 2 * R_HOLE_MIN
A_MIN = 15.0          # drop holes smaller than this, mm^2
SIMPLIFY = 0.03       # polyline simplification tolerance, mm
SYM_TOL = 0.2         # centroid mismatch under rotation and mirror, mm
GLARE_BIG = 15.0      # glare zone holes above this size are marked red, mm

PANEL = [(RV * math.cos(math.radians(72 * k)), RV * math.sin(math.radians(72 * k))) for k in range(5)]
EDGE_N = [(math.cos(math.radians(36 + 72 * k)), math.sin(math.radians(36 + 72 * k))) for k in range(5)]
PANEL_AREA = 5 * RP * RP * math.tan(math.radians(36))


def web_req(size):
    """Required bridge (mm) next to a hole of the given size (largest extent, mm)."""
    return 3.0 + np.clip((size - 15.0) / 20.0, 0.0, 1.0)


# ---------- panel geometry ----------
def elevation(x, y, ring=None):
    """Elevation (deg) of a point on a ring panel's outer face, base frame.
    ring: +1 upper ring, -1 lower ring (default: current panel)."""
    ring = CFG["ring"] if ring is None else ring
    a = math.radians(ring * RING_N)          # face normal elevation
    v = -ring * x                            # distance up the panel from its centre
    px = RI * np.cos(a) - v * np.sin(a)
    pz = RI * np.sin(a) + v * np.cos(a)
    return np.degrees(np.arctan2(pz, np.hypot(px, y)))


# Key footprints: (edge index, offset along the edge from its centre, mm)
KEYS = [(k, sgn * E_KEY / 2) for k in range(5) for sgn in (-1, 1)]


def _rect(k, off, d_in, d_out, w):
    """Rectangle from d_in to d_out along the normal of edge k, width w along the edge at off."""
    ux, uy = EDGE_N[k]
    tx, ty = -uy, ux
    a, b = off - w / 2, off + w / 2
    return [(d_in * ux + a * tx, d_in * uy + a * ty), (d_in * ux + b * tx, d_in * uy + b * ty),
            (d_out * ux + b * tx, d_out * uy + b * ty), (d_out * ux + a * tx, d_out * uy + a * ty)]


def rect_corners(i):
    """Key footprint i: TK along the edge, L_ARM from the edge into the panel."""
    k, off = KEYS[i]
    return _rect(k, off, RP - L_ARM, RP, TK)


def slot_corners(i):
    """Key slot i: TK along the edge, W_TAB across, centred H_TAB from the edge."""
    k, off = KEYS[i]
    return _rect(k, off, RP - H_TAB - W_TAB / 2, RP - H_TAB + W_TAB / 2, TK)


def _rect_sdf(X, Y, k, off, d_in, d_out, w):
    """Signed distance to the rectangle of _rect (positive outside)."""
    ux, uy = EDGE_N[k]
    tx, ty = -uy, ux
    s = X * ux + Y * uy - (d_in + d_out) / 2
    t = X * tx + Y * ty - off
    qx, qy = np.abs(s) - (d_out - d_in) / 2, np.abs(t) - w / 2
    return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0)


def rect_sdf(X, Y, i):
    """Signed distance to key footprint i (positive outside)."""
    k, off = KEYS[i]
    return _rect_sdf(X, Y, k, off, RP - L_ARM, RP, TK)


def slot_sdf(X, Y, i):
    """Signed distance to key slot i (positive outside)."""
    k, off = KEYS[i]
    return _rect_sdf(X, Y, k, off, RP - H_TAB - W_TAB / 2, RP - H_TAB + W_TAB / 2, TK)


def key_keepout(X, Y):
    """Keep-out field of all keys (positive where cutouts are allowed): a node of
    CFG["slot_margin"] around each slot, ARM_MARGIN around each arm footprint."""
    n = range(len(KEYS))
    slot_margin = CFG.get("slot_margin", SLOT_MARGIN)
    return np.minimum(np.min(np.stack([slot_sdf(X, Y, i) for i in n]), axis=0) - slot_margin,
                      np.min(np.stack([rect_sdf(X, Y, i) for i in n]), axis=0) - ARM_MARGIN)


# ---------- Penrose tilings ----------
def p3_tiles(n):
    """P3: half-rhombs as edge pairs. Half-rhomb (kind, A, B, C), A = apex, kind 0 thin (36 deg),
    1 thick (108 deg). Edges AB and AC; BC is the rhomb diagonal shared with the mirror half."""
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
    """P2: half-kites ('K', apex, side, corner) and half-darts ('D', reflex, side, tip) as edge
    pairs. Kite edges apex-side (long) and side-corner (short); axis apex-corner.
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
    while a_t * PHI ** n < (RV + 3 * a_t) / 0.9:
        n += 1
    gen = p3_tiles if tiling == "p3" else p2_tiles
    radius = a_t * PHI ** n
    rot = cmath.rect(1, math.pi / 5) if rot36 else 1
    seen, segs = set(), []
    for e in (e for tri in gen(n) for e in tri):
        p, q = (z * radius * rot for z in e)
        key = tuple(sorted([(round(p.real, 4), round(p.imag, 4)), (round(q.real, 4), round(q.imag, 4))]))
        if key in seen or min(abs(p), abs(q)) > RV + 2 * a_t:
            continue
        seen.add(key)
        segs.append([[p.real, p.imag], [q.real, q.imag]])
    return np.array(segs)


def bar_width(a_t):
    """Bar width (mm): bridge rule for the long tile diagonal (1.902 a_t) + BAR_MARGIN."""
    return float(web_req(2 * a_t * math.cos(math.radians(18)))) + BAR_MARGIN


def seg_dist(xs, ys, segs, cap):
    """Distance from the grid (xs, ys) to the nearest segment, capped at cap. Each segment
    updates only the grid window within cap of it."""
    D = np.full((len(ys), len(xs)), float(cap))
    gx, gy = xs[1] - xs[0], ys[1] - ys[0]
    for (ax, ay), (bx, by) in segs:
        i0 = max(int((min(ax, bx) - cap - xs[0]) / gx), 0)
        i1 = min(int((max(ax, bx) + cap - xs[0]) / gx) + 2, len(xs))
        j0 = max(int((min(ay, by) - cap - ys[0]) / gy), 0)
        j1 = min(int((max(ay, by) + cap - ys[0]) / gy) + 2, len(ys))
        if i0 >= i1 or j0 >= j1:
            continue
        X, Y = np.meshgrid(xs[i0:i1], ys[j0:j1])
        dx, dy = bx - ax, by - ay
        t = np.clip(((X - ax) * dx + (Y - ay) * dy) / max(dx * dx + dy * dy, 1e-12), 0, 1)
        np.minimum(D[j0:j1, i0:i1], np.hypot(X - ax - t * dx, Y - ay - t * dy), out=D[j0:j1, i0:i1])
    return D


def penrose_field(segs, a_t):
    """Cutout field before keep-outs (positive inside the tiles), for build()."""
    w = bar_width(a_t)

    def field(xs, ys):
        return seg_dist(xs, ys, segs, a_t) - w / 2   # cap a_t > inradius of every tile
    return field


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


def centroid(p):
    """Area centroid of a closed polygon."""
    x, y = p[:, 0], p[:, 1]
    c = x * np.roll(y, -1) - np.roll(x, -1) * y
    a6 = 3 * c.sum()
    return float(((x + np.roll(x, -1)) * c).sum() / a6), float(((y + np.roll(y, -1)) * c).sum() / a6)


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


def build(field):
    """Hole polylines. field(xs, ys): cutout field on the grid (positive inside the holes).
    CFG["glare_keepout"] (Marrakech prototype only): drop holes that reach below E_EYE_TOP."""
    xs = np.arange(-RP - 2, RV + 2, GRID)
    ys = np.arange(-RV - 2, RV + 2, GRID)
    X, Y = np.meshgrid(xs, ys)
    border = np.min(np.stack([RP - (X * nx + Y * ny) for nx, ny in EDGE_N]), axis=0) - BORDER
    F = blur(np.minimum.reduce([field(xs, ys), border, key_keepout(X, Y)]), BLUR / GRID)
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
        if CFG.get("glare_keepout") and elevation(p[:, 0], p[:, 1]).min() <= E_EYE_TOP:
            continue                     # bulb visible to a viewer: drop the hole whole
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
    """Worst margins (actual - required) between holes, to the edge, to the keys (to the slots
    by the bridge rule, to the arm footprints by ARM_MARGIN); lowest elevation of a hole
    centroid and of any hole point."""
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
        for i in range(len(KEYS)):
            rc = np.array(rect_corners(i))
            d_arm = seg_point_dist(p, rc, np.roll(rc, -1, axis=0)).min()
            sc = np.array(slot_corners(i))
            d_slot = seg_point_dist(p, sc, np.roll(sc, -1, axis=0)).min()
            keep = min(keep, d_slot - web_req(max(sz, W_TAB)), d_arm - (ARM_MARGIN - 0.1))
    allp = np.vstack(holes)
    e_cent = min(float(elevation(*centroid(p))) for p in holes)
    return bridge, pair, edge, keep, e_cent, float(elevation(allp[:, 0], allp[:, 1]).min())


def symmetry(holes):
    """Worst centroid mismatch (mm) under rotation by 72 deg and under the x-axis mirror."""
    c = np.array([centroid(p) for p in holes])
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
        e = elevation(p[:, 0], p[:, 1])
        if CFG["ring"] > 0:
            if e.min() < E_GLARE_HI:
                glare.append(i)
            if e.min() < E_EYE_TOP:
                eye.append(i)
        elif np.any((e > E_GLARE_LO) & (e < E_GLARE_HI)):
            glare.append(i)
    return glare, eye


# ---------- output ----------
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


def laser_panel(loops, panel_path, path):
    """Laser file: the plain panel DXF (layers OUTLINE and CUT) plus the loops on layer CUT.
    Returns False when the plain panel DXF does not exist yet."""
    if not os.path.exists(panel_path):
        return False
    lines = open(panel_path).read().split("\n")
    end = max(i for i in range(len(lines) - 1) if lines[i].strip() == "0" and lines[i + 1].strip() == "ENDSEC")
    ent = []
    for p in loops:
        for i in range(len(p)):
            (x0, y0), (x1, y1) = p[i], p[(i + 1) % len(p)]
            ent += ["0", "LINE", "8", "CUT", "10", f"{x0:.4f}", "20", f"{y0:.4f}", "30", "0",
                    "11", f"{x1:.4f}", "21", f"{y1:.4f}", "31", "0"]
    with open(path, "w") as f:
        f.write("\n".join(lines[:end] + ent + lines[end:]))
    return True


def draw_panel(ax, holes, colours=None, hatched=()):
    """Panel, key footprints, slots and holes. colours: hole index -> face colour."""
    bg = "#fcfcfb"
    ax.add_patch(MplPolygon(PANEL, closed=True, facecolor="#d8b07a", edgecolor="#3d3c39", linewidth=1.2))
    for i in range(len(KEYS)):
        ax.add_patch(MplPolygon(rect_corners(i), closed=True, facecolor="#a9a8a2", alpha=0.6, edgecolor="none"))
        ax.add_patch(MplPolygon(slot_corners(i), closed=True, facecolor=bg, edgecolor="#3d3c39", linewidth=0.5))
    for i, p in enumerate(holes):
        ax.add_patch(MplPolygon(p, closed=True, facecolor=(colours or {}).get(i, bg), edgecolor="#3d3c39",
                                linewidth=0.5, hatch="////" if i in hatched else None))


def elevation_grid():
    """Elevation of the panel points (NaN outside the panel) for the zone contours."""
    xs = np.linspace(-RP, RV, 300)
    ys = np.linspace(-RV, RV, 300)
    X, Y = np.meshgrid(xs, ys)
    inside = np.min(np.stack([RP - (X * nx + Y * ny) for nx, ny in EDGE_N]), axis=0) > 0
    return xs, ys, np.where(inside, elevation(X, Y), np.nan)


def preview(holes, glare, eye, path, title):
    """Preview with the design zones (dashed) and the glare zone holes coloured."""
    bg = "#fcfcfb"
    fig, ax = plt.subplots(figsize=(6, 6.3))
    fig.patch.set_facecolor(bg)
    ax.set_facecolor(bg)
    colours = {i: "#e0392b" if size(holes[i]) > GLARE_BIG else "#f6c48f" for i in glare}
    draw_panel(ax, holes, colours, eye)
    xs, ys, E = elevation_grid()
    if CFG["ring"] > 0:
        levels = [E_EYE_TOP, E_GLARE_HI]
        ax.text(RV - 24, RP * 0.62, f"glare zone\n(e < {E_GLARE_HI:+.0f}°)", fontsize=7, color="#52514e")
        ax.text(-RP + 3, RP * 0.92, f"projection zone\n(e > {E_GLARE_HI:+.0f}°)", fontsize=7, color="#52514e")
    else:
        levels = [E_GLARE_LO, E_GLARE_HI]
        ax.text(-RP + 3, RP * 0.92, f"table zone\n(e < {E_GLARE_LO:.0f}°)", fontsize=7, color="#52514e")
        ax.text(RV - 22, RP * 0.40, f"projection\n(e > {E_GLARE_HI:+.0f}°)", fontsize=7, color="#52514e")
        ax.text(-8, -RV * 0.88, "glare zone", fontsize=7, color="#52514e")
    ax.contour(xs, ys, E, levels=levels, colors="#eb6834", linewidths=1, linestyles=[(0, (3, 2))])
    ax.set_aspect("equal")
    ax.set_xlim(-RP - 4, RV + 4)
    ax.set_ylim(-RV - 4, RV + 4)
    ax.axis("off")
    legend = (f"Glare zone holes: light orange <= {GLARE_BIG:.0f} mm, red > {GLARE_BIG:.0f} mm"
              + (f", hatched: below e = {E_EYE_TOP:+.1f}° (bulb visible)" if CFG["ring"] > 0 else "")
              + f". Dashed: e = {', '.join(f'{v:+.1f}°' for v in levels)}.")
    ax.set_title(title, fontsize=8, color="#0b0b0b", loc="left")
    fig.text(0.02, 0.015, legend, fontsize=6.5, color="#52514e")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(path, facecolor=bg)
    plt.close(fig)


def run(panel, tiling=None, a_t=None, rot36=None, svg_path=None, dxf_stem=None, kerf_dxf=True, laser=True):
    """Build, check and write one Penrose panel pattern. Defaults: PANELS[panel] and the target
    outputs (see the module docstring). Returns 0, or 1 when a check fails (no DXF written)."""
    global CFG
    CFG = dict(PANELS[panel])
    for k, v in (("tiling", tiling), ("a_t", a_t), ("rot36", rot36)):
        if v is not None:
            CFG[k] = v
    tiling, a_t, rot36 = CFG["tiling"], CFG["a_t"], CFG["rot36"]
    CFG["slot_margin"] = bar_width(a_t)
    svg_path = svg_path or os.path.join(IMG_DIR, f"{panel}_panel_pattern.svg")
    dxf_stem = dxf_stem or os.path.join(CAD_DIR, f"{panel}_pattern")

    segs = tile_edges(tiling, a_t, rot36)
    holes = build(penrose_field(segs, a_t))
    bridge, pair, edge, keep, _, emin = check(holes)
    rot_err, mir_err = symmetry(holes)
    glare, eye = glare_holes(holes)
    open_area = sum(polygon_area(p) for p in holes)
    open_pct = 100 * open_area / PANEL_AREA
    sizes = [size(p) for p in holes]
    g_max = max((sizes[i] for i in glare), default=0.0)
    print(f"{panel}: {TILING_NAMES[tiling]}{', rot36' if rot36 else ''}, a_t = {a_t:.2f} mm, "
          f"bar {bar_width(a_t):.2f} mm, slot margin {CFG['slot_margin']:.2f} mm, {len(segs)} edges")
    print(f"a = {A:.2f} mm, rp = {RP:.2f} mm, ek = {E_KEY:.2f} mm")
    print(f"{len(holes)} holes, {min(sizes):.1f} mm to {max(sizes):.1f} mm, open area {open_area:.0f} mm^2 "
          f"({open_pct:.0f} %), {sum(len(p) for p in holes)} segments")
    print(f"check: bridge margin {bridge:+.2f} mm (actual {pair[0]:.2f}, required {pair[1]:.2f}), "
          f"edge margin {edge:+.2f} mm, key margin {keep:+.2f} mm")
    print(f"symmetry: rotation 72 deg {rot_err:.3f} mm, mirror {mir_err:.3f} mm (limit {SYM_TOL} mm)")
    print(f"glare zone: {len(glare)} holes, largest {g_max:.1f} mm, "
          f"{sum(sizes[i] > GLARE_BIG for i in glare)} above {GLARE_BIG:.0f} mm"
          + (f"; {len(eye)} holes below e = {E_EYE_TOP:+.1f} deg (lowest point {emin:+.1f} deg)"
             if CFG["ring"] > 0 else ""))
    title = (f"{CFG['title']}: {TILING_NAMES[tiling]}, edge {a_t:g} mm{', turned 36°' if rot36 else ''}, "
             f"{len(holes)} holes, open {open_pct:.0f} %. {CFG['tip'].capitalize()}.")
    os.makedirs(os.path.dirname(svg_path), exist_ok=True)
    preview(holes, glare, eye, svg_path, title)
    print(f"written: {os.path.relpath(svg_path)}")
    if bridge < 0 or edge < 0 or keep < 0 or max(rot_err, mir_err) > SYM_TOL:
        print("CHECK FAILED: no DXF written")
        return 1
    os.makedirs(os.path.dirname(dxf_stem), exist_ok=True)
    dxf(holes, f"{dxf_stem}.dxf")
    print(f"written: {os.path.relpath(dxf_stem)}.dxf")
    if not kerf_dxf:
        return 0
    kerf = [offset_in(p, KERF / 2) for p in holes]
    dxf(kerf, f"{dxf_stem}_kerf.dxf")
    print(f"written: {os.path.relpath(dxf_stem)}_kerf.dxf")
    if laser:
        out = os.path.join(CAD_DIR, f"{panel}_panel_x5.dxf")
        if laser_panel(kerf, os.path.join(CAD_DIR, "panel_x1.dxf"), out):
            print(f"written: {os.path.relpath(out)}")
        else:
            print("panel_x1.dxf missing (export sketch PanelLaser): no laser file written")
    return 0


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "upper"
    if name not in PANELS or len(sys.argv) > 2:
        sys.exit(f"usage: panel_pattern.py [{'|'.join(PANELS)}]")
    sys.exit(run(name))


if __name__ == "__main__":
    main()

"""Top panel with a central bayonet hole and the hub that carries the shade. Writes DXF and an SVG
preview.

Concept (docs/overview.md, Bulb change):
- Top panel: the 12th panel, same outline and key slots as the other panels (sketch PanelLaser),
  glued to its 10 keys. Pattern: Penrose P3, the tiling of the lower ring panels (TILING), with a
  central hole H.
- H: the union of the tiles with the centre within R_OPEN, shrunk by BAR / 2. Its outline follows
  the tile edges, so it is not round.
- Hub: two plywood layers, glued, on the nipple between the nut and the spacer to the socket.
  - Lower layer L (thickness tp): H turned by 36 deg, shrunk by C. Turned by 36 deg against the
    shade, L passes H. At the seat its 10 points lie under the panel and carry the shade.
  - Upper layer U (thickness t): the part of H that H turned by 36 deg also covers, shrunk by C.
    U passes H in both positions. At the seat U lies in H, flush with the outer face, and locks
    the turn. U is invariant under a 36 deg turn, so the shade turns either way.
- Mount: push the shade up until U is below the panel, turn 36 deg, lower. U drops into H.
  Remove: lift the shade by t, turn 36 deg, lower. No force: clearance C all round.

Pattern (maximum open area): every tile outside H is a hole, also over the points of L (L bears
on the bars). A hole is the tile shrunk by BAR / 2, shrunk further (up to SHRINK_MAX) until it
clears the frame, the key nodes and H; a tile that still does not fit is clipped and kept when at
least CLIP_MIN of its hole remains. Hub: the tiles of H are holes too (same rule, 3 mm web to the
hub outline, solid within R_HUB_CORE), so the pattern runs across the hub.

Checks (no DXF if one fails): bridge rule between holes and to the panel edge, H and the key
slots, hub webs, bulb passes H, L and U pass H turned by 36 deg, turn play of U in H, bearing area
of L on the panel bars, solid hub core, 5-fold symmetry with mirror.

Frame: base panel frame (sketch PanelLaser): vertex on +x, edge normals at 36 + 72k deg.

Outputs (relative to platonic_lampshades/):
  cad/dodecahedron/top_pattern.dxf       nominal panel cutouts incl. H (3D cut)
  cad/dodecahedron/top_pattern_kerf.dxf  cutouts shrunk by kerf/2
  cad/dodecahedron/top_panel_x1.dxf      laser file: panel_x1.dxf + kerf cutouts on CUT
  cad/dodecahedron/hub_lower.dxf         nominal L with holes (3D)
  cad/dodecahedron/hub_upper.dxf         nominal U with holes (3D)
  cad/dodecahedron/hub_x1.dxf            laser file: L, U and the Hsp / t spacer rings (Dsp, nipple
                                         hole dn) side by side, kerf-compensated,
                                         outlines on OUTLINE, holes on CUT
  docs/img/top_panel_pattern.svg         preview: seated, turned, light

Usage: python3 platonic_lampshades/tools/top_panel.py [--svg PATH] [--r-open MM]
"""
import argparse
import math
import os
import sys

import numpy as np
from shapely import affinity
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import panel_pattern as pp  # noqa: E402
from design import KIT  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402  (backend set by panel_pattern)
from matplotlib.patches import PathPatch  # noqa: E402
from matplotlib.path import Path  # noqa: E402

DN, KERF, DB, DSP, HSP, T = KIT["dn"], KIT["kerf"], KIT["Db"], KIT["Dsp"], KIT["Hsp"], KIT["t"]
N_SPACER = round(HSP / T)   # spacer rings of plywood thickness t

R_OPEN = 34.0          # H: round core (bulb passage), mm
R_POINT = 68.0         # H: 5 rhombus petals towards the vertices, tip radius, mm
E_POINT = 30.14        # ... rhomb edge of the petal (upper ring tile x phi), mm
R_NOTCH = 48.0         # H: 5 rhombus lock petals towards the edges (U's teeth), tip radius, mm
E_NOTCH = 18.63        # ... rhomb edge of the petal (upper ring tile), mm
WINDOW = 4.0           # turn play when the hub passes H and when U drops into H, +- deg
TILING = "lower"       # panel_pattern.PANELS entry: tile edge and phase
BAR = pp.bar_width(pp.PANELS[TILING]["a_t"])  # bridge rule for the long tile diagonal + 0.3 mm
BORDER = 5.0           # minimum frame width, mm
C = 1.5                # hub clearance to H, mm
RCORNER = 1.0          # corner radius of holes and hub, mm
SHRINK_MAX = 3.0       # a hole may shrink by this much beyond BAR / 2 to fit, mm
CLIP_MIN = 0.4         # a tile that does not fit is clipped; kept when >= this share of its hole
TURN = 36.0            # bayonet turn, deg
R_HUB_CORE = DSP / 2   # hub solid within this radius: the spacer rings bear here, mm
PLAY_MAX = 12.0        # check: turn play of U in H (lock), well below TURN - WINDOW, deg
BEAR_MIN = 300.0       # check: bearing area of L on the panel, mm^2
ARC = 64
SYM_TOL = 0.2
IMG = os.path.join(pp.IMG_DIR, "top_panel_pattern.svg")


def rot(g, deg):
    return affinity.rotate(g, deg, origin=(0, 0))


def rounded(g, r=RCORNER):
    return g.buffer(-r, ARC // 4).buffer(r, ARC // 4)


def union_tiles(ts):
    """Union without hairline gaps between neighbouring tiles."""
    return unary_union([t.buffer(0.01, join_style="mitre") for t in ts]).buffer(-0.01, join_style="mitre")


def tiles(a_t, rot36):
    """P3 rhombs (shapely polygons) in the base panel frame, covering the panel."""
    n = 0
    while a_t * pp.PHI ** n < (pp.RV + 3 * a_t) / 0.9:
        n += 1
    radius = a_t * pp.PHI ** n
    turn = complex(math.cos(math.pi / 5), math.sin(math.pi / 5)) if rot36 else 1
    halves = {}
    for (a, b), (_, c) in pp.p3_tiles(n):
        a, b, c = (z * radius * turn for z in (a, b, c))
        if min(abs(a), abs(b), abs(c)) > pp.RV + a_t:
            continue
        key = tuple(sorted([(round(b.real, 3) + 0.0, round(b.imag, 3) + 0.0),
                            (round(c.real, 3) + 0.0, round(c.imag, 3) + 0.0)]))
        halves.setdefault(key, []).append((a, b, c))
    out = []
    for hs in halves.values():
        if len(hs) == 2:
            (a1, b, c), (a2, _, _) = hs
            out.append(Polygon([(z.real, z.imag) for z in (a1, b, a2, c)]))
    return out


def panel_polygon():
    return Polygon(pp.PANEL)


def key_feet():
    """Plan footprints of the 10 keys under the panel (arm footprint, full key depth)."""
    return unary_union([Polygon(pp.rect_corners(i)) for i in range(len(pp.KEYS))])


R_KEYS = math.hypot(pp.RP - pp.L_ARM, pp.E_KEY / 2 - pp.TK / 2)   # inner ends of the keys, mm


def key_zones():
    """Solid zones of the keys: slot node (slot margin BAR) and arm footprint + ARM_MARGIN."""
    z = []
    for i in range(len(pp.KEYS)):
        z.append(Polygon(pp.slot_corners(i)).buffer(BAR, ARC // 4))
        z.append(Polygon(pp.rect_corners(i)).buffer(pp.ARM_MARGIN, ARC // 4))
    return unary_union(z)


def fit_hole(tile, allowed):
    """The tile shrunk by BAR / 2 or more until it lies in allowed; None if it does not fit."""
    o = BAR / 2
    while o <= BAR / 2 + SHRINK_MAX + 1e-9:
        h = tile.buffer(-o, join_style="mitre")
        if h.is_empty or h.geom_type != "Polygon":
            return None
        h = rounded(h)
        if h.is_empty or h.geom_type != "Polygon":
            return None
        if allowed.contains(h):
            if h.area < pp.A_MIN or h.buffer(-pp.R_HOLE_MIN).is_empty:
                return None
            return h
        o += 0.25
    return None


def size(p):
    x0, y0, x1, y1 = p.bounds
    return max(x1 - x0, y1 - y0)


def fit_or_clip(tile, allowed):
    """Whole tile hole (shrunk to fit); otherwise the nominal hole clipped to allowed, when it keeps
    at least CLIP_MIN of the nominal area. Returns a list of polygons."""
    h = fit_hole(tile, allowed)
    if h is not None:
        return [h]
    nominal = tile.buffer(-BAR / 2, join_style="mitre")
    if nominal.is_empty:
        return []
    c = nominal.intersection(allowed)
    if c.is_empty:
        return []
    c = rounded(c)
    parts = [c] if c.geom_type == "Polygon" else [p for p in getattr(c, "geoms", []) if p.geom_type == "Polygon"]
    out = []
    for p in parts:
        if p.area >= CLIP_MIN * nominal.area and p.area >= pp.A_MIN and not p.buffer(-pp.R_HOLE_MIN).is_empty:
            out.append(p)
    return out


def sector(a_deg, half_deg, r):
    a, h = math.radians(a_deg), math.radians(half_deg)
    return Polygon([(0, 0), (r * math.cos(a - h), r * math.sin(a - h)), (r * math.cos(a), r * math.sin(a)),
                    (r * math.cos(a + h), r * math.sin(a + h))])


def rhomb_petal(a_deg, r_tip, edge):
    """Thick rhomb (72 deg) with tile edge length edge, its long diagonal on the ray a_deg, tip at
    r_tip. Its sides run at +-36 deg to the ray, parallel to tile edges."""
    a = math.radians(a_deg)
    u = np.array([math.cos(a), math.sin(a)])
    v = np.array([-u[1], u[0]])
    long_d = 2 * edge * math.cos(math.radians(36))
    half = edge * math.sin(math.radians(36))
    m = (r_tip - long_d / 2) * u
    return Polygon([tuple(m - long_d / 2 * u), tuple(m + half * v), tuple(r_tip * u), tuple(m - half * v)])


def hole_shape(r_open):
    """H before rounding: disc r_open, 5 rhombus petals to R_POINT towards the pentagon vertices
    (72k deg) and 5 rhombus lock petals to R_NOTCH towards the edges (36 + 72k deg)."""
    parts = [Point(0, 0).buffer(r_open, ARC)]
    parts += [rhomb_petal(72 * k, R_POINT, E_POINT) for k in range(5)]
    parts += [rhomb_petal(36 + 72 * k, R_NOTCH, E_NOTCH) for k in range(5)]
    return unary_union(parts)


def swept_fit(region, at):
    """The part of the hub that stays inside region turned by at - WINDOW .. at + WINDOW deg."""
    out = None
    for th in np.arange(-WINDOW, WINDOW + 1e-9, 0.5):
        r = rot(region, at + th)
        out = r if out is None else out.intersection(r)
    return out


def largest(g):
    return g if g.geom_type == "Polygon" else max(g.geoms, key=lambda p: p.area)


def build(r_open=R_OPEN):
    up = pp.PANELS[TILING]
    ts = tiles(up["a_t"], up["rot36"])
    H = rounded(hole_shape(r_open), 2.0)
    core = [t for t in ts if H.contains(t.centroid)]       # tiles inside H: candidates for hub holes
    core_ids = {id(t) for t in core}
    # L passes H at TURN +- WINDOW; U passes H at TURN +- WINDOW and sits in H at 0 +- WINDOW
    Hc = H.buffer(-C, join_style="mitre")
    # L turns under the panel within the key depth: it stays inside the inner ends of the keys
    L = largest(rounded(swept_fit(Hc, TURN).intersection(Point(0, 0).buffer(R_KEYS - C, ARC))))
    U = largest(rounded(swept_fit(Hc, TURN).intersection(swept_fit(Hc, 0)).intersection(L)))
    nip = Point(0, 0).buffer(DN / 2, ARC)
    # panel holes: everywhere outside H, the frame and the key nodes (also over the points of L)
    allowed = (panel_polygon().buffer(-BORDER, join_style="mitre").difference(key_zones())
               .difference(H.buffer(float(pp.web_req(size(H))) + 0.05, ARC // 4)))
    holes = []
    for t in ts:
        if id(t) not in core_ids:
            holes += fit_or_clip(t, allowed)
    # hub holes: the core tiles continue the pattern across the hub (U and L, glued)
    hub = U.intersection(L)
    hub_web = float(pp.web_req(2 * up["a_t"] * math.cos(math.radians(18))))   # largest tile hole
    hub_allowed = hub.buffer(-hub_web, join_style="mitre").difference(Point(0, 0).buffer(R_HUB_CORE, ARC))
    hub_holes = []
    for t in core:
        hub_holes += fit_or_clip(t, hub_allowed)
    # holes in the points of L: under each panel hole, the same hole with a 3 mm web to L
    l_allowed = L.buffer(-3.0, join_style="mitre").difference(U.buffer(3.0, ARC // 4)).union(hub_allowed)
    l_holes = []
    for h in holes:
        c = h.intersection(l_allowed)
        if c.is_empty:
            continue
        c = rounded(c)
        for p in ([c] if c.geom_type == "Polygon" else [q for q in getattr(c, "geoms", []) if q.geom_type == "Polygon"]):
            if p.area >= pp.A_MIN and not p.buffer(-pp.R_HOLE_MIN).is_empty:
                l_holes.append(p)
    return dict(H=H, L=L, U=U, nip=nip, holes=holes, hub_holes=hub_holes, l_holes=l_holes,
                a_t=up["a_t"], rot36=up["rot36"])


# ---------- checks ----------
def max_inscribed(poly):
    """Radius of the largest circle centred at the origin inside poly."""
    poly = largest(poly)
    return poly.exterior.distance(Point(0, 0)) if poly.contains(Point(0, 0)) else 0.0


def window(part, H, at):
    """Largest w (deg) for which part stays inside H turned by at - w .. at + w."""
    tol = H.buffer(1e-6)
    w = 0.0
    for th in np.arange(0.05, 18, 0.05):
        if not (tol.contains(rot(part, at + th)) and tol.contains(rot(part, at - th))):
            break
        w = th
    return w


def turn_play(U, H):
    """Largest turn (deg) of U inside H without contact, to either side (U is symmetric)."""
    play = 0.0
    for th in np.arange(0.1, 36, 0.1):
        if not H.contains(rot(U, th)):
            break
        play = th
    return play


def check(g):
    H, L, U, holes, hh = g["H"], g["L"], g["U"], g["holes"], g["hub_holes"]
    allh = holes + [H]
    r = {}
    bridge = math.inf
    for i in range(len(allh)):
        for j in range(i + 1, len(allh)):
            d = allh[i].distance(allh[j])
            if d < 8:
                bridge = min(bridge, d - float(pp.web_req(max(size(allh[i]), size(allh[j])))))
    r["bridge"] = bridge
    edge = panel_polygon().exterior
    r["edge"] = min(edge.distance(h) - float(pp.web_req(size(h))) for h in allh)
    keep = math.inf
    for h in allh:
        for i in range(len(pp.KEYS)):
            keep = min(keep, Polygon(pp.slot_corners(i)).distance(h) - float(pp.web_req(max(size(h), pp.W_TAB))),
                       Polygon(pp.rect_corners(i)).distance(h) - (pp.ARM_MARGIN - 0.1))
    r["key"] = keep
    panel_solid = panel_polygon().difference(unary_union(allh))
    r["bear"] = L.difference(unary_union(g["l_holes"] + hh)).intersection(panel_solid).area
    r["bulb"] = 2 * max_inscribed(H)
    tol = H.buffer(1e-6)
    r["pass"] = all(tol.contains(rot(x, s * TURN)) for x in (L, U) for s in (1, -1))
    r["play"] = turn_play(U, H)
    r["pass_window"] = min(window(L, H, TURN), window(U, H, TURN))
    feet = key_feet()
    r["key_sweep"] = min(rot(x, th).distance(feet) for x in (L, U) for th in np.arange(-TURN, TURN + 1e-9, 1.0))
    r["seat_window"] = window(U, H, 0.0)
    r["hub_core"] = min([L.exterior.distance(Point(0, 0)), U.exterior.distance(Point(0, 0))]
                        + [h.distance(Point(0, 0)) for h in hh])
    hub = U.intersection(L)
    hb = min((hub.exterior.distance(h) - float(pp.web_req(size(h))) for h in hh), default=math.inf)
    for i in range(len(hh)):
        for j in range(i + 1, len(hh)):
            hb = min(hb, hh[i].distance(hh[j]) - float(pp.web_req(max(size(hh[i]), size(hh[j])))))
    lh = g["l_holes"]
    for h in lh:
        hb = min(hb, L.exterior.distance(h) - 3.0 + 0.05)
        for o in hh + [x for x in lh if x is not h]:
            if o.distance(h) < 6:
                hb = min(hb, o.distance(h) - float(pp.web_req(max(size(o), size(h)))))
    r["hub_bridge"] = hb
    c = np.array([[h.centroid.x, h.centroid.y] for h in holes + hh])
    z = c[:, 0] + 1j * c[:, 1]
    r["sym"] = max(float(np.abs(zt[:, None] - z[None, :]).min(1).max())
                   for zt in (z * np.exp(1j * math.radians(72)), np.conj(z)))
    # open area of the top seen from the ceiling (seated)
    hub_solid = unary_union([U.difference(unary_union(hh)), L.difference(unary_union(hh + g["l_holes"]))])
    light = unary_union(holes + [H]).difference(hub_solid)
    r["open"] = 100 * light.area / pp.PANEL_AREA
    return r


# ---------- output ----------
def loops(geom):
    polys = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)
    out = []
    for p in polys:
        out.append(np.array(p.exterior.coords)[:-1])
        out += [np.array(i.coords)[:-1] for i in p.interiors]
    return out


def ccw(p):
    return p if pp.polygon_area(p) > 0 else p[::-1]


def dxf_layers(items, path):
    """items: (layer, loop) pairs."""
    out = ["0", "SECTION", "2", "ENTITIES"]
    for layer, p in items:
        for i in range(len(p)):
            (x0, y0), (x1, y1) = p[i], p[(i + 1) % len(p)]
            out += ["0", "LINE", "8", layer, "10", f"{x0:.4f}", "20", f"{y0:.4f}", "30", "0",
                    "11", f"{x1:.4f}", "21", f"{y1:.4f}", "31", "0"]
    out += ["0", "ENDSEC", "0", "EOF"]
    with open(path, "w") as f:
        f.write("\n".join(out) + "\n")


def draw(ax, g, title, mode):
    bg, wood, hub_c, ink, grey = "#fcfcfb", "#d8b07a", "#b9824a", "#3d3c39", "#8f8e88"

    def patch(geom, **kw):
        for p in ([geom] if geom.geom_type == "Polygon" else geom.geoms):
            verts, codes = [], []
            for ring in [p.exterior, *p.interiors]:
                xy = np.array(ring.coords)
                verts += list(xy)
                codes += [Path.MOVETO] + [Path.LINETO] * (len(xy) - 2) + [Path.CLOSEPOLY]
            ax.add_patch(PathPatch(Path(verts, codes), **kw))
    hub_cut = unary_union(g["hub_holes"] + [g["nip"]])
    if mode == "light":
        ax.add_patch(plt.Rectangle((-95, -95), 190, 190, facecolor="#2b2a28", edgecolor="none"))
        light = unary_union(g["holes"] + [g["H"].difference(g["U"])] + g["hub_holes"])
        light = light.difference(g["L"].difference(unary_union([hub_cut] + g["l_holes"])))
        patch(light, facecolor="#f8e7b0", edgecolor="none")
    else:
        turn = TURN if mode == "pass" else 0.0
        L = rot(g["L"].difference(unary_union([hub_cut] + g["l_holes"])), turn)
        patch(L, facecolor=hub_c, edgecolor=ink, linewidth=0.5, alpha=0.55)
        panel = panel_polygon().difference(unary_union(g["holes"] + [g["H"]]))
        patch(panel, facecolor=wood, edgecolor=ink, linewidth=0.6, alpha=0.85)
        for i in range(len(pp.KEYS)):
            patch(Polygon(pp.rect_corners(i)), facecolor=grey, edgecolor="none")
        patch(rot(g["U"].difference(hub_cut), turn), facecolor=hub_c, edgecolor=ink, linewidth=0.6)
    ax.set_aspect("equal")
    ax.set_xlim(-pp.RP - 3, pp.RV + 3)
    ax.set_ylim(-pp.RV - 3, pp.RV + 3)
    ax.axis("off")
    ax.set_title(title, fontsize=7.5, color="#0b0b0b", loc="left")


def preview(g, r, path):
    bg = "#fcfcfb"
    fig, axs = plt.subplots(1, 3, figsize=(12, 4.6))
    fig.patch.set_facecolor(bg)
    draw(axs[0], g, "Seated: U in H, points of L (shaded) under the panel", "seat")
    draw(axs[1], g, f"Turned {TURN:g}°: L and U pass H", "pass")
    draw(axs[2], g, "Light through the top (seated)", "light")
    fig.text(0.01, 0.02,
             f"Top panel: Penrose P3, edge {g['a_t']:g} mm{', turned 36°' if g['rot36'] else ''}, H: core R {R_OPEN:g} mm, "
             f"points R {R_POINT:g} mm, notches R {R_NOTCH:g} mm, "
             f"{len(g['holes'])} + {len(g['hub_holes'])} holes. Hub clearance {C:g} mm, pass window ±{r['pass_window']:.1f}°, "
             f"seat window ±{r['seat_window']:.1f}°, lock play ±{r['play']:.1f}°, "
             f"open {r['open']:.0f} %, bearing {r['bear']:.0f} mm², bulb passage Ø {r['bulb']:.0f} mm.",
             fontsize=8, color="#3d3c39")
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(path, facecolor=bg)
    plt.close(fig)


def main():
    global R_OPEN
    ap = argparse.ArgumentParser(description="Top panel with bayonet hole and hub.")
    ap.add_argument("--svg", default=IMG)
    ap.add_argument("--r-open", type=float, help="study value of R_OPEN (preview only)")
    args = ap.parse_args()
    if args.r_open:
        R_OPEN = args.r_open
    g = build(R_OPEN)
    r = check(g)
    print(f"top: P3, a_t = {g['a_t']:.2f} mm{', rot36' if g['rot36'] else ''}, core R {R_OPEN:g} mm, "
          f"bar {BAR:.2f} mm, border {BORDER:g} mm, {len(g['holes'])} panel holes, {len(g['hub_holes'])} hub holes, "
          f"{len(g['l_holes'])} holes in the points of L, "
          f"open (seated, seen from the ceiling) {r['open']:.0f} %")
    print(f"bayonet: turn {TURN:g} deg, L and U pass H {r['pass']}, pass window +-{r['pass_window']:.1f} deg, "
          f"seat window +-{r['seat_window']:.1f} deg (min {WINDOW:g}), clearance {C:g} mm, turn play of U +-{r['play']:.1f} deg (max {PLAY_MAX:g}), "
          f"hub to the keys over the turn {r['key_sweep']:.2f} mm (min {C:g}), bearing of L on the panel {r['bear']:.0f} mm^2 (min {BEAR_MIN:g}), "
          f"bulb passage {r['bulb']:.1f} mm (bulb {DB:g} mm)")
    print(f"check: bridge margin {r['bridge']:+.2f} mm, edge margin {r['edge']:+.2f} mm, key margin {r['key']:+.2f} mm, "
          f"hub core R {r['hub_core']:.1f} mm (min {R_HUB_CORE:g}), hub bridge margin {r['hub_bridge']:+.2f} mm, "
          f"symmetry {r['sym']:.3f} mm")
    ok = (min(r["bridge"], r["edge"], r["key"], r["hub_bridge"]) >= 0 and r["pass"]
          and min(r["pass_window"], r["seat_window"]) >= WINDOW - 0.05 and r["key_sweep"] >= C - 0.05
          and r["play"] <= PLAY_MAX and r["bear"] >= BEAR_MIN and r["bulb"] >= DB + 2
          and r["hub_core"] >= R_HUB_CORE and r["sym"] <= SYM_TOL)
    os.makedirs(os.path.dirname(os.path.abspath(args.svg)), exist_ok=True)
    preview(g, r, args.svg)
    print(f"written: {os.path.relpath(args.svg)}")
    if not ok:
        print("CHECK FAILED: no DXF written")
        return 1
    if args.r_open:
        print("study (--r-open): no DXF written")
        return 0
    cuts = [ccw(p) for h in g["holes"] + [g["H"]] for p in loops(h)]
    stem = os.path.join(pp.CAD_DIR, "top_pattern")
    pp.dxf(cuts, f"{stem}.dxf")
    kerf = [pp.offset_in(p, KERF / 2) for p in cuts]
    pp.dxf(kerf, f"{stem}_kerf.dxf")
    print(f"written: {os.path.relpath(stem)}.dxf, {os.path.relpath(stem)}_kerf.dxf")
    out = os.path.join(pp.CAD_DIR, "top_panel_x1.dxf")
    if pp.laser_panel(kerf, os.path.join(pp.CAD_DIR, "panel_x1.dxf"), out):
        print(f"written: {os.path.relpath(out)}")
    else:
        print("panel_x1.dxf missing (export sketch PanelLaser): no laser file written")
    cut_u = g["hub_holes"] + [g["nip"]]
    cut_l = g["hub_holes"] + g["l_holes"] + [g["nip"]]
    for name, part, cut in (("hub_lower", g["L"], cut_l), ("hub_upper", g["U"], cut_u)):
        pp.dxf(loops(part.difference(unary_union(cut))), os.path.join(pp.CAD_DIR, f"{name}.dxf"))
    items = []
    shift = 0.0
    ring = Point(0, 0).buffer(DSP / 2, ARC)
    for part, cut in ((g["L"], cut_l), (g["U"], cut_u)) + tuple((ring, [g["nip"]]) for _ in range(N_SPACER)):
        x0, _, x1, _ = part.bounds
        dx = shift - x0
        k = affinity.translate(part.buffer(KERF / 2, ARC // 4, join_style="mitre"), dx)
        items.append(("OUTLINE", np.array(k.exterior.coords)[:-1]))
        for h in cut:
            n = affinity.translate(h.buffer(-KERF / 2, ARC // 4, join_style="mitre"), dx)
            items.append(("CUT", np.array(n.exterior.coords)[:-1]))
        shift += x1 - x0 + 5
    dxf_layers(items, os.path.join(pp.CAD_DIR, "hub_x1.dxf"))
    print("written: cad/dodecahedron/hub_lower.dxf, hub_upper.dxf, hub_x1.dxf")
    return 0


if __name__ == "__main__":
    sys.exit(main())

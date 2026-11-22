"""Top plate: bayonet seat for the 10 lug keys and a Penrose P3 pattern around a solid core.
Writes DXF and an SVG preview with the bayonet sweep.

Frame: the plate frame of the design (sketch PlateCutSketch, plane z = zpl): plate centre at the
origin, top edge k with its outward normal at 72k deg. Lug key (k, s): edge k, offset s = +-ek/2
along the edge.

Bayonet (docs/overview.md, Bulb change):
- Gap: the plan footprint of each lug key, turned by +-[turn - PLAY, turn + PLAY] about the axis
  and grown by cb. The plate passes the lug keys in this turn range.
- The gap edges have the shape of the turned key footprint. Lowered at any turn below the gap,
  the lock tab touches the plate first and rides on it; the bearing edge never rests on a lobe
  corner while the tab hangs beside it ("false seat"). Turning back to 0 drops the tab into the
  lock slot.
- Lock slot: lock tab (wlock radial x tk) + clock on each side.
- Seat: the bearing edge (rp - Larm to rp - Dkey cot(delta/2)) on the plate at turn 0.
- Ride band: the lock tab swept over the support range. The pattern keeps it solid, so the tab
  cannot drop into a pattern hole.

Pattern:
- Tiling: the tiling of the upper ring panel and the bottom panel (P3, a_t, phase), in the plate
  frame (base panel frame turned by -36 deg). The lug key footprints lie on tile edges, as the
  keys on the panels.
- Holes: whole tiles only (no clipped tiles), each shrunk by BAR / 2, corners rounded by RCORNER.
  A tile becomes a hole when the shrunk tile lies inside the allowed zone: plate inset by BORDER,
  outside the core (tiles with the centre within R_CORE stay solid), outside the seat, ride band
  and slot keep-outs.
- Core: solid. It carries the socket face and the washer and takes the load of the 10 seats.

Checks (no DXF if one fails): bridge rule between holes and to the outline and the slots
(panel_pattern.web_req), solid core radius >= R_SOLID, bayonet sweep (support and pass windows,
no false seat in the support range), one connected plate, 5-fold symmetry with mirror.

Outputs (relative to platonic_lampshades/):
  cad/dodecahedron/top_plate_cuts.dxf   cut loops for the 3D model: gaps (beyond Rpl), lock slots,
                                        pattern holes (plate frame; nipple hole not included)
  cad/dodecahedron/top_plate_kerf.dxf   laser sketch input: outline grown and holes shrunk by
                                        kerf/2, nipple hole included
  docs/img/top_plate.svg                preview: plate, lug keys at the seat, bayonet sweep

Usage: python3 platonic_lampshades/tools/top_plate.py [--svg PATH]
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

import matplotlib  # noqa: E402  (configured by panel_pattern)
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import PathPatch  # noqa: E402
from matplotlib.path import Path  # noqa: E402

# Design values, mm and deg (tools/design.py)
RP, LARM, TK, EK = KIT["rp"], KIT["Larm"], KIT["tk"], KIT["ek"]
DKEY, DELTA, CB = KIT["Dkey"], KIT["delta"], KIT["cb"]
HLOCK, WLOCK, CLOCK = KIT["hlock"], KIT["wlock"], KIT["clock"]
RPL, DN, KERF = KIT["Rpl"], KIT["dn"], KIT["kerf"]
TURN = KIT["turn"]
COT = 1 / math.tan(math.radians(DELTA) / 2)

# Bayonet
PLAY = 4.0             # half width of the turn range of the gap around turn, deg
STEP = 0.25            # sweep step, deg
SUPPORT_MIN = 10.0     # check: all 10 tabs supported for |turn| up to this, deg
PASS_MIN = 7.0         # check: width of the pass window, deg
# Pattern
R_CORE = 32.0          # tiles with the centre within this radius stay solid, mm
R_SOLID = 25.0         # check: no hole within this radius (socket face, washer), mm
BAR = 4.3              # bar width: bridge rule maximum + 0.3 mm (as the bottom panel), mm
BORDER = 4.0           # solid rim along the outline, mm
RCORNER = 1.0          # hole corner radius, mm
RIDE_MARGIN = 3.0      # solid wood around the seat and the ride band, mm
ARC = 128              # segments of a full circle in the output
SYM_TOL = 0.2          # mm

IMG = os.path.join(pp.IMG_DIR, "top_plate.svg")
KEYS = [(k, sg * EK / 2) for k in range(5) for sg in (-1, 1)]


# ---------- lug keys and bayonet ----------
def rect(k, s, d0, d1, w):
    """Rectangle from d0 to d1 along the normal of top edge k, w wide along the edge at offset s."""
    a = math.radians(72 * k)
    n = np.array([math.cos(a), math.sin(a)])
    t = np.array([-n[1], n[0]])
    return Polygon([d0 * n + (s - w / 2) * t, d1 * n + (s - w / 2) * t,
                    d1 * n + (s + w / 2) * t, d0 * n + (s + w / 2) * t])


def footprint(i):
    """Plan footprint of lug key i over its full height (inner end to beyond the plate rim)."""
    k, s = KEYS[i]
    return rect(k, s, RP - LARM, RP + 5, TK)


def bearing(i):
    """Bearing edge of lug key i (rests on the plate top)."""
    k, s = KEYS[i]
    return rect(k, s, RP - LARM, RP - DKEY * COT, TK)


def lock_tab(i):
    k, s = KEYS[i]
    return rect(k, s, RP - HLOCK - WLOCK / 2, RP - HLOCK + WLOCK / 2, TK)


def lock_slot(i):
    k, s = KEYS[i]
    return rect(k, s, RP - HLOCK - WLOCK / 2 - CLOCK, RP - HLOCK + WLOCK / 2 + CLOCK, TK + 2 * CLOCK)


def rot(g, deg):
    return affinity.rotate(g, deg, origin=(0, 0))


def turns(lo, hi):
    return np.arange(lo, hi + STEP / 2, STEP)


def gaps():
    """Gap region: all key footprints turned by +-[TURN - PLAY, TURN + PLAY], grown by cb."""
    feet = unary_union([footprint(i) for i in range(len(KEYS))])
    a = turns(TURN - PLAY, TURN + PLAY)
    return unary_union([rot(feet, x) for x in np.concatenate([a, -a])]).buffer(CB, ARC // 4)


def sweep(plate, keys=(0, 1)):
    """State per shade turn (deg) for the keys given (the others are symmetric copies):
    S: every tab on the plate (rides, or sits in its slot at 0), P: every key free (passes),
    F: a key touches the plate but its tab does not (false seat), X: mixed S and P."""
    out = []
    for phi in turns(-34, 34):
        st = set()
        for i in keys:
            tab = rot(lock_tab(i), phi)
            seated = lock_slot(i).buffer(1e-6).contains(tab)
            on_tab = seated or tab.intersection(plate).area > 0.01
            on_foot = rot(footprint(i), phi).intersection(plate).area > 0.01
            st.add("S" if on_tab else "F" if on_foot else "P")
        out.append((float(phi), "S" if st == {"S"} else "P" if st == {"P"} else "F" if "F" in st else "X"))
    return out


def windows(states):
    """Support half-width (from 0), pass window (first P run above 0), false seats in the support range."""
    pos = [(p, s) for p, s in states if p >= 0]
    sup = 0.0
    for p, s in pos:
        if s != "S":
            break
        sup = p
    run = [p for p, s in pos if s == "P"]
    lo = run[0] if run else math.nan
    hi = lo
    for p, s in pos:
        if p > lo and s == "P":
            hi = p
        elif p > lo:
            break
    false = [p for p, s in states if s == "F" and abs(p) <= sup + STEP]
    return sup, (lo, hi), false


# ---------- pattern ----------
def tiles(a_t, rot36):
    """P3 rhombs (shapely polygons) in the plate frame, covering the plate."""
    n = 0
    while a_t * pp.PHI ** n < (RPL + 3 * a_t) / 0.9:
        n += 1
    radius = a_t * pp.PHI ** n
    turn = complex(math.cos(math.pi / 5), math.sin(math.pi / 5)) if rot36 else 1
    frame = complex(math.cos(-math.pi / 5), math.sin(-math.pi / 5))   # base panel frame -> plate frame
    halves = {}
    for (a, b), (_, c) in pp.p3_tiles(n):
        a, b, c = (z * radius * turn * frame for z in (a, b, c))
        if min(abs(a), abs(b), abs(c)) > RPL + a_t:
            continue
        key = tuple(sorted([(round(b.real, 3), round(b.imag, 3)), (round(c.real, 3), round(c.imag, 3))]))
        halves.setdefault(key, []).append((a, b, c))
    out = []
    for hs in halves.values():
        if len(hs) != 2:
            continue
        (a1, b, c), (a2, _, _) = hs
        out.append(Polygon([(z.real, z.imag) for z in (a1, b, a2, c)]))
    return out


def keepout():
    """Zones that stay solid: seats, ride bands (tab swept over the support range), slot webs."""
    sup = TURN - PLAY
    zones = []
    for i in range(len(KEYS)):
        zones.append(bearing(i).buffer(RIDE_MARGIN, ARC // 4))
        ride = unary_union([rot(lock_tab(i), x) for x in turns(-sup, sup)])
        zones.append(ride.buffer(RIDE_MARGIN, ARC // 4))
        zones.append(lock_slot(i).buffer(pp.web_req(WLOCK + 2 * CLOCK), ARC // 4))
    return unary_union(zones)


def pattern_holes(plate, a_t, rot36):
    allowed = plate.buffer(-BORDER, ARC // 4).difference(keepout())
    holes = []
    for t in tiles(a_t, rot36):
        if t.centroid.distance(Point(0, 0)) < R_CORE:
            continue
        h = t.buffer(-BAR / 2, join_style="mitre").buffer(-RCORNER, ARC // 8).buffer(RCORNER, ARC // 8)
        if h.is_empty or h.area < pp.A_MIN:
            continue
        if allowed.contains(h):
            holes.append(h)
    return holes


# ---------- checks ----------
def hole_size(h):
    x0, y0, x1, y1 = h.bounds
    return max(x1 - x0, y1 - y0)


def check(plate, holes):
    """Worst margins (actual - required, mm) and the other check values."""
    r = {}
    bridge = math.inf
    for i in range(len(holes)):
        for j in range(i + 1, len(holes)):
            d = holes[i].distance(holes[j])
            if d < 6:
                bridge = min(bridge, d - float(pp.web_req(max(hole_size(holes[i]), hole_size(holes[j])))))
    r["bridge"] = bridge
    outline = Polygon(plate.exterior)
    r["edge"] = min((outline.exterior.distance(h) - float(pp.web_req(hole_size(h))) for h in holes), default=math.inf)
    slots = [lock_slot(i) for i in range(len(KEYS))]
    r["slot"] = min(min(s.distance(h) for s in slots) - float(pp.web_req(max(hole_size(h), WLOCK + 2 * CLOCK)))
                    for h in holes) if holes else math.inf
    r["slot_rim"] = min(outline.exterior.distance(s) for s in slots) - float(pp.web_req(WLOCK + 2 * CLOCK))
    r["solid"] = min((h.distance(Point(0, 0)) for h in holes), default=math.inf)
    r["pieces"] = 1 if plate.geom_type == "Polygon" else len(plate.geoms)
    c = np.array([[h.centroid.x, h.centroid.y] for h in holes])
    z = c[:, 0] + 1j * c[:, 1]
    r["sym"] = max(float(np.abs(zt[:, None] - z[None, :]).min(1).max())
                   for zt in (z * np.exp(1j * math.radians(72)), np.conj(z))) if len(z) else 0.0
    return r


# ---------- output ----------
def loops(geom):
    """Closed coordinate loops (without the repeated end point) of a polygon or multipolygon."""
    polys = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)
    out = []
    for p in polys:
        out.append(np.array(p.exterior.coords)[:-1])
        out += [np.array(i.coords)[:-1] for i in p.interiors]
    return out


def preview(plate, holes, states, sup, pw, path, title):
    bg, wood, ink, grey = "#fcfcfb", "#d8b07a", "#3d3c39", "#a9a8a2"
    fig = plt.figure(figsize=(6, 7.4))
    fig.patch.set_facecolor(bg)
    ax = fig.add_axes([0.02, 0.24, 0.96, 0.70])
    ax.set_facecolor(bg)

    def patch(g, **kw):
        for p in ([g] if g.geom_type == "Polygon" else g.geoms):
            verts, codes = [], []
            for ring in [p.exterior, *p.interiors]:
                xy = np.array(ring.coords)
                verts += list(xy)
                codes += [Path.MOVETO] + [Path.LINETO] * (len(xy) - 2) + [Path.CLOSEPOLY]
            ax.add_patch(PathPatch(Path(verts, codes), **kw))
    patch(plate, facecolor=wood, edgecolor=ink, linewidth=0.8)
    ride = unary_union([rot(lock_tab(i), x) for i in range(len(KEYS)) for x in turns(-sup, sup)])
    if not ride.intersection(plate).is_empty:
        patch(ride.intersection(plate), facecolor="#c9965a", edgecolor="none")
    for i in range(len(KEYS)):
        patch(footprint(i).intersection(Point(0, 0).buffer(RP)), facecolor=grey, alpha=0.55, edgecolor="none")
        patch(rot(footprint(i), TURN).intersection(Point(0, 0).buffer(RP)), facecolor="none",
              edgecolor="#eb6834", linewidth=0.6, linestyle=(0, (2, 1.5)))
    patch(Point(0, 0).buffer(RP, ARC), facecolor="none", edgecolor=grey, linewidth=0.5, linestyle=(0, (4, 3)))
    ax.set_aspect("equal")
    lim = RP + 4
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.axis("off")
    ax.set_title(title, fontsize=8, color="#0b0b0b", loc="left")

    bx = fig.add_axes([0.08, 0.07, 0.88, 0.09])
    colours = {"S": "#5a9e4b", "P": "#4a7fc1", "F": "#e0392b", "X": "#f6c48f"}
    for p, s in states:
        bx.add_patch(plt.Rectangle((p - STEP / 2, 0), STEP, 1, facecolor=colours[s], edgecolor="none"))
    bx.set_xlim(-34, 34)
    bx.set_ylim(0, 1)
    bx.set_yticks([])
    bx.set_xticks(range(-30, 31, 10))
    bx.tick_params(labelsize=7, colors=ink)
    bx.set_xlabel("shade turn from the seat (deg)", fontsize=7, color=ink)
    bx.set_facecolor(bg)
    fig.text(0.02, 0.185, "Bayonet sweep: green = all lock tabs on the plate (ride, click into the slot at 0°), "
             "blue = all keys pass,\nred = false seat (key on the plate, tab beside it), orange = mixed. "
             f"Grey: lug keys at the seat. Dashed: lug keys turned {TURN:g}°. Dark: ride band.",
             fontsize=6.5, color="#52514e")
    fig.text(0.02, 0.01, f"Support |turn| <= {sup:.2f}°, pass window {pw[0]:.2f}° to {pw[1]:.2f}°.",
             fontsize=7, color=ink)
    fig.savefig(path, facecolor=bg)
    plt.close(fig)


def build():
    disc = Point(0, 0).buffer(RPL, ARC)
    slots = unary_union([lock_slot(i) for i in range(len(KEYS))])
    plate = disc.difference(gaps()).difference(slots)
    up = pp.PANELS["upper"]
    holes = pattern_holes(plate, up["a_t"], up["rot36"])
    return disc, plate, slots, holes


def main():
    ap = argparse.ArgumentParser(description="Top plate: bayonet seat and Penrose pattern.")
    ap.add_argument("--svg", default=IMG)
    args = ap.parse_args()
    up = pp.PANELS["upper"]
    disc, plate, slots, holes = build()
    states = sweep(plate)
    sup, pw, false = windows(states)
    plate_full = plate.difference(unary_union(holes)) if holes else plate
    r = check(plate, holes)
    area = disc.area - plate_full.area
    print(f"top plate: Rpl {RPL:.2f} mm, turn {TURN:g} deg +- {PLAY:g} deg, cb {CB:g} mm, "
          f"slot {WLOCK + 2 * CLOCK:g} x {TK + 2 * CLOCK:g} mm")
    print(f"bayonet: support |turn| <= {sup:.2f} deg, pass {pw[0]:.2f} deg to {pw[1]:.2f} deg, "
          f"false seats in the support range: {len(false)}")
    print(f"pattern: P3, a_t = {up['a_t']:.2f} mm{', rot36' if up['rot36'] else ''}, core R {R_CORE:g} mm, "
          f"bar {BAR:g} mm, {len(holes)} holes, "
          + (f"{min(map(hole_size, holes)):.1f} mm to {max(map(hole_size, holes)):.1f} mm, " if holes else "")
          + f"open {100 * area / disc.area:.0f} % of the disc, plate mass {plate_full.area * KIT['tp'] * 0.65e-3:.0f} g")
    print(f"check: bridge margin {r['bridge']:+.2f} mm, edge margin {r['edge']:+.2f} mm, "
          f"slot margin {r['slot']:+.2f} mm, slot to rim margin {r['slot_rim']:+.2f} mm, "
          f"solid core R {r['solid']:.1f} mm (min {R_SOLID:g}), pieces {r['pieces']}, symmetry {r['sym']:.3f} mm")
    ok = (min(r["bridge"], r["edge"], r["slot"], r["slot_rim"]) >= 0 and r["solid"] >= R_SOLID
          and r["pieces"] == 1 and r["sym"] <= SYM_TOL and sup >= SUPPORT_MIN
          and pw[1] - pw[0] >= PASS_MIN and not false)
    title = (f"Top plate: Penrose P3, edge {up['a_t']:g} mm, solid core, {len(holes)} holes. "
             f"Bayonet turn {TURN:g}° ± {PLAY:g}°.")
    os.makedirs(os.path.dirname(os.path.abspath(args.svg)), exist_ok=True)
    preview(plate_full, holes, states, sup, pw, args.svg, title)
    print(f"written: {os.path.relpath(args.svg)}")
    if not ok:
        print("CHECK FAILED: no DXF written")
        return 1
    # 3D cuts: gap loops reach beyond Rpl, so the cut trims the cylinder TopPlate
    ring = Point(0, 0).buffer(RPL + 3, ARC).difference(Point(0, 0).buffer(RPL - 20, ARC))
    gap_loops = gaps().intersection(ring).difference(Point(0, 0).buffer(RPL + 3, ARC).exterior.buffer(0))
    cuts = loops(unary_union([gap_loops, slots, *holes]))
    stem = os.path.join(pp.CAD_DIR, "top_plate")
    pp.dxf(cuts, f"{stem}_cuts.dxf")
    laser = plate_full.difference(Point(0, 0).buffer(DN / 2, ARC // 2)).buffer(KERF / 2, ARC // 8, join_style="mitre")
    pp.dxf(loops(laser), f"{stem}_kerf.dxf")
    print(f"written: {os.path.relpath(stem)}_cuts.dxf, {os.path.relpath(stem)}_kerf.dxf")
    return 0


if __name__ == "__main__":
    sys.exit(main())

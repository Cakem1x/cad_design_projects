"""Sight lines and light zones of the dodecahedron lamp. Writes figures to ../docs/img/.

The elevation angle e is measured at the lamp centre, from the horizontal, positive upward.
The dodecahedron stands on a face. Its faces cover 4 face zones: bottom panel, lower ring
(5 panels), upper ring (5 panels), top plate. The design zones (table, glare, projection)
follow from the viewer envelopes at the chosen lamp height.

Figures:
  sight_lines_side_view.svg   room side view at the chosen height, design zones, viewer envelopes
  sight_lines_elevation.svg   viewer elevation against shade height
  panel_zones.svg             design zones on a lower-ring and an upper-ring panel

Usage: python3 platonic_lampshades/tools/plot_sight_lines.py
"""
import math
import os

import matplotlib

matplotlib.use("svg")
# Deterministic SVG output: fixed element IDs, no date stamp.
matplotlib.rcParams["svg.hashsalt"] = "platonic_lampshades"
matplotlib.rcParams["svg.fonttype"] = "path"
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, Polygon, Rectangle  # noqa: E402

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "img")

# Room, m
ROOM_H = 2.5
WALL_X = 3.0
TABLE_H = 0.75
TABLE_HALF = 0.8          # half length; half width 0.45 m
TABLE_HALF_W = 0.45

# Lamp, from the design (docs/overview.md), m
A = 0.10597               # edge length
T = 0.003                 # plywood thickness
LF, LB, H_PIN, EP = 0.016, 0.030, 0.009, 0.016   # bracket flange, length, pin distance, pin spacing
RI = A / 2 * math.sqrt((25 + 11 * math.sqrt(5)) / 10)   # inradius
RC = A * math.sqrt(3) * (1 + math.sqrt(5)) / 4           # circumradius
RM = A * (3 + math.sqrt(5)) / 4                          # midradius
S_INSET = T / math.tan(math.radians(180 - math.degrees(math.atan(2))) / 2)
RP = A / (2 * math.tan(math.radians(36))) - S_INSET      # panel inradius (outer face)

SHADE_BOTTOM = 1.00                                      # chosen: shade bottom above table, m
ZC = TABLE_H + SHADE_BOTTOM + RI                         # lamp centre above floor, m

# Face zone boundaries, deg
THETA_V = math.degrees(math.acos(RI / RC))   # face normal to vertex
THETA_E = math.degrees(math.acos(RI / RM))   # face normal to edge midpoint
RING_N = math.degrees(math.atan(0.5))        # ring face normal elevation, 26.57 deg
E_CAP_V = 90 - THETA_V                       # cap boundary at a vertex, 52.62 deg
E_CAP_E = 90 - THETA_E                       # cap boundary at an edge midpoint, 58.28 deg
E_MID = THETA_V - RING_N                     # ring faces reach past the equator, 10.81 deg

# Viewer envelopes: (name, distance range from lamp axis m, eye height range m)
ENVELOPES = [
    ("seated at table", (0.9, 1.4), (1.10, 1.30)),
    ("seated in room", (1.5, WALL_X), (1.00, 1.20)),
    ("standing", (1.0, WALL_X), (1.45, 1.80)),
]
MARGIN = 5.0   # deg, added on both sides of the viewer envelope

# Representative viewers for the elevation chart: (label, distance m, eye height m, line style)
VIEWERS = [
    ("seated at table", 1.15, 1.20, "-"),
    ("standing, 1.6 m away", 1.6, 1.65, "--"),
    ("standing, 2.6 m away", 2.6, 1.65, "-."),
    ("seated in room, 2.6 m away", 2.6, 1.10, ":"),
]

# Colours: reference palette slots 4 (yellow), 2 (orange), 1 (blue)
C_TABLE, C_GLARE, C_PROJ = "#eda100", "#eb6834", "#2a78d6"
SURFACE = "#fcfcfb"
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
GRID = "#e4e3df"
INK = "#3d3c39"
FURNITURE = "#a9a8a2"


def elev(x, z, zc=ZC):
    return math.degrees(math.atan2(z - zc, x))


def envelope_range(zc=ZC):
    lo, hi = 90.0, -90.0
    for _, (x0, x1), (z0, z1) in ENVELOPES:
        for x in (x0, x1):
            for z in (z0, z1):
                e = elev(x, z, zc)
                lo, hi = min(lo, e), max(hi, e)
    return lo, hi


ENV_LO, ENV_HI = envelope_range()
E_GLARE_LO = math.floor(ENV_LO - MARGIN)     # below: table zone
E_GLARE_HI = math.ceil(ENV_HI + MARGIN)      # above: projection zone
DESIGN_ZONES = [
    ("table", -90, E_GLARE_LO, C_TABLE),
    ("glare", E_GLARE_LO, E_GLARE_HI, C_GLARE),
    ("projection", E_GLARE_HI, 90, C_PROJ),
]


def style(ax, equal=True):
    ax.set_facecolor(SURFACE)
    if equal:
        ax.set_aspect("equal")
    ax.tick_params(colors=TEXT_SECONDARY, length=0, labelsize=8)
    for s in ax.spines:
        ax.spines[s].set_visible(False)


def ray_to_room(x0, z0, ang_deg, side):
    """Point where a ray from (x0, z0) leaves the room. side = +1 right, -1 left."""
    a = math.radians(ang_deg)
    dx, dz = side * math.cos(a), math.sin(a)
    ts = []
    if abs(dx) > 1e-9:
        ts.append((side * WALL_X - x0) / dx)
    if dz > 1e-9:
        ts.append((ROOM_H - z0) / dz)
    if dz < -1e-9:
        ts.append((0 - z0) / dz)
    t = min(v for v in ts if v > 0)
    return x0 + t * dx, z0 + t * dz


def wedge(x0, z0, lo, hi, side):
    pts = [(x0, z0)]
    n = 60
    for i in range(n + 1):
        pts.append(ray_to_room(x0, z0, lo + (hi - lo) * i / n, side))
    return pts


def draw_seated(ax, x, eye, facing):
    """facing: +1 if the person faces +x."""
    seat = eye - 0.75
    ax.add_patch(Circle((x, eye + 0.02), 0.09, facecolor="none", edgecolor=INK, linewidth=1.2, zorder=5))
    ax.plot([x, x], [eye - 0.08, seat], color=INK, linewidth=1.2, zorder=5)
    ax.plot([x, x + facing * 0.4, x + facing * 0.4], [seat, seat, 0.0], color=INK, linewidth=1.2, zorder=5)
    ax.plot([x - facing * 0.12, x - facing * 0.12, x + facing * 0.2, x + facing * 0.2],
            [eye - 0.25, seat, seat, 0], color=FURNITURE, linewidth=1.5, zorder=4)


def draw_standing(ax, x, eye):
    ax.add_patch(Circle((x, eye + 0.02), 0.09, facecolor="none", edgecolor=INK, linewidth=1.2, zorder=5))
    hip = eye * 0.55
    ax.plot([x, x], [eye - 0.08, hip], color=INK, linewidth=1.2, zorder=5)
    ax.plot([x - 0.12, x, x + 0.12], [0, hip, 0], color=INK, linewidth=1.2, zorder=5)


def side_view():
    fig, ax = plt.subplots(figsize=(10, 4.4))
    fig.patch.set_facecolor(SURFACE)
    style(ax)

    for name, lo, hi, col in DESIGN_ZONES:
        for side in (1, -1):
            ax.add_patch(Polygon(wedge(0, ZC, lo, hi, side), closed=True, facecolor=col, alpha=0.14,
                                 edgecolor="none", zorder=1))
    for ang in (E_GLARE_LO, E_GLARE_HI):
        for side in (1, -1):
            x1, z1 = ray_to_room(0, ZC, ang, side)
            ax.plot([0, x1], [ZC, z1], color=INK, linewidth=1.0, zorder=2)
        d = 1.0
        ax.text(d * math.cos(math.radians(ang)), ZC + d * math.sin(math.radians(ang)), f"{ang:+.0f}°",
                fontsize=7.5, color=TEXT_PRIMARY, ha="center", va="center", zorder=7,
                bbox=dict(facecolor=SURFACE, edgecolor="none", pad=0.6))
    # Face zone boundaries, thin dashed, left half only
    for ang in (-E_CAP_V, -E_MID, E_MID, E_CAP_V):
        x1, z1 = ray_to_room(0, ZC, ang, -1)
        ax.plot([0, x1], [ZC, z1], color=TEXT_SECONDARY, linewidth=0.7, linestyle=(0, (3, 3)), zorder=2)

    # Viewer envelopes (eye boxes), right half
    for name, (x0, x1), (z0, z1) in ENVELOPES:
        ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, facecolor="none", edgecolor=INK,
                               linewidth=0.9, linestyle=(0, (2, 2)), zorder=3))
    ax.text(0.92, 1.33, "eyes seated\nat table", fontsize=7, color=TEXT_SECONDARY, va="bottom")
    ax.text(2.25, 0.93, "eyes seated in room", fontsize=7, color=TEXT_SECONDARY, va="top", ha="center")
    ax.text(2.05, 1.83, "eyes standing", fontsize=7, color=TEXT_SECONDARY, va="bottom", ha="center")

    labels = [("projection\n→ ceiling, upper walls", 0.55, 2.33), ("glare zone\n→ eyes", 1.95, 0.55),
              ("table zone\n→ table", 0.12, 0.98)]
    for text, x, z in labels:
        ax.text(x, z, text, fontsize=8, color=TEXT_PRIMARY, ha="left", va="center", zorder=6,
                bbox=dict(facecolor=SURFACE, edgecolor="none", pad=0.6, alpha=0.8))
    ax.text(-2.92, 0.08, "dashed: face boundaries\n±10.8°, ±52.6°", fontsize=7, color=TEXT_SECONDARY,
            va="bottom")

    # Room
    for xs, zs in (([-WALL_X, WALL_X], [0, 0]), ([-WALL_X, WALL_X], [ROOM_H, ROOM_H]),
                   ([-WALL_X, -WALL_X], [0, ROOM_H]), ([WALL_X, WALL_X], [0, ROOM_H])):
        ax.plot(xs, zs, color=INK, linewidth=2)
    ax.add_patch(Rectangle((-TABLE_HALF, TABLE_H - 0.04), 2 * TABLE_HALF, 0.04, facecolor=FURNITURE,
                           edgecolor="none", zorder=4))
    for lx in (-TABLE_HALF + 0.08, TABLE_HALF - 0.08):
        ax.plot([lx, lx], [0, TABLE_H - 0.04], color=FURNITURE, linewidth=2, zorder=4)

    # People: left half as examples; envelopes on the right
    draw_seated(ax, -1.15, 1.20, facing=1)
    draw_standing(ax, -2.0, 1.65)
    draw_seated(ax, 1.15, 1.20, facing=-1)
    draw_standing(ax, 2.6, 1.70)

    # Lamp
    ax.plot([0, 0], [ZC + RC, ROOM_H], color=INK, linewidth=1, zorder=5)
    ax.add_patch(Circle((0, ZC), RC, facecolor=SURFACE, edgecolor=INK, linewidth=1.5, zorder=6))

    ax.set_xlim(-WALL_X - 0.1, WALL_X + 0.1)
    ax.set_ylim(-0.05, ROOM_H + 0.05)
    ax.set_xlabel("horizontal distance from lamp axis (m)", color=TEXT_SECONDARY, fontsize=8)
    ax.set_ylabel("height (m)", color=TEXT_SECONDARY, fontsize=8)
    ax.set_title(f"Design zones. Shade bottom {SHADE_BOTTOM:.2f} m above table, lamp centre {ZC:.3f} m above "
                 f"floor, room height {ROOM_H} m. Glare zone = viewer envelopes ± {MARGIN:.0f}°.",
                 color=TEXT_PRIMARY, fontsize=9, loc="left")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "sight_lines_side_view.svg"), facecolor=SURFACE)
    plt.close(fig)


def elevation_chart():
    fig, ax = plt.subplots(figsize=(8, 4.6))
    fig.patch.set_facecolor(SURFACE)
    style(ax, equal=False)
    hs = [0.5 + 0.01 * i for i in range(71)]   # shade bottom above table
    ylo, yhi = -70, 30
    face = [(-90, -E_CAP_V, C_TABLE), (-E_CAP_V, -E_MID, C_GLARE), (-E_MID, E_MID, GRID),
            (E_MID, E_CAP_V, "#1baf7a"), (E_CAP_V, 90, C_PROJ)]
    for lo, hi, col in face:
        ax.axhspan(max(lo, ylo), min(hi, yhi), color=col, alpha=0.13, linewidth=0, zorder=0)
    ax.axhspan(-E_CAP_E, -E_CAP_V, color=GRID, alpha=0.6, linewidth=0, zorder=0)
    for text, y in (("upper ring", 20), ("both rings\n(zigzag)", 0), ("lower ring", -35),
                    ("zigzag", -55.4), ("bottom panel", -64)):
        ax.text(1.46, y, text, color=TEXT_PRIMARY if text != "zigzag" else TEXT_SECONDARY,
                fontsize=8 if text != "zigzag" else 7, va="center")
    for y in (-E_CAP_V, -E_MID, E_MID):
        ax.axhline(y, color=TEXT_SECONDARY, linewidth=0.6, zorder=1)
    for label, x, eye, ls in VIEWERS:
        ys = [elev(x, eye, TABLE_H + h + RI) for h in hs]
        ax.plot(hs, ys, color=INK, linewidth=2, linestyle=ls, zorder=3)
        ax.text(hs[-1] + 0.005, ys[-1], label, color=TEXT_PRIMARY, fontsize=7.5, va="center",
                ha="left", zorder=4, bbox=dict(facecolor=SURFACE, edgecolor="none", pad=0.5))
    ax.axvline(SHADE_BOTTOM, color=INK, linewidth=1, zorder=2)
    ax.text(SHADE_BOTTOM, 27, "chosen", ha="center", fontsize=7.5, color=TEXT_PRIMARY,
            bbox=dict(facecolor=SURFACE, edgecolor="none", pad=0.5))
    ax.set_xlim(0.5, 1.6)
    ax.set_ylim(ylo, yhi)
    ax.set_xticks([0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2])
    ax.set_xlabel("shade bottom above table (m)", color=TEXT_SECONDARY, fontsize=8)
    ax.set_ylabel("elevation of the viewer's eye\nseen from the lamp centre (°)", color=TEXT_SECONDARY,
                  fontsize=8)
    ax.set_title("Where viewers' eyes lie on the lamp, by shade height", color=TEXT_PRIMARY, fontsize=9,
                 loc="left")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "sight_lines_elevation.svg"), facecolor=SURFACE)
    plt.close(fig)


# Panel-local coordinates (mm): u horizontal along the panel, v up the panel (in its plane).
# The panel's outer face lies at distance RI from the centre.
def panel_frame(normal_elev):
    a = math.radians(normal_elev)
    n = (math.cos(a), 0.0, math.sin(a))
    u = (0.0, 1.0, 0.0)
    v = (-math.sin(a), 0.0, math.cos(a))
    return n, u, v


def panel_elev(normal_elev, pu, pv):
    n, u, v = panel_frame(normal_elev)
    p = [RI * 1000 * n[i] + pu * u[i] + pv * v[i] for i in range(3)]
    return math.degrees(math.atan2(p[2], math.hypot(p[0], p[1])))


def pentagon(vertex_up):
    rc = RP * 1000 / math.cos(math.radians(36))
    start = 90 if vertex_up else 270
    return [(rc * math.cos(math.radians(start + 72 * k)), rc * math.sin(math.radians(start + 72 * k)))
            for k in range(5)]


def centerline_crossing(normal_elev, target, v0, v1):
    for _ in range(80):
        vm = (v0 + v1) / 2
        if (panel_elev(normal_elev, 0, vm) - target) * (panel_elev(normal_elev, 0, v0) - target) <= 0:
            v1 = vm
        else:
            v0 = vm
    return (v0 + v1) / 2


def draw_panel(ax, title, normal_elev, vertex_up):
    poly = pentagon(vertex_up)
    patch = Polygon(poly, closed=True, facecolor="none", edgecolor=INK, linewidth=1.5, zorder=5)
    ax.add_patch(patch)
    n = 160
    rc = RP * 1000 / math.cos(math.radians(36))
    us = [-rc + 2 * rc * i / n for i in range(n + 1)]
    vs = [-rc + 2 * rc * j / n for j in range(n + 1)]
    grid = [[panel_elev(normal_elev, uu, vv) for uu in us] for vv in vs]
    levels = [-90, E_GLARE_LO, E_GLARE_HI, 90]
    cf = ax.contourf(us, vs, grid, levels=levels, colors=[C_TABLE, C_GLARE, C_PROJ], alpha=0.25, zorder=1)
    cf.set_clip_path(patch)
    iso = [x for x in range(-60, 31, 10)]
    cl = ax.contour(us, vs, grid, levels=iso, colors=TEXT_SECONDARY, linewidths=0.5, linestyles="solid",
                    zorder=2)
    cl.set_clip_path(patch)
    # Labels on the vertical line u = 30 mm, inside the panel
    for lev in iso:
        vlo, vhi = (-RP * 1000, rc) if vertex_up else (-rc, RP * 1000)
        if (panel_elev(normal_elev, 30, vlo) - lev) * (panel_elev(normal_elev, 30, vhi) - lev) > 0:
            continue
        a, b = vlo, vhi
        for _ in range(60):
            m = (a + b) / 2
            if (panel_elev(normal_elev, 30, a) - lev) * (panel_elev(normal_elev, 30, m) - lev) <= 0:
                b = m
            else:
                a = m
        if patch.get_path().contains_point((30, a)) and abs(a) < rc - 12:
            ax.text(30, a, f"{lev:+d}°", fontsize=6.5, color=TEXT_SECONDARY, ha="center", va="center",
                    zorder=6, bbox=dict(facecolor=SURFACE, edgecolor="none", pad=0.3, alpha=0.85))
    cb = ax.contour(us, vs, grid, levels=[E_GLARE_LO, E_GLARE_HI], colors=INK, linewidths=1.4,
                    linestyles="solid", zorder=3)
    cb.set_clip_path(patch)
    # Bracket footprints and pin holes on every edge
    for k in range(5):
        (x0, y0), (x1, y1) = poly[k], poly[(k + 1) % 5]
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        L = math.hypot(x1 - x0, y1 - y0)
        tx, ty = (x1 - x0) / L, (y1 - y0) / L
        nx, ny = -mx / math.hypot(mx, my), -my / math.hypot(mx, my)   # inward normal
        hb, lf = LB * 500, LF * 1000
        corners = [(mx - hb * tx, my - hb * ty), (mx + hb * tx, my + hb * ty),
                   (mx + hb * tx + lf * nx, my + hb * ty + lf * ny), (mx - hb * tx + lf * nx, my - hb * ty + lf * ny)]
        ax.add_patch(Polygon(corners, closed=True, facecolor=FURNITURE, alpha=0.45, edgecolor="none", zorder=4))
        for sgn in (-1, 1):
            cx = mx + sgn * EP * 500 * tx + H_PIN * 1000 * nx
            cy = my + sgn * EP * 500 * ty + H_PIN * 1000 * ny
            ax.add_patch(Circle((cx, cy), 2.0, facecolor=SURFACE, edgecolor=INK, linewidth=0.6, zorder=5))
    style(ax)
    ax.set_xlim(-rc - 4, rc + 4)
    ax.set_ylim(-rc - 4, rc + 4)
    ax.set_title(title, color=TEXT_PRIMARY, fontsize=9, loc="left")
    ax.set_xlabel("u (mm)", color=TEXT_SECONDARY, fontsize=8)
    ax.set_ylabel("v, up the panel (mm)", color=TEXT_SECONDARY, fontsize=8)


def panel_zones():
    fig, axs = plt.subplots(1, 2, figsize=(10, 5.2))
    fig.patch.set_facecolor(SURFACE)
    draw_panel(axs[0], "Lower ring panel (outer face, seen from outside)", -RING_N, True)
    draw_panel(axs[1], "Upper ring panel (outer face, seen from outside)", RING_N, False)
    fig.text(0.01, 0.015, f"Fill: table zone (e < {E_GLARE_LO}°), glare zone ({E_GLARE_LO}° to "
             f"{E_GLARE_HI:+d}°), projection zone (e > {E_GLARE_HI:+d}°). Grey: bracket footprints "
             "with pin holes. Thin lines: elevation every 10°.", fontsize=7.5, color=TEXT_SECONDARY)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(os.path.join(OUT_DIR, "panel_zones.svg"), facecolor=SURFACE)
    plt.close(fig)


def report():
    print(f"a = {A*1000:.2f} mm, ri = {RI*1000:.1f} mm, rc = {RC*1000:.1f} mm, rp = {RP*1000:.2f} mm")
    print(f"face zones: caps {E_CAP_V:.2f} deg (vertex) / {E_CAP_E:.2f} deg (edge), "
          f"ring overlap +-{E_MID:.2f} deg, ring normal {RING_N:.2f} deg")
    print(f"shade bottom {SHADE_BOTTOM:.2f} m above table, lamp centre {ZC:.3f} m above floor, "
          f"{ROOM_H - ZC:.3f} m below ceiling")
    for name, (x0, x1), (z0, z1) in ENVELOPES:
        es = [elev(x, z) for x in (x0, x1) for z in (z0, z1)]
        print(f"envelope {name}: x {x0}-{x1} m, eye {z0}-{z1} m -> e {min(es):+.1f} .. {max(es):+.1f} deg")
    print(f"all viewers: {ENV_LO:+.1f} .. {ENV_HI:+.1f} deg; glare zone with margin: "
          f"{E_GLARE_LO:+d} .. {E_GLARE_HI:+d} deg")
    for label, x, eye, _ in VIEWERS:
        print(f"viewer {label}: {elev(x, eye):+.1f} deg")
    h = TABLE_H + SHADE_BOTTOM + RI - TABLE_H
    print(f"table: end {-math.degrees(math.atan2(h, TABLE_HALF)):+.1f} deg, corner "
          f"{-math.degrees(math.atan2(h, math.hypot(TABLE_HALF, TABLE_HALF_W))):+.1f} deg")
    print(f"bottom cap cone on table: r {h / math.tan(math.radians(E_CAP_V)):.2f} m (vertex), "
          f"{h / math.tan(math.radians(E_CAP_E)):.2f} m (edge)")
    print(f"table zone cone on table: r {h / math.tan(math.radians(-E_GLARE_LO)):.2f} m")
    hc = ROOM_H - ZC
    print(f"top cap cone on ceiling: r {hc / math.tan(math.radians(E_CAP_V)):.2f} m")
    x_wall, z_wall = ray_to_room(0, ZC, E_GLARE_HI, 1)
    print(f"projection zone lower ray hits wall at {x_wall:.2f} m, height {z_wall:.2f} m")
    rc = RP * 1000 / math.cos(math.radians(36))
    rp = RP * 1000
    v = centerline_crossing(-RING_N, E_GLARE_LO, -rp, rc)
    print(f"lower ring: e = {E_GLARE_LO} deg on centre line at {v + rp:.1f} mm above bottom edge")
    v = centerline_crossing(-RING_N, E_GLARE_HI, -rp, rc)
    print(f"lower ring: e = {E_GLARE_HI:+d} deg on centre line at {rc - v:.1f} mm below top vertex")
    v = centerline_crossing(RING_N, E_GLARE_HI, -rc, rp)
    print(f"upper ring: e = {E_GLARE_HI:+d} deg on centre line at {v + rc:.1f} mm above bottom vertex")
    print(f"panel height (edge to vertex): {rp + rc:.1f} mm")


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    side_view()
    elevation_chart()
    panel_zones()
    report()

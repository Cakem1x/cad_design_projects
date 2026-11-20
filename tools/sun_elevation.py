"""Plot the sun elevation over the day at a given latitude.

Usage: python3 tools/sun_elevation.py [output.svg]

Time axis: local solar time (12:00 = solar noon). The spring and autumn
equinoxes have the same declination (0°) and therefore the same curve.
"""
import math
import sys

import matplotlib

matplotlib.use("svg")
import matplotlib.pyplot as plt  # noqa: E402

LATITUDE_DEG = 50.0
HIGHLIGHT_HOURS = (6, 9, 12, 15, 18, 21)
MIN_ELEVATION_DEG = 10.0

# (label, declination in °, colour: reference palette slots 1-3)
SEASONS = (
    ("Summer solstice (Jun 21)", 23.44, "#eb6834"),
    ("Spring / autumn equinox (Mar 20, Sep 22)", 0.0, "#1baf7a"),
    ("Winter solstice (Dec 21)", -23.44, "#2a78d6"),
)

SURFACE = "#fcfcfb"
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
GRID = "#e4e3df"


def elevation_deg(lat_deg, decl_deg, solar_hour):
    lat, decl = math.radians(lat_deg), math.radians(decl_deg)
    hour_angle = math.radians(15.0 * (solar_hour - 12.0))
    s = math.sin(lat) * math.sin(decl) + math.cos(lat) * math.cos(decl) * math.cos(hour_angle)
    return math.degrees(math.asin(s))


def main(out_path):
    hours = [h / 20 for h in range(0, 24 * 20 + 1)]
    fig, ax = plt.subplots(figsize=(9, 5.2), dpi=100)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)

    for h in HIGHLIGHT_HOURS:
        ax.axvline(h, color=GRID, linewidth=1, zorder=0)
    ax.axhline(MIN_ELEVATION_DEG, color=TEXT_SECONDARY, linewidth=1, zorder=1)
    ax.text(21.4, MIN_ELEVATION_DEG + 1.0, f"min_sun_elevation\n= {MIN_ELEVATION_DEG:.0f}°",
            ha="right", va="bottom", color=TEXT_SECONDARY, fontsize=9)

    for label, decl, color in SEASONS:
        elev = [elevation_deg(LATITUDE_DEG, decl, t) for t in hours]
        pts = [(t, e) for t, e in zip(hours, elev) if e >= 0]
        ax.plot([p[0] for p in pts], [p[1] for p in pts], color=color, linewidth=2,
                solid_capstyle="round", solid_joinstyle="round", label=label, zorder=2)
        marks = [(h, elevation_deg(LATITUDE_DEG, decl, h)) for h in HIGHLIGHT_HOURS]
        marks = [m for m in marks if m[1] >= 0]
        ax.scatter([m[0] for m in marks], [m[1] for m in marks], s=64, color=color,
                   edgecolors=SURFACE, linewidths=2, zorder=3)
        noon = elevation_deg(LATITUDE_DEG, decl, 12)
        ax.text(12, noon + 2.0, f"{label.split(' (')[0]}: {noon:.1f}° at noon",
                ha="center", va="bottom", color=TEXT_PRIMARY, fontsize=9)

    ax.set_xlim(3, 21.5)
    ax.set_ylim(0, 75)
    ax.set_xticks(HIGHLIGHT_HOURS)
    ax.set_xticklabels([f"{h:02d}:00" for h in HIGHLIGHT_HOURS])
    ax.set_xlabel("Local solar time", color=TEXT_SECONDARY)
    ax.set_ylabel("Sun elevation (°)", color=TEXT_SECONDARY)
    ax.yaxis.grid(True, color=GRID, linewidth=1)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=TEXT_SECONDARY, length=0)
    ax.set_title(f"Sun elevation at {LATITUDE_DEG:.0f}° N", loc="left", color=TEXT_PRIMARY, fontsize=12)
    leg = ax.legend(loc="upper right", frameon=False, fontsize=9)
    for text in leg.get_texts():
        text.set_color(TEXT_PRIMARY)
    fig.tight_layout()
    fig.savefig(out_path, facecolor=SURFACE)

    print("| Time | " + " | ".join(s[0] for s in SEASONS) + " |")
    print("|------|" + "|".join("---" for _ in SEASONS) + "|")
    for h in HIGHLIGHT_HOURS:
        cells = []
        for _, decl, _ in SEASONS:
            e = elevation_deg(LATITUDE_DEG, decl, h)
            cells.append(f"{e:.1f}°" if e >= 0 else "below horizon")
        print(f"| {h:02d}:00 | " + " | ".join(cells) + " |")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "docs/img/sun_elevation_50N.svg")

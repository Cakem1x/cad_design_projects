"""Estimate how often the reflector needs re-aiming (sun elevation tracking).

Assumptions:
- The unit is turned to face the sun azimuth. The sun angle in the cross-section plane then
  equals the sun elevation.
- A reflector setting accepts the sun within ±theta_a. At each adjustment, the aim is chosen to
  keep the sun inside the window for as long as possible (greedy interval cover).
- Cooking time: sun elevation >= MIN_ELEVATION_DEG.
- The acceptance edge of a truncated CPC is gradual, so the results are rough estimates.
"""
from solar import elevation_deg

MIN_ELEVATION_DEG = 10.0
LATITUDE_DEG = 50.0
STEP_H = 1 / 60

SEASONS = (("Summer", 23.44), ("Equinox", 0.0), ("Winter", -23.44))


def schedule(theta_a_deg, decl_deg, lat_deg=LATITUDE_DEG):
    """Return the list of (start_h, end_h) intervals covered by one reflector setting each."""
    times = [i * STEP_H for i in range(int(24 / STEP_H) + 1)]
    elev = [elevation_deg(lat_deg, decl_deg, t) for t in times]
    usable = [i for i, e in enumerate(elev) if e >= MIN_ELEVATION_DEG]
    if not usable:
        return []
    intervals = []
    i, last = usable[0], usable[-1]
    while i <= last:
        lo = hi = elev[i]
        j = i
        while j + 1 <= last:
            lo2, hi2 = min(lo, elev[j + 1]), max(hi, elev[j + 1])
            if hi2 - lo2 > 2 * theta_a_deg:
                break
            lo, hi, j = lo2, hi2, j + 1
        intervals.append((times[i], times[j]))
        i = j + 1
    return intervals


if __name__ == "__main__":
    for ta in (20, 25, 30, 35):
        for name, decl in SEASONS:
            iv = schedule(ta, decl)
            print(ta, name, len(iv), round(min(b - a for a, b in iv), 2), [(round(a, 2), round(b, 2)) for a, b in iv])

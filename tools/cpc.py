"""Involute CPC profile for a cylindrical absorber.

Coordinates: absorber centre at the origin, optical axis +y, units mm.
Returns the right branch; the left branch is its mirror image about the y axis.
Equations: Rabl (1976), see docs/optics.md.
"""
import math


def _rho(r, theta, theta_a):
    if theta <= theta_a + math.pi / 2:
        return r * theta
    return r * (theta + theta_a + math.pi / 2 - math.cos(theta - theta_a)) / (1 + math.sin(theta - theta_a))


def _point(r, theta, theta_a):
    rho = _rho(r, theta, theta_a)
    return (r * math.sin(theta) - rho * math.cos(theta),
            -r * math.cos(theta) - rho * math.sin(theta))


def full_profile(r, theta_a_deg, n=2000):
    """Right branch of the untruncated CPC, from the cusp to the aperture."""
    theta_a = math.radians(theta_a_deg)
    end = 1.5 * math.pi - theta_a
    return [_point(r, end * i / n, theta_a) for i in range(n + 1)]


def cusp_y(r):
    return -r


def bottom_y(points):
    return min(p[1] for p in points)


def truncate(points, height):
    """Keep the points up to `height` above the lowest point of the profile."""
    y0 = bottom_y(points)
    return [p for p in points if p[1] - y0 <= height]


def aperture_width(points):
    return 2 * max(p[0] for p in points)


def concentration(points, r):
    return aperture_width(points) / (2 * math.pi * r)


def arc_length(points):
    return sum(math.dist(points[i], points[i + 1]) for i in range(len(points) - 1))


def cut_at_radius(points, radius):
    """Remove the points closer than `radius` to the absorber centre (gap option G1)."""
    return [p for p in points if math.hypot(*p) >= radius]

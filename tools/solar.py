"""Sun position helpers."""
import math


def elevation_deg(lat_deg, decl_deg, solar_hour):
    """Sun elevation for latitude, declination and local solar time (12 = solar noon)."""
    lat, decl = math.radians(lat_deg), math.radians(decl_deg)
    hour_angle = math.radians(15.0 * (solar_hour - 12.0))
    s = math.sin(lat) * math.sin(decl) + math.cos(lat) * math.cos(decl) * math.cos(hour_angle)
    return math.degrees(math.asin(s))

"""Coordinate helpers shared by the pipeline.
Model frame (same as lemo-opuscar's white-model demo): x = east, z = south, y = up, 1 unit = 1 model metre.
Ground metres come from a UTM zone chosen from the city's longitude, so footprints and heights share one metre."""
import math
from pyproj import Transformer, CRS

R = 6378137.0


def utm_epsg(lon, lat):
    zone = int((lon + 180) // 6) + 1
    return (32600 if lat >= 0 else 32700) + zone


class Frame:
    """Ground (UTM metres) <-> model units for one city box. box = (west, south, east, north) in degrees."""

    def __init__(self, box, scale, near=()):
        """near: other boxes a position may lie in (the land beyond the plate); model_lonlat stops on a position more than a
        plate's width beyond the plate and them"""
        self.box = box
        w, s, e, n = box
        self.epsg = utm_epsg((w + e) / 2, (s + n) / 2)
        self.to_utm = Transformer.from_crs(4326, self.epsg, always_xy=True)
        self.to_wgs = Transformer.from_crs(self.epsg, 4326, always_xy=True)
        self.merc_to_utm = Transformer.from_crs(3857, self.epsg, always_xy=True)
        # the crop in ground metres is the UTM bbox of the four corners' centre lines (a near-rectangle at city scale)
        xs, ys = zip(*[self.to_utm.transform(lon, lat) for lon, lat in ((w, s), (e, s), (e, n), (w, n))])
        self.x0, self.x1 = (xs[0] + xs[3]) / 2, (xs[1] + xs[2]) / 2
        self.y0, self.y1 = (ys[0] + ys[1]) / 2, (ys[2] + ys[3]) / 2
        self.cx, self.cy = (self.x0 + self.x1) / 2, (self.y0 + self.y1) / 2
        self.scale = scale
        self.size = [(self.x1 - self.x0) * scale, (self.y1 - self.y0) * scale]   # plate width (east-west), depth (north-south)
        self.reach = [(self.x0, self.y0, self.x1, self.y1)]
        for b in near:
            bx, by = zip(*[self.to_utm.transform(lon, lat) for lon, lat in ((b[0], b[1]), (b[2], b[1]), (b[2], b[3]), (b[0], b[3]))])
            self.reach.append((min(bx), min(by), max(bx), max(by)))
        self.slack = max(self.x1 - self.x0, self.y1 - self.y0)

    def inside(self, x, y):
        return self.x0 <= x <= self.x1 and self.y0 <= y <= self.y1

    def model(self, x, y):
        """ground metres -> [x_east, z_south] in model units"""
        return [round((x - self.cx) * self.scale, 5), round(-(y - self.cy) * self.scale, 5)]

    def model_lonlat(self, lon, lat):
        x, y = self.to_utm.transform(lon, lat)
        far = min(math.hypot(max(x0 - x, 0, x - x1), max(y0 - y, 0, y - y1)) for x0, y0, x1, y1 in self.reach)
        if not far <= self.slack:   # (also a latitude past 90, which projects to inf)
            raise SystemExit(f'position [{lon}, {lat}] lies {far / 1000:.0f} km beyond the plate {list(self.box)}: a typo in the city\'s '
                             f'coordinates (longitude first, then latitude)? Search city.yaml for {lon}')
        return self.model(x, y)

    def uv(self, x, y):
        """ground metres -> texture uv in [0,1] (u east, v south: v = 0 at the north edge)"""
        return (x - self.x0) / (self.x1 - self.x0), (self.y1 - y) / (self.y1 - self.y0)

    def ground_wgs(self, x, y):
        return self.to_wgs.transform(x, y)


def ring_area(r):
    return abs(sum(r[i][0] * r[i + 1][1] - r[i + 1][0] * r[i][1] for i in range(len(r) - 1)) / 2)

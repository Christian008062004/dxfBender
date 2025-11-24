"""Spline-Handling: freiform Kurven (SPLINE) ueber Polyline approximieren."""

from typing import List, Tuple

from ezdxf.math import Vec3


def spline_to_points(entity) -> Tuple[List[Vec3], bool]:
    # Spline wird ueber eine Polyline approximiert.
    pts = [Vec3(p) for p in entity.flattening(0.5)]
    return pts, bool(getattr(entity, "closed", False))

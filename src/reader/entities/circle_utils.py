"Circle-Handling: Vollkreis, definiert durch Mittelpunkt und Radius."

from typing import List, Tuple

from ezdxf.math import ConstructionArc, Vec3


def circle_to_points(entity) -> Tuple[List[Vec3], bool]:
    # Vollkreis als Arc 0..360 Grad behandeln.
    circle = ConstructionArc(
        center=entity.dxf.center,
        radius=entity.dxf.radius,
        start_angle=0,
        end_angle=360,
        is_counter_clockwise=True,
    )
    pts = [Vec3(p) for p in circle.flattening(0.5)]
    return pts, True

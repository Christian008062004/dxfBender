"Arc-Handling: Kreisbogen mit Start-/Endwinkel und Radius."
# Halt nur nen Teil vom Kreis
from typing import List, Tuple

from ezdxf.math import ConstructionArc, Vec3


def arc_to_points(entity) -> Tuple[List[Vec3], bool]:
    # DXF-Arc in Konstruktion umwandeln und auf Punkte abflachen.
    arc = ConstructionArc(
        center=entity.dxf.center,
        radius=entity.dxf.radius,
        start_angle=entity.dxf.start_angle,
        end_angle=entity.dxf.end_angle,
        is_counter_clockwise=entity.dxf.extrusion.z >= 0,
    )
    pts = [Vec3(p) for p in arc.flattening(0.5)]
    return pts, False

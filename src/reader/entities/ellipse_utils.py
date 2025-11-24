"""Ellipse-Handling: Ellipse oder Teilellipse, ggf. geschlossen bei voller 2*pi-Spanweite."""
#Halt son zerquetschten Kreis
import math
from typing import List, Tuple

from ezdxf.math import ConstructionEllipse, Vec3


def ellipse_to_points(entity) -> Tuple[List[Vec3], bool]:
    # Ellipse/Teilellipse konstruieren und auf Punkte abflachen.
    ell = ConstructionEllipse(
        center=entity.dxf.center,
        major_axis=entity.dxf.major_axis,
        ratio=entity.dxf.ratio,
        start_param=entity.dxf.start_param,
        end_param=entity.dxf.end_param,
        extrusion=getattr(entity.dxf, "extrusion", Vec3(0, 0, 1)),
        ccw=entity.dxf.extrusion.z >= 0,
    )
    pts = [Vec3(p) for p in ell.flattening(0.5)]
    # Geschlossen, wenn Parameter-Spanne 0 bzw. 2*pi innerhalb Toleranz ist.
    closed = math.isclose(
        (entity.dxf.end_param - entity.dxf.start_param) % (2 * math.pi),
        0.0,
        abs_tol=1e-6,
    )
    return pts, closed

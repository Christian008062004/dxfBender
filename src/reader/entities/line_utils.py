"Line-Handling: einfache Strecke mit Start- und Endpunkt."

from typing import List, Tuple

from ezdxf.math import Vec3


def line_to_points(entity) -> Tuple[List[Vec3], bool]:
    # Linie besteht aus Start- und Endpunkt.
    return [Vec3(entity.dxf.start), Vec3(entity.dxf.end)], False

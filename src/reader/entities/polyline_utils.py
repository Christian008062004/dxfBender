"""Polyline-Handling (z.B. LWPOLYLINE): verbundene Stuetzpunkte, offen oder geschlossen."""
#Einfach ganz viele aneinander gereihte Linien
from typing import Iterable, List, Tuple

from ezdxf.math import Vec3


def pairwise(points: Iterable[Vec3]) -> Iterable[Tuple[Vec3, Vec3]]:
    # Gibt aufeinanderfolgende Punkte als Tupel (P_i, P_i+1) aus.
    pts = list(points)
    for a, b in zip(pts, pts[1:]):
        yield a, b


def polyline_length(points: List[Vec3], closed: bool) -> float:
    """Berechnet die Laenge ueber alle Segmente, optional mit Schlusskante."""
    total = 0.0
    if len(points) < 2:
        return total

    # Bei geschlossener Kontur die letzte Kante zum Startpunkt zufuegen.
    iter_points = list(points)
    if closed and points[0] != points[-1]:
        iter_points.append(points[0])

    # Segmentlaengen aufsummieren.
    for a, b in pairwise(iter_points):
        total += (b - a).magnitude
    return total


def distance_point_to_segment(pt: Vec3, a: Vec3, b: Vec3) -> float:
    """Minimaler Abstand eines Punkts zu einem Liniensegment."""
    ab = b - a
    ab_len_sq = ab.dot(ab)
    if ab_len_sq == 0:
        return (pt - a).magnitude

    # Projektion des Punkts auf das Segment [0,1] clampen.
    t = max(0.0, min(1.0, (pt - a).dot(ab) / ab_len_sq))
    closest = a + ab * t
    return (pt - closest).magnitude


def point_on_polyline(points: List[Vec3], test: Vec3, closed: bool, tol: float) -> bool:
    """Prueft, ob der Testpunkt innerhalb der Toleranz auf einer Polyline liegt."""
    if len(points) < 2:
        return False

    # Geschlossene Polylinie mit Abschlusskante versehen.
    iter_points = list(points)
    if closed and points[0] != points[-1]:
        iter_points.append(points[0])

    # Treffer, wenn Abstands-Test auf mindestens einem Segment innerhalb tol ist.
    return any(
        distance_point_to_segment(test, a, b) <= tol
        for a, b in pairwise(iter_points)
    )


def lwpolyline_to_points(entity) -> Tuple[List[Vec3], bool]:
    # DXF-LWPOLYLINE-Vertices (X,Y) in Vec3-Liste mit Z=0 umwandeln.
    pts = [Vec3(x, y, 0) for x, y, *_ in entity.lwpoints]
    return pts, bool(entity.closed)

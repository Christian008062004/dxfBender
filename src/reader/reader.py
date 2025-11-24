import argparse
import sys
from pathlib import Path
from typing import Optional, Tuple, List

import ezdxf
from ezdxf.math import Vec3

#!/usr/bin/env python
# Ermoeglicht lokale Imports auch bei direktem Skriptaufruf.
CURRENT_DIR = Path(__file__).resolve().parent
PARENT_DIR = CURRENT_DIR / "entities"
for p in (CURRENT_DIR, PARENT_DIR):
    if str(p) not in sys.path:
        sys.path.append(str(p))

from entities.polyline_utils import (  # noqa: E402
    pairwise,
    polyline_length,
    point_on_polyline,
    lwpolyline_to_points,
)
from entities.spline_utils import spline_to_points  # noqa: E402
from entities.arc_utils import arc_to_points  # noqa: E402
from entities.circle_utils import circle_to_points  # noqa: E402
from entities.ellipse_utils import ellipse_to_points  # noqa: E402
from entities.line_utils import line_to_points  # noqa: E402

# Standard-Pfad zu einer Beispieldatei, falls kein Pfad uebergeben wird.
DEFAULT_DXF = Path("data/dxfData/Cubische Bezierkurve.dxf")


def get_curve_info(entity) -> Optional[Tuple[Vec3, Vec3, float, List[Vec3], bool]]:
    """Konvertiert unterstuetzte DXF-Entities in eine Polyline-Repraesentation."""
    kind = entity.dxftype()
    # Mapping von DXF-Typ zu Konverter-Funktion.
    converters = {
        "LINE": line_to_points,
        "ARC": arc_to_points,
        "CIRCLE": circle_to_points,
        "ELLIPSE": ellipse_to_points,
        "LWPOLYLINE": lwpolyline_to_points,
        "SPLINE": spline_to_points,
    }

    if kind not in converters:
        return None

    # Punkte + Closed-Flag erzeugen.
    pts, closed = converters[kind](entity)
    if len(pts) == 0:
        return None

    # Start/Ende bestimmen (bei geschlossenem Objekt Ende = Start) und Laenge.
    start = pts[0]
    end = pts[0] if closed else pts[-1]
    length = polyline_length(pts, closed)
    return start, end, length, pts, closed


def main() -> None:
    parser = argparse.ArgumentParser(description="DXF-Kurven auslesen.")
    parser.add_argument(
        "dxf_file",
        nargs="?",
        default=str(DEFAULT_DXF),
        help=f"Pfad zur DXF-Datei (Standard: {DEFAULT_DXF})",
    )
    parser.add_argument(
        "--point",
        nargs=2,
        type=float,
        metavar=("X", "Y"),
        help="Testpunkt in der Form: X Y",
    )
    parser.add_argument(
        "--tol",
        type=float,
        default=1e-3,
        help="Toleranz fuer Punkttest (Standard: 1e-3)",
    )
    args = parser.parse_args()

    # Eingabe pruefen und Testpunkt optional anlegen.
    dxf_path = Path(args.dxf_file)
    if not dxf_path.exists():
        raise SystemExit(f"DXF-Datei nicht gefunden: {dxf_path}")

    test_point = Vec3(args.point[0], args.point[1], 0) if args.point else None

    # DXF lesen und alle Entities im Modelspace durchlaufen.
    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()

    print(f"\nDatei: {dxf_path}")
    print("Gefundene Kurven:")
    for entity in msp:
        # Nur unterstuetzte Kurventypen verarbeiten.
        info = get_curve_info(entity)
        if info is None:
            continue

        start, end, length, polyline, closed = info

        print("------------------------------------------------")
        print(f"Kurventyp:  {entity.dxftype()}")
        print(f"Startpunkt: {start}")
        print(f"Endpunkt:   {end}")
        print(f"Laenge:     {length:.3f}")
        print(f"Closed:     {closed}")

        if test_point is not None:
            # Punkt-Kurve-Test mit Toleranz.
            if point_on_polyline(polyline, test_point, closed=closed, tol=args.tol):
                print(f"Punkt {test_point} LIEGT auf der Kurve (tol={args.tol}).")
            else:
                print(f"Punkt {test_point} liegt NICHT auf der Kurve (tol={args.tol}).")


if __name__ == "__main__":
    main()

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

from entities.base.entity_interface import EntityInterface  # noqa: E402
from entities.shapes.polyline_utils import LwPolylineEntity  # noqa: E402
from entities.shapes.spline_utils import SplineEntity  # noqa: E402
from entities.shapes.arc_utils import ArcEntity  # noqa: E402
from entities.shapes.circle_utils import CircleEntity  # noqa: E402
from entities.shapes.ellipse_utils import EllipseEntity  # noqa: E402
from entities.shapes.line_utils import LineEntity  # noqa: E402

# Standard-Pfad zu einer Beispieldatei, falls kein Pfad uebergeben wird.
DEFAULT_DXF = Path("data/dxfData/Cubische Bezierkurve.dxf")
CONVERTERS = {
    "LINE": LineEntity.from_dxf,
    "ARC": ArcEntity.from_dxf,
    "CIRCLE": CircleEntity.from_dxf,
    "ELLIPSE": EllipseEntity.from_dxf,
    "LWPOLYLINE": LwPolylineEntity.from_dxf,
    "SPLINE": SplineEntity.from_dxf,
}


def get_curve_info(entity) -> Optional[Tuple[Vec3, Vec3, float, List[Vec3], bool]]:
    """Konvertiert unterstuetzte DXF-Entities in eine Polyline-Repraesentation."""
    kind = entity.dxftype()
    # Mapping von DXF-Typ zu Entity-Wrappern.
    if kind not in CONVERTERS:
        return None

    curve: EntityInterface = CONVERTERS[kind](entity)
    pts, closed = curve.as_polyline()
    if len(pts) == 0:
        return None

    # Start/Ende bestimmen (bei geschlossenem Objekt Ende = Start) und Laenge.
    start = curve.start()
    end = curve.end()
    length = curve.length()
    return start, end, length, pts, closed


def _add_segmentized_entity(
    entity, out_msp, segment_length: float, layer: str = "0"
) -> None:
    """Fuegt segmentierte Linien fuer eine Eingabe-Entity in den Ziel-Modelspace ein."""
    curve: EntityInterface = CONVERTERS[entity.dxftype()](entity)
    seg_pts, seg_closed = curve.segmentize(segment_length)
    if len(seg_pts) < 2:
        return

    pts2d = [(float(p.x), float(p.y), 0.0) for p in seg_pts]
    for a, b in zip(pts2d, pts2d[1:]):
        out_msp.add_line(a, b, dxfattribs={"layer": layer})
    if seg_closed and pts2d[0] != pts2d[-1]:
        out_msp.add_line(pts2d[-1], pts2d[0], dxfattribs={"layer": layer})


def main() -> None:
    parser = argparse.ArgumentParser(description="DXF-Kurven auslesen.")
    parser.add_argument(
        "dxf_file",
        nargs="?",
        default=str(DEFAULT_DXF),
        help=f"Pfad zur DXF-Datei (Standard: {DEFAULT_DXF})",
    )
    parser.add_argument(
        "--segment-length",
        type=float,
        default=5.0,
        help="Maximale Segmentlaenge fuer Ausgabe-DXF (Standard: 5.0)",
    )
    parser.add_argument(
        "--segmentized-dxf",
        type=Path,
        help="Optionaler Pfad fuer eine ausgegebene DXF mit segmentierten Kurven.",
    )
    args = parser.parse_args()

    # Eingabe pruefen und Testpunkt optional anlegen.
    dxf_path = Path(args.dxf_file)
    if not dxf_path.exists():
        raise SystemExit(f"DXF-Datei nicht gefunden: {dxf_path}")

    # DXF lesen und alle Entities im Modelspace durchlaufen.
    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()

    out_doc = ezdxf.new("R2000", setup=True) if args.segmentized_dxf else None
    out_msp = out_doc.modelspace() if out_doc else None
    if out_doc:
        # Einheit metrisch: Millimeter (4)
        out_doc.header["$INSUNITS"] = 4

    print(f"\nDatei: {dxf_path}")
    print("Gefundene Kurven:")
    for entity in msp:
        # Nur unterstuetzte Kurventypen verarbeiten.
        info = get_curve_info(entity)
        if info is None:
            continue

        start, end, length, polyline, closed = info
        # Segmentierte Ausgabe bauen, falls angefordert.
        if out_msp is not None:
            _add_segmentized_entity(entity, out_msp, args.segment_length, layer="0")

        print("------------------------------------------------")
        print(f"Kurventyp:  {entity.dxftype()}")
        print(f"Startpunkt: {start}")
        print(f"Endpunkt:   {end}")
        print(f"Laenge:     {length:.3f}")
        print(f"Closed:     {closed}")

    if out_doc and args.segmentized_dxf:
        args.segmentized_dxf.parent.mkdir(parents=True, exist_ok=True)
        out_doc.saveas(args.segmentized_dxf)
        print(f"\nSegmentierte DXF gespeichert nach: {args.segmentized_dxf}")


if __name__ == "__main__":
    main()

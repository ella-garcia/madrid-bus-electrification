"""Build the BI visualisation (Deliverable 3): one self-contained HTML file with Files 1-4 embedded.

Used from notebook 01 §10:
    from bi.build_bi import route_geometry, build_html
    routes = route_geometry(os.path.join(RAW, "emt_kml", REF_DATE))
    build_html(F, routes, os.path.join(OUT, "Madrid_Bus_BI.html"), meta)

`F` maps "File_1.csv" ... "File_4.csv" to the DataFrames read back AS SAVED (brief 5.3: the HTML shows exactly
the data of Files 1-4). A missing file is shown as "pending" in its view, never filled with other numbers.
"""
import glob, json, math, os, re
import xml.etree.ElementTree as ET

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "bi_template.html")
FILES = ("File_1.csv", "File_2.csv", "File_3.csv", "File_4.csv")


def _simplify(pts, tol):
    """Douglas-Peucker on (lon, lat) pairs; tol in degrees (~1e-4 = 10 m)."""
    if len(pts) < 3:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        (x1, y1), (x2, y2) = pts[a], pts[b]
        dx, dy = x2 - x1, y2 - y1
        norm = math.hypot(dx, dy) or 1e-12
        best, idx = 0.0, None
        for i in range(a + 1, b):
            x0, y0 = pts[i]
            d = abs(dy * x0 - dx * y0 + x2 * y1 - y2 * x1) / norm
            if d > best:
                best, idx = d, i
        if idx is not None and best > tol:
            keep[idx] = True
            stack += [(a, idx), (idx, b)]
    return [p for p, k in zip(pts, keep) if k]


def route_geometry(kml_dir, direction="D1", tol=1.2e-4):
    """{route_id: [[lat, lon], ...]} from EMT's KML route files (one direction per line keeps the file small).

    Each KML holds a route as many street segments in driving order; they are chained, de-duplicated and simplified.
    Where a segment does not continue from the previous one, a new part starts, so gaps are never bridged."""
    ns = "{http://www.opengis.net/kml/2.2}"
    out = {}
    for path in sorted(glob.glob(os.path.join(kml_dir, f"L*_{direction}.kml"))):
        rid = re.match(r"L(.+)_D\d", os.path.basename(path)).group(1)
        parts, cur = [], []
        for el in ET.parse(path).getroot().iter(f"{ns}coordinates"):
            seg = [tuple(round(float(v), 5) for v in xy.split(",")[:2]) for xy in el.text.split()]
            if cur and seg and math.dist(cur[-1], seg[0]) > 3e-4:   # > ~30 m jump: new part
                parts.append(cur); cur = []
            for p in seg:
                if not cur or p != cur[-1]:
                    cur.append(p)
        if cur:
            parts.append(cur)
        out[rid] = [[[lat, lon] for lon, lat in _simplify(p, tol)] for p in parts if len(p) > 1]
    return out


def _records(df):
    return None if df is None else json.loads(df.to_json(orient="records"))


def build_html(F, routes, out_path, meta, status=None, route_to_line=None):
    """Write the dashboard. F: {"File_1.csv": DataFrame or None, ...}; meta: dict shown in the header and notes.

    routes: geometry from route_geometry(), keyed by EMT route code ("034"); route_to_line maps that code to
    File 2's line_id ("34") so the embedded File 2 stays exactly as saved.
    status: optional {"File_2.csv": "provisional", ...}; default "final" for present files, "pending" for missing."""
    status = dict(status or {})
    if route_to_line:
        routes = {route_to_line[k]: v for k, v in routes.items() if k in route_to_line}
    f2 = F.get("File_2.csv")
    if f2 is not None:
        routes = {k: v for k, v in routes.items() if k in set(f2.line_id.astype(str))}
    data = {"meta": meta, "routes": routes, "files": {}, "status": {}}
    for name in FILES:
        df = F.get(name)
        data["files"][name] = _records(df)
        data["status"][name] = status.get(name, "final" if df is not None else "pending")
    html = open(TEMPLATE, encoding="utf-8").read()
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = html.replace("/*__DATA__*/null", payload)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return out_path

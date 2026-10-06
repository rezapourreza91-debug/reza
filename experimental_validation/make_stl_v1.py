# -*- coding: utf-8 -*-
"""make_stl_v1.py - write the experimental-validation STL files (numpy + matplotlib only).

Geometry: geometry_33cell_from_drawing.json, derived from reentrant-dim.pdf (the project's
true-scale vector drawing of the 64.5 x 49.125 mm frame) by derive_geometry_from_pdf.py.
Checks against the FE volumes (conventions_v4.md): filler cell 42.76 mm2 vs FE 42.75 (+0.03 %),
empty frame 1455.8 mm2 vs FE 1425.7 (+2.1 %, NOT resolved - decks are on Z:\\33cell).

Printed specimen = frame + filled cells, extruded 25 mm. XY = lattice plane (print flat),
Z = 25 mm depth, Y = loading direction. Pattern string = c1..c33, c1 top-left, row by row.

Run:  python make_stl_v1.py          (from this folder)
"""
import json, struct, hashlib, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
G = json.load(open(os.path.join(HERE, "geometry_33cell_from_drawing.json")))
V = np.array(G["V"], float)
DEPTH = 25.0
RHO = 1.04e-3  # g/mm3, the FE density

SPECIMENS = {
    "P1_1097":        "000100000110000111000011000010100",
    "P2_1104":        "110001010000001000001000101100100",
    "P3_1016":        "100010001000100010001000100011010",
    "P4_1093":        "000000000000000000000111001111111",
    "P5_BLIND_GP01":  "000110000011000001100001010001001",
    "X1_empty_frame": "0" * 33,
}


def prism(V2, tris, h):
    """Extrude a CCW-triangulated planar region (conforming triangles) to height h."""
    tris = [list(t) for t in tris]
    faces = []
    for a, b, c in tris:                       # caps
        faces.append(((V2[a], 0.0), (V2[c], 0.0), (V2[b], 0.0)))      # bottom, normal -z
        faces.append(((V2[a], h), (V2[b], h), (V2[c], h)))            # top, normal +z
    count = {}
    for a, b, c in tris:                       # boundary = directed edges with no twin
        for e in ((a, b), (b, c), (c, a)):
            count[e] = count.get(e, 0) + 1
    for (a, b) in list(count):
        if (b, a) in count:
            continue
        pa, pb = V2[a], V2[b]                  # CCW region -> outward wall normal
        faces.append(((pa, 0.0), (pb, 0.0), (pb, h)))
        faces.append(((pa, 0.0), (pb, h), (pa, h)))
    return faces


def dogbone_1BA():
    """ISO 527-2 type 1BA: overall 75, ends 10 wide, gauge 5 wide x 30 parallel, l2 = 58, h = 2.
    The 14 mm transitions are circular arcs tangent to the gauge; r = 40.45 mm (ISO: r >= 30)."""
    b1, b2, l1, l2, l3, h = 5.0, 10.0, 30.0, 58.0, 75.0, 2.0
    dw, L = (b2 - b1) / 2, (l2 - l1) / 2
    r = (L ** 2 + dw ** 2) / (2 * dw)
    t = np.linspace(0, 1, 40)
    xs = l1 / 2 + L * t
    ys = b1 / 2 + (r - np.sqrt(np.maximum(r ** 2 - (L * t) ** 2, 0)))
    st = [(-l3 / 2, b2 / 2)] + [(-x, y) for x, y in zip(xs[::-1], ys[::-1])] + \
         [(x, y) for x, y in zip(xs, ys)] + [(l3 / 2, b2 / 2)]
    pts, tris = [], []
    for x, y in st:                            # stations: (x, +y) and (x, -y)
        pts += [(x, -y), (x, y)]
    for i in range(len(st) - 1):               # one trapezoid per station pair, CCW
        a, b, c, d = 2 * i, 2 * i + 2, 2 * i + 3, 2 * i + 1
        tris += [[a, b, c], [a, c, d]]
    return np.array(pts), tris, h


def check_and_volume(faces):
    edges = {}
    vol = 0.0
    for f in faces:
        p = [np.array([q[0][0], q[0][1], q[1]]) for q in f]
        vol += np.dot(p[0], np.cross(p[1], p[2])) / 6.0
        k = [tuple(np.round(x, 6)) for x in p]
        for e in ((k[0], k[1]), (k[1], k[2]), (k[2], k[0])):
            edges[e] = edges.get(e, 0) + 1
    closed = all(edges.get((b, a), 0) == n for (a, b), n in edges.items())
    return vol, closed


def write_stl(path, faces, name):
    with open(path, "wb") as fh:
        fh.write(name.encode()[:80].ljust(80, b" "))
        fh.write(struct.pack("<I", len(faces)))
        for f in faces:
            p = [np.array([q[0][0], q[0][1], q[1]]) for q in f]
            n = np.cross(p[1] - p[0], p[2] - p[0]); n = n / (np.linalg.norm(n) or 1)
            fh.write(struct.pack("<12fH", *n, *p[0], *p[1], *p[2], 0))


def main():
    out = os.path.join(HERE, "STL"); os.makedirs(out, exist_ok=True)
    manifest = {}
    jobs = {k: (V, G["FT"] + [t for i, ts in enumerate(G["CT"]) if p[i] == "1" for t in ts], DEPTH)
            for k, p in SPECIMENS.items()}
    jobs["T1_tensile_ISO527-2_1BA"] = dogbone_1BA()
    sq = np.array([[-6.35, -6.35], [6.35, -6.35], [6.35, 6.35], [-6.35, 6.35]])
    jobs["T2_compression_ASTM-D695_prism"] = (sq, [[0, 1, 2], [0, 2, 3]], 25.4)
    for name, (V2, tris, h) in jobs.items():
        faces = prism(V2, tris, h)
        vol, closed = check_and_volume(faces)
        path = os.path.join(out, name + ".stl")
        write_stl(path, faces, name)
        manifest[name] = dict(file="STL/%s.stl" % name, pattern=SPECIMENS.get(name), triangles=len(faces),
                              closed_manifold=closed, volume_mm3=round(vol, 1),
                              target_mass_g=round(vol * RHO, 2),
                              sha256=hashlib.sha256(open(path, "rb").read()).hexdigest())
        print("%-32s closed=%s  tris=%5d  vol=%9.1f mm3  mass=%6.2f g" % (name, closed, len(faces), vol, vol * RHO))
    json.dump(manifest, open(os.path.join(HERE, "stl_manifest.json"), "w"), indent=1)
    preview()


def preview():
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    lab = {"P1_1097": "P1  run 1097  FE EA 214.6 J  (best, knee)",
           "P2_1104": "P2  run 1104  FE EA 159.6 J  (one vertical chain, peak)",
           "P3_1016": "P3  run 1016  FE EA 114.3 J  (dispersed, peak)",
           "P4_1093": "P4  run 1093  FE EA 62.4 J  (bottom band, worst)\nupside down = run 1094 (FE 77.9 J)",
           "P5_BLIND_GP01": "P5  BLIND GP01  never simulated\nGP predicts EA 190 +/- 13 J",
           "X1_empty_frame": "X1  empty frame (optional)"}
    fig, axs = plt.subplots(2, 3, figsize=(15, 8.6))
    for ax, (n, p) in zip(axs.ravel(), SPECIMENS.items()):
        ax.add_collection(PolyCollection([V[t] for t in G["FT"]], facecolor="#9aa3ad", edgecolor="#9aa3ad", lw=0.3))
        for i, ts in enumerate(G["CT"]):
            if p[i] == "1":
                col = "#b4342a" if n.startswith("P5") else "#1f7a3a"
                ax.add_collection(PolyCollection([V[t] for t in ts], facecolor=col, edgecolor=col, lw=0.3))
            c = V[G["CO"][i]].mean(0)
            ax.text(c[0], c[1], str(i + 1), ha="center", va="center", fontsize=6.5, color="white" if p[i] == "1" else "#555")
        ax.annotate("", xy=(66.5, 30), xytext=(66.5, 44), arrowprops=dict(arrowstyle="->"))
        ax.set_xlim(-1, 68); ax.set_ylim(-1, 50.5); ax.set_aspect("equal"); ax.axis("off"); ax.set_title(lab[n], fontsize=9.5)
    fig.suptitle("Experimental-validation set: 64.5 x 49.125 x 25 mm, 10 of 33 cells filled; load along the vertical axis; numbers = c1..c33", fontsize=11)
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "patterns_preview.png"), dpi=150)


if __name__ == "__main__":
    main()

"""Choix rural / urbain pour AERMOD selon la méthode d'Auer (guide EPA, Appendix W).

Occupation du sol Corine Land Cover 2018 (WFS Géoplateforme) dans un cercle de 3 km autour de
la cheminée. Règle : option urbaine si les types urbains d'Auer (I1, I2, C1, R2, R3) couvrent plus
de 50 % du cercle. Correspondance Corine → Auer (jugement, documenté) :
  111 tissu urbain continu, 121 zones industrielles ou commerciales, 122 réseaux routiers et
  ferroviaires, 123 zones portuaires → urbain ;
  112 tissu urbain discontinu → ambigu (habitat individuel peu dense = R1, rural chez Auer) :
  on donne le résultat avec et sans cette classe.
"""

import json
from collections import defaultdict
from pathlib import Path

from shapely.geometry import Point, shape

PROJET = Path(__file__).resolve().parent.parent
SOURCE = PROJET / "donnees" / "occupation_sol" / "clc18.json"
CHEMINEE = (576601.2, 5453845.2)
RAYON = 3000.0
URBAIN_SUR = {"111", "121", "122", "123"}
AMBIGU = {"112"}
NOMS = {"111": "Tissu urbain continu", "112": "Tissu urbain discontinu",
        "121": "Zones industrielles ou commerciales", "122": "Réseaux routiers et ferroviaires",
        "124": "Aéroports", "133": "Chantiers", "141": "Espaces verts urbains",
        "142": "Équipements sportifs et de loisirs", "211": "Terres arables",
        "221": "Vignobles", "231": "Prairies", "242": "Systèmes culturaux complexes",
        "311": "Forêts de feuillus", "324": "Forêt et végétation arbustive en mutation"}

if __name__ == "__main__":
    cercle = Point(CHEMINEE).buffer(RAYON, quad_segs=64)
    surfaces = defaultdict(float)
    for entite in json.loads(SOURCE.read_text())["features"]:
        code = entite["properties"]["code_18"]
        surfaces[code] += shape(entite["geometry"]).intersection(cercle).area
    total = cercle.area
    print(f"Cercle de {RAYON / 1000:.0f} km : {total / 1e6:.2f} km², couvert à {100 * sum(surfaces.values()) / total:.1f} %\n")
    for code, s in sorted(surfaces.items(), key=lambda t: -t[1]):
        if s > 0:
            print(f"  {code} {NOMS.get(code, '?'):42s} {100 * s / total:5.1f} %")
    sur = sum(surfaces[c] for c in URBAIN_SUR) / total
    amb = sum(surfaces[c] for c in AMBIGU) / total
    print(f"\nUrbain certain (111, 121, 122, 123) : {100 * sur:.1f} %")
    print(f"Urbain si on compte aussi 112       : {100 * (sur + amb):.1f} %")
    print("Seuil d'Auer : 50 %")

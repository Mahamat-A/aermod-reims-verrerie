"""Établissements sensibles (BD TOPO, zones d'activité ou d'intérêt) dans un rayon de 4 km de la cheminée.

Sensibles au sens du guide INERIS : enseignement (écoles, collèges, lycées), santé (hôpitaux,
maisons de retraite), accueil de personnes handicapées. Un point par établissement (point intérieur
du polygone), écrit en CSV pour AERMAP, AERMOD et PostGIS.
"""

import csv
import json
import math
from pathlib import Path

from shapely.geometry import shape

PROJET = Path(__file__).resolve().parent.parent
SOURCE = PROJET / "donnees" / "sensibles" / "zai.json"
SORTIE = PROJET / "donnees" / "sensibles" / "etablissements_sensibles.csv"
CHEMINEE = (576601.2, 5453845.2)
RAYON = 4000.0
NATURES = {"Enseignement primaire": "école", "Collège": "collège", "Lycée": "lycée",
           "Hôpital": "hôpital", "Etablissement hospitalier": "hôpital",
           "Maison de retraite": "maison de retraite",
           "Structure d'accueil pour personnes handicapées": "accueil handicap"}

if __name__ == "__main__":
    lignes = []
    for entite in json.loads(SOURCE.read_text())["features"]:
        p = entite["properties"]
        if p.get("nature") not in NATURES or entite["geometry"] is None:
            continue
        point = shape(entite["geometry"]).representative_point()
        distance = math.hypot(point.x - CHEMINEE[0], point.y - CHEMINEE[1])
        if distance <= RAYON:
            lignes.append({"id": f"S{len(lignes) + 1:03d}", "type": NATURES[p["nature"]],
                           "nom": p.get("toponyme") or "", "x": round(point.x, 1), "y": round(point.y, 1),
                           "distance_m": round(distance)})
    with SORTIE.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(lignes[0]))
        w.writeheader()
        w.writerows(lignes)
    from collections import Counter
    print(f"{len(lignes)} établissements sensibles à moins de {RAYON / 1000:.0f} km :", dict(Counter(l['type'] for l in lignes)))
    print("le plus proche :", min(lignes, key=lambda l: l["distance_m"]))

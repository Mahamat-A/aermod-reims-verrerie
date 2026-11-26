"""Écrit l'entrée BPIPPRM (effet de sillage des bâtiments) à partir de la BD TOPO de l'IGN.

Bâtiments : donnees/batiments/bati.json (WFS Géoplateforme, BDTOPO_V3:batiment, UTM 31N),
un bâtiment BPIP par polygone (sans les trous), un seul étage (tier), hauteur = champ « hauteur »,
base = « altitude_minimale_sol ». On garde ceux à moins de RAYON m des cheminées et d'au moins
HAUTEUR_MIN m : au-delà, BPIPPRM les ignorerait (influence limitée à 5 L du bâtiment).
"""

import json
import math
from pathlib import Path

PROJET = Path(__file__).resolve().parent.parent
SOURCE = PROJET / "donnees" / "batiments" / "bati.json"
SORTIE = PROJET / "aermod" / "batiments" / "bpip.inp"
CHEMINEES = {"CHEM1": (576601.2, 5453845.2, 86.17), "CHEM1B": (576566.2, 5453873.1, 86.47)}
HAUTEUR_CHEMINEE = 59.0
RAYON = 600.0
HAUTEUR_MIN = 3.0


def polygones(chemin):
    """(nom, base, hauteur, sommets) pour chaque polygone extérieur retenu."""
    entites = json.loads(chemin.read_text())["features"]
    for k, entite in enumerate(entites):
        p, g = entite["properties"], entite["geometry"]
        if not p.get("hauteur") or p["hauteur"] < HAUTEUR_MIN or p.get("altitude_minimale_sol") is None:
            continue
        parties = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for n, partie in enumerate(parties):
            sommets = [(x, y) for x, y, *_ in partie[0]]
            if sommets[0] == sommets[-1]:
                sommets = sommets[:-1]
            distance = min(math.hypot(x - cx, y - cy) for x, y in sommets for cx, cy, _ in CHEMINEES.values())
            if distance <= RAYON and len(sommets) >= 3:
                yield f"B{k:04d}_{n}", p["altitude_minimale_sol"], p["hauteur"], sommets


def ecrire(chemin, batiments):
    lignes = ["'O-I Reims - batiments BD TOPO IGN autour de la cheminee'",
              "'P'", "'METERS' 1.0", "'UTMN' 0.0", str(len(batiments))]
    for nom, base, hauteur, sommets in batiments:
        lignes.append(f"'{nom}' 1 {base:.2f}")
        lignes.append(f"{len(sommets)} {hauteur:.2f}")
        lignes += [f" {x:.2f} {y:.2f}" for x, y in sommets]
    lignes.append(str(len(CHEMINEES)))
    for nom, (x, y, base) in CHEMINEES.items():
        lignes.append(f"'{nom}' {base:.2f} {HAUTEUR_CHEMINEE:.2f} {x:.2f} {y:.2f}")
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text("\n".join(lignes) + "\n")


if __name__ == "__main__":
    batiments = list(polygones(SOURCE))
    ecrire(SORTIE, batiments)
    plus_haut = max(batiments, key=lambda b: b[2])
    print(f"{len(batiments)} bâtiments retenus (≥ {HAUTEUR_MIN:g} m, à moins de {RAYON:g} m) ; "
          f"le plus haut : {plus_haut[2]:.1f} m")
    print(f"Écrit : {SORTIE}")

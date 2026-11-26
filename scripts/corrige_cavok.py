"""Écrit une copie ISD avec une couche à 0 octa pour les METAR ciblés."""

import re
from pathlib import Path
from tempfile import NamedTemporaryFile

PROJET = Path(__file__).resolve().parent.parent
NOM_ISD = "070720-99999-2024"
SOURCE = PROJET / "donnees" / "meteo_brute" / NOM_ISD
SORTIE = PROJET / "donnees" / "meteo_corrigee" / f"{NOM_ISD}_cavok"
GA1_CIEL_CLAIR = b"GA1001+999999999"
CODES_CIEL_CLAIR = re.compile(rb"\b(?:CAVOK|NSC|NCD)\b")


def corriger_ligne(ligne):
    """Insère le GA1 synthétique uniquement dans un METAR admissible."""
    if ligne[41:46] != b"FM-15":
        return ligne
    debut_rem = ligne.find(b"REM", 105)
    if debut_rem < 0 or not CODES_CIEL_CLAIR.search(ligne, debut_rem + 3):
        return ligne
    debut_add = ligne.find(b"ADD", 105, debut_rem)
    if debut_add < 0:
        return ligne
    insertion = debut_add + 3
    if b"GA1" in ligne[insertion:debut_rem]:
        return ligne

    compteur = int(ligne[:4]) + len(GA1_CIEL_CLAIR)
    if compteur > 9999:
        raise ValueError("Le compteur corrigé dépasse quatre chiffres.")
    return (
        f"{compteur:04d}".encode("ascii")
        + ligne[4:insertion]
        + GA1_CIEL_CLAIR
        + ligne[insertion:]
    )


def verifier_longueurs(chemin):
    with chemin.open("rb") as fichier:
        for numero, ligne in enumerate(fichier, 1):
            contenu = ligne.rstrip(b"\r\n")
            compteur = contenu[:4]
            if (
                len(contenu) < 105
                or not compteur.isdigit()
                or int(compteur) != len(contenu) - 105
            ):
                raise ValueError(f"Ligne {numero} : compteur ISD incohérent.")


def corriger_fichier(source, sortie):
    sortie.parent.mkdir(parents=True, exist_ok=True)
    modifiees = 0
    with source.open("rb") as original:
        temporaire = NamedTemporaryFile(dir=sortie.parent, delete=False)
        chemin_temporaire = Path(temporaire.name)
        try:
            with temporaire:
                for ligne in original:
                    corrigee = corriger_ligne(ligne)
                    temporaire.write(corrigee)
                    modifiees += corrigee != ligne
            verifier_longueurs(chemin_temporaire)
            chemin_temporaire.replace(sortie)
        finally:
            chemin_temporaire.unlink(missing_ok=True)
    return modifiees


if __name__ == "__main__":
    try:
        total = corriger_fichier(SOURCE, SORTIE)
    except (OSError, ValueError) as erreur:
        raise SystemExit(str(erreur))
    print(f"Lignes modifiées : {total}")
    print(f"Compteurs vérifiés sur toutes les lignes : {SORTIE}")

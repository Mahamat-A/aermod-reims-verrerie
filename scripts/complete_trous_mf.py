"""Comble les heures absentes du fichier ISD avec la base horaire Météo-France.

Les heures absentes de la NOAA (28-31/03 et 18-20/11/2024) existent dans la
base horaire Météo-France de Reims-Prunay (poste 51449002). Sur les heures
communes, les températures des deux sources sont identiques : on fabrique
donc, pour chaque heure absente, une ligne SYNOP (FM-12) au format ISD.
"""

import csv
import gzip
from pathlib import Path
from tempfile import NamedTemporaryFile

PROJET = Path(__file__).resolve().parent.parent
NOM_ISD = "070720-99999-2024"
SOURCE_ISD = PROJET / "donnees" / "meteo_corrigee" / f"{NOM_ISD}_cavok"
SOURCE_MF = PROJET / "donnees" / "meteo_brute" / "H_51_2020-2024.csv.gz"
SORTIE = PROJET / "donnees" / "meteo_corrigee" / f"{NOM_ISD}_complet"
POSTE_MF = "51449002"
ANNEE = "2024"
# En-tête de contrôle repris des SYNOP NOAA de la station (positions 5 à 60).
CONTROLE = "07072099999{date}{heure}4+49217+004150FM-12+009699999V020"


def valeur(texte):
    """Renvoie un nombre, ou None si la case Météo-France est vide."""
    texte = texte.strip()
    return float(texte) if texte else None


def champ(nombre, largeur, facteur=1, signe=False, manquant=None):
    """Écrit un nombre ISD entier sur une largeur fixe (valeur × facteur).

    Avec signe, la largeur compte le signe : -0.8 °C sur 5 caractères donne -0008.
    """
    if nombre is None:
        return manquant
    entier = round(nombre * facteur)
    return f"{entier:+0{largeur}d}" if signe else f"{entier:0{largeur}d}"


def ligne_isd(heure_mf, mesures):
    """Construit une ligne ISD FM-12 à partir d'une heure Météo-France."""
    date, heure = heure_mf[:8], heure_mf[8:10] + "00"
    vitesse, direction = mesures["FF"], mesures["DD"]
    calme = vitesse == 0
    if calme:
        vent = "999" + "1" + "C" + "0000" + "1"
    else:
        vent = (
            champ(direction, 3, manquant="999") + "1" + "N"
            + champ(vitesse, 4, 10, manquant="9999") + "1"
        )
    obligatoire = (
        vent
        + "99999" + "9" + "9" + "N"          # plafond inconnu
        + "999999" + "9" + "9" + "9"         # visibilité inconnue
        + champ(mesures["T"], 5, 10, True, "+9999") + "1"
        + champ(mesures["TD"], 5, 10, True, "+9999") + "1"
        + champ(mesures["PMER"], 5, 10, manquant="99999") + "1"
    )
    nebulosite = mesures["N"]
    groupes = "ADD"
    if nebulosite is not None and 0 <= nebulosite <= 8:
        # GF1 : couverture totale en octas, le reste inconnu (23 caractères).
        groupes += "GF1" + f"{int(nebulosite):02d}" + "991999999999999999999"
    if mesures["PSTAT"] is not None:
        groupes += "MA1" + "99999" + "9" + champ(mesures["PSTAT"], 5, 10) + "1"
    variable = groupes + "REMSYNMF Meteo-France 51449002"
    ligne = CONTROLE.format(date=date, heure=heure) + obligatoire + variable
    return f"{len(variable):04d}" + ligne


def lire_meteo_france(chemin):
    """Renvoie {AAAAMMJJHH: mesures} pour le poste et l'année voulus."""
    heures = {}
    with gzip.open(chemin, "rt", encoding="utf-8") as fichier:
        lecteur = csv.reader(fichier, delimiter=";")
        entete = next(lecteur)
        index = {nom: entete.index(nom) for nom in ("FF", "DD", "T", "TD", "PMER", "PSTAT", "N")}
        for ligne in lecteur:
            if ligne[0] == POSTE_MF and ligne[5].startswith(ANNEE):
                heures[ligne[5]] = {nom: valeur(ligne[i]) for nom, i in index.items()}
    return heures


def heures_isd(chemin):
    """Heures (AAAAMMJJHH) déjà présentes, tous messages confondus, à hh:00."""
    with chemin.open() as fichier:
        return {ligne[15:25] for ligne in fichier if ligne[25:27] == "00"}


def verifier_longueurs(chemin):
    with chemin.open() as fichier:
        for numero, ligne in enumerate(fichier, 1):
            contenu = ligne.rstrip("\r\n")
            if int(contenu[:4]) != len(contenu) - 105:
                raise ValueError(f"Ligne {numero} : compteur ISD incohérent.")


def completer(source, sortie, meteo_france):
    presentes = heures_isd(source)
    ajouts = {
        heure: ligne_isd(heure, mesures)
        for heure, mesures in meteo_france.items()
        if heure not in presentes and mesures["FF"] is not None and mesures["T"] is not None
    }
    with source.open() as fichier:
        lignes = [ligne.rstrip("\r\n") for ligne in fichier]
    # Tri chronologique (date et heure en positions 16 à 27), comme le fichier NOAA.
    lignes = sorted(lignes + list(ajouts.values()), key=lambda ligne: ligne[15:27])
    temporaire = NamedTemporaryFile("w", dir=sortie.parent, delete=False)
    chemin_temporaire = Path(temporaire.name)
    try:
        with temporaire:
            temporaire.write("\n".join(lignes) + "\n")
        verifier_longueurs(chemin_temporaire)
        chemin_temporaire.replace(sortie)
    finally:
        chemin_temporaire.unlink(missing_ok=True)
    return sorted(ajouts)


if __name__ == "__main__":
    try:
        ajoutees = completer(SOURCE_ISD, SORTIE, lire_meteo_france(SOURCE_MF))
    except (OSError, ValueError) as erreur:
        raise SystemExit(str(erreur))
    print(f"Heures ajoutées depuis Météo-France : {len(ajoutees)}")
    if ajoutees:
        print(f"Première : {ajoutees[0]}  Dernière : {ajoutees[-1]}")
    print(f"Fichier écrit et compteurs vérifiés : {SORTIE}")

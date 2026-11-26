"""Contrôle de la couverture horaire des SYNOP de Reims-Prunay en 2024."""

from datetime import datetime
from pathlib import Path
import re

FICHIER_ISD = (
    Path(__file__).resolve().parent.parent
    / "donnees" / "meteo_brute" / "070720-99999-2024"
)
HEURES_ATTENDUES = (2184, 2184, 2208, 2208)
# Approximation pour la ville de Reims : absence de nuages significatifs.
# Des cirrus peuvent être présents et l'effet radiatif du ciel peut être sous-estimé.
OCTAS_SANS_NUAGES_SIGNIFICATIFS = 0
COUCHES_METAR = re.compile(r"GA[1-6](0[0-8])")
CIEL_SANS_NUAGES_SIGNIFICATIFS = re.compile(r"\b(?:CAVOK|NSC|NCD)\b")


def lire_nombre(texte, code_manquant, diviseur=1):
    """Renvoie None pour un champ manquant ou illisible."""
    if texte == code_manquant:
        return None
    try:
        return int(texte) / diviseur
    except ValueError:
        return None


def controler(chemin):
    heures = {}
    nuages_metar = {}

    with chemin.open(encoding="ascii") as fichier:
        for ligne in fichier:
            type_message = ligne[41:46]
            if type_message not in ("FM-12", "FM-15"):
                continue
            try:
                date_utc = datetime.strptime(ligne[15:27], "%Y%m%d%H%M")
            except ValueError:
                continue
            if date_utc.year != 2024:
                continue

            heure = date_utc.replace(minute=0)
            # Les groupes additionnels commencent après les 105 caractères fixes.
            debut_add = ligne.find("ADD", 105)
            debut_rem = ligne.find("REM", max(105, debut_add + 3))
            fin_add = debut_rem if debut_rem >= 0 else len(ligne)
            groupes = ligne[debut_add + 3:fin_add] if debut_add >= 0 else ""

            if type_message == "FM-15":
                if date_utc.minute != 0:
                    continue
                couches = COUCHES_METAR.findall(groupes)
                if couches:
                    couverture = max(map(int, couches))
                    precedente = nuages_metar.get(heure)
                    if precedente is None or precedente[0] is False or couverture > precedente[1]:
                        nuages_metar[heure] = (True, couverture)
                elif debut_rem >= 0 and CIEL_SANS_NUAGES_SIGNIFICATIFS.search(ligne[debut_rem:]):
                    nuages_metar.setdefault(heure, (False, OCTAS_SANS_NUAGES_SIGNIFICATIFS))
                continue

            direction = lire_nombre(ligne[60:63], "999")
            vitesse = lire_nombre(ligne[65:69], "9999", 10)
            temperature = lire_nombre(ligne[87:92], "+9999", 10)
            position_gf1 = groupes.find("GF1")
            nebulosite = None
            if position_gf1 >= 0:
                nebulosite = lire_nombre(groupes[position_gf1 + 3:position_gf1 + 5], "99")

            valides = heures.setdefault(heure, {})
            calme = ligne[64] == "C" and vitesse == 0
            vent_mesure = direction is not None and 0 <= direction <= 360 and vitesse is not None
            if calme or vent_mesure:
                valides["vent"] = vitesse
            if temperature is not None:
                valides["temperature"] = temperature
            if nebulosite is not None and 0 <= nebulosite <= 8:
                valides["nebulosite"] = nebulosite

    for heure, valides in heures.items():
        if "nebulosite" in valides:
            valides["nuages_completes"] = valides["nebulosite"]
        elif heure in nuages_metar:
            valides["nuages_completes"] = nuages_metar[heure][1]
    return heures


def afficher_bilan(heures):
    print("Couverture SYNOP 2024 (UTC, pourcentages sur toutes les heures du trimestre)")
    print(
        f"{'Trim.':<6} {'Heures présentes':>17} {'Vent':>9} {'Temp.':>9} "
        f"{'Nuages':>9} {'Nuages complétés':>17}"
    )
    for trimestre, attendues in enumerate(HEURES_ATTENDUES, start=1):
        donnees = [
            valides for heure, valides in heures.items()
            if (heure.month - 1) // 3 + 1 == trimestre
        ]
        pourcentages = [
            100 * sum(champ in valides for valides in donnees) / attendues
            for champ in ("vent", "temperature", "nebulosite", "nuages_completes")
        ]
        vent, temperature, nebulosite, nuages_completes = pourcentages
        presence = f"{len(donnees)}/{attendues}"
        print(
            f"T{trimestre:<5} {presence:>17} {vent:8.2f}% {temperature:8.2f}% "
            f"{nebulosite:8.2f}% {nuages_completes:16.2f}%"
        )


if __name__ == "__main__":
    try:
        afficher_bilan(controler(FICHIER_ISD))
    except FileNotFoundError:
        raise SystemExit(f"Fichier ISD introuvable : {FICHIER_ISD}")

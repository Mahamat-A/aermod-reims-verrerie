"""Langue des figures : français par défaut, anglais avec l'option --en (fichiers suffixés _en.png).

t(texte) renvoie la traduction anglaise d'un texte de figure (erreur si elle manque, pour ne rien laisser en
français) ; nombre(s) met la virgule décimale en français ; fichier(nom) ajoute _en au nom de la figure.
"""
import sys

EN = "--en" in sys.argv

TRADUCTIONS = {
    # stations
    "Jean d'Aulan\n(fond urbain)": "Jean d'Aulan\n(urban background)",
    "Doumer\n(trafic)": "Doumer\n(traffic)",
    "Bétheny\n(fond périurbain)": "Bétheny\n(suburban background)",
    "Jean d'Aulan (fond urbain)": "Jean d'Aulan (urban background)",
    "Doumer (trafic)": "Doumer (traffic)",
    "Bétheny (fond périurbain)": "Bétheny (suburban background)",
    "Bétheny (périurbain)": "Bétheny (suburban)",
    # cartes annuelles (carte_aermod.py)
    "option urbaine (182 000 hab. ; densité ~3 000 hab/km² dans un rayon de 3 km)":
        "urban option (182,000 inhabitants; density ~3,000 inhabitants/km² within 3 km)",
    "option rurale (méthode d'Auer : 24 % de sols urbains dans un rayon de 3 km)":
        "rural option (Auer method: 24 % urban land within 3 km)",
    "AERMOD 26135 – météo Reims-Prunay 2024 (AERMET, radiosondages Trappes / Idar-Oberstein) – "
    "relief IGN RGE ALTI 25 m\n"
    "Source : cheminée 59 m, 523 K, 8 m/s, Ø 2,51 m ; 143 t NOx en 2024 (IREP), modulées par mois "
    "(arrêt du four 3 le 12/07)\n"
    "Sillage des bâtiments : BPIPPRM, BD TOPO IGN ; {option}\n"
    "NO₂ ≈ 0,9 × NOx (OLM, ozone en excès). Fond : Plan IGN (Géoplateforme)":
        "AERMOD 26135 – Reims-Prunay 2024 meteorology (AERMET, Trappes / Idar-Oberstein soundings) – "
        "IGN RGE ALTI 25 m terrain\n"
        "Source: 59 m stack, 523 K, 8 m/s, Ø 2.51 m; 143 t NOx in 2024 (IREP), modulated by month "
        "(furnace 3 shut down on 12 July)\n"
        "Building downwash: BPIPPRM, IGN BD TOPO; {option}\n"
        "NO₂ ≈ 0.9 × NOx (OLM, ozone in excess). Background: Plan IGN (Géoplateforme)",
    "Verrerie O-I\n(cheminée 59 m)": "O-I glass plant\n(59 m stack)",
    "NOx (éq. NO₂) – contribution de la verrerie O-I – moyenne annuelle 2024 – option {option}":
        "NOx (as NO₂) – contribution of the O-I glass plant – 2024 annual mean – {option} option",
    "NOx (éq. NO₂) – contribution de la verrerie O-I – maximum horaire 2024 – option {option}":
        "NOx (as NO₂) – contribution of the O-I glass plant – 2024 maximum hourly value – {option} option",
    "urbaine": "urban",
    "rurale": "rural",
    # cartes mensuelles (carte_mois.py)
    "Prunay (référence), option rurale": "Prunay (reference), rural option",
    "Prunay, option urbaine": "Prunay, urban option",
    "WRF 1 km, z0 0,25 m, option rurale": "WRF 1 km, z0 0.25 m, rural option",
    "WRF 1 km, z0 0,25 m, option urbaine": "WRF 1 km, z0 0.25 m, urban option",
    "janvier": "January",
    "juillet": "July",
    "0,03 m en hiver": "0.03 m in winter",
    "0,15 m en été": "0.15 m in summer",
    "0,45": "0.45",
    "0,35": "0.35",
    ", four 3 arrêté le 12/07": ", furnace 3 shut down on 12 July",
    "AERMOD 26135, {nom} 2024 (744 h). Prunay : AERMET avec la surface autour du mât (z0 {z0}). "
    "WRF 4.7.1 (ERA5, 9/3/1 km) → MMIF 4.1.1 → AERMET, maille de la cheminée,\n"
    "z0 0,25 m estimé dans 1 km autour de la source, albédo 0,19, Bowen {bowen}. Cheminée 59 m, 523 K, 8 m/s, Ø 2,51 m ; "
    "NOx 2024 (IREP) modulés par mois{emis}.\nBâtiments BPIPPRM (BD TOPO), relief RGE ALTI 25 m. "
    "NO₂ ≈ 0,9 × NOx. Fond : Plan IGN (Géoplateforme).":
        "AERMOD 26135, {nom} 2024 (744 h). Prunay: AERMET with the surface around the mast (z0 {z0}). "
        "WRF 4.7.1 (ERA5, 9/3/1 km) → MMIF 4.1.1 → AERMET, stack grid cell,\n"
        "z0 0.25 m estimated within 1 km of the source, albedo 0.19, Bowen {bowen}. Stack 59 m, 523 K, 8 m/s, Ø 2.51 m; "
        "2024 NOx (IREP) modulated by month{emis}.\nBuildings BPIPPRM (BD TOPO), terrain RGE ALTI 25 m. "
        "NO₂ ≈ 0.9 × NOx. Background: Plan IGN (Géoplateforme).",
    "NOx (éq. NO₂) – contribution de la verrerie O-I – moyenne de {mois} 2024":
        "NOx (as NO₂) – contribution of the O-I glass plant – {mois} 2024 mean",
    "NOx (éq. NO₂) – contribution de la verrerie O-I – maximum horaire de {mois} 2024":
        "NOx (as NO₂) – contribution of the O-I glass plant – {mois} 2024 maximum hourly value",
    # secteurs de vent (figure_secteurs.py)
    "direction\nde l'usine": "direction\nof the plant",
    "Direction d'où vient le vent (°)": "Wind direction (blowing from, °)",
    "NO₂ mesuré (µg/m³)": "Measured NO₂ (µg/m³)",
    "Contribution modélisée\nde la verrerie, NO₂ (µg/m³)": "Modelled contribution\nof the plant, NO₂ (µg/m³)",
    "Reims 2024 – NO₂ moyen par secteur de vent de 10° (vent : Reims-Prunay) : "
    "mesures ATMO Grand Est et contribution AERMOD de la verrerie O-I":
        "Reims 2024 – mean NO₂ by 10° wind sector (wind: Reims-Prunay): "
        "ATMO Grand Est measurements and AERMOD contribution of the O-I glass plant",
    "Mesures : LCSQA/ATMO Grand Est, valeurs validées. Modèle : AERMOD 26135, OLM "
    "(ozone mesuré, NO₂/NOx à l'émission 0,10), option urbaine, bâtiments BPIPPRM. Échelles verticales différentes "
    "(facteur ~50).":
        "Measurements: LCSQA/ATMO Grand Est, validated values. Model: AERMOD 26135, OLM "
        "(measured ozone, in-stack NO₂/NOx 0.10), urban option, BPIPPRM buildings. Different vertical scales "
        "(factor ~50).",
    # expérience naturelle (experience_naturelle.py)
    "option urbaine": "urban option",
    "option rurale": "rural option",
    "mesures, corrigées de la tendance (± 1 écart type)": "measurements, detrended (± 1 standard deviation)",
    "pente prévue par AERMOD, {nom} — β mesuré = {beta:.2f} ± {beta_et:.2f}":
        "slope predicted by AERMOD, {nom} — measured β = {beta:.2f} ± {beta_et:.2f}",
    "Émissions de NOx d'O-I (t/an, IREP)": "O-I NOx emissions (t/yr, IREP)",
    "NO₂ : secteur usine − secteurs voisins (µg/m³)": "NO₂: plant sector − neighbouring sectors (µg/m³)",
    "Expérience naturelle 2013–2025 : le NO₂ par vent venant de l'usine suit-il ses émissions ? "
    "(β = 1 : modèle juste ; β = 0 : aucun effet)":
        "Natural experiment 2013–2025: does NO₂ with wind from the plant follow its emissions? "
        "(β = 1: model right; β = 0: no effect)",
    # relief (figure_relief.py)
    "Relief IGN (RGE ALTI, 25 m) et domaine des récepteurs (20 × 20 km)":
        "IGN terrain (RGE ALTI, 25 m) and receptor domain (20 × 20 km)",
    "Cheminée O-I": "O-I stack",
    "Est (km depuis la cheminée)": "East (km from the stack)",
    "Nord (km)": "North (km)",
    "Altitude (m)": "Elevation (m)",
}


def t(texte):
    return TRADUCTIONS[texte] if EN else texte


def nombre(s):
    return s if EN else s.replace(".", ",")


def fichier(nom):
    return nom.replace(".png", "_en.png") if EN else nom

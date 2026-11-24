import math
import re
import unicodedata

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px

from matplotlib import cm
from matplotlib.colors import Normalize


"""Fonds géographiques partagés pour les cartes par académie."""

# Contours officiels des académies, partagés par les deux cartes.
URL_CONTOURS = (
    "https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-contour-academies-2020/exports/geojson"
)

# Les noms changent selon les années : Caen + Rouen -> Normandie (2020), etc.
HARMONISATION = {
    "Caen": "Normandie", "Rouen": "Normandie",
    "Besancon": "Besançon",
    "Réunion": "La Réunion",
}


def normaliser(nom):
    """Normalise les libellés pour joindre les données aux contours."""
    nom = unicodedata.normalize("NFKD", str(nom)).encode("ascii", "ignore").decode()
    nom = nom.lower().strip()
    nom = re.sub(r"^academie (de la |de l'|de |d')", "", nom)
    nom = re.sub(r"^la ", "", nom)
    return re.sub(r"[^a-z]", "", nom)


def charger_base_academies():
    """Télécharge les contours des académies depuis data.education."""
    gdf = gpd.read_file(URL_CONTOURS)  #gdf est le tableau géographique créé par GeoPandas : il contient les informations sur les académies et leurs formes
    return gdf


def creer_base_geographique_academies(noms_academies):
    """Associe les contours data.education aux noms d'académie des données."""
    gdf = charger_base_academies().copy()
    if "name" not in gdf.columns:
        raise ValueError(
            "La couche data.education ne contient pas la colonne attendue 'name'."
        )

    correspondance = {
        normaliser(HARMONISATION.get(nom, nom)): HARMONISATION.get(nom, nom)
        for nom in noms_academies
    }
    gdf["academie"] = gdf["name"].map(normaliser).map(correspondance)
    gdf = gdf.dropna(subset=["academie"])
    return gdf.dissolve(by="academie").reset_index()[["academie", "geometry"]]


"""Carte de la mobilité inter-académique Parcoursup (2018-2025).

admis venus d'une autre académie = acc_tot - acc_aca_orig
"""

def creer_carte(base, dossier_sortie=".", col_aca="acad_mies", col_dep="dep"):
    """Calcule la part d'admis venant d'une autre académie et trace les cartes.

    Renvoie (agg, fig, fig2) : le tableau, la figure matplotlib et la figure plotly.
    """
    base = base.copy()                      # on ne modifie pas la base de l'appelant
    base["academie"] = base[col_aca].replace(HARMONISATION)

    # Indicateurs par académie et par année
    agg = (base.groupby(["session", "academie"], as_index=False)
               .agg(admis=("acc_tot", "sum"), meme_aca=("acc_aca_orig", "sum")))
    agg["entrants"] = agg["admis"] - agg["meme_aca"]
    agg["part_entrants"] = 100 * agg["entrants"] / agg["admis"]

    # fond de carte
    acad = creer_base_geographique_academies(agg["academie"].unique())

    # Cartes statiques : une par année, même échelle de couleurs
    annees = sorted(agg["session"].unique())
    vmin, vmax = agg["part_entrants"].min(), agg["part_entrants"].max()

    ncols = 4
    nrows = math.ceil(len(annees) / ncols)
    fig, axes = plt.subplots(nrows, ncols, figsize=(18, 5 * nrows))
    axes = axes.ravel()
    for ax, an in zip(axes, annees):
        d = acad.merge(agg[agg["session"] == an], on="academie", how="left")
        d.plot(column="part_entrants", cmap="YlOrRd", vmin=vmin, vmax=vmax,
               edgecolor="white", linewidth=0.4, ax=ax,
               missing_kwds={"color": "lightgrey"})
        ax.set_title(str(an), fontsize=14)
        ax.set_axis_off()
    for ax in axes[len(annees):]:
        ax.set_visible(False)

    sm = plt.cm.ScalarMappable(cmap="YlOrRd", norm=plt.Normalize(vmin, vmax))
    fig.colorbar(sm, ax=list(axes), shrink=0.6,
                 label="% d'admis venus d'une autre académie")
    fig.suptitle("Parcoursup : part des admis venant d'une autre académie", fontsize=16)
    plt.close(fig)        # évite l'affichage en double dans le notebook

    # Carte interactive animée (curseur sur les années)
    geo = acad.set_index("academie").__geo_interface__
    fig2 = px.choropleth(
        agg, geojson=geo, locations="academie", featureidkey="id",
        color="part_entrants", animation_frame="session",
        color_continuous_scale="YlOrRd", range_color=(vmin, vmax),
        hover_data={"entrants": ":,", "admis": ":,"},
        labels={"part_entrants": "% venus d'ailleurs"},
    )
    fig2.update_geos(fitbounds="locations", visible=False)
    
    return agg, fig, fig2

"""

Cartes de l'évolution du taux de poursuite des bacheliers dans le supérieur,
par académie, une carte par année (à partir de 2018).

"""

# Académies d'outre-mer : exclues de la carte (échelle incompatible avec la métropole)
ACADEMIES_DROM = ["Guadeloupe", "Guyane", "La Réunion", "Martinique", "Mayotte"]

def carte_poursuite(base, tab_taux, aca_lib="aca_lib", rentree_session="rentree_session"):
    """
    Trace une carte par année du taux de poursuite des bacheliers dans le supérieur,
    avec une échelle de couleur commune pour pouvoir comparer les années.

    Renvoie (fig, tableau) où tableau est le DataFrame des taux utilisés.
    """
    cmap = "YlOrRd"  # palette de couleurs
    # calcul de l'indicateur
    taux = tab_taux
    taux = taux.rename("taux").reset_index().rename(
        columns={aca_lib: "zone", rentree_session: "annee"}
    )
    taux = taux[~taux["zone"].isin(ACADEMIES_DROM)]
    gdf = creer_base_geographique_academies(taux["zone"].unique())
    gdf = gdf.assign(_cle=gdf["academie"].map(normaliser))
    taux = taux.assign(_cle=taux["zone"].map(normaliser))

    annees = sorted(taux["annee"].unique())

    # Zones du fond de carte sans données (DROM, etc.) : écartées
    gdf = gdf[gdf["_cle"].isin(taux["_cle"].unique())]
    manquantes = set(taux["_cle"]) - set(gdf["_cle"])
    if manquantes:
        print(f"Attention : zones sans contour : {sorted(manquantes)}")

    # Échelle commune à toutes les cartes
    norm = Normalize(vmin=taux["taux"].min(), vmax=taux["taux"].max())

    lignes = int(np.ceil(len(annees) / 4))
    fig, axes = plt.subplots(lignes, 4, figsize=(4.2 * 4, 4.4 * lignes))
    axes = np.atleast_1d(axes).ravel()

    for ax, annee in zip(axes, annees):
        data = gdf.merge(taux[taux["annee"] == annee][["_cle", "taux"]], on="_cle")
        data.plot(
            column="taux",
            cmap=cmap,
            norm=norm,
            edgecolor="white",
            linewidth=0.4,
            ax=ax,
        )
        ax.set_title(str(annee), fontsize=13, fontweight="bold")
        ax.set_axis_off()
    for ax in axes[len(annees):]:
        ax.set_axis_off()

    sm = cm.ScalarMappable(norm=norm, cmap=cmap)
    cbar = fig.colorbar(sm, ax=axes.tolist(), orientation="horizontal",
                        fraction=0.04, pad=0.03, shrink=0.6)
    cbar.set_label("Taux de poursuite dans le supérieur (%)")
    cbar.ax.xaxis.set_major_formatter(lambda x, _: f"{x:.1f}%")

    fig.suptitle(
        "Poursuite des bacheliers dans le supérieur, par académie",
        fontsize=15,
        y=0.99,
    )

    return fig
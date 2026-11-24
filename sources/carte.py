"""Carte de la mobilité inter-académique Parcoursup (2018-2025).

admis venus d'une autre académie = acc_tot - acc_aca_orig
"""
import io
import math

import geopandas as gpd
import matplotlib.pyplot as plt
import plotly.express as px
import requests

GEOJSON_DEP = ("https://raw.githubusercontent.com/gregoiredavid/"
               "france-geojson/master/departements-version-simplifiee.geojson")

# Les noms changent selon les années : Caen + Rouen -> Normandie (2020), etc.
HARMONISATION = {
    "Caen": "Normandie", "Rouen": "Normandie",
    "Besancon": "Besançon",
    "Réunion": "La Réunion",
}


def code_dep(s):
    """Met les codes département au format du GeoJSON ('075' -> '75', '1' -> '01')."""
    s = s.astype(str).str.strip().str.upper().str.replace(r"\.0$", "", regex=True)
    s = s.str.replace(r"^0(\d{2})$", r"\1", regex=True)
    return s.str.zfill(2)


def creer_carte(base, dossier_sortie=".", col_aca="acad_mies", col_dep="dep"):
    """Calcule la part d'admis venant d'une autre académie et trace les cartes.

    Renvoie (agg, fig, fig2) : le tableau, la figure matplotlib et la figure plotly.
    """
    base = base.copy()                      # on ne modifie pas la base de l'appelant
    base["academie"] = base[col_aca].replace(HARMONISATION)
    base["dep"] = code_dep(base[col_dep])

    # Indicateurs par académie et par année
    agg = (base.groupby(["session", "academie"], as_index=False)
               .agg(admis=("acc_tot", "sum"), meme_aca=("acc_aca_orig", "sum")))
    agg["entrants"] = agg["admis"] - agg["meme_aca"]
    agg["part_entrants"] = 100 * agg["entrants"] / agg["admis"]

    # Fond de carte : table département -> académie déduite de la base
    dep2aca = (base.dropna(subset=["dep"])
                   .groupby("dep")["academie"]
                   .agg(lambda s: s.mode().iloc[0])
                   .to_dict())
    dep2aca.update({"20": "Corse", "2A": "Corse", "2B": "Corse"})

    deps = gpd.read_file(io.BytesIO(requests.get(GEOJSON_DEP, timeout=30).content))
    deps["academie"] = deps["code"].map(dep2aca)
    deps = deps.dropna(subset=["academie"])
    acad = deps.dissolve(by="academie").reset_index()[["academie", "geometry"]]

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
    #fig2.write_html(f"{dossier_sortie}/mobilite_parcoursup_animation.html")

    return agg, fig, fig2
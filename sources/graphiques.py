import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import PercentFormatter


def courbes(tableau, titre, axe_y, source, annee_reperee=None, texte_repere=None, depuis_zero=True):
    """Trace une courbe par colonne d'un tableau dont l'index contient les années.

    tableau : DataFrame avec une ligne par année et une colonne par série
              (par exemple le résultat d'un .unstack()).
    titre, axe_y : titre du graphique et nom de l'axe vertical.
    source : texte affiché sous le graphique (d'où viennent les données).
    annee_reperee : si on la donne, trace une ligne verticale en pointillés à cette
                    année (par exemple 2018 pour l'arrivée de Parcoursup), avec texte_repere.
    depuis_zero : l'axe vertical commence à 0 (à garder pour des pourcentages, pour ne pas
                  exagérer les écarts ; à mettre à False pour un rapport proche de 1).
    Renvoie la figure, pour pouvoir l'enregistrer si besoin (fig.savefig(...)).
    """
    fig, ax = plt.subplots(figsize=(9, 5))

    for colonne in tableau.columns:
        ax.plot(tableau.index, tableau[colonne], marker="o", label=str(colonne))

    if depuis_zero:
        ax.set_ylim(bottom=0)

    if annee_reperee is not None:
        # La ligne est placée un demi-cran avant l'année : entre l'ancienne et la nouvelle période
        ax.axvline(annee_reperee - 0.5, color="grey", linestyle="--")
        ax.text(annee_reperee - 0.4, ax.get_ylim()[1], texte_repere,
                va="top", color="grey")

    ax.set_title(titre)
    ax.set_xlabel("Année")
    ax.set_ylabel(axe_y)
    ax.set_xticks(tableau.index)                # une graduation par année, sans décimales
    ax.grid(alpha=0.3)
    ax.legend()
    fig.text(0.01, 0.01, f"Source : {source}", fontsize=8, color="grey")
    fig.tight_layout(rect=(0, 0.03, 1, 1))     # laisse de la place en bas pour la source
    return fig


def barres(tableau, titre, axe_y, source):
    """Barres groupées : un groupe de barres par ligne du tableau, une barre par colonne.

    Par exemple : une ligne par tranche d'IPS, une colonne par année comparée (2018, 2025).
    """
    fig, ax = plt.subplots(figsize=(9, 5))
    tableau.plot.bar(ax=ax, rot=0)  # rot=0 : étiquettes de l'axe horizontal à l'horizontale

    ax.set_title(titre)
    ax.set_xlabel(tableau.index.name)
    ax.set_ylabel(axe_y)
    ax.grid(axis="y", alpha=0.3)
    fig.text(0.01, 0.01, f"Source : {source}", fontsize=8, color="grey")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    return fig


def nuage(tableau, x, y, etiquette, titre, axe_x, axe_y, source, a_nommer=None):
    """Nuage de points, avec le nom de chaque point et la diagonale y = x.

    tableau : une ligne par point (par exemple une académie).
    x, y : noms des colonnes en abscisse et en ordonnée (dans la même unité).
    etiquette : nom de la colonne écrite à côté des points.
    a_nommer : liste des points dont on écrit le nom (tous si None), pour éviter que
               les noms se chevauchent quand les points sont serrés.
    La diagonale sert de repère : un point en dessous a une valeur y plus faible que x.
    """
    fig, ax = plt.subplots(figsize=(8, 7))
    ax.scatter(tableau[x], tableau[y])

    for _, ligne in tableau.iterrows():
        if a_nommer is not None and ligne[etiquette] not in a_nommer:
            continue  # on passe au point suivant sans écrire son nom
        ax.annotate(ligne[etiquette], (ligne[x], ligne[y]), fontsize=7,
                    xytext=(3, 3), textcoords="offset points")

    maximum = max(tableau[x].max(), tableau[y].max()) * 1.05
    ax.plot([0, maximum], [0, maximum], color="grey", linestyle="--", label="y = x")
    ax.set_xlim(0, maximum)
    ax.set_ylim(0, maximum)

    ax.set_title(titre)
    ax.set_xlabel(axe_x)
    ax.set_ylabel(axe_y)
    ax.grid(alpha=0.3)
    ax.legend()
    fig.text(0.01, 0.01, f"Source : {source}", fontsize=8, color="grey")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    return fig


def tableau_comp_1(base, selection, total, debut, fin, col_annee = "session", col_etab = "cod_uai"):
    """Tableau (établissement x année) du ratio selection/total,
    avec l'évolution entre la première et la dernière année (qu'on peut choisir).

    selection  : nom de la colonne du numérateur (ex. nb de formations sélectives)
    total      : nom de la colonne du dénominateur (ex. nb total de formations)
    """
    df = base[base[col_annee].between(debut, fin)]

    # Somme par établissement et par année (gère les plusieurs lignes par établissement)
    agg = (df.groupby([col_etab, col_annee])[[selection, total]]
             .sum()
             .reset_index())

    # Ratio, en évitant la division par zéro
    agg["ratio"] = agg[selection] / agg[total].where(agg[total] != 0)

    # Une ligne par établissement, une colonne par année
    tableau = agg.pivot(index=col_etab, columns=col_annee, values="ratio")

    # Évolution entre la première et la dernière année (en points de ratio)
    if debut in tableau.columns and fin in tableau.columns:
        tableau["evolution"] = tableau[fin] - tableau[debut]

    return tableau.round(3)


def diagramme_baton_normalise(tableau, groupe, titre="", ylabel="Part", ax=None):
    """Bâtons empilés normalisés : part sélective vs non sélective par année.

    tableau : sortie de tableau_comp_1 (lignes = établissements, colonnes = années + 'evolution')
    groupe  : valeur de l'index à tracer (ici un code UAI)
    """
    # Ratio de l'établissement choisi, sans la colonne d'évolution
    ratio = tableau.loc[groupe].drop("evolution", errors="ignore")

    # Deux composantes qui forment un tout (somme = 1)
    parts = pd.DataFrame({"Sélectif": ratio, "Non sélectif": 1 - ratio})

    ax = parts.plot(kind="bar", stacked=True, figsize=(10, 5), ax=ax, width=0.8)
    ax.set_title(titre or str(groupe))
    ax.set_ylabel(ylabel)
    ax.set_ylim(0, 1)
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=1))
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    return ax

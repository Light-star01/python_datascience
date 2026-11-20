import matplotlib.pyplot as plt


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

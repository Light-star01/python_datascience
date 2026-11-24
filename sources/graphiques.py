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


def graphique_indice_mentions(indice, mentions=("acc_b", "acc_tb"),
                              labels={1.0: "Filières sélectives", 0.0: "Filières non sélectives"}):
    noms = {"acc_sansmention": "Sans mention", "acc_ab": "Assez bien",
            "acc_b": "Bien", "acc_tb": "Très bien"}
    fig, axes = plt.subplots(1, len(mentions), figsize=(12, 4.5), sharey=True)
    for ax, m in zip(axes, mentions):
        for g, lab in labels.items():
            ax.plot(indice.loc[g][m], marker="o", label=lab)
        ax.axhline(1, color="grey", linestyle="--")
        ax.set_title(noms.get(m, m))
        ax.set_xlabel("Session")
    axes[0].set_ylabel("Indice (1 = profil des bacheliers)")
    axes[-1].legend()
    fig.suptitle("Mentions dans le supérieur par rapport à l'ensemble des bacheliers")
    plt.tight_layout()
    return fig

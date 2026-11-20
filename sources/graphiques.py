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



from matplotlib.ticker import PercentFormatter

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

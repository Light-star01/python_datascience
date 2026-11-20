import pandas as pd


# Les 3 académies d'Île-de-France, qui forment un seul secteur Parcoursup depuis 2019
ACADEMIES_IDF = ["Paris", "Créteil", "Versailles"]


def taux_poursuite(poursuite, par):
    """Taux de poursuite dans le supérieur (en %) par groupe, par exemple par=["annee", "voie"].

    Comme le recommande la documentation du jeu de données, on somme d'abord les
    poursuivants et les bacheliers du groupe, puis on divise (et non une moyenne de taux).
    """
    sommes = poursuite.groupby(par)[["poursuivants", "bacheliers"]].sum()
    return (sommes["poursuivants"] / sommes["bacheliers"] * 100).round(1)


def part_poursuite_autre_academie_idf(poursuite):
    """Part (en %) des bacheliers franciliens poursuivant dans une autre académie d'Île-de-France.

    Calculée parmi les bacheliers franciliens qui poursuivent dans le supérieur, chaque année.
    Paris, Créteil et Versailles forment une seule région académique : une poursuite dans
    une autre académie francilienne est donc comptée dans poursuivants_autre_academie_meme_region.
    """
    idf = poursuite[poursuite["academie"].isin(ACADEMIES_IDF)]
    sommes = idf.groupby("annee")[["poursuivants_autre_academie_meme_region", "poursuivants"]].sum()
    return (sommes["poursuivants_autre_academie_meme_region"] / sommes["poursuivants"] * 100).round(1)


def boursiers_admis_et_candidats(base, par):
    """Part de boursiers parmi les néo-bacheliers, côté vœux et côté admis, par groupe (en %).

    par : colonnes de regroupement, par exemple ["session", "selective"].
    - part_voeux : boursiers parmi les vœux des néo-bacheliers (bacs général, techno, pro)
      en phase principale. Attention : ce sont des vœux, pas des candidats uniques
      (un candidat fait plusieurs vœux).
    - part_admis : boursiers parmi les néo-bacheliers admis (acc_brs / acc_neobac).
    - rapport : part_admis / part_voeux. Au-dessus de 1, les boursiers sont plus présents
      parmi les admis que parmi les vœux.
    On compare les deux parts la même année, parce que le nombre de boursiers recensés
    change en 2020 et en 2025 aussi chez les candidats : comparer les niveaux bruts d'une
    année à l'autre mesurerait ce changement de comptage, pas la sélection.
    """
    voeux = ["nb_voe_pp_bg", "nb_voe_pp_bt", "nb_voe_pp_bp"]
    voeux_boursiers = ["nb_voe_pp_bg_brs", "nb_voe_pp_bt_brs", "nb_voe_pp_bp_brs"]
    sommes = base.groupby(par)[voeux + voeux_boursiers + ["acc_brs", "acc_neobac"]].sum()

    # sum(axis=1) : somme des colonnes bac général + techno + pro, groupe par groupe
    part_voeux = sommes[voeux_boursiers].sum(axis=1) / sommes[voeux].sum(axis=1) * 100
    part_admis = sommes["acc_brs"] / sommes["acc_neobac"] * 100

    resultat = pd.DataFrame({
        "part_voeux": part_voeux,
        "part_admis": part_admis,
        "rapport": part_admis / part_voeux,
    })
    return resultat.round(2)


def part_admis_meme_academie(base, academie):
    """Part (en %) des admis venant de la même académie, dans les formations d'une académie.

    acc_aca_orig : nombre d'admis issus de la même académie que la formation.
    """
    formations = base[base["academie"] == academie]
    sommes = formations.groupby("session")[["acc_aca_orig", "acc_tot"]].sum()
    return (sommes["acc_aca_orig"] / sommes["acc_tot"] * 100).round(1)

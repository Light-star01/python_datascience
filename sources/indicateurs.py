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


def ajouter_tranche_ips(base):
    """Ajoute la colonne tranche_ips : le quart (quartile) de l'IPS du lycée de la formation.

    pd.qcut coupe les IPS en 4 groupes de même taille : le premier quart contient les
    formations des lycées les moins favorisés, le dernier celles des plus favorisés.
    Les formations sans IPS (hors lycée) restent sans tranche.
    """
    base = base.copy()
    base["tranche_ips"] = pd.qcut(base["ips_lycee"], 4,
                                  labels=["1 (moins favorisés)", "2", "3", "4 (plus favorisés)"])
    return base


def part_bac_admis(base, filiere, colonne_bac):
    """Part (en %) d'un type de bac parmi les néo-bacheliers admis d'une filière, par session.

    colonne_bac : acc_bp (bac professionnel), acc_bt (bac technologique) ou acc_bg (général).
    """
    formations = base[base["filiere"] == filiere]
    sommes = formations.groupby("session")[[colonne_bac, "acc_neobac"]].sum()
    return (sommes[colonne_bac] / sommes["acc_neobac"] * 100).round(1)


def bac_pro_bacheliers_et_admis(panel, annee):
    """Par académie, part des bacs pro parmi les bacheliers et parmi les néo-bacheliers admis (en %).

    panel : résultat de panel_academies (une ligne par académie et par année).
    part_bacheliers vient du fichier de poursuite d'études, part_admis de Parcoursup.
    """
    p = panel[panel["annee"] == annee].copy()
    bacheliers = p[["bacheliers_Bac général", "bacheliers_Bac professionnel",
                    "bacheliers_Bac technologique"]].sum(axis=1)
    p["part_bacheliers"] = p["bacheliers_Bac professionnel"] / bacheliers * 100
    p["part_admis"] = p["acc_bp"] / p["acc_neobac"] * 100
    return p[["academie", "part_bacheliers", "part_admis"]].round(1)


def part_admis_meme_academie(base, academie):
    """Part (en %) des admis venant de la même académie, dans les formations d'une académie.

    acc_aca_orig : nombre d'admis issus de la même académie que la formation.
    """
    formations = base[base["academie"] == academie]
    sommes = formations.groupby("session")[["acc_aca_orig", "acc_tot"]].sum()
    return (sommes["acc_aca_orig"] / sommes["acc_tot"] * 100).round(1)

def part_filles_globale(base, col_f, col_tot, col_annee="session"):
    agg = base.groupby(col_annee)[[col_f, col_tot]].sum()
    return agg[col_f] / agg[col_tot]

def parts_mentions(base, mentions, tot, col_annee="session", col_groupe="selective"):
    """Part de chaque mention parmi les néo-bacheliers admis,
    par groupe (ex. sélectif / non sélectif) et par année.

    mentions : liste de colonnes (ex. ["acc_sansmention", "acc_ab", ...])
    tot      : colonne du dénominateur (ex. "acc_neobac")
    """
    # on somme les effectifs, puis on calcule les parts
    agg = base.groupby([col_groupe, col_annee])[mentions + [tot]].sum()
    return agg[mentions].div(agg[tot], axis=0)

def indice_mentions(base, ref_bac, mentions=("acc_sansmention", "acc_ab", "acc_b", "acc_tb")):
    mentions = list(mentions)
    b = base.copy()
    # Très bien + félicitations du jury. La colonne acc_tbf n'existe qu'à partir de 2021 :
    b["acc_tb"] = b["acc_tb"] + b["acc_tbf"].fillna(0)
    agg = b.groupby(["selective", "session"])[mentions].sum()
    parts = agg.div(agg.sum(axis=1), axis=0) * 100
    sessions = parts.index.get_level_values("session")
    return parts / ref_bac.loc[sessions, mentions].values
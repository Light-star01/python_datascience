# Etude de la démocratisation de l’enseignement supérieur depuis l’ouverture de Parcoursup en 2018

Projet Python pour la data science, ENSAE (2A), 2026-2027.

## Question

**Observe-t-on une démocratisation de l'enseignement supérieur depuis l'ouverture de la plateforme Parcoursup ?**

On ne cherche pas à établir un effet causal de la plateforme. On décrit comment le profil des candidats et des admis a évolué entre 2018 et 2025 (boursiers, type de bac, mention, origine géographique, sexe), selon la filière et la sélectivité des formations, en signalant les limites des données.

## Données

- Parcoursup, vœux de poursuite d'études et de réorientation, sessions 2018 à 2025 : open data du ministère de l'Enseignement supérieur ([data.enseignementsup-recherche.gouv.fr](https://data.enseignementsup-recherche.gouv.fr/explore/?q=parcoursup)). Une ligne correspond à une formation pour une session.
- Indice de position sociale (IPS) des lycées, rentrées 2016 à 2025 : open data de l'Éducation nationale ([data.education.gouv.fr](https://data.education.gouv.fr/explore/?q=indice+de+position+sociale)), en trois fichiers. Joint aux formations par le code UAI et l'année (CPGE et BTS principalement).
- Taux de poursuite des néo-bacheliers dans l'enseignement supérieur par académie, 2010 à 2025 : open data du ministère de l'Enseignement supérieur ([fiche du jeu de données](https://data.enseignementsup-recherche.gouv.fr/explore/dataset/fr-esr-taux-poursuite-enseignement-superieur-par-academie/information/)). Joint aux admis de Parcoursup par académie et par année.
- Contours des régions, départements, arrondissements, cantons et communes de France (métropole et départements d'outre-mer) au format GeoJSON (https://packagist.org/packages/gregoiredavid/france-geojson)
- Notes d'informations de la DEPP sur les résultats au bac de 2018 à 2025 (https://www.education.gouv.fr/sites/default/files/2025-07/depp-ni-2025-45-pdf-441555.pdf ) --> les données ont été extraites manuellement de ces rapports publiés par la DEPP (pas d'accès aux données d'origines)

Les données sont téléchargées directement depuis les URL publiques. Elles ne sont pas stockées dans le dépôt.

## Installation

```
git clone https://github.com/Light-star01/python_datascience
cd python_datascience
pip install -r requirements.txt
```

Ce projet est testé sur le SSP Cloud (Onyxia, Genes et Insee).

## Lancement

Ouvrir `notebooks/rapport.ipynb` et exécuter toutes les cellules. Les données sont téléchargées automatiquement dans `data/`.

## Organisation du dépôt

- `notebooks/rapport.ipynb` : notebook final, qui importe les fonctions de `sources/`.
- `notebooks/exploration.ipynb` : notebook d'exploration. Il garde la trace des vérifications qui justifient nos choix (identifiant, sélectivité, filières) et enregistre la base empilée dans `data/`.
- `sources/` : fonctions Python importées par les notebooks (`chargement_data.py` pour télécharger les données ; `cleaning_data.py`, `indicateurs.py` et `graphiques.py` à remplir).
- `data/` : données téléchargées ou générées, non versionnées (voir `.gitignore`).





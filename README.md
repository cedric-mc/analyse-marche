# Projet DVO : Création d'un Pipeline de Données
## Analyse du Marché de l'Immobilier
### Auteur : MARIYA CONSTANTINE & Gaëtan PERRIER
### Date : 10/10/2025
## Introduction

L'objectif est de créer un pipeline de données complet pour analyser le marché immobilier. Ce projet vise à automatiser la collecte, le traitement et l'analyse des données immobilières afin de fournir des insights pertinents sur le marché de l'immobilier à travers un tableau de bord interactif.

## Structure du Projet

Le projet est structuré avec un dossier contenant le code source `src`, un dossier contenant la pipeline d'automatisation (CI/CD) `.github/workflows/` ainsi que le fichier `README.md` pour la documentation (qui est celui que vous lisez actuellement).

### Dossier `src`

Le dossier `src` contient les scripts Python nécessaires pour chaque étape du pipeline de données. Voici une description des principaux fichiers :
- `webscraping/` : Contient le module de **Spider** Scrapy pour l'extraction des données ainsi que de nettoyage et de structuration des données.
    - `spiders/` : Contient les spiders spécifiques pour le scraping des données immobilières.
        - `french_immobilier.py` : Spider principal pour extraire les données des annonces immobilières dans un fichier `json`.
    - `items.py` : Définit les structures de données pour les annonces immobilières (structures de données par défaut).
    - `pipelines.py` : Contient la pipeline de traitement des données extraites en nettoyant et en structurant les données dans un fichier `csv`.
    - `settings.py` : Configuration du projet Scrapy (paramètres par défaut).
    - `middlewares.py` : Contient les middlewares pour Scrapy (par défaut).
-
# Projet DVF — Pipeline d'analyse du marché immobilier

Ce dépôt contient un pipeline complet pour extraire, nettoyer et analyser des annonces immobilières en France, et une application Streamlit pour visualiser les résultats.

## Version publiée

La version publiée de l'application Streamlit est disponible ici :

https://analyse-marche-k3cvzui58kbdjbahcome8b.streamlit.app/

> Cette URL pointe vers l'instance publique déployée de l'application Streamlit contenant le tableau de bord et les outils d'analyse. Pour utiliser l'interface dans de bonnes conditions, il est recommandé d'utiliser le thème clair du navigateur/système.

## Structure du projet

Racine du dépôt

- `src/` : code source
  - `app.py` : application Streamlit (interface utilisateur)
  - `clean.py` : script de nettoyage / transformation des données
  - `requirements.txt` : dépendances Python
  - `webscraping/` : projet Scrapy
    - `webscraping/` : package Scrapy (spiders, settings, pipelines...)
      - `spiders/french_immobilier.py` : spider principal

- `.github/workflows/` : workflows GitHub Actions
  - `main.yml` : workflow principal qui lance le scraping, nettoie les données et pousse le CSV
  - `update_data.yml` : (autre workflow si présent)

## Objectifs

- Automatiser le scraping des annonces immobilières (Scrapy).
- Nettoyer et structurer les données (`clean.py`) pour produire `annonces_propres.csv`.
- Visualiser et explorer les données dans une application Streamlit (`src/app.py`).
- Permettre le déclenchement manuel du pipeline via l'interface Streamlit (bouton qui appelle l'API GitHub pour lancer le workflow Actions).

## Dépendances

Le projet utilise Python 3.11 (déclaré dans les workflows). Installez les dépendances :

```sh
python -m venv .venv
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
pip install -r src/requirements.txt
```

## Exécution locale

1. Activer l'environnement virtuel (voir ci-dessus).
2. Lancer l'application Streamlit depuis la racine du dépôt :

```sh
streamlit run src/app.py
```

3. Ouvrez l'interface dans votre navigateur (Streamlit ouvrira automatiquement une page locale).

## GitHub Actions — pipeline CI/CD

Le workflow principal `main.yml` (dans `.github/workflows`) effectue les étapes suivantes :

1. Checkout du code.
2. Setup de Python.
3. Installation des dépendances (`pip install -r src/requirements.txt`).
4. Exécution du spider Scrapy et export des données (JSON/CSV selon la config).
5. Nettoyage des données via `clean.py` pour produire `annonces_propres.csv`.
6. Commit et push du fichier CSV sur la branche `main`.

Si vous obtenez l'erreur `scrapy: command not found`, vérifiez que la dépendance `scrapy` est bien listée dans `src/requirements.txt` et que le workflow installe correctement `pip install -r src/requirements.txt`.

## Déclencher le workflow depuis Streamlit

L'application Streamlit contient (ou peut contenir) un bouton qui déclenche le workflow GitHub Actions via l'API REST `POST /repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches`.

Points importants pour utiliser cette fonctionnalité:

- Le token utilisé doit être un Personal Access Token (PAT) ou `GITHUB_TOKEN` avec le scope `repo` et `workflow` si vous utilisez un PAT. Si vous utilisez `GITHUB_TOKEN` fourni par GitHub Actions, il n'est pas possible de l'utiliser depuis l'application Streamlit externe ; préférez un PAT stocké de façon sécurisée.
- Dans l'interface Streamlit, vous pouvez fournir le token via une variable d'environnement (fichier `.env`) ou via un champ de saisie sécurisé. Le code doit utiliser ce token pour appeler l'API GitHub.
- Le webhook `workflow_dispatch` doit être présent dans le fichier `.github/workflows/main.yml` (déclencheur manuel). Ce dépôt inclut `workflow_dispatch`.

Exemple minimal de requête en Python (requests) :

```py
import requests

owner = "cedric-mc"
repo = "analyse-marche"
workflow_id = "main.yml"  # ou l'ID du workflow
url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches"
headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {token}",
}
data = {"ref": "main"}
resp = requests.post(url, headers=headers, json=data)
resp.raise_for_status()
```

## Sécurité

- Ne jamais committer de tokens ou secrets dans le dépôt.
- Stockez les PATs dans un gestionnaire de secrets (ex : GitHub Secrets pour les workflows, ou un fichier `.env` local non commité pour le dev).

## Développement et contributions

1. Forkez le dépôt.
2. Créez une branche feature/bugfix.
3. Ouvrez une Pull Request en décrivant vos changements.

## Contact

Pour toute question ou problème, ouvrez une issue dans le dépôt ou contactez les auteurs du projet.

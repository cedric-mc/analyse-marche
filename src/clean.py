import pandas as pd
import re
import sys


# =========================
# Prix : enlever les espaces, €, CC, etc., et convertir en float
# =========================
def clean_prix(prix_str):
    if not isinstance(prix_str, str):
        return None
    # Extraire les chiffres
    prix_clean = prix_str.replace(" ", "").replace("€", "").replace("CC", "")
    prix_clean = re.sub(r"[^\d\.]", "", prix_clean)  # garder uniquement les chiffres et le point
    return float(prix_clean) if prix_clean else None


# =========================
# Surface : enlever "m²" et convertir en float
# =========================
def clean_surface(surface_str):
    if not isinstance(surface_str, str):
        return None
    surface_clean = re.sub(r"[^\d\.]", "", surface_str)
    return float(surface_clean) if surface_clean else None


# =========================
# Pipeline de nettoyage
# =========================
def main():
    # 1️⃣ Charger le JSON
    # df = pd.read_json("annonces.json")

    if len(sys.argv) != 2:
        print("Usage: python clean.py <input_json_file>")
        sys.exit(1)
    input_file = sys.argv[1]
    df = pd.read_json(input_file)

    # 2️⃣ Nettoyage des colonnes
    df['prix'] = df['prix'].apply(clean_prix)
    df['surface'] = df['surface'].apply(clean_surface)

    # Chambres, salles de bain, garage : convertir en int
    for col in ['chambres', 'salles_bain', 'garage']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # 3️⃣ Gérer les valeurs manquantes
    df = df.dropna(subset=['prix', 'surface'])  # on enlève les lignes sans prix ou surface

    # 4️⃣ Calculer le prix au m²
    df['prix_m2'] = df['prix'] / df['surface']

    # 5️⃣ Sauvegarder en CSV
    df.to_csv("annonces_propres.csv", index=False, encoding='utf-8', sep=';')

    print("✅ Nettoyage terminé. Fichier 'annonces_propres.csv' créé.")


# =========================
# Main
# =========================
if __name__ == "__main__":
    main()
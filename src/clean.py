import pandas as pd
import re
import sys


def clean_str(str_val):
    """Nettoyer une chaîne de caractères en enlevant les espaces inutiles."""
    if not isinstance(str_val, str):
        return None
    str_clean = str_val.strip()
    return str_clean if str_clean else None


def clean_type(type_str): # "type": "Maisons à vendre" ou "Appartements à vendre" or "Terrain à vendre" or "Immeubles à vendre" donc enlever "à vendre" et mettre au singulier
    """Nettoyer le type de bien."""
    if not isinstance(type_str, str):
        return None
    type_clean = type_str.replace("à vendre", "").strip()
    type_singular = {
        "Maisons": "Maison",
        "Appartements": "Appartement",
        "Terrains": "Terrain",
        "Commerces": "Commerce",
        "Parkings": "Parking",
        "Autres": "Autre"
    }
    return type_singular.get(type_clean, type_clean)


def clean_prix(prix_str):
    """Nettoyer le prix en euros."""
    if not isinstance(prix_str, str) or not re.search(r"\d", prix_str):
        return None
    # Extraire les chiffres
    prix_clean = prix_str.replace(" ", "").replace("€", "")
    prix_clean = re.sub(r"[^\d\.]", "", prix_str)  # garder uniquement les chiffres et le point
    return float(prix_clean) if prix_clean else None


def clean_surface(surface_str):
    """Nettoyer la surface en m²."""
    if not isinstance(surface_str, str):
        return None
    surface_clean = re.sub(r"[^\d\.]", "", surface_str) # garder uniquement les chiffres et le point
    return float(surface_clean) if surface_clean else None


def clean_localisation(localisation_str):
    """Nettoyer la localisation en séparant ville et code postal."""
    # "\n            — Moissy-Cramayel 77550 —\n        "
    if not isinstance(localisation_str, str):
        return None, None
    localisation_clean = localisation_str.strip()
    match = re.search(r"(\d{5})", localisation_clean)
    if match:
        code_postal = match.group(1)
        ville = localisation_clean.replace(code_postal, "").strip(" —\n\t").strip()
        # print(ville, code_postal)
        return ville, code_postal
    return None, None


def clean_pieces(pieces_str): # "pieces": "3 pièces"
    """Nettoyer le nombre de pièces."""
    if not isinstance(pieces_str, str):
        return None
    pieces_clean = re.sub(r"[^\d]", "", pieces_str)  # garder uniquement les chiffres
    return int(pieces_clean) if pieces_clean else None


# =========================
# Pipeline de nettoyage
# =========================
def main():
    # 1️⃣ Charger le JSON
    # df = pd.read_json("annonces.json")

    if len(sys.argv) != 3:
        print("Usage: python clean.py <input_json_file> <output_csv_file>")
        sys.exit(1)
    input_file = sys.argv[1]
    df = pd.DataFrame(pd.read_json(input_file))

    # 2️⃣ Nettoyage des colonnes
    df['titre'] = df['titre'].apply(clean_str)
    df['type'] = df['type'].apply(clean_type)
    df['prix'] = df['prix'].apply(clean_prix)
    df['surface'] = df['surface'].apply(clean_surface)
    df['surface_terrain'] = df['surface_terrain'].apply(clean_surface)
    df['ville'], df['code_postal'] = zip(*df['localisation'].apply(clean_localisation))
    df['pieces'] = df['pieces'].apply(clean_pieces)
    df['parking'] = df['parking'].apply(lambda x: True if x else False)
    df['jardin'] = df['jardin'].apply(lambda x: True if x else False)
    df['balcon_terrasse'] = df['balcon_terrasse'].apply(lambda x: True if x else False)
    df['piscine'] = df['piscine'].apply(lambda x: True if x else False)
    df['ascenseur'] = df['ascenseur'].apply(lambda x: True if x else False)
    df['acces_handicape'] = df['acces_handicape'].apply(lambda x: True if x else False)
    df['agence'] = df['agence'].apply(clean_str)

    # 3️⃣ Gérer les valeurs manquantes et supprimer les colonnes inutiles
    df = df.dropna(subset=['prix', 'surface'])  # on enlève les lignes sans prix ou surface
    df = df.drop(columns=['localisation'], errors='ignore')  # on enlève la colonne localisation

    # 4️⃣ Calculer le prix au m² (2 décimales)
    df['prix_m2'] = (df['prix'] / df['surface']).round(2)

    # 5️⃣ Sauvegarder en CSV
    output_file = sys.argv[2]
    df.to_csv(output_file, index=False, encoding='utf-8')

    print(f"✅ Nettoyage terminé. Fichier '{output_file}' créé.")


# =========================
# Main
# =========================
if __name__ == "__main__":
    main()
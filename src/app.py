import streamlit as st
import pandas as pd
import requests
from os import getenv
from dotenv import load_dotenv
from io import StringIO
import plotly.express as px


# =========================
# Configuration GitHub
# =========================
load_dotenv()
GITHUB_TOKEN = getenv('GITHUB_TOKEN')
REPO = "cedric-mc/analyse-marche"
CSV_PATH = "annonces_propres.csv"
url = f"https://raw.githubusercontent.com/{REPO}/main/{CSV_PATH}"


# =========================
# Charger et afficher les données
# =========================
def load_data(csv_string):
    df = pd.read_csv(StringIO(csv_string))

    # -----------------
    # Mise en page
    # -----------------
    st.set_page_config(layout="wide", page_title="Analyse Immo", page_icon="🏠")

    st.title("🏠 Analyse du marché immobilier")
    st.markdown("### Données extraites et nettoyées des annonces immobilières en France")

    # Stats rapides en 3 colonnes
    col1, col2, col3 = st.columns(3)
    col1.metric("📊 Nombre d'annonces ", len(df))
    if "prix_m2" in df.columns:
        col2.metric("💶 Prix moyen/m²", f"{df['prix_m2'].mean():.0f} €")
    if "surface" in df.columns:
        col3.metric("📐 Surface moyenne", f"{df['surface'].mean():.0f} m²")

    # -----------------
    # Tableau interactif
    # -----------------
    st.subheader("Aperçu des données")
    
    # Transformer les URLs en balises HTML <img>
    df_display = df.copy()
    df_display['lien'] = df_display['lien'].apply(lambda x: f'<a href="{x}" target="_blank">Détails</a>')
    df_display["image"] = df_display["image"].apply(lambda x: f'<img src="{x}" width="120">')
    df_display = df_display.fillna('') # Fill
    # Transformer les floats en int pour l'affichage, uniquement les colonnes spéficifées
    # for col in ['chambres', 'garage']:
    #     if col in df_display.columns:
    #         df_display[col] = df_display[col].apply(lambda x: int(x) if pd.notnull(x) else x)
    st.write(df_display.to_html(escape=False), unsafe_allow_html=True)

    # -----------------
    # Visualisations
    # -----------------
    if "prix" in df.columns:
        st.subheader("Distribution des prix (€)")
        fig = px.histogram(df, x="prix", nbins=30, title="Histogramme des prix")
        st.plotly_chart(fig, use_container_width=True)

    if "ville" in df.columns:
        st.subheader("Répartition par ville")
        fig = px.bar(
            df["ville"].value_counts().reset_index(),
            x="index",
            y="ville",
            labels={"index": "Ville", "ville": "Nombre d'annonces"},
            title="Nombre d'annonces par ville"
        )
        st.plotly_chart(fig, use_container_width=True)

    return df


# =========================
# Main
# =========================
def main():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        csv_string = response.content.decode('utf-8')
        load_data(csv_string)
    else:
        st.error(f"❌ Impossible de charger le fichier CSV (code {response.status_code})")
        st.stop()


if __name__ == "__main__":
    main()

import streamlit as st
import pandas as pd
import requests
from os import getenv
from dotenv import load_dotenv
from io import StringIO
import plotly.express as px

# =========================
# Configuration
# =========================
load_dotenv()
GITHUB_TOKEN = getenv("GITHUB_TOKEN")
REPO = "cedric-mc/analyse-marche"
CSV_PATH = "annonces_propres.csv"
CSV_URL = f"https://raw.githubusercontent.com/{REPO}/main/{CSV_PATH}"

st.set_page_config(
    page_title="🏠 Analyse Immo LDF",
    layout="wide",
    page_icon="🏡"
)

# =========================
# Chargement des données
# =========================
@st.cache_data
def load_data():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(CSV_URL, headers=headers)
    if response.status_code == 200:
        df = pd.read_csv(StringIO(response.text))
        return df
    else:
        st.error(f"❌ Impossible de charger le fichier CSV ({response.status_code})")
        return pd.DataFrame()

df = load_data()
if df.empty:
    st.stop()

# =========================
# En-tête et résumé
# =========================
st.title("🏠 Tableau de Bord — Analyse du Marché Immobilier")
st.markdown("##### _Projet LDF : Pipeline complet de données immobilières_")

# Statistiques clés
col1, col2, col3, col4 = st.columns(4)
col1.metric("📊 Nombre d'annonces", len(df))
if "prix_m2" in df:
    col2.metric("💶 Prix moyen/m²", f"{df['prix_m2'].mean():,.0f} €")
if "surface" in df:
    col3.metric("📐 Surface moyenne", f"{df['surface'].mean():.0f} m²")
if "ville" in df:
    col4.metric("🏙️ Nombre de villes", df['ville'].nunique())

st.divider()

# =========================
# Filtres interactifs
# =========================
st.sidebar.header("🎯 Filtres")

ville = st.sidebar.multiselect(
    "Ville", options=sorted(df["ville"].dropna().unique()), default=[], placeholder="Sélectionner une ou plus"
)
type_bien = st.sidebar.multiselect(
    "Type de bien", options=sorted(df["type"].dropna().unique()), default=[], placeholder="Sélectionner un ou plus"
)
prix_min, prix_max = st.sidebar.slider(
    "Prix (€)", 
    int(df["prix"].min()), 
    int(df["prix"].max()), 
    (int(df["prix"].min()), int(df["prix"].max()))
)
surface_min, surface_max = st.sidebar.slider(
    "Surface (m²)", 
    int(df["surface"].min()), 
    int(df["surface"].max()), 
    (int(df["surface"].min()), int(df["surface"].max()))
)

# Application des filtres
filtered_df = df.copy()
if ville:
    filtered_df = filtered_df[filtered_df["ville"].isin(ville)]
if type_bien:
    filtered_df = filtered_df[filtered_df["type"].isin(type_bien)]
filtered_df = filtered_df[
    (filtered_df["prix"] >= prix_min) & (filtered_df["prix"] <= prix_max) &
    (filtered_df["surface"] >= surface_min) & (filtered_df["surface"] <= surface_max)
]

# =========================
# Onglets (tableau / visualisations / images)
# =========================
tab1, tab2 = st.tabs(["📋 Données", "📊 Visualisations"])

with tab1:
    st.subheader("Aperçu des annonces filtrées")

    page_size = 10
    total_rows = len(filtered_df)
    total_pages = (total_rows - 1) // page_size + 1
    page = st.number_input("Page", 1, total_pages, 1)
    start = (page - 1) * page_size
    end = start + page_size
    page_df = filtered_df.iloc[start:end].copy()

    # Colonnes affichées
    colonnes_affichees = ["type", "ville", "prix", "surface", "prix_m2", "images_page", "lien"]
    page_df = page_df[[c for c in colonnes_affichees if c in page_df.columns]]

    # Formatage des colonnes
    if "prix" in page_df.columns:
        page_df["prix"] = page_df["prix"].apply(lambda x: f"{x} €")

    if "surface" in page_df.columns:
        page_df["surface"] = page_df["surface"].apply(lambda x: f"{x} m²")

    if "prix_m2" in page_df.columns:
        page_df["prix_m2"] = page_df["prix_m2"].apply(lambda x: f"{x} €/m²")

    # Lien cliquable
    page_df["lien"] = page_df["lien"].apply(
        lambda x: f'<a href="{x}" target="_blank">Lien</a>'
    )

    # Galerie d'images (si dispo)
    if "images_page" in page_df.columns:
        def render_gallery(images):
            try:
                imgs = eval(images) if isinstance(images, str) else images
                if isinstance(imgs, list) and imgs:
                    return " ".join([f'<img src="{img}" width="100">' for img in imgs[:5]])
                else:
                    return "N/A"
            except Exception:
                return "N/A"
        page_df["galerie"] = page_df["images_page"].apply(render_gallery)
        page_df.drop(columns=["images_page"], inplace=True)

    page_df.columns = ['Type', 'Ville', 'Prix', 'Surface (m²)', 'Prix/m²', 'Lien', 'Galerie']

    st.write(page_df.to_html(escape=False, index=False), unsafe_allow_html=True)
    st.caption(f"Page {page}/{total_pages} — {total_rows} annonces affichées")

with tab2:
    st.subheader("Visualisations")

    colA, colB = st.columns(2)
    with colA:
        if "prix" in filtered_df:
            prix_range = st.slider(
                "Filtrer par prix",
                min_value=int(filtered_df["prix"].min()),
                max_value=int(filtered_df["prix"].max()),
                value=(int(filtered_df["prix"].min()), int(filtered_df["prix"].max())),
                step=1000
            )
            filtered_df = filtered_df[
                (filtered_df["prix"] >= prix_range[0]) & (filtered_df["prix"] <= prix_range[1])
            ]
            fig = px.histogram(filtered_df, x="prix", nbins=30, title="Distribution des prix (€) après filtrage")
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Interprétation :** Ce graphique montre la répartition des prix des annonces après application des filtres. Vous pouvez ajuster le filtre de prix pour voir comment cela affecte la distribution.")
            st.markdown(f"**Prix moyen :** {filtered_df['prix'].mean():,.0f} €  \n**Prix médian :** {filtered_df['prix'].median():,.0f} €")
    with colB:
        if "prix_m2" in filtered_df:
            fig = px.box(filtered_df, y="prix_m2", title="Boxplot du prix au m²")
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Interprétation :** Le boxplot du prix au m² permet d'identifier les valeurs aberrantes et de comprendre la dispersion des prix au mètre carré.")
            st.markdown(f"**Prix moyen/m² :** {filtered_df['prix_m2'].mean():,.0f} €  \n**Prix médian/m² :** {filtered_df['prix_m2'].median():,.0f} €")

    if "ville" in filtered_df:
        st.subheader("Répartition par ville")
        fig = px.bar(
            df["ville"].value_counts().reset_index(),
            x="ville",
            y="count",
            labels={"index": "Ville", "ville": "Nombre d'annonces"},
            title="Nombre d'annonces par ville"
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("**Interprétation :** Ce graphique montre le nombre d'annonces disponibles dans chaque ville. Cela peut aider à identifier les zones avec plus d'offres immobilières.")

    colA, colB = st.columns(2)
    with colA:
        if "dpe" in filtered_df:
            st.subheader("Répartition par DPE")
            dpe_counts = filtered_df["dpe"].value_counts().reindex(['A', 'B', 'C', 'D', 'E', 'F', 'G']).fillna(0)
            fig = px.bar(
                dpe_counts.reset_index(),
                x=df["dpe"].value_counts().reindex(['A', 'B', 'C', 'D', 'E', 'F', 'G']).fillna(0).index,
                y=dpe_counts.values,
                labels={"index": "Classe DPE", "y": "Nombre d'annonces"},
                title="Répartition des annonces par classe DPE",
                text_auto=True
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Interprétation :** Ce graphique montre la répartition des annonces selon leur classe énergétique (DPE). Cela peut aider à évaluer l'efficacité énergétique des biens proposés.")

    with colB:
        if "ges" in filtered_df:
            st.subheader("Répartition par GES")
            ges_counts = filtered_df["ges"].value_counts().reindex(['A', 'B', 'C', 'D', 'E', 'F', 'G']).fillna(0)
            fig = px.bar(
                ges_counts.reset_index(),
                x=ges_counts.index,
                y=ges_counts.values,
                labels={"index": "Classe GES", "y": "Nombre d'annonces"},
                title="Répartition des annonces par classe GES",
                text_auto=True
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**Interprétation :** Ce graphique montre la répartition des annonces selon leur classe d'émissions de gaz à effet de serre (GES). Cela peut aider à évaluer l'impact environnemental des biens proposés.")
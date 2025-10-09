import streamlit as st
import pandas as pd
import requests
from os import getenv
from dotenv import load_dotenv
from io import StringIO
import plotly.express as px

# =========================
# Configuration générale
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
# Fonctions utilitaires
# =========================
def apply_custom_css():
    """Injecte le style personnalisé dans la page Streamlit."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    /* Styles de la page */
    html, body, [class*="css"]  {
        font-family: 'Poppins', sans-serif;
        background-color: #f7f9fb;
        color: #222;
    }
    /* Titres du niveau 1 à 5 */
    h1, h2, h3, h4, h5 {
        color: #2E4057;
        font-weight: 600;
    }
    /* Styles des métriques (valeurs et étiquettes) */
    [data-testid="stMetricValue"] { /* Valeurs */
        font-size: 1.6rem;
        color: #2E4057;
    }
    [data-testid="stMetricLabel"] { /* Étiquettes */
        color: #6c757d;
    }
    div[data-testid="stHorizontalBlock"] { /* Conteneurs de métriques en ligne */
        background-color: white;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 6px 14px rgba(0,0,0,0.06);
    }
    section[data-testid="stSidebar"] { /* Barre latérale */
        background-color: #f0f2f6;
        border-right: 2px solid #e0e0e0;
    }
    section[data-testid="stSidebar"] h2 { /* Titres de la barre latérale */
        color: #2E4057;
    }
    /* Styles des tableaux */
    table {
        border-collapse: collapse;
        width: 100%;
        border-radius: 12px;
        overflow: hidden;
    }
    table th {
        background-color: #2E4057;
        color: white;
        padding: 10px;
    }
    table td {
        padding: 8px;
        background-color: #ffffff;
    }
    table tr:nth-child(even) td {
        background-color: #f8f9fa;
    }
    table tr:hover td {
        background-color: #e9ecef;
    }
    /* Styles des images dans les tableaux */
    table img {
        border-radius: 8px;
        margin-right: 4px;
        box-shadow: 0 3px 6px rgba(0,0,0,0.1);
    }
    /* Styles des graphiques Plotly */
    .plotly-graph-div {
        background-color: white !important;
        border-radius: 12px;
        box-shadow: 0 6px 14px rgba(0,0,0,0.06);
        padding: 15px;
    }
    /* Styles des onglets */
    [role="tab"] {
        background-color: #e9ecef;
        color: #2E4057;
        border-radius: 8px 8px 0 0;
        padding: 8px 16px;
        margin-right: 4px;
        font-weight: 600;
    }
    [role="tab"][aria-selected="true"] {
        background-color: #3b82f6;
        color: white;
    }
    [role="tabpanel"] {
        background-color: white;
        border-radius: 0 0 12px 12px;
        padding: 20px;
        box-shadow: 0 6px 14px rgba(0,0,0,0.06);
    }
    /* Styles des boutons */
    button {
        background-color: #3b82f6;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
    }
    button:hover {
        background-color: #2563eb;
        cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)


@st.cache_data
def load_data() -> pd.DataFrame:
    """
    Charge les données depuis le fichier CSV hébergé sur GitHub.

    Retourne:
    - DataFrame contenant les données des annonces.
    """
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(CSV_URL, headers=headers)
    if response.status_code == 200:
        return pd.read_csv(StringIO(response.text))
    st.error(f"❌ Impossible de charger le fichier CSV ({response.status_code})")
    return pd.DataFrame()


def render_header():
    """Affiche le titre principal et la description du tableau de bord."""
    st.markdown(
        "<h1 style='text-align:center'>🏡 Tableau de Bord — "
        "<span style='color:#3b82f6'>Analyse du Marché Immobilier</span></h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align:center; color:#6c757d'>Projet LDF — Création d'un Pipeline de Données</p>",
        unsafe_allow_html=True
    )
    st.divider()


def render_summary(df: pd.DataFrame):
    """
    Affiche les métriques principales.
    
    Paramètres:
    - df : DataFrame contenant les données des annonces.
    """
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("**📊 Nombre d'annonces**", len(df))
    if "prix_m2" in df:
        col2.metric("**💶 Prix moyen/m²**", f"{df['prix_m2'].mean():,.0f} €")
    if "surface" in df:
        col3.metric("**📐 Surface moyenne**", f"{df['surface'].mean():.0f} m²")
    if "ville" in df:
        col4.metric("**🏙️ Nombre de villes**", df['ville'].nunique())
    st.divider()


def sidebar_filters(df: pd.DataFrame):
    """
    Crée et applique les filtres de la barre latérale avec un vrai reset visuel.
    """
    st.sidebar.header("🎯 Filtres")
    st.sidebar.markdown("Affinez votre recherche ci-dessous 👇")

    # --- Initialisation globale ---
    if "filters_reset_count" not in st.session_state:
        st.session_state.filters_reset_count = 0  # 👈 sert à forcer la recréation des widgets

    # --- Bouton de reset ---
    if st.sidebar.button("🔄 Réinitialiser les filtres"):
        st.session_state.filters_reset_count += 1
        st.rerun()  # recharge la page avec de nouvelles clés

    # --- Clés dynamiques pour forcer le reset visuel ---
    key_suffix = f"_{st.session_state.filters_reset_count}"

    # === Widgets ===
    ville = st.sidebar.multiselect(
        "🏙️ Ville",
        sorted(df["ville"].dropna().unique()),
        default=[],
        key=f"ville_filter{key_suffix}"
    )
    type_bien = st.sidebar.multiselect(
        "🏠 Type de bien",
        sorted(df["type"].dropna().unique()),
        default=[],
        key=f"type_filter{key_suffix}"
    )
    prix_min, prix_max = st.sidebar.slider(
        "💰 Prix (€)",
        int(df["prix"].min()),
        int(df["prix"].max()),
        (int(df["prix"].min()), int(df["prix"].max())),
        key=f"prix_range{key_suffix}"
    )
    surface_min, surface_max = st.sidebar.slider(
        "📏 Surface (m²)",
        int(df["surface"].min()),
        int(df["surface"].max()),
        (int(df["surface"].min()), int(df["surface"].max())),
        key=f"surface_range{key_suffix}"
    )

    # === Application des filtres ===
    filtered_df = df.copy()
    if ville:
        filtered_df = filtered_df[filtered_df["ville"].isin(ville)]
    if type_bien:
        filtered_df = filtered_df[filtered_df["type"].isin(type_bien)]
    filtered_df = filtered_df[
        (filtered_df["prix"] >= prix_min)
        & (filtered_df["prix"] <= prix_max)
        & (filtered_df["surface"] >= surface_min)
        & (filtered_df["surface"] <= surface_max)
    ]

    return filtered_df


def render_data_table(df: pd.DataFrame):
    """
    Affiche la table paginée des annonces avec :
    - Boutons Précédent / Suivant
    - Numéro de page pour sauter directement
    - Boutons rapides pour avancer ou reculer de 5 pages
    """
    st.subheader("📋 Annonces filtrées")

    page_size = 10
    total_rows = len(df)
    total_pages = (total_rows - 1) // page_size + 1

    # --- 🩵 Réinitialisation automatique si le nombre de lignes a changé ---
    if "last_total_rows" not in st.session_state:
        st.session_state.last_total_rows = total_rows

    if "current_page" not in st.session_state:
        st.session_state.current_page = 1

    # Si le dataset filtré a changé → revenir à la page 1
    if total_rows != st.session_state.last_total_rows:
        st.session_state.current_page = 1
        st.session_state.last_total_rows = total_rows

    # --- Navigation ---
    col_prev5, col_prev1, col_page, col_next1, col_next5 = st.columns([1, 1, 2, 1, 1])

    if col_prev5.button("⏮️ -5"):
        st.session_state.current_page = max(1, st.session_state.current_page - 5)
    if col_prev1.button("⬅️"):
        st.session_state.current_page = max(1, st.session_state.current_page - 1)
    # Ajoute la page actuelle au milieu + le nombre total de pages (affichage sécurisé, page/<total_pages>)
    if col_page.button(f"Page {st.session_state.current_page} / {total_pages}"):
        pass  # Ne fait rien, juste pour l'affichage
    if col_next1.button("➡️"):
        st.session_state.current_page = min(total_pages, st.session_state.current_page + 1)
    if col_next5.button("⏭️ +5"):
        st.session_state.current_page = min(total_pages, st.session_state.current_page + 5)

    # --- Champ pour aller à une page spécifique ---
    st.session_state.current_page = st.number_input(
        "Aller à la page :", 
        min_value=1,
        max_value=total_pages,
        value=min(st.session_state.current_page, total_pages),  # 👈 sécurité supplémentaire
        step=1
    )

    # Affichage de la page actuelle
    st.markdown(
        f"<p style='text-align:center; font-weight:600'>Page {st.session_state.current_page} / {total_pages}</p>",
        unsafe_allow_html=True
    )

    # Découpage des données
    start = (st.session_state.current_page - 1) * page_size
    end = st.session_state.current_page * page_size
    page_df = df.iloc[start:end].copy()

    colonnes_affichees = ["type", "ville", "prix", "surface", "prix_m2", "images_page", "lien"]
    page_df = page_df[[c for c in colonnes_affichees if c in page_df.columns]]

    # === Formats ===
    if "prix" in page_df:
        page_df["prix"] = page_df["prix"].apply(lambda x: f"{x:,.0f} €")
    if "surface" in page_df:
        page_df["surface"] = page_df["surface"].apply(lambda x: f"{x:,.0f} m²")
    if "prix_m2" in page_df:
        page_df["prix_m2"] = page_df["prix_m2"].apply(lambda x: f"{x:,.0f} €/m²")

    # === Liens ===
    if "lien" in page_df:
        page_df["lien"] = page_df["lien"].apply(lambda x: f'<a href="{x}" target="_blank">🔗 Voir</a>')

    # === Galerie ===
    if "images_page" in page_df:
        def render_gallery(images):
            try:
                imgs = eval(images) if isinstance(images, str) else images
                if isinstance(imgs, list) and imgs:
                    return " ".join([f'<img src="{img}" width="60">' for img in imgs[:5]])
                return "—"
            except Exception:
                return "—"
        page_df["galerie"] = page_df["images_page"].apply(render_gallery)
        page_df.drop(columns=["images_page"], inplace=True)

    page_df.columns = ['Type', 'Ville', 'Prix', 'Surface', 'Prix/m²', 'Lien', 'Galerie']

    st.write(page_df.to_html(escape=False, index=False), unsafe_allow_html=True)
    st.caption(f"📄 Total : {total_rows} annonces")



def render_visualizations(df: pd.DataFrame):
    """
    Affiche les graphiques d'analyse.

    Paramètres:
    - df : DataFrame contenant les données des annonces.
    """
    st.subheader("📊 Visualisations")
    colA, colB = st.columns(2)

    with colA:
        if "prix" in df:
            fig = px.histogram(df, x="prix", nbins=30, color_discrete_sequence=["#3b82f6"])
            fig.update_layout(title="Distribution des prix (€)", title_x=0.3, xaxis_title="Prix (€)", yaxis_title="Nombre d'annonces")
            st.plotly_chart(fig, use_container_width=True)

    with colB:
        if "prix_m2" in df:
            fig = px.box(df, y="prix_m2", color_discrete_sequence=["#10b981"])
            fig.update_layout(title="Boxplot du prix au m²", title_x=0.3, yaxis_title="Prix/m² (€)")
            st.plotly_chart(fig, use_container_width=True)

    if "ville" in df:
        st.subheader("🏙️ Répartition par ville")

        # On prépare les données
        data_villes = df["ville"].value_counts().reset_index()
        data_villes.columns = ["Ville", "Nombre d'annonces"]

        # On laisse Plotly gérer la couleur par Ville
        fig = px.bar(
            data_villes,
            x="Ville",
            y="Nombre d'annonces",
            color="Ville",  # 👈 clé : une couleur par ville
            title="Nombre d'annonces par ville",
        )

        # Options visuelles
        fig.update_layout(
            title_x=0.3,
            showlegend=False,  # tu peux mettre True si tu veux afficher la légende
        )

        st.plotly_chart(fig, use_container_width=True)


def render_rankings(df: pd.DataFrame):
    """
    Affiche les classements des villes selon le prix moyen/m² et la surface moyenne.
    Montre le top 10 et le bottom 10 pour chaque critère.
    """
    st.subheader("🏅 Classements des villes")

    # --- Classement par prix au m² ---
    if "ville" in df and "prix_m2" in df:
        classement_prix = (
            df.groupby("ville")["prix_m2"]
            .mean()
            .reset_index()
            .sort_values(by="prix_m2", ascending=True)
        )
        classement_prix.columns = ["Ville", "Prix moyen/m² (€)"]

        # Top 10 moins chères
        top_10_moins_cheres = classement_prix.head(10).reset_index(drop=True)
        top_10_moins_cheres.index += 1  # Pour afficher la position

        # Top 10 plus chères
        top_10_plus_cheres = classement_prix.tail(10).sort_values(by="Prix moyen/m² (€)", ascending=False).reset_index(drop=True)
        top_10_plus_cheres.index += 1

        st.markdown("### 💶 Classement par prix moyen/m²")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**🔹 10 villes les moins chères (€/m²)**")
            st.write(top_10_moins_cheres.style.format({"Prix moyen/m² (€)": "{:,.0f} €"}).to_html(escape=False), unsafe_allow_html=True)
        with col2:
            st.markdown("**🔸 10 villes les plus chères (€/m²)**")
            st.write(top_10_plus_cheres.style.format({"Prix moyen/m² (€)": "{:,.0f} €"}).to_html(escape=False), unsafe_allow_html=True)

    # --- Classement par surface moyenne ---
    if "ville" in df and "surface" in df:
        classement_surface = (
            df.groupby("ville")["surface"]
            .mean()
            .reset_index()
            .sort_values(by="surface", ascending=False)
        )
        classement_surface.columns = ["Ville", "Surface moyenne (m²)"]

        # Top 10 plus grandes
        top_10_plus_grandes = classement_surface.head(10).reset_index(drop=True)
        top_10_plus_grandes.index += 1

        # Top 10 plus petites
        top_10_plus_petites = classement_surface.tail(10).sort_values(by="Surface moyenne (m²)", ascending=True).reset_index(drop=True)
        top_10_plus_petites.index += 1

        st.markdown("### 📏 Classement par surface moyenne")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**🔹 10 villes avec la plus grande surface moyenne**")
            st.write(top_10_plus_grandes.style.format({"Surface moyenne (m²)": "{:,.0f} m²"}).to_html(escape=False), unsafe_allow_html=True)

        with col2:
            st.markdown("**🔸 10 villes avec la plus petite surface moyenne**")
            st.write(top_10_plus_petites.style.format({"Surface moyenne (m²)": "{:,.0f} m²"}).to_html(escape=False), unsafe_allow_html=True)


def render_settings():
    """Affiche les paramètres de l'application."""
    st.subheader("⚙️ Paramètres")
    st.markdown("Aucun paramètre disponible pour le moment.")


# =========================
# Application principale
# =========================
def main():
    apply_custom_css()

    df = load_data()
    if df.empty:
        st.stop()

    render_header()
    filtered_df = sidebar_filters(df)

    render_summary(filtered_df)

    tab1, tab2, tab3, tab4 = st.tabs(["📋 Données", "📊 Visualisations", "🏅 Classements", "⚙️ Paramètres"])
    with tab1:
        render_data_table(filtered_df)
    with tab2:
        render_visualizations(filtered_df)
    with tab3:
        render_rankings(filtered_df)
    with tab4:
        render_settings()


if __name__ == "__main__":
    main()

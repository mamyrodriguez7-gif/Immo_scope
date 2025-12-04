import streamlit as st
import pandas as pd
import plotly.express as px

from immo_scope.visualizer import Visualizer
from immo_scope.map_visualizer import MapVisualizer


# -------------------------------------------------
# CONFIGURATION DU DASHBOARD
# -------------------------------------------------
st.set_page_config(
    page_title="Immo_Scope - Dashboard DVF",
    page_icon="🏡",
    layout="wide"
)

# 🎨 CSS STYLE C — PRO + LISIBLE (bleu/violet clair)
st.markdown(
    """
    <style>

    .stApp {
        background: linear-gradient(180deg, #E8F1FF 0%, #F6F2FF 50%, #FFFFFF 100%);
        color: #1E1E2F;
    }

    h1, h2, h3 {
        color: #3B2E67 !important;
        font-family: "Segoe UI", sans-serif;
        margin-top: 0px;          /* 🔹 enlève la marge au-dessus du titre */
    }

    [data-testid="stSidebar"] {
        background: #C7CEEA;
        color: #1E1E2F;
    }

    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] label {
        color: #1E1E2F !important;
        font-weight: bold;
    }

    /* 🔹 on réduit le padding en haut de la page */
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 1.5rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# LOGO + TITRE
# -------------------------------------------------
st.markdown("""
<h1 style='text-align:center; font-size:40px; margin-top:0;'>
🏡 Immo_Scope – Analyse du marché immobilier français
</h1>
""", unsafe_allow_html=True)


    


# -------------------------------------------------
# CHARGEMENT DES MODULES
# -------------------------------------------------
viz = Visualizer()
map_viz = MapVisualizer()

base_df = viz.df.copy()   # DataFrame complet


# -------------------------------------------------
# SIDEBAR : MENU + FILTRES
# -------------------------------------------------
st.sidebar.markdown("## 📌 Navigation")

page = st.sidebar.radio(
    "Aller à :",
    ["Accueil", "Visualisations", "Carte interactive", "À propos", "Contact"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("## 🎛 Filtres")


# --- FILTRES ---
selected_years = st.sidebar.multiselect(
    "Année",
    options=sorted(base_df["annee"].dropna().unique()),
    default=sorted(base_df["annee"].dropna().unique())
)

selected_types = st.sidebar.multiselect(
    "Type de bien",
    options=sorted(base_df["type_local"].dropna().unique()),
    default=sorted(base_df["type_local"].dropna().unique())
)

selected_deps = st.sidebar.multiselect(
    "Département",
    options=sorted(base_df["code_departement"].dropna().unique()),
    default=sorted(base_df["code_departement"].dropna().unique())
)

# application des filtres :
filtered_df = base_df[
    (base_df["annee"].isin(selected_years)) &
    (base_df["type_local"].isin(selected_types)) &
    (base_df["code_departement"].isin(selected_deps))
]

st.sidebar.markdown(f"**Nombre de lignes après filtre :** {len(filtered_df)}")


# -------------------------------------------------
# FONCTIONS POUR GRAPHIQUES FILTRÉS
# -------------------------------------------------
def plot_property_types(df):
    stats = df["type_local"].value_counts()
    fig = px.pie(
        values=stats.values,
        names=stats.index,
        title="Répartition des types de biens",
        color_discrete_sequence=["#4C5C99", "#C7CEEA", "#90CAF9"]
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_price_distribution(df):
    fig = px.histogram(
        df,
        x="prix_m2",
        nbins=40,
        title="Distribution des prix au m²",
        opacity=0.7,
        color_discrete_sequence=["#4C5C99"]
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_top_cities(df):
    stats = df["nom_commune"].value_counts().head(10)
    fig = px.bar(
        x=stats.values,
        y=stats.index,
        orientation="h",
        title="Top communes par nombre de transactions",
        text=stats.values,
        color=stats.values,
        color_continuous_scale="Blues"
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_price_vs_surface(df):
    sample = df.sample(min(500, len(df)))
    fig = px.scatter(
        sample,
        x="surface_reelle_bati",
        y="prix_m2",
        color="type_local",
        title="Relation surface / prix",
        opacity=0.7
    )
    st.plotly_chart(fig, use_container_width=True)


# -------------------------------------------------
# CONTENU DES PAGES
# -------------------------------------------------

# 🏠 ACCUEIL
if page == "Accueil":
    st.header("Bienvenue 👋")

    st.markdown("""
    <div style='font-size:25px; line-height:1.6;'>
    Ce dashboard présente une analyse complète du marché immobilier français à partir des données DVF 
    (Demandes de Valeurs Foncières), publiées par le Ministère de l’Économie. Ces données regroupent 
    l’ensemble des transactions immobilières réalisées en France, ce qui en fait une source essentielle 
    pour comprendre l’évolution des prix, les dynamiques territoriales et la structure du marché.

    Notre objectif est d’offrir un outil visuel, clair et interactif permettant d’explorer le marché 
    selon différents critères : année, type de bien et département.  
    Les analyses permettent d’identifier les tendances majeures, les zones les plus actives et les 
    disparités géographiques du marché immobilier.

    Ce projet s’inscrit dans le cadre du parcours **Statistique et Science des Données** à 
    l’Université de Montpellier.
    </div>
    """, unsafe_allow_html=True)


# 📊 VISUALISATIONS
elif page == "Visualisations":
    st.header("📊 Visualisations interactives (avec filtres)")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Types de biens", "Distribution des prix", "Top communes", "Surface vs Prix"]
    )

    # -------- 1) TYPES DE BIENS --------
    with tab1:
        st.subheader("Répartition des types de biens")
        fig = plot_property_types(filtered_df)
        if fig:
            fig.update_layout(height=400)  # 🔹 Taille graphique ajustée
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("""
        <div style='font-size:25px; margin-top:10px;'>
        Ce graphique montre la proportion de chaque type de bien dans les transactions DVF.  
        Il permet d’identifier rapidement la dominance des maisons, appartements ou autres biens.
        </div>
        """, unsafe_allow_html=True)

    # -------- 2) DISTRIBUTION DES PRIX --------
    with tab2:
        st.subheader("Distribution des prix au m²")
        fig = plot_price_distribution(filtered_df)
        if fig:
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("""
        <div style='font-size:25px; margin-top:10px;'>
        L’histogramme met en lumière la répartition des prix au m².  
        On visualise clairement le niveau moyen ainsi que les variations extrêmes du marché.
        </div>
        """, unsafe_allow_html=True)

    # -------- 3) TOP COMMUNES --------
    with tab3:
        st.subheader("Communes les plus actives")
        fig = plot_top_cities(filtered_df)
        if fig:
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("""
        <div style='font-size:25px; margin-top:10px;'>
        Ce graphique met en avant les communes enregistrant le plus de transactions.  
        Il révèle les zones où l’activité immobilière est la plus dynamique.
        </div>
        """, unsafe_allow_html=True)

    # -------- 4) SURFACE VS PRIX --------
    with tab4:
        st.subheader("Relation entre surface et prix au m²")
        fig = plot_price_vs_surface(filtered_df)
        if fig:
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("""
        <div style='font-size:25px; margin-top:10px;'>
        Le graphique montre comment la surface d’un bien influe sur son prix au m².  
        Les petites surfaces ressortent souvent comme plus chères proportionnellement.
        </div>
        """, unsafe_allow_html=True)

# 🗺️ CARTE INTERACTIVE
elif page == "Carte interactive":
    st.header("🗺️ Carte – Prix moyen au m² par département")

    # Génération de la carte + réduction de taille
    fig_map = map_viz.create_price_map()
    fig_map.update_layout(height=450)   # 🔹 Réduit la taille de la carte

    st.plotly_chart(fig_map, use_container_width=True)

    # Texte explicatif en taille 22px
    st.markdown("""
    <div style='font-size:25px; margin-top:15px; line-height:1.5;'>
    Cette carte met en évidence les différences de prix moyens au m² entre les départements.  
    Elle permet d’identifier rapidement les zones les plus chères et celles où le marché reste plus accessible.
    </div>
    """, unsafe_allow_html=True)



# ℹ️ À PROPOS
elif page == "À propos":
    st.header("À propos du projet Immo_Scope")

    st.markdown("""
    <div style='font-size:25px; line-height:1.6;'>

    **Immo_Scope** est un projet d’analyse du marché immobilier français basé sur les données 
    DVF (Demandes de Valeurs Foncières). Ces données officielles regroupent toutes les 
    transactions immobilières sur le territoire français et constituent une ressource essentielle 
    pour l'étude des prix, de la dynamique des zones urbaines et rurales, et de l’évolution du marché.

    Le projet vise à :
    - explorer la structure du marché (types de biens, volumes de vente)
    - analyser la distribution des prix au m²
    - identifier les communes les plus actives
    - visualiser les disparités géographiques via une carte interactive
    - offrir un outil interactif de filtrage (année, bien, département)

    Ce tableau de bord permet ainsi d’obtenir une vision claire, pédagogique et interactive de 
    l’immobilier en France, grâce à des visualisations modernes et accessibles.
    
    </div>
    """, unsafe_allow_html=True)


# 📧 CONTACT

elif page == "Contact":
    st.header("Contact & Équipe")

    st.markdown("""
    <div style='font-size:25px; line-height:1.6;'>

    **Équipe du projet Immo_Scope :**  
    - Hadjer BENAISSA — hadjer.benaissa@etu.umontpellier.fr  
    - Léa BENAMEUR — lea.benameur@etu.umontpellier.fr  
    - Rodrigue MAMY — rodrigue.mamy@etu.umontpellier.fr  

    Projet réalisé dans le cadre de la formation  
    <br><strong>Statistique et Science des Données – Université de Montpellier</strong>.
    
    </div>
    """, unsafe_allow_html=True)


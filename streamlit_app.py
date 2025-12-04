import streamlit as st
from immo_scope.visualizer import Visualizer
from immo_scope.map_visualizer import MapVisualizer
# --- CORRECTION DE L'ERREUR : Importation de datetime ---
from datetime import datetime
import pandas as pd
import plotly.express as px

# --- OPTIMISATION CRITIQUE : Utilisation du cache Streamlit ---
@st.cache_resource
def load_visualizers():
    """Instancie et met en cache les classes de visualisation."""
    try:
        # Les classes Visualizer et MapVisualizer contiennent la logique de chargement de dvf_cleaned.csv
        return Visualizer(), MapVisualizer()
    except Exception as e:
        # Pour la démo, on affiche juste l'erreur sans bloquer le lancement si le df est vide.
        return None, None

viz, map_viz = load_visualizers()

st.set_page_config(
    page_title="Immo_Scope Dashboard",
    page_icon="🏡",
    layout="wide"
)

# --- STYLE PROFESSIONNEL : Utiliser des colonnes pour le titre et le statut ---
col_logo, col_title = st.columns([1, 6])
with col_logo:
    # Icône ou logo de projet (peut être remplacé par votre propre image)
    st.image("https://placehold.co/100x100/4ECDC4/white?text=IMMO", width=80) 

with col_title:
    st.title("🏡 Immo_Scope – Analyse du marché immobilier français")
    st.markdown("Plateforme interactive : **Visualisations** | **Qualité** | **Ingénierie de Données**")

st.divider() # Séparateur visuel

# ----------------------------------------------------------------------
# VÉRIFICATION D'ERREUR AU CHARGEMENT
# ----------------------------------------------------------------------

if viz is None or map_viz is None:
    st.error(" Les modules de visualisation ou les données (dvf_cleaned.csv) n'ont pas pu être chargés.")
    st.info("Vérifiez l'exécution du DataLoader (rapport_rodrigue.py) pour générer les données.")
    st.stop() 

# Navigation (Widget principal)
menu = st.sidebar.selectbox(
    "📌 Navigation",
    ["Accueil", "Visualisations", "Carte interactive", "Dashboard complet"]
)

# ----------------------------------------------------------------------
# CONTENU DYNAMIQUES
# ----------------------------------------------------------------------

if menu == "Accueil":
    st.header("1. Présentation et Bilan du Projet 👋")
    
    st.markdown("""
    Cette plateforme est le résultat d'un pipeline complet de Data Science appliqué aux données **DVF (Demandes de Valeurs Foncières) 2023** en France.
    """)

    st.subheader("Objectifs et Répartition des Rôles")
    
    # --- BILAN D'ÉQUIPE (Stylisé) ---
    with st.container(border=True):
        st.markdown("**Statut : Phase de Données Terminée & Dashboard Opérationnel**")
        st.markdown("""
        Ce tableau résume la contribution de chaque membre aux exigences clés du projet :
        """)
        
        st.table(pd.DataFrame({
            'Exigence': ['Nettoyage & POO Avancée', 'Tests Unitaires (Qualité)', 'Dashboard Interactif (Widgets)'],
            'Responsable': ['Rodrigue', 'Léa', 'Hadjer'],
        }))
        
    st.subheader("Résultats Clés de l'Analyse")
    try:
        df_all = viz.df
        st.info(f"**Données :** {len(df_all):,} transactions analysées dans {df_all['nom_commune'].nunique()} communes.")
        st.metric("Prix Moyen / m²", f"{viz.data['metrics']['avg_price_m2']:.0f} €", 
                  delta=f"Surface Moyenne: {viz.df['surface_reelle_bati'].mean():.0f} m²")
    except Exception:
        pass # Affichage de base en cas d'échec des métriques

elif menu == "Visualisations":
    st.header("2. Analyse Détaillée des Tendances")

    # --- ACCÈS AUX DONNÉES ET FILTRES (DEPUIS LE VISUALIZER) ---
    df_all = viz.df.copy()

    try:
        # Accéder au DataFrame pour calculer les villes les plus fréquentes
        if not df_all.empty and 'nom_commune' in df_all.columns:
            top_cities = df_all['nom_commune'].value_counts().head(5).index.tolist()
            st.caption(f"Analyse basée sur {len(df_all['nom_commune'].unique())} communes. Top 5 : {', '.join(top_cities)}")
    except Exception as e:
        st.warning(f"Erreur lors de l'accès aux données pour l'aperçu : {e}")

    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Types de biens", "Distribution des prix", "Top communes", "Surface vs Prix"]
    )

    with tab1:
        st.subheader("Répartition par type de bien")
        st.plotly_chart(viz.create_property_types_chart(), use_container_width=True)
        st.caption("Le graphique montre la répartition entre Maisons et Appartements.")

    with tab2:
        st.subheader("Distribution des Prix au m²")
        st.plotly_chart(viz.create_price_distribution(), use_container_width=True)
        st.caption("Ligne rouge : Prix moyen national. Utile pour identifier les extrêmes et la concentration des prix.")

    with tab3:
        st.subheader("Top Communes par transactions")
        st.plotly_chart(viz.create_top_cities_chart(), use_container_width=True)
        st.caption("Classement des villes ayant le plus grand volume de transactions DVF.")

    with tab4:
        st.subheader("Relation Surface (m²) vs Prix au m² (€)")
        st.plotly_chart(viz.create_price_vs_surface(), use_container_width=True)
        st.caption("Le nuage de points permet de détecter les corrélations ou les anomalies de prix par rapport à la taille du bien.")

elif menu == "Carte interactive":
    st.header("3. Carte Interactive des Transactions")
    
    # --- ACCÈS AUX DONNÉES ET WIDGETS ---
    df_map_source = viz.df.copy()
    
    # 1. Widget de sélection du département (Pour filtrer la carte)
    try:
        departments = df_map_source['code_departement'].unique().tolist()
        departments.sort()
        
        selected_dept = st.selectbox(
            "Filtrer la carte par Département :",
            options=["Tous les départements"] + departments,
            key="map_dept_select"
        )
        
        # 2. Application du filtre
        if selected_dept != "Tous les départements":
            df_filtered = df_map_source[df_map_source['code_departement'] == selected_dept].copy()
            
            # Affichage des villes filtrées (Confirmation pour l'utilisateur)
            top_cities_dept = df_filtered['nom_commune'].value_counts().head(5).index.tolist()
            st.info(f"Les 5 villes les plus actives dans le **{selected_dept}** sont : **{', '.join(top_cities_dept)}**.")
        else:
            df_filtered = df_map_source
        
        st.markdown("---")
        
        # 3. Affichage de la carte (utilise le Scatter Mapbox pour les noms de ville)
        
        if len(df_filtered) > 0:
            st.subheader("Transactions individuelles")
            
            # Appel de la méthode Scatter Map dans MapVisualizer pour les villes
            scatter_fig = map_viz.create_scatter_map(df_filtered) 
            st.plotly_chart(scatter_fig, use_container_width=True)
            
            st.caption("Chaque point représente une transaction. Survolez-le pour voir le nom de la commune et les détails.")
        else:
             st.warning("Aucune transaction trouvée pour ce filtre.")

    except Exception as e:
        st.error(f"Erreur lors de l'affichage de la carte: {e}")
        st.info("Vérifiez que les classes MapVisualizer et Visualizer ont bien la colonne 'code_departement'.")


elif menu == "Dashboard complet":
    st.header("4. Synthèse Globale du Marché")
    
    # --- AJOUT DU FILTRE ET DE LA CARTE INTERACTIVE ---
    df_map_source = viz.df.copy()
    
    # 1. Widget de sélection du département
    try:
        departments = df_map_source['code_departement'].unique().tolist()
        departments.sort()
        
        selected_dept = st.selectbox(
            "Filtrer les transactions par Département :",
            options=["Tous les départements"] + departments,
            key="dashboard_dept_select" # Nouvelle clé pour éviter les conflits
        )
        
        # 2. Application du filtre
        if selected_dept != "Tous les départements":
            df_filtered = df_map_source[df_map_source['code_departement'] == selected_dept].copy()
            st.info(f"Filtre actif : Affichage de {len(df_filtered):,} transactions pour le département **{selected_dept}**.")
        else:
            df_filtered = df_map_source
        
        st.divider()

    except Exception as e:
        st.error(f"Erreur lors de l'application du filtre : {e}")
        df_filtered = viz.df.copy()
        
    # --- SYNTHÈSE DU PRIX MOYEN PAR DÉPARTEMENT (CARTE CHOROPLÈTHE GLOBALE) ---
    with st.container(border=True):
        st.subheader("Prix Moyen au m² par Département (Vue Agrégée)")
        st.plotly_chart(map_viz.create_price_map(), use_container_width=True)
        st.caption("Cette carte choroplèthe offre une vue nationale et n'est pas affectée par le filtre départemental ci-dessus.")

    # --- CARTE INTERACTIVE FILTRÉE ---
    st.subheader("Transactions Filtrées")
    if len(df_filtered) > 0:
        # Appel de la méthode Scatter Map pour les villes
        scatter_fig = map_viz.create_scatter_map(df_filtered) 
        st.plotly_chart(scatter_fig, use_container_width=True)
        st.caption("Carte détaillée des transactions, mise à jour par le filtre du département sélectionné.")
    else:
        st.warning("Aucune transaction trouvée pour le département sélectionné.")

    # --- VUE DÉTAILLÉE DU MARCHÉ ---
    st.subheader("Rapport Multi-Dimensionnel Global")
    # Pour l'aperçu général, on garde l'appel à la fonction d'origine pour ne pas impacter le travail de Rodrigue, 
    # mais vous pouvez choisir d'utiliser df_filtered ici si la méthode supporte le filtrage.
    st.plotly_chart(viz.create_dashboard_overview(), use_container_width=True)
    st.caption("Vue compilée des principales tendances de prix et de répartition.")
    
st.sidebar.markdown("---")
st.sidebar.caption(f"Dernière mise à jour : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


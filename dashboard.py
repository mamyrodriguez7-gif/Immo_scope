# dashboard.py - VERSION COMPLÈTE AVEC ANALYSE MULTI-ANNÉES
import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

# Ajouter le package immo_scope au chemin
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # Importer depuis votre package
    from immo_scope.data_loader import DataLoader
    from immo_scope.visualizer import PlotVisualizer
    IMPORT_SUCCESS = True
except ImportError as e:
    IMPORT_SUCCESS = False

# Configuration de la page
st.set_page_config(
    page_title="ImmoScope - Dashboard Immobilier",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏠 ImmoScope - Analyse du Marché Immobilier Français")
st.markdown("**Dashboard interactif utilisant les données DVF 2021-2024 - Analyses multi-années**")

def load_data():
    """Charge les données depuis le fichier nettoyé"""
    try:
        df = pd.read_csv("data/processed/dvf_cleaned.csv")
        
        # Vérifier si la colonne année existe, sinon l'ajouter (rétrocompatibilité)
        if 'annee' not in df.columns:
            df['annee'] = 2024  # Année par défaut pour les anciennes données
            
        st.success(f"✅ {len(df):,} transactions chargées ({df['annee'].nunique()} années)")
        return df
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement: {e}")
        st.info("💡 Utilisez le DataLoader pour télécharger les données multi-années")
        return None

def main():
    # Charger les données
    df = load_data()
    
    if df is None:
        st.stop()
    
    # Afficher le statut des imports
    if IMPORT_SUCCESS:
        st.sidebar.success("✅ Package immo_scope importé")
        loader = DataLoader()
        visualizer = PlotVisualizer()
    else:
        st.sidebar.warning("⚠️ Mode basique - imports avancés non disponibles")
    
    # ===== SIDEBAR - FILTRES =====
    st.sidebar.header("🎯 Filtres Principaux")
    
    # Filtre par année (si données multi-années)
    if 'annee' in df.columns and df['annee'].nunique() > 1:
        annees = sorted(df['annee'].unique())
        selected_years = st.sidebar.multiselect(
            "Période d'analyse :",
            annees,
            default=annees
        )
        df = df[df['annee'].isin(selected_years)]
        st.sidebar.info(f"📅 {len(selected_years)} année(s) sélectionnée(s)")
    
    # Filtre par département
    st.sidebar.header("🏛️ Analyse par Département")
    
    # Créer automatiquement la liste des départements disponibles
    depts_codes = sorted(df['code_departement'].unique())
    
    # Mapping des codes aux noms
    noms_departements = {
        '75': 'Paris (75)',
        '13': 'Marseille (13)', 
        '69': 'Lyon (69)',
        '33': 'Bordeaux (33)',
        '34': 'Montpellier (34)',
        '59': 'Lille (59)',
        '31': 'Toulouse (31)',
        '06': 'Nice (06)',
        '44': 'Nantes (44)',
        '67': 'Strasbourg (67)'
    }
    
    # Créer la liste des options
    options_departements = ["Tous"]
    for code in depts_codes:
        if code in noms_departements:
            options_departements.append(noms_departements[code])
        else:
            options_departements.append(f"Département {code}")
    
    dept_choice = st.sidebar.selectbox(
        "Choisir un département :",
        options_departements
    )
    
    if dept_choice != "Tous":
        # Trouver le code du département sélectionné
        code_dept = dept_choice.split('(')[-1].replace(')', '') if '(' in dept_choice else dept_choice.replace('Département ', '')
        df_dept = df[df['code_departement'] == code_dept]
        st.info(f"🏛️ Analyse département : {dept_choice} ({len(df_dept):,} transactions)")
    else:
        df_dept = df
    
    # Filtre par ville
    st.sidebar.header("🏙️ Focus Ville")
    
    # Prendre les 8 villes avec le plus de transactions
    top_villes = df_dept['nom_commune'].value_counts().head(8).index.tolist()
    
    ville_choice = st.sidebar.selectbox(
        "Choisir une ville à analyser :",
        ["Toutes"] + top_villes
    )
    
    if ville_choice != "Toutes":
        df_ville = df_dept[df_dept['nom_commune'] == ville_choice]
        st.info(f"🔍 Analyse focus : {ville_choice} ({len(df_ville):,} transactions)")
    else:
        df_ville = df_dept
    
    # Utiliser les données filtrées selon le choix
    data_filtree = df_ville
    
    # FILTRES AVANCÉS
    st.sidebar.header("🔧 Filtres Avancés")
    
    min_price, max_price = st.sidebar.slider(
        "Prix au m² (€)", 
        0, 20000, 
        (0, int(min(data_filtree['prix_m2'].max(), 20000)))
    )
    
    min_surface, max_surface = st.sidebar.slider(
        "Surface (m²)", 
        0, 500, 
        (0, 150)
    )
    
    filtered_df = data_filtree[
        (data_filtree['prix_m2'].between(min_price, max_price)) &
        (data_filtree['surface_reelle_bati'].between(min_surface, max_surface))
    ]
    
    st.sidebar.info(f"**{len(filtered_df):,}** transactions après filtrage")
    
    # ===== INDICATEURS CLÉS =====
    st.header("📊 Indicateurs Clés")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        prix_moyen = filtered_df['prix_m2'].mean()
        st.metric("Prix moyen au m²", f"{prix_moyen:.0f} €")
    
    with col2:
        surface_moyenne = filtered_df['surface_reelle_bati'].mean()
        st.metric("Surface moyenne", f"{surface_moyenne:.0f} m²")
    
    with col3:
        budget_moyen = filtered_df['valeur_fonciere'].mean()
        st.metric("Budget moyen", f"{budget_moyen:.0f} €")
    
    with col4:
        st.metric("Transactions analysées", f"{len(filtered_df):,}")
    
    # ===== ANALYSE TEMPORELLE =====
    if 'annee' in filtered_df.columns and filtered_df['annee'].nunique() > 1:
        st.header("📅 Analyse Temporelle")
        
        # Évolution des prix
        prix_par_annee = filtered_df.groupby('annee')['prix_m2'].mean().round(0).reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Évolution du prix au m²")
            if IMPORT_SUCCESS:
                try:
                    temporal_figs = visualizer.plot_temporal_evolution(filtered_df)
                    if temporal_figs and 'price_evolution' in temporal_figs:
                        st.plotly_chart(temporal_figs['price_evolution'], width='stretch')
                    else:
                        fig_evolution = px.line(
                            prix_par_annee, x='annee', y='prix_m2',
                            title="Évolution du prix moyen au m²",
                            labels={'prix_m2': 'Prix au m² (€)', 'annee': 'Année'}
                        )
                        st.plotly_chart(fig_evolution, width='stretch')
                except:
                    fig_evolution = px.line(prix_par_annee, x='annee', y='prix_m2')
                    st.plotly_chart(fig_evolution, width='stretch')
            else:
                fig_evolution = px.line(prix_par_annee, x='annee', y='prix_m2')
                st.plotly_chart(fig_evolution, width='stretch')
        
        with col2:
            st.subheader("Volume des transactions")
            transactions_par_annee = filtered_df['annee'].value_counts().sort_index().reset_index()
            transactions_par_annee.columns = ['annee', 'count']
            
            if IMPORT_SUCCESS:
                try:
                    if temporal_figs and 'volume_evolution' in temporal_figs:
                        st.plotly_chart(temporal_figs['volume_evolution'], width='stretch')
                    else:
                        fig_volume = px.bar(
                            transactions_par_annee, x='annee', y='count',
                            title="Volume des transactions par année",
                            labels={'count': 'Nombre de transactions', 'annee': 'Année'}
                        )
                        st.plotly_chart(fig_volume, width='stretch')
                except:
                    fig_volume = px.bar(transactions_par_annee, x='annee', y='count')
                    st.plotly_chart(fig_volume, width='stretch')
            else:
                fig_volume = px.bar(transactions_par_annee, x='annee', y='count')
                st.plotly_chart(fig_volume, width='stretch')
    
    # ===== VISUALISATIONS PRINCIPALES =====
    st.header("📈 Visualisations Interactives")
    
    # Ligne 1 : Distribution et Top villes
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribution des prix au m²")
        if IMPORT_SUCCESS:
            try:
                fig_dist = visualizer.plot_price_distribution(filtered_df)
                st.plotly_chart(fig_dist, width='stretch')
            except:
                st.bar_chart(filtered_df['prix_m2'].value_counts().head(20))
        else:
            st.bar_chart(filtered_df['prix_m2'].value_counts().head(20))
    
    with col2:
        st.subheader("Top 10 villes par transactions")
        ville_counts = filtered_df['nom_commune'].value_counts().head(10)
        if IMPORT_SUCCESS:
            try:
                fig_villes = px.bar(
                    ville_counts,
                    title="Villes les plus actives sur le marché",
                    labels={'value': 'Nombre de transactions', 'index': 'Ville'}
                )
                st.plotly_chart(fig_villes, width='stretch')
            except:
                st.bar_chart(ville_counts)
        else:
            st.bar_chart(ville_counts)
    
    # Ligne 2 : Relation prix/surface et Types de biens
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Relation prix vs surface")
        if IMPORT_SUCCESS:
            try:
                fig_scatter = visualizer.plot_price_vs_surface(filtered_df.head(500))  # Limiter pour performance
                st.plotly_chart(fig_scatter, width='stretch')
            except:
                st.scatter_chart(filtered_df[['surface_reelle_bati', 'prix_m2']].head(200))
        else:
            st.scatter_chart(filtered_df[['surface_reelle_bati', 'prix_m2']].head(200))
    
    with col4:
        st.subheader("Types de biens")
        if 'type_local' in filtered_df.columns:
            if IMPORT_SUCCESS:
                try:
                    fig_pie = visualizer.plot_property_types(filtered_df)
                    if fig_pie:
                        st.plotly_chart(fig_pie, width='stretch')
                except:
                    type_counts = filtered_df['type_local'].value_counts()
                    fig_pie_fallback = px.pie(type_counts, values=type_counts.values, names=type_counts.index)
                    st.plotly_chart(fig_pie_fallback, width='stretch')
            else:
                type_counts = filtered_df['type_local'].value_counts()
                st.bar_chart(type_counts)
        else:
            st.info("Information sur les types de biens non disponible")
    
    # ===== DONNÉES DÉTAILLÉES =====
    st.header("📋 Données Détailées")
    
    # Statistiques par ville
    ville_stats = filtered_df.groupby('nom_commune').agg({
        'prix_m2': ['mean', 'count'],
        'surface_reelle_bati': 'mean',
        'valeur_fonciere': 'mean'
    }).round(0)
    
    ville_stats.columns = ['Prix_m2_moyen', 'Nb_transactions', 'Surface_moyenne', 'Budget_moyen']
    ville_stats = ville_stats.sort_values('Nb_transactions', ascending=False)
    
    st.dataframe(ville_stats.head(20), width='stretch')
    
    # ===== TÉLÉCHARGEMENT DONNÉES MULTI-ANNÉES =====
    st.sidebar.header("🔄 Mise à jour des données")
    
    if st.sidebar.button("📥 Télécharger données multi-années"):
        if IMPORT_SUCCESS:
            with st.spinner("Téléchargement des données 2021-2024..."):
                try:
                    df_nouvelles = loader.download_dvf_data(years=[2024, 2023, 2022, 2021], sample_per_year=15000)
                    if df_nouvelles is not None:
                        loader.save_processed_data(df_nouvelles)
                        st.sidebar.success("✅ Données mises à jour!")
                        st.rerun()
                    else:
                        st.sidebar.error("❌ Échec du téléchargement")
                except Exception as e:
                    st.sidebar.error(f"❌ Erreur: {e}")
        else:
            st.sidebar.warning("Package immo_scope non disponible")
    
        # ===== CONTEXTE PÉDAGOGIQUE =====
    st.sidebar.markdown("---")
    st.sidebar.header("🎓 Contexte Pédagogique")
    st.sidebar.info("""
    **Projet développement logiciel**
    
    **Fonctionnalités avancées :**
    ✅ Données multi-années (2021-2024)
    ✅ Analyses temporelles
    ✅ Dashboard interactif Streamlit
    ✅ Pipeline de nettoyage des données
    ✅ Architecture modulaire Python
    
    **Équipe :** Rodrigue, Hadjer, Léa
    
    **GitHub :** https://github.com/mamyrodriguez7-gif/Immo_scope
    """)

# ⭐⭐ CORRECTION ICI - AJOUTEZ LE TRY ⭐⭐
try:
    if __name__ == "__main__":
        main()
except Exception as e:
    st.error(f"❌ Erreur: {e}")
# dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(
    page_title="ImmoScope - Dashboard Immobilier",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 ImmoScope - Analyse du Marché Immobilier Français")
st.markdown("**Dashboard interactif utilisant les données DVF 2024 - Analyses territoriales**")

# Charger les données
try:
    df = pd.read_csv("data/processed/dvf_cleaned.csv")
    st.success(f"✅ {len(df)} transactions chargées")
    
    # ANALYSE PAR VILLE
    st.sidebar.header("🎯 Focus Ville")
    
    # Prendre les 8 villes avec le plus de transactions
    top_villes = df['nom_commune'].value_counts().head(8).index.tolist()
    
    ville_choice = st.sidebar.selectbox(
        "Choisir une ville à analyser :",
        ["France entière"] + top_villes
    )
    
    if ville_choice != "France entière":
        df_ville = df[df['nom_commune'] == ville_choice]
        st.info(f"🔍 Analyse focus : {ville_choice} ({len(df_ville)} transactions)")
    else:
        df_ville = df
    
    # ANALYSE PAR DÉPARTEMENT
    st.sidebar.header("🏛️ Analyse par Département")
    
    # Départements français principaux avec leurs villes principales
    departements = {
        '34': 'Hérault (Montpellier)',
        '75': 'Paris',
        '13': 'Bouches-du-Rhône (Marseille)',
        '69': 'Rhône (Lyon)',
        '33': 'Gironde (Bordeaux)',
        '59': 'Nord (Lille)',
        '31': 'Haute-Garonne (Toulouse)',
        '67': 'Bas-Rhin (Strasbourg)',
        '44': 'Loire-Atlantique (Nantes)',
        '06': 'Alpes-Maritimes (Nice)'
    }
    
    # Vérifier quels départements sont dans nos données
    depts_disponibles = [dept for dept in departements.values() 
                        if dept.split(' ')[0] in df['code_departement'].values]
    
    dept_choice = st.sidebar.selectbox(
        "Choisir un département :",
        ["Tous"] + depts_disponibles
    )
    
    if dept_choice != "Tous":
        # Trouver le code du département sélectionné
        code_dept = [code for code, nom in departements.items() if nom == dept_choice][0]
        df_dept = df[df['code_departement'] == code_dept]
        st.info(f"🏛️ Analyse département : {dept_choice} ({len(df_dept)} transactions)")
    else:
        df_dept = df
    
    # FILTRES COMMUNS
    st.sidebar.header("🔧 Filtres Avancés")
    
    # Utiliser les données filtrées selon le choix
    if ville_choice != "France entière":
        data_filtree = df_ville
    elif dept_choice != "Tous":
        data_filtree = df_dept
    else:
        data_filtree = df
    
    min_price, max_price = st.sidebar.slider(
        "Prix au m² (€)", 
        0, 15000, 
        (0, int(data_filtree['prix_m2'].max()))
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
    
    st.sidebar.info(f"**{len(filtered_df)}** transactions filtrées")
    
    # INDICATEURS CLÉS
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
    
    # ANALYSE COMPARATIVE SI VILLE SÉLECTIONNÉE
    if ville_choice != "France entière":
        st.header(f"🏙️ Analyse Comparative : {ville_choice}")
        
        prix_france = df['prix_m2'].mean()
        prix_ville = filtered_df['prix_m2'].mean()
        ecart_percent = ((prix_ville - prix_france) / prix_france) * 100
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                f"Prix moyen {ville_choice}",
                f"{prix_ville:.0f} €/m²",
                delta=f"{ecart_percent:+.1f}% vs France"
            )
        with col2:
            st.metric(
                "Niveau de prix",
                "Au-dessus" if ecart_percent > 0 else "En-dessous",
                delta=f"{abs(ecart_percent):.1f}% de la moyenne"
            )
    
    # ANALYSE PAR DÉPARTEMENT SI SÉLECTIONNÉ
    if dept_choice != "Tous":
        st.header(f"🏛️ Analyse Départementale : {dept_choice}")
        
        prix_dept = filtered_df['prix_m2'].mean()
        prix_france = df['prix_m2'].mean()
        ecart_dept = ((prix_dept - prix_france) / prix_france) * 100
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Prix moyen département", f"{prix_dept:.0f} €/m²")
        with col2:
            st.metric("Écart vs France", f"{ecart_dept:+.1f}%")
        with col3:
            # Dynamisme du marché
            transactions_par_ville = filtered_df['nom_commune'].nunique()
            st.metric("Villes actives", transactions_par_ville)
    
    # VISUALISATIONS
    st.header("📈 Visualisations Interactives")
    
    # Ligne 1 : Distribution des prix et Top villes
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribution des prix au m²")
        fig1 = px.histogram(
            filtered_df, 
            x='prix_m2', 
            nbins=30,
            title=f"Distribution des prix - {ville_choice if ville_choice != 'France entière' else 'France'}"
        )
        st.plotly_chart(fig1, width='stretch')
    
    with col2:
        st.subheader("Top 10 villes par transactions")
        ville_counts = filtered_df['nom_commune'].value_counts().head(10)
        fig2 = px.bar(
            ville_counts,
            title="Villes les plus actives sur le marché"
        )
        st.plotly_chart(fig2, width='stretch')
    
    # Ligne 2 : Relation prix/surface et Types de biens
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Relation prix vs surface")
        fig3 = px.scatter(
            filtered_df.head(200),  # Limiter pour performance
            x='surface_reelle_bati',
            y='prix_m2',
            title="Relation surface et prix au m²",
            labels={'surface_reelle_bati': 'Surface (m²)', 'prix_m2': 'Prix au m² (€)'}
        )
        st.plotly_chart(fig3, width='stretch')
    
    with col4:
        st.subheader("Types de biens")
        if 'type_local' in filtered_df.columns:
            type_counts = filtered_df['type_local'].value_counts()
            fig4 = px.pie(
                type_counts,
                values=type_counts.values,
                names=type_counts.index,
                title="Répartition par type de bien"
            )
            st.plotly_chart(fig4, width='stretch')
        else:
            # Analyse par département à la place
            dept_counts = filtered_df['code_departement'].value_counts().head(8)
            fig4 = px.pie(
                dept_counts,
                values=dept_counts.values,
                names=dept_counts.index,
                title="Répartition par département"
            )
            st.plotly_chart(fig4, width='stretch')
    
    # DONNÉES DÉTAILLÉES
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
    
    # CONTEXTE PÉDAGOGIQUE
    st.sidebar.markdown("---")
    st.sidebar.header("🎓 Contexte Pédagogique")
    st.sidebar.info("""
    **Projet développement logiciel**
    
    **Fonctionnalités implémentées :**
    ✅ Application Streamlit exécutable
    ✅ Analyses multi-niveaux (ville/département)
    ✅ Visualisations interactives Plotly
    ✅ Filtres dynamiques
    ✅ Comparaisons territoriales
    ✅ Architecture modulaire Python
    
    **Équipe :** Rodrigue, Hadjer, Léa
    """)

except Exception as e:
    st.error(f"❌ Erreur: {e}")
    st.info("Vérifiez que le fichier 'data/processed/dvf_cleaned.csv' existe")
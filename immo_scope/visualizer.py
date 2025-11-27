# 📁 immo_scope/visualizer.py - VERSION CORRIGÉE
"""
MODULE DE VISUALISATION - HADJER
Développement du dashboard interactif
"""
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

class Visualizer:
    def __init__(self):
        """Initialise le visualizer avec les données"""
        # Chemins corrigés
        current_dir = Path(__file__).parent
        project_root = current_dir.parent
        
        dashboard_file = project_root / "data" / "reports" / "dashboard_data.json"
        data_file = project_root / "data" / "processed" / "dvf_cleaned.csv"
        
        print("🎨 Visualizer initialisé avec succès!")
        
        # Charger les données agrégées
        with open(dashboard_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        print("✅ Données dashboard chargées")
        
        # Charger les données complètes
        self.df = pd.read_csv(data_file)
        print(f"✅ {len(self.df)} transactions chargées")
        
        # Afficher un résumé
        print(f"📊 Résumé: {self.data['metrics']['total_transactions']} transactions")
        print(f"💰 Prix moyen: {self.data['metrics']['avg_price_m2']} €/m²")
    
    def create_property_types_chart(self):
        """Crée un camembert des types de biens - HADJER PEUT PERSONNALISER"""
        types_data = self.data['visualization_data']['property_types']
        
        fig = px.pie(
            values=list(types_data.values()),
            names=list(types_data.keys()),
            title="🏠 Répartition des types de biens immobiliers en France",
            color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#FFD166']  # 🎨 HADJER CHANGE LES COULEURS
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate="<b>%{label}</b><br>%{value} transactions<br>%{percent}",
            textfont_size=14
        )
        
        fig.update_layout(
            title_x=0.5,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        return fig
    
    def create_price_distribution(self):
        """Crée un histogramme des prix au m² - HADJER PEUT AMÉLIORER"""
        fig = px.histogram(
            self.df,
            x='prix_m2',
            nbins=30,
            title="📊 Distribution des prix au m² en France",
            labels={'prix_m2': 'Prix au m² (€)'},
            color_discrete_sequence=['#45B7D1'],  # 🎨 HADJER CHANGE LA COULEUR
            opacity=0.8
        )
        
        # Ajouter une ligne pour le prix moyen
        avg_price = self.df['prix_m2'].mean()
        fig.add_vline(x=avg_price, line_dash="dash", line_color="red", 
                     annotation_text=f"Moyenne: {avg_price:.0f}€")
        
        fig.update_layout(
            xaxis_title="Prix au m² (€)",
            yaxis_title="Nombre de transactions",
            showlegend=False,
            title_x=0.5
        )
        
        return fig
    
    def create_top_cities_chart(self, top_n=10):
        """Crée un graphique des top communes - HADJER PEUT AJOUTER DES EFFETS"""
        city_counts = self.df['nom_commune'].value_counts().head(top_n)
        
        fig = px.bar(
            x=city_counts.values,
            y=city_counts.index,
            orientation='h',
            title=f"🏆 Top {top_n} communes par nombre de transactions",
            labels={'x': 'Nombre de transactions', 'y': 'Commune'},
            color=city_counts.values,
            color_continuous_scale='Viridis',  # 🎨 HADJER ESSAYE D'AUTRES ÉCHELLES
            text=city_counts.values
        )
        
        fig.update_traces(
            texttemplate='%{text} transactions',
            textposition='outside'
        )
        
        fig.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            title_x=0.5,
            showlegend=False
        )
        
        return fig
    
    def create_price_vs_surface(self):
        """Graphique prix vs surface - HADJER PEUT AJOUTER DES INTERACTIONS"""
        # Prendre un échantillon pour de meilleures performances
        sample_df = self.df.sample(min(200, len(self.df)))
        
        fig = px.scatter(
            sample_df,
            x='surface_reelle_bati',
            y='prix_m2',
            color='type_local',
            title='🏘️ Relation entre surface et prix au m²',
            labels={
                'surface_reelle_bati': 'Surface (m²)',
                'prix_m2': 'Prix au m² (€)',
                'type_local': 'Type de bien'
            },
            hover_data=['nom_commune'],  # 🎨 HADJER PEUT AJOUTER PLUS D'INFOS
            size_max=15
        )
        
        fig.update_layout(
            title_x=0.5,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        return fig
    
    def create_dashboard_overview(self):
        """Crée un dashboard complet - HADJER PEUT RECONCEVOIR LE LAYOUT"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                '🏠 Répartition types de biens', 
                '💰 Distribution prix au m²',
                '🏆 Top communes',
                '📐 Surface vs Prix'
            ),
            specs=[
                [{"type": "domain"}, {"type": "xy"}],
                [{"type": "xy"}, {"type": "xy"}]
            ]
        )
        
        # Graphique 1: Camembert types de biens
        pie_fig = self.create_property_types_chart()
        for trace in pie_fig.data:
            fig.add_trace(trace, row=1, col=1)
        
        # Graphique 2: Histogramme prix
        hist_fig = self.create_price_distribution()
        for trace in hist_fig.data:
            fig.add_trace(trace, row=1, col=2)
        
        # Graphique 3: Top communes
        bar_fig = self.create_top_cities_chart(8)
        for trace in bar_fig.data:
            fig.add_trace(trace, row=2, col=1)
        
        # Graphique 4: Surface vs Prix
        scatter_fig = self.create_price_vs_surface()
        for trace in scatter_fig.data:
            fig.add_trace(trace, row=2, col=2)
        
        fig.update_layout(
            height=900, 
            title_text="📊 Dashboard Immobilier France - Vue d'ensemble",
            showlegend=True,
            title_x=0.5
        )
        
        return fig

# TEST DU MODULE - HADJER PEUT TESTER CHAQUE FONCTION
if __name__ == "__main__":
    print("🧪 HADJER - Test du Visualizer...")
    print("=" * 50)
    
    # Initialiser le visualizer
    viz = Visualizer()
    
    # Menu de test interactif
    print("\n🎯 QUE VEUX-TU TESTER ?")
    print("1. Camembert types de biens")
    print("2. Histogramme prix")
    print("3. Top communes") 
    print("4. Graphique surface vs prix")
    print("5. Dashboard complet")
    print("6. Tout tester")
    
    try:
        choix = input("\n👉 Ton choix (1-6): ").strip()
        
        if choix in ['1', '6']:
            print("\n📊 Test camembert...")
            fig1 = viz.create_property_types_chart()
            fig1.show()
            
        if choix in ['2', '6']:
            print("\n💰 Test histogramme...")
            fig2 = viz.create_price_distribution()
            fig2.show()
            
        if choix in ['3', '6']:
            print("\n🏆 Test top communes...")
            fig3 = viz.create_top_cities_chart()
            fig3.show()
            
        if choix in ['4', '6']:
            print("\n📐 Test surface vs prix...")
            fig4 = viz.create_price_vs_surface()
            fig4.show()
            
        if choix in ['5', '6']:
            print("\n🎨 Test dashboard complet...")
            dashboard = viz.create_dashboard_overview()
            dashboard.show()
            
        print("\n✅ Tests terminés! Hadjer peut maintenant personnaliser les graphiques.")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        print("💡 Hadjer peut debugger en regardant l'erreur")
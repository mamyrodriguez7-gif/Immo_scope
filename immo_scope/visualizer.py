
"""
MODULE DE VISUALISATION
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
        current_dir = Path(__file__).parent
        project_root = current_dir.parent
        
        dashboard_file = project_root / "data" / "reports" / "dashboard_data.json"
        data_file = project_root / "data" / "processed" / "dvf_cleaned.csv"
        
        print("Visualizer initialisé avec succès!")
        
        #Les données agrégées
        with open(dashboard_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        print("Données dashboard chargées")
        
        #Les données complètes
        self.df = pd.read_csv(data_file)
        print(f"{len(self.df)} transactions chargées")
        
        # Afficher un résumé
        print(f"Résumé: {self.data['metrics']['total_transactions']} transactions")
        print(f"Prix moyen: {self.data['metrics']['avg_price_m2']} €/m²")
    
    # --------------------------------------------------------------------
    #  Graphique  : Répartition des types de biens
    # --------------------------------------------------------------------
    def create_property_types_chart(self):

        if "type_local" not in self.df.columns:
            print(" Colonne 'type_local' manquante")
            return None

        stats = self.df["type_local"].value_counts()

        fig = px.pie(
            values=stats.values,
            names=stats.index,
            title=" Répartition des types de biens immobiliers",
            color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#FFD166']
        )

        fig.update_traces(textinfo='percent+label', textposition='inside')
        fig.update_layout(title_x=0.5)

        return fig


    # --------------------------------------------------------------------
    #  Graphique : Distribution des prix
    # --------------------------------------------------------------------
    def create_price_distribution(self):

        fig = px.histogram(
            self.df,
            x='prix_m2',
            nbins=40,
            title=" Distribution des prix au m² en France",
            color_discrete_sequence=['#45B7D1'],
            opacity=0.7
        )

        avg_price = self.df['prix_m2'].mean()
        fig.add_vline(
            x=avg_price, line_dash="dash", line_color="red",
            annotation_text=f"Moyenne : {avg_price:.0f}€"
        )

        fig.update_layout(title_x=0.5)

        return fig


    # --------------------------------------------------------------------
    #  Graphique : Top communes
    # --------------------------------------------------------------------
    def create_top_cities_chart(self, top_n=10):

        stats = self.df["nom_commune"].value_counts().head(top_n)

        fig = px.bar(
            x=stats.values,
            y=stats.index,
            orientation='h',
            labels={'x': 'Nombre de transactions', 'y': 'Commune'},
            title=f" Top {top_n} communes par transactions",
            color=stats.values,
            color_continuous_scale="Viridis",
            text=stats.values
        )

        fig.update_layout(title_x=0.5)
        fig.update_traces(textposition='outside')

        return fig


    # --------------------------------------------------------------------
    #  Graphique : Surface vs Prix
    # --------------------------------------------------------------------
    def create_price_vs_surface(self):

        sample_df = self.df.sample(min(300, len(self.df)))

        fig = px.scatter(
            sample_df,
            x='surface_reelle_bati',
            y='prix_m2',
            color='type_local',
            title=' Relation entre surface et prix au m²',
            labels={
                'surface_reelle_bati': 'Surface (m²)',
                'prix_m2': 'Prix au m² (€)',
                'type_local': 'Type de bien'
            },
            hover_data=['nom_commune'],
        )

        fig.update_layout(title_x=0.5)
        return fig


    # --------------------------------------------------------------------
    #  Dashboard complet
    # --------------------------------------------------------------------
    def create_dashboard_overview(self):

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                ' Types de biens',
                ' Distribution prix',
                ' Top communes',
                ' Surface vs Prix'
            ],
            specs=[[{"type": "domain"}, {"type": "xy"}],
                   [{"type": "xy"}, {"type": "xy"}]]
        )

        # Ajouter chaque graphique dans le dashboard
        charts = [
            self.create_property_types_chart(),
            self.create_price_distribution(),
            self.create_top_cities_chart(8),
            self.create_price_vs_surface()
        ]

        positions = [(1,1), (1,2), (2,1), (2,2)]

        for chart, pos in zip(charts, positions):
            if chart:
                for trace in chart.data:
                    fig.add_trace(trace, row=pos[0], col=pos[1])

        fig.update_layout(
            height=900,
            title=" Dashboard Immobilier France - Vue d'ensemble",
            title_x=0.5
        )

        return fig



# --------------------------------------------------------------------
#   TEST DU MODULE
# --------------------------------------------------------------------
if __name__ == "__main__":
    
    
    # Initialiser le visualizer
    viz = Visualizer()
    
    # Menu de test interactif
    print("\n QUE VEUX-TU TESTER ?")
    print("1. Camembert types de biens")
    print("2. Histogramme prix")
    print("3. Top communes") 
    print("4. Graphique surface vs prix")
    print("5. Dashboard complet")
    print("6. Tout tester")
    
    try:
        choix = input("\n Ton choix (1-6): ").strip()
        
        if choix in ['1', '6']:
            print("\n Test camembert...")
            fig1 = viz.create_property_types_chart()
            fig1.show()
            
        if choix in ['2', '6']:
            print("\n Test histogramme...")
            fig2 = viz.create_price_distribution()
            fig2.show()
            
        if choix in ['3', '6']:
            print("\n Test top communes...")
            fig3 = viz.create_top_cities_chart()
            fig3.show()
            
        if choix in ['4', '6']:
            print("\n Test surface vs prix...")
            fig4 = viz.create_price_vs_surface()
            fig4.show()
            
        if choix in ['5', '6']:
            print("\n Test dashboard complet...")
            dashboard = viz.create_dashboard_overview()
            dashboard.show()
            
        
        
    except Exception as e:
        print(f" Erreur: {e}")

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

class PlotVisualizer:
    def plot_price_distribution(self, df):
        """Crée un histogramme de la distribution des prix au m²"""
        fig = px.histogram(df, x='prix_m2', 
                          title="Distribution des prix au m² en France",
                          labels={'prix_m2': 'Prix au m² (€)'},
                          nbins=50)
        fig.update_layout(xaxis_title="Prix au m² (€)", 
                         yaxis_title="Nombre de transactions")
        return fig
    
    def plot_price_by_department(self, df, top_n=20):
        """Crée un graphique des prix moyens par département"""
        # Calculer le prix moyen par département
        dept_stats = df.groupby('code_departement').agg({
            'prix_m2': 'mean',
            'nom_commune': 'count'
        }).round(0).reset_index()
        
        dept_stats = dept_stats[dept_stats['nom_commune'] > 5]  # Au moins 5 transactions
        dept_stats = dept_stats.nlargest(top_n, 'prix_m2')
        
        fig = px.bar(dept_stats, x='code_departement', y='prix_m2',
                    title=f"Top {top_n} départements par prix au m² moyen",
                    labels={'prix_m2': 'Prix au m² moyen (€)', 
                           'code_departement': 'Département'})
        return fig
    
    def plot_price_vs_surface(self, df):
        """Crée un scatter plot prix vs surface"""
        fig = px.scatter(df, x='surface_reelle_bati', y='valeur_fonciere',
                        color='prix_m2', 
                        title="Relation entre surface et prix",
                        labels={'surface_reelle_bati': 'Surface (m²)',
                               'valeur_fonciere': 'Prix (€)',
                               'prix_m2': 'Prix au m² (€)'},
                        opacity=0.6)
        return fig
    
    def plot_property_types(self, df):
        """Répartition par type de bien"""
        if 'type_local' in df.columns:
            type_stats = df['type_local'].value_counts().reset_index()
            type_stats.columns = ['Type', 'Count']
            
            fig = px.pie(type_stats, values='Count', names='Type',
                        title="Répartition des types de biens immobiliers")
            return fig
        else:
            print("⚠️ Colonne 'type_local' non disponible")
            return None
    
    def plot_commune_comparison(self, df, communes=None):
        """Compare les prix entre différentes communes"""
        if communes is None:
            communes = ['Paris', 'Marseille', 'Lyon', 'Montpellier', 'Bordeaux']
        
        # Filtrer les données pour les communes sélectionnées
        df_communes = df[df['nom_commune'].isin(communes)]
        
        if len(df_communes) > 0:
            fig = px.box(df_communes, x='nom_commune', y='prix_m2',
                        title="Comparaison des prix au m² entre communes",
                        labels={'prix_m2': 'Prix au m² (€)', 
                               'nom_commune': 'Commune'})
            return fig
        else:
            print("⚠️ Aucune donnée pour les communes sélectionnées")
            return None

# Test des visualisations
if __name__ == "__main__":
    print("🧪 Test des visualisations...")
    
    # Créer des données de test avec Montpellier
    np.random.seed(42)
    test_data = pd.DataFrame({
        'valeur_fonciere': np.random.randint(50000, 500000, 100),
        'surface_reelle_bati': np.random.randint(30, 150, 100),
        'prix_m2': np.random.randint(1000, 8000, 100),
        'code_departement': np.random.choice(['75', '13', '69', '34', '33'], 100),  # 34 = Hérault (Montpellier)
        'nom_commune': ['Paris', 'Marseille', 'Lyon', 'Montpellier', 'Bordeaux'] * 20,
        'type_local': np.random.choice(['Maison', 'Appartement'], 100)
    })
    
    visualizer = PlotVisualizer()
    
    # Tester chaque visualisation
    fig1 = visualizer.plot_price_distribution(test_data)
    fig2 = visualizer.plot_price_by_department(test_data)
    fig3 = visualizer.plot_price_vs_surface(test_data)
    fig4 = visualizer.plot_property_types(test_data)
    fig5 = visualizer.plot_commune_comparison(test_data)
    
    print("✅ Toutes les visualisations fonctionnent!")
    print("🏙️  Montpellier ajouté aux communes analysées!")
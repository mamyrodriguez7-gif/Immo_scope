"""
MAP VISUALIZER
Carte interactive des prix immobiliers par département (France)
"""

import json
import pandas as pd
import plotly.express as px
from pathlib import Path
import numpy as np # Ajouté pour les opérations de DataFrame

class MapVisualizer:

    def __init__(self):
        """Initialise la visualisation cartographique"""

        current_dir = Path(__file__).parent
        project_root = current_dir.parent

        data_file = project_root / "data" / "processed" / "dvf_cleaned.csv"
        geo_file = project_root / "data" / "geo" / "departements.geojson"

        print("Initialisation de MapVisualizer...")

        # Charger les données DVF
        self.df = pd.read_csv(data_file)
        self.df['prix_m2_median'] = self.df['prix_m2'].median() # Prépare une colonne pour le fallback Scatter Map
        print(f"{len(self.df)} transactions chargées.")

        # Charger le GeoJSON des départements
        with open(geo_file, "r", encoding="utf-8") as f:
            self.geojson = json.load(f)
        print("GeoJSON des départements chargé.")

    # -------------------------------------------------------------
    # CARTE 1: Prix moyen au m² par département (Choropleth, pour le Dashboard général)
    # -------------------------------------------------------------
    def create_price_map(self):
        """
        Crée une carte choroplèthe du prix moyen au m² par département 
        (pour la vue agrégée du Dashboard).
        """
        df_grouped = (
            self.df.groupby("code_departement")
            .agg(avg_price_m2=("prix_m2", "mean"))
            .reset_index()
        )

        fig = px.choropleth_mapbox(
            df_grouped,
            geojson=self.geojson,
            locations="code_departement",
            featureidkey="properties.code",
            color="avg_price_m2",
            color_continuous_scale="Viridis",
            mapbox_style="carto-positron",
            zoom=4.5,
            center={"lat": 46.5, "lon": 2.5},
            opacity=0.7,
            labels={"avg_price_m2": "Prix moyen (€/m²)"},
            title="Prix moyen au m² par département (Vue agrégée)",
        )

        fig.update_layout(title_x=0.5, height=600)
        return fig
    
    # -------------------------------------------------------------
    # CARTE 2: Scatter Mapbox (POUR L'INTERACTIVITÉ AVEC LES VILLES)
    # -------------------------------------------------------------
    def create_scatter_map(self, df_filtered: pd.DataFrame):
        """
        Crée une carte affichant les transactions individuelles 
        avec le nom de la commune au survol.
        
        Parameters
        ----------
        df_filtered : pd.DataFrame
            DataFrame déjà filtré par le widget Streamlit (département, etc.).
        """
        # Pour des raisons de performance, on ne prend qu'un échantillon de 2000 points max.
        sample_df = df_filtered.sample(min(2000, len(df_filtered)))
        
        # Centrer la carte sur la région filtrée
        if not sample_df.empty:
            center_lat = sample_df['latitude'].mean()
            center_lon = sample_df['longitude'].mean()
        else:
            center_lat = 46.5
            center_lon = 2.5
            
        fig = px.scatter_mapbox(
            sample_df,
            lat="latitude", 
            lon="longitude", 
            hover_name="nom_commune", # <--- C'EST CET ÉLÉMENT QUI AFFICHE LE NOM DE LA VILLE
            hover_data=['prix_m2', 'surface_reelle_bati'],
            color="prix_m2",
            color_continuous_scale=px.colors.sequential.Plasma,
            mapbox_style="carto-positron",
            zoom=7, # Zoom initial plus serré
            center={"lat": center_lat, "lon": center_lon},
            opacity=0.8,
            title="Transactions individuelles (Nom des villes au survol)"
        )
        
        fig.update_layout(title_x=0.5, height=600, margin={"r":0,"t":40,"l":0,"b":0})
        return fig


# -------------------------------------------------------------
# Test direct du module
# -------------------------------------------------------------
<<<<<<< HEAD
# ... (bloc if __name__ == "__main__": inchangé)
=======
# ... (bloc if __name__ == "__main__": inchangé)
>>>>>>> f6868508e2fd2b1feba7fed56ee8eda00922db62

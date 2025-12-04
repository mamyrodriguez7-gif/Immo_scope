"""
MAP VISUALIZER
Carte interactive des prix immobiliers par département (France)
"""

import json
import pandas as pd
import plotly.express as px
from pathlib import Path

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
        print(f"{len(self.df)} transactions chargées.")

        # Charger le GeoJSON des départements
        with open(geo_file, "r", encoding="utf-8") as f:
            self.geojson = json.load(f)
        print("GeoJSON des départements chargé.")

    # -------------------------------------------------------------
    #  CARTE : Prix moyen au m² par département
    # -------------------------------------------------------------
    def create_price_map(self):

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
            title="Prix moyen au m² par département",
        )

        fig.update_layout(title_x=0.5)
        return fig


# -------------------------------------------------------------
# Test direct du module
# -------------------------------------------------------------
if __name__ == "__main__":

    viz = MapVisualizer()
    fig = viz.create_price_map()
    fig.show()

"""
MAP VISUALIZER
Génère des snippets HTML Plotly pour chaque graphique.
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

        self.df = pd.read_csv(data_file)
        print(f"{len(self.df)} transactions chargées.")

        with open(geo_file, "r", encoding="utf-8") as f:
            self.geojson = json.load(f)
        print("GeoJSON des départements chargé.")

    # ----------------- Graphiques -----------------
    def create_price_map(self):
        df_grouped = self.df.groupby("code_departement").agg(avg_price_m2=("prix_m2", "mean")).reset_index()
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

    def create_price_histogram(self):
        fig = px.histogram(
            self.df,
            x="prix_m2",
            nbins=50,
            title="Distribution des prix au m²",
            labels={"prix_m2": "Prix au m² (€)"},
        )
        fig.update_layout(title_x=0.5)
        return fig

    def create_price_scatter(self):
        fig = px.scatter(
            self.df,
            x="surface_reelle_bati",   # <- colonne correcte
            y="prix_m2",
            title="Prix au m² en fonction de la surface",
            labels={"surface_reelle_bati": "Surface (m²)", "prix_m2": "Prix au m² (€)"},
            opacity=0.6,
        )
        fig.update_layout(title_x=0.5)
        return fig



# ----------------- Génération des snippets HTML -----------------
if __name__ == "__main__":
    viz = MapVisualizer()

    # Créer les figures
    fig_map = viz.create_price_map()
    fig_hist = viz.create_price_histogram()
    fig_scatter = viz.create_price_scatter()

    # Exporter chaque graphique en snippet HTML
    with open("snippets/map.html", "w", encoding="utf-8") as f:
        f.write(fig_map.to_html(full_html=False, include_plotlyjs='cdn'))

    with open("snippets/histogram.html", "w", encoding="utf-8") as f:
        f.write(fig_hist.to_html(full_html=False, include_plotlyjs=False))

    with open("snippets/scatter.html", "w", encoding="utf-8") as f:
        f.write(fig_scatter.to_html(full_html=False, include_plotlyjs=False))

    print("Snippets HTML générés dans le dossier 'snippets/' !")

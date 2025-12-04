from flask import Flask, render_template
from map_visualizer import MapVisualizer
from visualizer import Visualizer
import json
from plotly.utils import PlotlyJSONEncoder

app = Flask(__name__)

# Initialiser les visualizers
map_viz = MapVisualizer()
dash_viz = Visualizer()

# Créer les figures
map_fig = map_viz.create_price_map()
property_types_fig = dash_viz.create_property_types_chart()
price_dist_fig = dash_viz.create_price_distribution()
top_cities_fig = dash_viz.create_top_cities_chart(8)
surface_price_fig = dash_viz.create_price_vs_surface()

# Convertir en JSON côté Python
def fig_to_json(fig):
    return json.dumps(fig, cls=PlotlyJSONEncoder)

figures = {
    "map": fig_to_json(map_fig),
    "property_types": fig_to_json(property_types_fig),
    "price_distribution": fig_to_json(price_dist_fig),
    "top_cities": fig_to_json(top_cities_fig),
    "surface_price": fig_to_json(surface_price_fig)
}

@app.route('/')
def index():
    return render_template("index.html", figures=figures)

if __name__ == "__main__":
    app.run(debug=True)

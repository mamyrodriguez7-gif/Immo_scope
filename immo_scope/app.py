from flask import Flask, render_template
from map_visualizer import MapVisualizer
import json
from plotly.utils import PlotlyJSONEncoder

app = Flask(__name__)

viz = MapVisualizer()
fig = viz.create_price_map()

@app.route('/')
def index():
    fig_json = json.dumps(fig, cls=PlotlyJSONEncoder)
    return render_template("index.html", fig_json=fig_json)


if __name__ == "__main__":
    app.run(debug=True)

import os
import requests
from pathlib import Path

def download_communes_geojson():

    # Chemin du projet
    project_root = Path(__file__).parent.parent

    # Dossier de destination
    geo_dir = project_root / "data" / "geo"
    geo_dir.mkdir(parents=True, exist_ok=True)

    # Fichier cible
    save_path = geo_dir / "communes.geojson"

    # URL officielle du fichier GeoJSON
    url = "https://raw.githubusercontent.com/etalab/geojson-communes-france/master/communes.geojson"

    print("Téléchargement du fichier communes.geojson...")

    response = requests.get(url)

    if response.status_code == 200:
        with open(save_path, "wb") as f:
            f.write(response.content)
        print(f"✔️ Fichier téléchargé avec succès : {save_path}")
    else:
        print(f"❌ Erreur de téléchargement : {response.status_code}")

if __name__ == "__main__":
    download_communes_geojson()

"""
SCRIPT DE PRÉPARATION DES DONNÉES POUR LE DASHBOARD IMMO_SCOPE
Ce script lit le fichier DVF nettoyé, calcule des métriques utiles
et génère un fichier JSON utilisé par le dashboard Streamlit
"""

import pandas as pd
import json
from pathlib import Path

def prepare_dashboard_data():
    print("Préparation des données DVF pour le dashboard...")

    # Détection du chemin
    project_root = Path(__file__).resolve().parents[1]

    # Fichier DVF nettoyé
    dvf_file = project_root / "data" / "processed" / "dvf_cleaned.csv"

    # Fichier de sortie JSON
    output_file = project_root / "data" / "reports" / "dashboard_data.json"

    # Charger le CSV
    df = pd.read_csv(dvf_file)

    # ----------------------------
    # CALCUL DES MÉTRIQUES
    # ----------------------------
    metrics = {
        "total_transactions": int(len(df)),
        "avg_price_m2": float(df["prix_m2"].mean()),
        "max_price_m2": float(df["prix_m2"].max()),
        "min_price_m2": float(df["prix_m2"].min()),
        "unique_communes": int(df["nom_commune"].nunique())
    }

    # ----------------------------
    # SAUVEGARDE DU JSON
    # ----------------------------
    output_data = {"metrics": metrics}

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=4, ensure_ascii=False)

    print(f" Données dashboard générées : {output_file}")


if __name__ == "__main__":
    prepare_dashboard_data()

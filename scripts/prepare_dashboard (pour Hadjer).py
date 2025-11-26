# -*- coding: utf-8 -*-
"""
Created on Wed Nov 26 14:48:45 2025

@author: mamyr
"""

"""
SCRIPT POUR HADJER - Préparation des données pour le dashboard
"""
import pandas as pd
import json
from pathlib import Path

print(" PRÉPARATION DASHBOARD - Données par Rodrigue")
print("=" * 50)

# Chemin correct
current_dir = Path(__file__).parent
data_file = current_dir.parent / "data" / "processed" / "dvf_cleaned.csv"

if not data_file.exists():
    print(" Données non trouvées. Génère les données d'abord.")
    exit()

# Charger les données de Rodrigue
df = pd.read_csv(data_file)

# Données agrégées pour le dashboard
dashboard_data = {
    "metrics": {
        "total_transactions": len(df),
        "avg_price_m2": int(df['prix_m2'].mean()),
        "avg_surface": int(df['surface_reelle_bati'].mean()),
        "total_cities": df['nom_commune'].nunique() if 'nom_commune' in df.columns else 0
    },
    "price_by_year": df.groupby('annee')['prix_m2'].mean().round().to_dict(),
    "transactions_by_type": df['type_local'].value_counts().to_dict() if 'type_local' in df.columns else {},
    "top_cities": df['nom_commune'].value_counts().head(10).to_dict() if 'nom_commune' in df.columns else {}
}

# Sauvegarder pour Hadjer
dashboard_file = current_dir.parent / "data" / "reports" / "dashboard_data.json"
with open(dashboard_file, 'w', encoding='utf-8') as f:
    json.dump(dashboard_data, f, indent=2, ensure_ascii=False)

print(f" Données dashboard préparées: {dashboard_file}")
print(f" Métriques pour Hadjer:")
print(f"   • {dashboard_data['metrics']['total_transactions']} transactions")
print(f"   • {dashboard_data['metrics']['avg_price_m2']} €/m² moyen")
print(f"   • {dashboard_data['metrics']['total_cities']} communes")
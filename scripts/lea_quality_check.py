# scripts/lea_quality_check.py
"""
SCRIPT SIMPLIFIÉ POUR LÉA - VÉRIFICATION QUALITÉ
"""
import json
import pandas as pd
from pathlib import Path

print(" LÉA - VÉRIFICATION QUALITÉ DES DONNÉES")
print("=" * 50)

# Charger les données
current_dir = Path(__file__).parent
project_root = current_dir.parent

quality_file = project_root / "data" / "reports" / "quality_report.json"
data_file = project_root / "data" / "processed" / "dvf_cleaned.csv"

# 1. Charger le rapport qualité
with open(quality_file, 'r') as f:
    quality_data = json.load(f)

# 2. Charger les données
df = pd.read_csv(data_file)

print("RAPPORT QUALITÉ - SYNTHÈSE")
print(f"• Score qualité: {quality_data['data_quality_metrics']['completeness_score']}%")
print(f"• Transactions: {quality_data['data_quality_metrics']['total_rows']}")
print(f"• Colonnes: {quality_data['data_quality_metrics']['total_columns']}")

print("\n VALIDATIONS :")
validations = quality_data['validation_checks']
for test_name, test_data in validations.items():
    status = "PASS" if "VALID" in test_data.get('status', '') else " CHECK"
    print(f"• {test_name}: {status}")

print("\n STATISTIQUES RAPIDES :")
print(f"• Prix m² - Min: {df['prix_m2'].min():.0f}€, Max: {df['prix_m2'].max():.0f}€")
print(f"• Surface - Min: {df['surface_reelle_bati'].min():.0f}m², Max: {df['surface_reelle_bati'].max():.0f}m²")
print(f"• Types: {df['type_local'].value_counts().to_dict()}")

print(f"\n LÉA - PROCHAINES ÉTAPES :")
print("1. python scripts/generate_quality_html.py")
print("2. Ouvrir data/quality_reports/quality_report.html")
print("3. Analyser les rapports dans le navigateur")

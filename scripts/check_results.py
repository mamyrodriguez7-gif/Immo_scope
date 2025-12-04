# -*- coding: utf-8 -*-
"""
Created on Wed Nov 26 14:39:00 2025

@author: mamyr
"""

# Fichier : check_results.py
import pandas as pd
import json
from pathlib import Path

print("ANALYSE DES RÉSULTATS")
print("=" * 50)

# 1. Vérifier les données principales
data_file = Path("data/processed/dvf_cleaned.csv")
if data_file.exists():
    df = pd.read_csv(data_file)
    print(f" DONNÉES DVF GÉNÉRÉES:")
    print(f"    Transactions: {len(df):,}")
    print(f"     Années: {sorted(df['annee'].unique())}")
    print(f"    Prix moyen: {df['prix_m2'].mean():.0f} €/m²")
    print(f"    Surface moyenne: {df['surface_reelle_bati'].mean():.0f} m²")
    
    if 'type_local' in df.columns:
        types = df['type_local'].value_counts()
        print(f"     Types de biens:")
        for type_bien, count in types.items():
            print(f"      • {type_bien}: {count} transactions")
    
    if 'nom_commune' in df.columns:
        print(f"     Communes: {df['nom_commune'].nunique()}")
        top_communes = df['nom_commune'].value_counts().head(5)
        print(f"      Top 5: {list(top_communes.index)}")
else:
    print(" Fichier de données non trouvé")

# 2. Vérifier le rapport
report_file = Path("data/reports/report.json")
if report_file.exists():
    with open(report_file, 'r') as f:
        report = json.load(f)
    print(f"\n RAPPORT QUALITÉ:")
    print(f"    Total: {report.get('total', 'N/A')} transactions")
    print(f"    Période: {report.get('years', 'N/A')}")
    print(f"    Prix moyen: {report.get('price_mean', 'N/A'):.0f} €/m²")
    print(f"     Communes: {report.get('communes', 'N/A')}")

print("\n PROCHAINES ÉTAPES POUR L'ÉQUIPE:")
print("1. Hadjer: Créer le dashboard avec ces données")
print("2. Léa: Tester la qualité des données")
print("3. Rodrigue: Préparer l'intégration Git")
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 26 14:56:26 2025

@author: mamyr
"""

# 📁 scripts/quick_check.py
import pandas as pd
import os

print(" VÉRIFICATION RAPIDE - RODRIGUE")
print("=" * 40)

# Vérifier si le fichier existe
data_path = "data/processed/dvf_cleaned.csv"

if os.path.exists(data_path):
    print(f" FICHIER TROUVÉ: {data_path}")
    
    # Charger juste les premières lignes pour vérifier
    df = pd.read_csv(data_path, nrows=5)
    print(f" Aperçu des données:")
    print(f"   Colonnes: {list(df.columns)}")
    print(f"   Première ligne:")
    for col, val in df.iloc[0].items():
        print(f"     {col}: {val}")
    
    # Statistiques basiques
    full_df = pd.read_csv(data_path)
    print(f"\n STATISTIQUES:")
    print(f"   Total: {len(full_df):,} transactions")
    print(f"   Années: {full_df['annee'].unique()}")
    
else:
    print(f" FICHIER NON TROUVÉ: {data_path}")
    print("💡 Solutions:")
    print("   1. Vérifier le chemin: ls -la data/processed/")
    print("   2. Regénérer les données si nécessaire")
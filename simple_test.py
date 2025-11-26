# -*- coding: utf-8 -*-
"""
Created on Wed Nov 26 14:29:51 2025

@author: mamyr
"""

# 📁 Fichier : simple_test.py
print(" TEST ULTRA-SIMPLE RODRIGUE")

import pandas as pd
from pathlib import Path

# Vérifier si les données existent déjà
data_file = Path("data/processed/dvf_cleaned.csv")

if data_file.exists():
    df = pd.read_csv(data_file)
    print(f" Données existantes: {len(df)} transactions")
    print(f" Prix moyen: {df['prix_m2'].mean():.0f} €/m²")
else:
    print(" Aucune donnée trouvée. Lance rodrigue_main.py d'abord.")
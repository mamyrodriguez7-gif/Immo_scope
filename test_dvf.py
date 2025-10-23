import pandas as pd
import requests
from pathlib import Path

print("🚀 Exploration des données DVF...")

# Téléchargement des données
url = "https://www.data.gouv.fr/fr/datasets/r/90a98de0-f562-4328-aa16-fe0dd1dca60d"

try:
    print("📥 Téléchargement en cours...")
    df = pd.read_csv(url, compression='zip', low_memory=False, nrows=10000)
    
    print(f"✅ Données téléchargées : {len(df)} lignes, {len(df.columns)} colonnes")
    
    print("\n📊 COLONNES DISPONIBLES:")
    print("=" * 40)
    for i, col in enumerate(df.columns, 1):
        print(f"{i:2d}. {col}")
    
    print("\n💰 COLONNES DE PRIX:")
    price_cols = [col for col in df.columns if 'prix' in col.lower() or 'valeur' in col.lower()]
    for col in price_cols:
        print(f"  - {col}")
    
    print("\n📏 COLONNES DE SURFACE:")
    surface_cols = [col for col in df.columns if 'surface' in col.lower()]
    for col in surface_cols:
        print(f"  - {col}")
    
    # Aperçu des données
    print("\n👀 APERÇU DES DONNÉES:")
    if 'valeur_fonciere' in df.columns and 'surface_reelle_bati' in df.columns:
        print(df[['valeur_fonciere', 'surface_reelle_bati', 'code_commune', 'code_postal']].head(3))
    else:
        print("Colonnes attendues non trouvées")
    
    # Sauvegarder pour exploration future
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    df.to_csv("data/processed/dvf_sample.csv", index=False)
    print("\n💾 Données sauvegardées dans data/processed/dvf_sample.csv")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

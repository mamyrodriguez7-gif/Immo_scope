# -*- coding: utf-8 -*-
"""
Created on Wed Nov 26 14:25:15 2025

@author: mamyr
"""

# 📁 Fichier : rodrigue_main.py
"""
SCRIPT PRINCIPAL RODRIGUE - Tout-en-un
Évite les problèmes d'import de modules
"""
import pandas as pd
import numpy as np
import requests
from pathlib import Path
import json
import warnings
import ssl
import urllib3
import time

# Configuration
warnings.filterwarnings('ignore')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

class RodrigueDataLoader:
    """
    DataLoader avancé par Rodrigue Mamy (22510795)
    """
    
    def __init__(self, base_dir="data"):
        self.base_dir = Path(base_dir)
        self.raw_dir = self.base_dir / "raw"
        self.processed_dir = self.base_dir / "processed"
        self.reports_dir = self.base_dir / "reports"
        
        for directory in [self.raw_dir, self.processed_dir, self.reports_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        self.dvf_base_url = "https://files.data.gouv.fr/geo-dvf/latest/csv"
    
    def download_dvf_data(self, years=[2023], sample_size=5000):
        print(" RODRIGUE - Début du téléchargement DVF...")
        all_data = []
        
        for year in years:
            print(f"\n Traitement {year}...")
            
            filename = f"dvf_{year}.csv.gz"
            file_path = self.raw_dir / filename
            url = f"{self.dvf_base_url}/{year}/full.csv.gz"
            
            try:
                if not file_path.exists():
                    print(f"   Téléchargement...")
                    response = requests.get(url, timeout=120, verify=False)
                    response.raise_for_status()
                    
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    print(f"   Fichier sauvegardé")
                else:
                    print(f"   Fichier existant")
                
                # Chargement et traitement
                df = pd.read_csv(file_path, compression='gzip', low_memory=False)
                
                if len(df) > sample_size:
                    df = df.sample(n=sample_size, random_state=42)
                
                df_clean = self._clean_data(df, year)
                if df_clean is not None and len(df_clean) > 0:
                    all_data.append(df_clean)
                    print(f"   {len(df_clean):,} transactions valides")
                
            except Exception as e:
                print(f"   Erreur: {e}")
                continue
        
        if all_data:
            final_df = pd.concat(all_data, ignore_index=True)
            self._save_data(final_df)
            return final_df
        else:
            print(" Aucune donnée valide")
            return None
    
    def _clean_data(self, df, year):
        try:
            df_clean = df.copy()
            
            # Colonnes essentielles
            cols = ['valeur_fonciere', 'surface_reelle_bati', 'type_local', 
                   'nom_commune', 'code_departement', 'latitude', 'longitude']
            cols = [c for c in cols if c in df_clean.columns]
            df_clean = df_clean[cols]
            
            # Conversion numérique
            for col in ['valeur_fonciere', 'surface_reelle_bati', 'latitude', 'longitude']:
                if col in df_clean.columns:
                    df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
            
            # Filtrage
            mask = (
                (df_clean['valeur_fonciere'] >= 10000) & 
                (df_clean['valeur_fonciere'] <= 2000000) &
                (df_clean['surface_reelle_bati'] >= 9) & 
                (df_clean['surface_reelle_bati'] <= 500)
            )
            
            if 'type_local' in df_clean.columns:
                mask &= (df_clean['type_local'].isin(['Maison', 'Appartement']))
            
            df_clean = df_clean[mask].copy()
            
            # Calcul prix m²
            df_clean['prix_m2'] = df_clean['valeur_fonciere'] / df_clean['surface_reelle_bati']
            df_clean['annee'] = year
            
            # Nettoyage final
            df_clean = df_clean[
                (df_clean['prix_m2'] >= 500) & 
                (df_clean['prix_m2'] <= 20000)
            ]
            
            if 'nom_commune' in df_clean.columns:
                df_clean['nom_commune'] = df_clean['nom_commune'].astype(str).str.title().str.strip()
            
            return df_clean.dropna().reset_index(drop=True)
            
        except Exception as e:
            print(f"    Nettoyage: {e}")
            return None
    
    def _save_data(self, df):
        output_file = self.processed_dir / "dvf_cleaned.csv"
        df.to_csv(output_file, index=False)
        print(f"\n Données sauvegardées: {output_file}")
        print(f" Taille: {len(df):,} transactions")
        
        # Rapport simple
        report = {
            "total": len(df),
            "years": df['annee'].unique().tolist(),
            "price_mean": float(df['prix_m2'].mean()),
            "communes": df['nom_commune'].nunique() if 'nom_commune' in df.columns else 0
        }
        
        report_file = self.reports_dir / "report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f" Rapport généré: {report_file}")

def main():
    print("=" * 60)
    print("🏠 RODRIGUE MAMY - DataLoader DVF")
    print("=" * 60)
    
    start = time.time()
    
    loader = RodrigueDataLoader()
    df = loader.download_dvf_data(years=[2023], sample_size=3000)
    
    if df is not None:
        duration = time.time() - start
        print(f"\n SUCCÈS en {duration:.1f}s!")
        print(f" {len(df)} transactions")
        print(f" {df['prix_m2'].mean():.0f} €/m²")
        print(f" {df['type_local'].value_counts().to_dict()}")
        
        print(f"\n Fichiers créés:")
        print(f"   data/processed/dvf_cleaned.csv")
        print(f"   data/reports/report.json")

if __name__ == "__main__":
    main()
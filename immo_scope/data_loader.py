"""
MODULE data_loader.py
Classe pour télécharger, charger et nettoyer les données DVF multi-années
"""
import pandas as pd
import requests
from pathlib import Path
import urllib3
import ssl

class DataLoader:
    def __init__(self):
        self.data_dir = Path("data")
        self.raw_dir = self.data_dir / "raw" 
        self.processed_dir = self.data_dir / "processed"
        
        # Créer les dossiers
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration SSL (pour développement)
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        ssl._create_default_https_context = ssl._create_unverified_context
    
    def download_dvf_data(self, years=[2024, 2023, 2022, 2021], sample_per_year=20000):
        """Télécharge les données DVF pour plusieurs années avec échantillonnage"""
        print(f"📥 Téléchargement des données DVF pour les années {years}...")
        all_data = []
        
        for year in years:
            print(f"\n🔹 Traitement de l'année {year}...")
            
            # URL des données DVF pour chaque année
            url = f"https://files.data.gouv.fr/geo-dvf/latest/csv/{year}/full.csv.gz"
            
            try:
                # Vérifier si le fichier existe déjà
                file_path = self.raw_dir / f"dvf_{year}.csv.gz"
                
                if not file_path.exists():
                    print(f"  📥 Téléchargement depuis {url}...")
                    response = requests.get(url, verify=False, timeout=60)
                    response.raise_for_status()
                    
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    print(f"  ✅ Fichier téléchargé: {file_path}")
                else:
                    print(f"  ✅ Fichier déjà existant: {file_path}")
                
                # Charger et nettoyer les données de cette année
                df_year = self.load_and_clean_data(file_path, sample_size=sample_per_year)
                if df_year is not None and len(df_year) > 0:
                    df_year['annee'] = year  # Ajouter la colonne année
                    all_data.append(df_year)
                    print(f"  ✅ Données {year} nettoyées: {len(df_year)} transactions")
                else:
                    print(f"  ⚠️  Aucune donnée valide pour {year}")
                
            except Exception as e:
                print(f"  ❌ Erreur pour l'année {year}: {e}")
                continue
        
        # Combiner toutes les années
        if all_data:
            df_combined = pd.concat(all_data, ignore_index=True)
            total_transactions = len(df_combined)
            print(f"\n🎉 DONNÉES COMBINÉES: {total_transactions:,} transactions sur {len(years)} années")
            
            # Statistiques par année
            print("📊 Répartition par année:")
            for year in years:
                count = len(df_combined[df_combined['annee'] == year])
                print(f"   • {year}: {count:,} transactions")
            
            return df_combined
        else:
            print("❌ Aucune donnée valide téléchargée")
            return None
    
    def load_and_clean_data(self, file_path, sample_size=None):
        """Charge et nettoie les données DVF"""
        print("  🧹 Chargement et nettoyage des données...")
        
        try:
            # Charger les données
            if sample_size:
                df = pd.read_csv(file_path, compression='gzip', low_memory=False, nrows=sample_size)
            else:
                df = pd.read_csv(file_path, compression='gzip', low_memory=False)
                
            print(f"  ✅ Données brutes chargées: {len(df)} lignes")
            
            # Nettoyer les données
            df_clean = self._clean_data(df)
            
            return df_clean
            
        except Exception as e:
            print(f"  ❌ Erreur lors du chargement: {e}")
            return None
    
    def _clean_data(self, df):
        """Nettoie les données DVF de manière complète"""
        print("  🔧 Nettoyage en cours...")
        
        # Copie pour éviter les modifications accidentelles
        df_clean = df.copy()
        
        # === ÉTAPE 1: NETTOYAGE DES COLONNES NUMÉRIQUES ===
        numeric_columns = {
            'valeur_fonciere': 'Prix de vente',
            'surface_reelle_bati': 'Surface bâtie', 
            'surface_terrain': 'Surface terrain',
            'nombre_pieces_principales': 'Nombre de pièces',
            'latitude': 'Latitude',
            'longitude': 'Longitude'
        }
        
        for col, desc in numeric_columns.items():
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        
        # === ÉTAPE 2: FILTRAGE DES DONNÉES ABERRANTES ===
        conditions_filtrage = []
        
        # Filtre sur les prix
        if 'valeur_fonciere' in df_clean.columns:
            conditions_filtrage.append(
                (df_clean['valeur_fonciere'] > 1000) & 
                (df_clean['valeur_fonciere'] < 5000000)
            )
        
        # Filtre sur les surfaces
        if 'surface_reelle_bati' in df_clean.columns:
            conditions_filtrage.append(
                (df_clean['surface_reelle_bati'] > 0) &
                (df_clean['surface_reelle_bati'] < 1000)
            )
        
        # Appliquer tous les filtres
        if conditions_filtrage:
            masque_combine = conditions_filtrage[0]
            for condition in conditions_filtrage[1:]:
                masque_combine &= condition
            
            df_clean = df_clean[masque_combine]
        
        # === ÉTAPE 3: CALCUL DES MÉTRIQUES ===
        # Calcul du prix au m²
        if all(col in df_clean.columns for col in ['valeur_fonciere', 'surface_reelle_bati']):
            df_clean['prix_m2'] = df_clean['valeur_fonciere'] / df_clean['surface_reelle_bati']
        
        # Filtrage des prix au m² aberrants
        if 'prix_m2' in df_clean.columns:
            df_clean = df_clean[
                (df_clean['prix_m2'] > 100) & 
                (df_clean['prix_m2'] < 20000)
            ]
        
        # === ÉTAPE 4: NETTOYAGE DES CHAÎNES DE CARACTÈRES ===
        # Nettoyer les noms de communes
        if 'nom_commune' in df_clean.columns:
            df_clean['nom_commune'] = df_clean['nom_commune'].str.title().str.strip()
        
        # Nettoyer les types de biens
        if 'type_local' in df_clean.columns:
            df_clean['type_local'] = df_clean['type_local'].str.strip()
        
        # === ÉTAPE 5: GESTION DES VALEURS MANQUANTES ===
        # Supprimer les lignes avec des valeurs essentielles manquantes
        colonnes_essentielles = ['valeur_fonciere', 'surface_reelle_bati', 'prix_m2']
        colonnes_presentes = [col for col in colonnes_essentielles if col in df_clean.columns]
        
        if colonnes_presentes:
            df_clean = df_clean.dropna(subset=colonnes_presentes)
        
        # Réinitialiser l'index après tous les filtrages
        df_clean = df_clean.reset_index(drop=True)
        
        print(f"  ✅ Nettoyage terminé: {len(df_clean)} transactions valides")
        
        return df_clean
    
    def get_data_quality_report(self, df):
        """Génère un rapport de qualité des données pour le dashboard"""
        if df is None or len(df) == 0:
            return {"erreur": "Aucune donnée disponible"}
        
        rapport = {
            'total_transactions': len(df),
            'columns_available': list(df.columns),
            'missing_values': df.isnull().sum().to_dict(),
            'data_quality_score': self._calculate_quality_score(df),
            'price_stats': {},
            'surface_stats': {},
            'geographic_coverage': {},
            'yearly_stats': {}
        }
        
        # Statistiques prix
        if 'prix_m2' in df.columns:
            rapport['price_stats'] = {
                'mean': round(df['prix_m2'].mean()),
                'median': round(df['prix_m2'].median()),
                'std': round(df['prix_m2'].std()),
                'min': round(df['prix_m2'].min()),
                'max': round(df['prix_m2'].max())
            }
        
        # Statistiques surface
        if 'surface_reelle_bati' in df.columns:
            rapport['surface_stats'] = {
                'mean': round(df['surface_reelle_bati'].mean()),
                'max': round(df['surface_reelle_bati'].max())
            }
        
        # Couverture géographique
        if 'nom_commune' in df.columns:
            rapport['geographic_coverage'] = {
                'unique_cities': df['nom_commune'].nunique(),
                'unique_departments': df['code_departement'].nunique() if 'code_departement' in df.columns else 0
            }
        
        # Statistiques par année
        if 'annee' in df.columns:
            yearly_stats = df.groupby('annee').agg({
                'prix_m2': ['mean', 'count'],
                'surface_reelle_bati': 'mean'
            }).round(0)
            
            yearly_stats.columns = ['prix_moyen', 'nb_transactions', 'surface_moyenne']
            rapport['yearly_stats'] = yearly_stats.to_dict()
        
        return rapport
    
    def _calculate_quality_score(self, df):
        """Calcule un score de qualité des données (0-100)"""
        score = 100
        
        # Pénalités pour valeurs manquantes
        total_cells = len(df) * len(df.columns)
        missing_cells = df.isnull().sum().sum()
        if total_cells > 0:
            missing_percentage = (missing_cells / total_cells) * 100
            score -= missing_percentage * 0.5
        
        # Vérification de la cohérence des prix
        if 'prix_m2' in df.columns:
            prix_aberrants = ((df['prix_m2'] < 100) | (df['prix_m2'] > 20000)).sum()
            if len(df) > 0:
                pourcentage_aberrant = (prix_aberrants / len(df)) * 100
                score -= pourcentage_aberrant * 0.3
        
        return max(0, min(100, round(score)))
    
    def save_processed_data(self, df, filename="dvf_cleaned.csv"):
        """Sauvegarde les données nettoyées"""
        file_path = self.processed_dir / filename
        df.to_csv(file_path, index=False)
        print(f"💾 Données sauvegardées: {file_path}")
        return file_path

# Test du DataLoader
if __name__ == "__main__":
    print("🧪 Test du DataLoader multi-années...")
    
    loader = DataLoader()
    
    # Tester avec 2 années d'abord pour être sûr
    df_clean = loader.download_dvf_data(years=[2024, 2023], sample_per_year=15000)
    
    if df_clean is not None:
        loader.save_processed_data(df_clean)
        print(f"🎉 DataLoader testé avec succès! {len(df_clean):,} transactions sur {df_clean['annee'].nunique()} années")
        
        # Afficher le rapport de qualité
        rapport = loader.get_data_quality_report(df_clean)
        print(f"📊 Score de qualité: {rapport['data_quality_score']}/100")
        
        # Afficher les statistiques par année (VERSION CORRIGÉE)
        print("📅 Statistiques par année:")
        for annee in df_clean['annee'].unique():
            count = len(df_clean[df_clean['annee'] == annee])
            prix_moyen = df_clean[df_clean['annee'] == annee]['prix_m2'].mean()
            print(f"   • {annee}: {count:,} transactions, {prix_moyen:.0f} €/m²")
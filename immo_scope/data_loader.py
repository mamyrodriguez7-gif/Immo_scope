"""
MODULE data_loader.py
Classe pour télécharger, charger et nettoyer les données DVF
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
    
    def download_dvf_data(self, year=2024):
        """Télécharge les données DVF pour une année donnée"""
        print(f"📥 Téléchargement des données DVF {year}...")
        
        # URL des données DVF 2024
        url = "https://files.data.gouv.fr/geo-dvf/latest/csv/2024/full.csv.gz"
        
        try:
            # Télécharger avec requests
            response = requests.get(url, verify=False, timeout=30)
            response.raise_for_status()
            
            # Sauvegarder le fichier
            file_path = self.raw_dir / f"dvf_{year}.csv.gz"
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ Données {year} téléchargées: {file_path}")
            return file_path
            
        except Exception as e:
            print(f"❌ Erreur lors du téléchargement: {e}")
            return None
    
    def load_and_clean_data(self, file_path, sample_size=None):
        """Charge et nettoie les données DVF"""
        print("🧹 Chargement et nettoyage des données...")
        
        try:
            # Charger les données
            if sample_size:
                df = pd.read_csv(file_path, compression='gzip', low_memory=False, nrows=sample_size)
            else:
                df = pd.read_csv(file_path, compression='gzip', low_memory=False)
                
            print(f"✅ Données brutes chargées: {len(df)} lignes")
            
            # Générer un rapport avant nettoyage
            rapport_avant = self._generate_quality_report(df, "AVANT nettoyage")
            
            # Nettoyer les données
            df_clean = self._clean_data(df)
            
            # Générer un rapport après nettoyage
            rapport_apres = self._generate_quality_report(df_clean, "APRÈS nettoyage")
            
            # Afficher le résumé du nettoyage
            self._display_cleaning_summary(len(df), len(df_clean), rapport_avant, rapport_apres)
            
            return df_clean
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement: {e}")
            return None
    
    def _clean_data(self, df):
        """Nettoie les données DVF de manière complète"""
        print("🔧 Nettoyage en cours...")
        
        # Copie pour éviter les modifications accidentelles
        df_clean = df.copy()
        
        # === ÉTAPE 1: NETTOYAGE DES COLONNES NUMÉRIQUES ===
        print("  📊 Conversion des colonnes numériques...")
        
        # Colonnes à convertir en numérique
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
                valeurs_manquantes = df_clean[col].isna().sum()
                if valeurs_manquantes > 0:
                    print(f"    ⚠️  {valeurs_manquantes} valeurs manquantes dans {desc}")
        
        # === ÉTAPE 2: FILTRAGE DES DONNÉES ABERRANTES ===
        print("  🎯 Filtrage des données aberrantes...")
        
        conditions_filtrage = []
        
        # Filtre sur les prix
        if 'valeur_fonciere' in df_clean.columns:
            conditions_filtrage.append(
                (df_clean['valeur_fonciere'] > 1000) & 
                (df_clean['valeur_fonciere'] < 5000000)  # Prix entre 1k€ et 5M€
            )
            prix_aberrants = len(df_clean) - (df_clean['valeur_fonciere'] > 1000).sum()
            print(f"    ✅ Prix filtrés: {prix_aberrants} valeurs aberrantes supprimées")
        
        # Filtre sur les surfaces
        if 'surface_reelle_bati' in df_clean.columns:
            conditions_filtrage.append(
                (df_clean['surface_reelle_bati'] > 0) &
                (df_clean['surface_reelle_bati'] < 1000)  # Surface entre 1m² et 1000m²
            )
            surface_aberrante = len(df_clean) - (df_clean['surface_reelle_bati'] > 0).sum()
            print(f"    ✅ Surfaces filtrées: {surface_aberrante} valeurs aberrantes supprimées")
        
        # Appliquer tous les filtres
        if conditions_filtrage:
            masque_combine = conditions_filtrage[0]
            for condition in conditions_filtrage[1:]:
                masque_combine &= condition
            
            df_clean = df_clean[masque_combine]
            print(f"    📉 Données après filtrage: {len(df_clean)} lignes")
        
        # === ÉTAPE 3: CALCUL DES MÉTRIQUES ===
        print("  📈 Calcul des métriques...")
        
        # Calcul du prix au m²
        if all(col in df_clean.columns for col in ['valeur_fonciere', 'surface_reelle_bati']):
            df_clean['prix_m2'] = df_clean['valeur_fonciere'] / df_clean['surface_reelle_bati']
            print("    ✅ Prix au m² calculé")
        
        # Filtrage des prix au m² aberrants
        if 'prix_m2' in df_clean.columns:
            df_clean = df_clean[
                (df_clean['prix_m2'] > 100) & 
                (df_clean['prix_m2'] < 20000)  # Prix au m² entre 100€ et 20,000€
            ]
            print(f"    ✅ Prix au m² filtrés: {len(df_clean)} lignes restantes")
        
        # === ÉTAPE 4: NETTOYAGE DES CHAÎNES DE CARACTÈRES ===
        print("  🔤 Nettoyage des textes...")
        
        # Nettoyer les noms de communes
        if 'nom_commune' in df_clean.columns:
            df_clean['nom_commune'] = df_clean['nom_commune'].str.title().str.strip()
            communes_uniques = df_clean['nom_commune'].nunique()
            print(f"    ✅ Communes nettoyées: {communes_uniques} communes uniques")
        
        # Nettoyer les types de biens
        if 'type_local' in df_clean.columns:
            df_clean['type_local'] = df_clean['type_local'].str.strip()
            types_locaux = df_clean['type_local'].value_counts()
            print(f"    ✅ Types de biens: {len(types_locaux)} catégories")
        
        # === ÉTAPE 5: GESTION DES VALEURS MANQUANTES ===
        print("  🗑️  Gestion des valeurs manquantes...")
        
        # Supprimer les lignes avec des valeurs essentielles manquantes
        colonnes_essentielles = ['valeur_fonciere', 'surface_reelle_bati', 'prix_m2']
        colonnes_presentes = [col for col in colonnes_essentielles if col in df_clean.columns]
        
        if colonnes_presentes:
            df_clean = df_clean.dropna(subset=colonnes_presentes)
            print(f"    ✅ Valeurs manquantes supprimées: {len(df_clean)} lignes restantes")
        
        # Réinitialiser l'index après tous les filtrages
        df_clean = df_clean.reset_index(drop=True)
        
        print(f"✅ Nettoyage terminé: {len(df_clean)} transactions valides")
        
        return df_clean
    
    def _generate_quality_report(self, df, etape):
        """Génère un rapport de qualité des données"""
        rapport = {
            'etape': etape,
            'nombre_lignes': len(df),
            'nombre_colonnes': len(df.columns),
            'colonnes_disponibles': list(df.columns),
            'valeurs_manquantes': {},
            'statistiques_prix': {},
            'statistiques_surface': {}
        }
        
        # Statistiques sur les valeurs manquantes
        for col in df.columns:
            manquants = df[col].isna().sum()
            if manquants > 0:
                rapport['valeurs_manquantes'][col] = manquants
        
        # Statistiques sur les prix
        if 'valeur_fonciere' in df.columns:
            rapport['statistiques_prix'] = {
                'moyenne': df['valeur_fonciere'].mean(),
                'mediane': df['valeur_fonciere'].median(),
                'min': df['valeur_fonciere'].min(),
                'max': df['valeur_fonciere'].max(),
                'ecart_type': df['valeur_fonciere'].std()
            }
        
        # Statistiques sur les surfaces
        if 'surface_reelle_bati' in df.columns:
            rapport['statistiques_surface'] = {
                'moyenne': df['surface_reelle_bati'].mean(),
                'mediane': df['surface_reelle_bati'].median(),
                'min': df['surface_reelle_bati'].min(),
                'max': df['surface_reelle_bati'].max()
            }
        
        return rapport
    
    def _display_cleaning_summary(self, total_avant, total_apres, rapport_avant, rapport_apres):
        """Affiche un résumé du processus de nettoyage"""
        print("\n" + "="*60)
        print("📊 RÉSUMÉ DU NETTOYAGE DES DONNÉES")
        print("="*60)
        
        pourcentage_garde = (total_apres / total_avant) * 100
        print(f"📈 Conservation des données: {pourcentage_garde:.1f}%")
        print(f"   • Avant nettoyage: {total_avant:,} transactions")
        print(f"   • Après nettoyage: {total_apres:,} transactions")
        print(f"   • Données supprimées: {total_avant - total_apres:,} transactions")
        
        if total_apres > 0:
            if 'prix_m2' in rapport_apres['colonnes_disponibles']:
                prix_moyen = self._get_df_from_memory().get('prix_m2_moyen', 0)
                print(f"💰 Prix au m² moyen: {prix_moyen:.0f} €/m²")
        
        print("✅ Nettoyage terminé avec succès!")
        print("="*60)
    
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
            'geographic_coverage': {}
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
        
        return rapport
    
    def _calculate_quality_score(self, df):
        """Calcule un score de qualité des données (0-100)"""
        score = 100
        
        # Pénalités pour valeurs manquantes
        total_cells = len(df) * len(df.columns)
        missing_cells = df.isnull().sum().sum()
        if total_cells > 0:
            missing_percentage = (missing_cells / total_cells) * 100
            score -= missing_percentage * 0.5  # Pénalité modérée
        
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

    def _get_df_from_memory(self):
        """Méthode utilitaire pour récupérer les stats des données"""
        try:
            df_temp = pd.read_csv(self.processed_dir / "dvf_cleaned.csv")
            return {
                'prix_m2_moyen': df_temp['prix_m2'].mean() if 'prix_m2' in df_temp.columns else 0
            }
        except:
            return {}

# Test du DataLoader
if __name__ == "__main__":
    print("🧪 Test du DataLoader...")
    
    loader = DataLoader()
    data_path = loader.download_dvf_data(2024)
    
    if data_path:
        # Tester avec un échantillon plus grand pour avoir plus de villes
        df_clean = loader.load_and_clean_data(data_path, sample_size=20000)
        if df_clean is not None:
            loader.save_processed_data(df_clean)
            print(f"🎉 DataLoader testé avec succès! {len(df_clean)} transactions valides")
            
            # Afficher le rapport de qualité
            rapport = loader.get_data_quality_report(df_clean)
            print(f"📊 Score de qualité: {rapport['data_quality_score']}/100")
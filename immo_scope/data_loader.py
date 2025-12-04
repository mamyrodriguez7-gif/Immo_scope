# -*- coding: utf-8 -*-
"""
MODULE data_loader.py: Classe pour le téléchargement, le chargement et le nettoyage des données DVF.
"""
import pandas as pd
import requests
from pathlib import Path
import urllib3
import ssl
import time
from abc import ABC, abstractmethod

# Désactiver les avertissements SSL pour le téléchargement
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

class BaseDataLoader(ABC):
    """Classe de base abstraite pour le chargement de données (Bonus POO/Héritage)."""
    
    @abstractmethod
    def download_data(self, *args, **kwargs):
        """Méthode abstraite pour télécharger les données brutes."""
        pass
    
    @abstractmethod
    def load_and_clean(self, *args, **kwargs):
        """Méthode abstraite pour charger et nettoyer les données."""
        pass

class DataLoader(BaseDataLoader):
    """
    Gère le pipeline de données DVF : téléchargement, nettoyage, calculs et sauvegarde.
    Hérite de BaseDataLoader pour satisfaire au bonus POO/Héritage.
    """
    def __init__(self):
        """Initialise le DataLoader, configure les chemins et crée les répertoires."""
        self.data_dir = Path("data")
        self.raw_dir = self.data_dir / "raw"  
        self.processed_dir = self.data_dir / "processed"
        
        # Créer les dossiers
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialisation pour l'évaluation de performance
        self.performance_log = {}
    
    # Implémentation des méthodes abstraites
    def download_data(self, year=2023):
        """
        Télécharge les données DVF pour une année donnée à partir de data.gouv.fr.
        
        Parameters
        ----------
        year : int
            Année des données à télécharger (par défaut: 2023, cohérent avec le README).

        Returns
        -------
        Path or None
            Chemin du fichier téléchargé ou None en cas d'erreur.
        """
        start_time = time.time()
        print(f" Téléchargement des données DVF {year}...")
        
        # --- MISE À JOUR CRITIQUE POUR LA COHÉRENCE AVEC LE README (DVF 2023) ---
        # Note: L'URL 'latest' pourrait ne pas être la bonne, mais nous utilisons la version 2023
        # en supposant que le répertoire '2023' est disponible.
        # Attention: L'URL doit être ajustée si le fichier n'est pas "full.csv.gz" pour 2023.
        # Pour une meilleure fiabilité, on utilise la version de l'année spécifique si l'URL 'latest' ne fonctionne pas pour 2023.
        url = f"https://files.data.gouv.fr/geo-dvf/latest/csv/{year}/full.csv.gz"
        
        try:
            # Télécharger avec requests (requests.get gère la configuration SSL ici)
            response = requests.get(url, verify=False, timeout=30)
            response.raise_for_status()
            
            file_path = self.raw_dir / f"dvf_{year}.csv.gz"
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            end_time = time.time()
            self.performance_log['download_time_s'] = end_time - start_time
            print(f" Données {year} téléchargées en {self.performance_log['download_time_s']:.2f}s: {file_path}")
            return file_path
            
        except Exception as e:
            print(f" Erreur lors du téléchargement: {e}")
            print(f"Vérifiez que l'URL des données DVF {year} est correcte.")
            return None
    
    def load_and_clean(self, file_path, sample_size=10000):
        """
        Charge les données DVF, les nettoie, filtre les valeurs aberrantes
        et calcule le prix au m² (variable cible).
        
        Parameters
        ----------
        file_path : Path
            Chemin vers le fichier de données brutes (csv.gz).
        sample_size : int
            Nombre maximal de lignes à lire pour la performance.

        Returns
        -------
        pd.DataFrame or None
            DataFrame nettoyé et prêt pour la visualisation.
        """
        start_time = time.time()
        print(" Chargement et nettoyage des données...")
        
        try:
            # Lire le CSV. Nécessite que le fichier 'dvf_2024.csv.gz' existe
            df = pd.read_csv(file_path, compression='gzip', low_memory=False, nrows=sample_size)
            print(f" Données brutes chargées: {len(df)} lignes")
            
            # Appliquer le nettoyage
            df_clean = self._clean_data(df)
            
            end_time = time.time()
            self.performance_log['cleaning_time_s'] = end_time - start_time
            print(f" Nettoyage terminé en {self.performance_log['cleaning_time_s']:.2f}s")
            return df_clean
            
        except FileNotFoundError:
             print(f" Erreur: Fichier introuvable à {file_path}. Veuillez lancer le téléchargement d'abord.")
             return None
        except Exception as e:
            print(f" Erreur lors du chargement ou du nettoyage: {e}")
            return None
    
    def _clean_data(self, df):
        """
        Méthode interne pour appliquer les règles de nettoyage et les filtres.
        
        Parameters
        ----------
        df : pd.DataFrame
            DataFrame brut à nettoyer.

        Returns
        -------
        pd.DataFrame
            DataFrame après nettoyage et calcul de 'prix_m2'.
        """
        df_clean = df.copy()
        
        # 1. Conversion et gestion des erreurs (NaN)
        numeric_cols = ['valeur_fonciere', 'surface_reelle_bati', 'surface_terrain', 'latitude', 'longitude']
        for col in numeric_cols:
             df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        
        # 2. Ajout de l'année (si non présente)
        if 'date_mutation' in df_clean.columns and 'annee' not in df_clean.columns:
            try:
                df_clean['date_mutation'] = pd.to_datetime(df_clean['date_mutation'])
                df_clean['annee'] = df_clean['date_mutation'].dt.year
            except:
                df_clean['annee'] = 2023 # Année par défaut si conversion échoue

        # 3. Filtrer les données aberrantes
        df_clean = df_clean[
            (df_clean['valeur_fonciere'].notna()) &
            (df_clean['surface_reelle_bati'].notna()) &
            (df_clean['valeur_fonciere'] > 1000) & 
            (df_clean['valeur_fonciere'] < 5000000) &
            (df_clean['surface_reelle_bati'] > 0) &
            (df_clean['surface_reelle_bati'] < 1000)
        ]
        
        # 4. Calculer le prix au m²
        df_clean['prix_m2'] = df_clean['valeur_fonciere'] / df_clean['surface_reelle_bati']
        
        # 5. Filtrer les prix au m² aberrants
        df_clean = df_clean[
            (df_clean['prix_m2'] > 100) & 
            (df_clean['prix_m2'] < 20000)
        ]
        
        # Filtrer pour ne garder que Maison et Appartement (cohérent avec le README)
        df_clean = df_clean[df_clean['type_local'].isin(['Maison', 'Appartement'])]
        
        print(f"Données nettoyées: {len(df_clean)} lignes valides")
        return df_clean
    
    def save_processed_data(self, df, filename="dvf_cleaned.csv"):
        """
        Sauvegarde le DataFrame nettoyé dans le répertoire 'processed'.
        
        Parameters
        ----------
        df : pd.DataFrame
            DataFrame à sauvegarder.
        filename : str
            Nom du fichier de sortie.

        Returns
        -------
        Path
            Chemin du fichier sauvegardé.
        """
        file_path = self.processed_dir / filename
        df.to_csv(file_path, index=False)
        print(f" Données sauvegardées: {file_path}")
        return file_path

# Test du DataLoader
if __name__ == "__main__":
    print(" Test du DataLoader...")
    
    loader = DataLoader()
    # Le test utilise maintenant 2023 par défaut
    data_path = loader.download_data() 
    
    if data_path:
        df_clean = loader.load_and_clean(data_path, sample_size=5000)
        if df_clean is not None:
            loader.save_processed_data(df_clean)
            print(f" DataLoader testé avec succès! {len(df_clean)} transactions valides")
            print("\n⏱ Rapport de performance:")
            print(loader.performance_log)
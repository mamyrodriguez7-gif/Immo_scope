import pytest
import pandas as pd
from pathlib import Path
import sys 
import importlib.util 

# --- CORRECTION ULTIME DE L'IMPORTATION (Reste identique) ---
FILE_PATH_DATALOADER = Path(__file__).parent.parent / "immo_scope" / "data_loader.py"

if not FILE_PATH_DATALOADER.exists():
    raise FileNotFoundError(f"Erreur Fatale: Le fichier du Data Loader est introuvable à {FILE_PATH_DATALOADER}. Vérifiez l'arborescence.")

spec = importlib.util.spec_from_file_location("data_loader_module", FILE_PATH_DATALOADER)
data_loader_module = importlib.util.module_from_spec(spec)
sys.modules["data_loader_module"] = data_loader_module
spec.loader.exec_module(data_loader_module)

try:
    DataLoader = data_loader_module.DataLoader
except AttributeError:
    raise AttributeError("Erreur Fatale: La classe DataLoader n'est pas définie dans immo_scope/data_loader.py")

# ----------------------------------------------------------------------------------

# Utiliser un fixture pour charger les données une seule fois
@pytest.fixture(scope="session")
def cleaned_dataframe():
    """
    Tente de charger les données nettoyées à partir du fichier dvf_cleaned.csv.
    Si le fichier n'existe pas, exécute le pipeline de base du DataLoader pour le créer.
    """
    # Chemin vers le fichier nettoyé (doit être accessible depuis la racine du projet)
    file_path = Path("data") / "processed" / "dvf_cleaned.csv"
    
    # Si le fichier n'existe pas, exécuter le pipeline de base pour le créer
    if not file_path.exists():
        print("\n[INFO] Tentative de création du fichier nettoyé pour les tests...")
        loader = DataLoader()
        
        # Le DataLoader est configuré pour l'année 2023 dans sa méthode download_data()
        data_path = loader.download_data(year=2023)
        
        if data_path:
            # Charger et nettoyer les données
            df = loader.load_and_clean(data_path, sample_size=5000)
            if df is not None and not df.empty:
                loader.save_processed_data(df)
            else:
                 pytest.skip("Impossible de générer des données valides pour les tests (le fichier DVF 2023 pourrait être vide ou inaccessible).")
    
    # Vérification additionnelle que le fichier n'est pas vide après la création/vérification
    if file_path.exists():
        try:
            df = pd.read_csv(file_path)
        except pd.errors.EmptyDataError:
            pytest.skip("Le fichier dvf_cleaned.csv existe mais est vide. Skippé.")
            return pd.DataFrame()
    else:
        pytest.skip("Le fichier dvf_cleaned.csv n'a pas été créé et n'existe pas. Skippé.")
        return pd.DataFrame()


    # Charger les données pour les tests
    df = pd.read_csv(file_path)
    # Convertir les colonnes essentielles au format numérique pour les tests de borne
    df['prix_m2'] = pd.to_numeric(df['prix_m2'], errors='coerce')
    df['surface_reelle_bati'] = pd.to_numeric(df['surface_reelle_bati'], errors='coerce')
    df['valeur_fonciere'] = pd.to_numeric(df['valeur_fonciere'], errors='coerce')
    return df

# -----------------------------------------------------------
# TESTS DE QUALITÉ DE DONNÉES (EXIGENCE DE 3 POINTS)
# -----------------------------------------------------------

def test_dataframe_is_not_empty(cleaned_dataframe: pd.DataFrame):
    """Vérifie que le nettoyage a produit des données exploitables."""
    assert not cleaned_dataframe.empty, "Le DataFrame nettoyé est vide, le pipeline de données n'a retourné aucune ligne valide."

def test_critical_columns_exist(cleaned_dataframe: pd.DataFrame):
    """Vérifie que les colonnes calculées essentielles ('prix_m2') existent."""
    required_cols = ['prix_m2', 'valeur_fonciere', 'surface_reelle_bati', 'latitude', 'longitude', 'type_local']
    for col in required_cols:
        assert col in cleaned_dataframe.columns, f"La colonne critique '{col}' est manquante dans les données nettoyées."

def test_no_missing_price_metrics(cleaned_dataframe: pd.DataFrame):
    """Vérifie l'absence de NaN dans les métriques de prix et de surface utilisées pour les calculs."""
    # Le nettoyage doit s'assurer que ces colonnes n'ont pas de valeurs manquantes
    critical_cols = ['prix_m2', 'valeur_fonciere', 'surface_reelle_bati']
    for col in critical_cols:
        assert cleaned_dataframe[col].isnull().sum() == 0, f"Erreur: La colonne '{col}' contient des valeurs manquantes après nettoyage."

def test_price_is_within_reasonable_bounds(cleaned_dataframe: pd.DataFrame):
    """
    Vérifie que le prix au m² respecte les bornes définies dans la méthode _clean_data.
    (100 €/m² à 20 000 €/m²)
    """
    min_expected_price = 100 
    max_expected_price = 20000
    
    assert (cleaned_dataframe['prix_m2'] >= min_expected_price).all(), "Prix au m² trouvé sous la limite basse de 100 €/m²."
    assert (cleaned_dataframe['prix_m2'] <= max_expected_price).all(), "Prix au m² trouvé au-dessus de la limite haute de 20 000 €/m²."

def test_geographical_bounds(cleaned_dataframe: pd.DataFrame):
    """
    Vérifie que les coordonnées sont dans des limites géographiques raisonnables pour la France 
    (incluant les DROM/COM mentionnés dans l'échantillon).
    """
    # BORNES CORRIGÉES FINALEMENT pour s'assurer que TOUS les territoires français DVF sont inclus.
    # Longitude: -80 (Ouest des Antilles) à 180 (Est du Pacifique)
    # Latitude: -60 (Terres Australes) à 52 (Nord de la France)
    min_lat, max_lat = -60.0, 52.0  
    min_lon, max_lon = -80.0, 180.0 
    
    # Tester uniquement les lignes où les coordonnées sont présentes
    df_geo = cleaned_dataframe.dropna(subset=['latitude', 'longitude'])
    
    assert (df_geo['latitude'].between(min_lat, max_lat)).all(), "Certaines latitudes sont hors des bornes attendues pour la France."
    assert (df_geo['longitude'].between(min_lon, max_lon)).all(), "Certaines longitudes sont hors des bornes attendues pour la France."
# -*- coding: utf-8 -*-
"""
MODULE rapport_rodrigue.py: Rapport est destiné à être le point de contrôle pour l'équipe (Hadjer et Léa) au format JSON.
"""
import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import numpy as np # Ajout pour la robustesse (vérification NaN)

def generer_rapport():
    """
    Charge les données nettoyées, calcule les métriques clés, et génère 
    un rapport d'étape complet au format JSON pour l'équipe.
    """
    print("RAPPORT POUR HADJER ET LÉA")
    print("=" * 50)
    
    # Chemin correct (hypothèse que ce script est dans Immo_scope/scripts/)
    current_dir = Path(__file__).parent
    # Remonte à la racine Immo_scope/ pour trouver les dossiers data/
    project_root = current_dir.parent 
    
    data_file = project_root / "data" / "processed" / "dvf_cleaned.csv"
    
    if not data_file.exists():
        print(" Données non trouvées. Génère les données d'abord (avec DataLoader).")
        return
    
    df = pd.read_csv(data_file)
    
    # Vérifications de robustesse
    if df.empty:
        print(" Le DataFrame est vide. Rapport annulé.")
        return
    
    # Nettoyage minimal pour les métriques
    df['prix_m2'] = pd.to_numeric(df['prix_m2'], errors='coerce').fillna(0)
    
    # ----------------------------------------------------------------------
    # 1. METRIQUES STATISTIQUES (à partir de dvf_cleaned.csv)
    # ----------------------------------------------------------------------
    
    stats_ok = True
    try:
        statistiques = {
            "transactions": len(df),
            "annees": sorted(df['annee'].unique().astype(str).tolist()),
            "prix_moyen_m2": int(df['prix_m2'].mean()) if not df['prix_m2'].empty else 0,
            "surface_moyenne": int(df['surface_reelle_bati'].mean()) if not df['surface_reelle_bati'].empty else 0,
            "communes": df['nom_commune'].nunique() if 'nom_commune' in df.columns else 0
        }
    except Exception as e:
        print(f"Erreur lors du calcul des statistiques: {e}")
        stats_ok = False
        statistiques = {}
    
    # ----------------------------------------------------------------------
    # 2. INTÉGRATION DU RAPPORT DE QUALITÉ (pour donner un aperçu à l'équipe)
    # ----------------------------------------------------------------------
    
    quality_report_data = {}
    quality_report_file = project_root / "data" / "reports" / "quality_report.json"
    if quality_report_file.exists():
        try:
            with open(quality_report_file, 'r', encoding='utf-8') as f:
                quality_report_data = json.load(f)
        except Exception as e:
            quality_report_data['erreur'] = f"Impossible de charger report.json: {e}"

    # ----------------------------------------------------------------------
    # 3. CONSTRUCTION DU RAPPORT FINAL
    # ----------------------------------------------------------------------
    
    rapport = {
        "generation_par": "Rodrigue Mamy (22510795)",
        "date": datetime.now().isoformat(),
        "statistiques": statistiques,
        "rapport_qualite_inclus": quality_report_data.get("metrics", "N/A"),
        "fichiers_fournis": [
            "data/processed/dvf_cleaned.csv - Données principales",
            "data/reports/quality_report.json - Métriques techniques"
        ],
        "prochaines_etapes": {
            "hadjer": "Finaliser le dashboard avec Plotly/Folium et les widgets",
            "lea": "Validation des résultats des tests unitaires et génération de la documentation API (Sphinx/Quarto)"
        },
        "statut_pipeline": "OK" if stats_ok else "ERREUR"
    }
    
    # Sauvegarder
    report_file = project_root / "data" / "reports" / "rapport_equipe.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(rapport, f, indent=2, ensure_ascii=False)
    
    print(f" Rapport sauvegardé: {report_file}")
    
    # Afficher résumé
    print(f"\n DONNÉES PRÊTES:")
    print(f"   • {statistiques.get('transactions', 0):,} transactions immobilières")
    print(f"   • Prix moyen: {statistiques.get('prix_moyen_m2', 0):.0f} €/m²")
    print(f"   • Période: {statistiques.get('annees', ['N/A'])}")
    print(f"   • {statistiques.get('communes', 0)} communes françaises")

if __name__ == "__main__":
    generer_rapport()
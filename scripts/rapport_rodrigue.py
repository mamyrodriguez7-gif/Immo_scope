import pandas as pd
import json
from datetime import datetime
from pathlib import Path

def generer_rapport():
    print(" RAPPORT RODRIGUE POUR HADJER ET LÉA")
    print("=" * 50)
    
    # Chemin correct
    current_dir = Path(__file__).parent
    data_file = current_dir.parent / "data" / "processed" / "dvf_cleaned.csv"
    
    if not data_file.exists():
        print(" Données non trouvées. Génère les données d'abord.")
        return
    
    df = pd.read_csv(data_file)
    
    rapport = {
        "generation_par": "Rodrigue Mamy (22510795)",
        "date": datetime.now().isoformat(),
        "statistiques": {
            "transactions": len(df),
            "annees": df['annee'].unique().tolist(),
            "prix_moyen_m2": int(df['prix_m2'].mean()),
            "communes": df['nom_commune'].nunique() if 'nom_commune' in df.columns else 0
        },
        "fichiers_fournis": [
            "data/processed/dvf_cleaned.csv - Données principales",
            "data/reports/report.json - Métriques techniques"
        ],
        "prochaines_etapes": {
            "hadjer": "Développer le dashboard avec Plotly/Folium",
            "lea": "Tests qualité données et validation"
        }
    }
    
    # Sauvegarder
    report_file = current_dir.parent / "data" / "reports" / "rapport_equipe.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(rapport, f, indent=2, ensure_ascii=False)
    
    print(f" Rapport sauvegardé: {report_file}")
    
    # Afficher résumé
    print(f"\n DONNÉES PRÊTES:")
    print(f"   • {len(df):,} transactions immobilières")
    print(f"   • Période: {sorted(df['annee'].unique())}")
    print(f"   • {df['nom_commune'].nunique()} communes françaises")

if __name__ == "__main__":
    generer_rapport()
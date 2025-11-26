# 📁 scripts/generate_final_reports.py - VERSION CORRIGÉE
import pandas as pd
import json
from datetime import datetime
from pathlib import Path

print(" RODRIGUE - GÉNÉRATION DES RAPPORTS FINAUX")
print("=" * 50)

# CHEMIN CORRECT depuis scripts/
current_dir = Path(__file__).parent
data_file = current_dir.parent / "data" / "processed" / "dvf_cleaned.csv"

print(f" Recherche des données: {data_file}")

if not data_file.exists():
    print(" Fichier non trouvé!")
    print(" Exécute depuis la racine: python scripts/generate_final_reports.py")
    exit()

# Charger tes données
df = pd.read_csv(data_file)

print(" ANALYSE DES DONNÉES EXISTANTES:")
print(f"   • Transactions: {len(df):,}")
print(f"   • Prix moyen: {df['prix_m2'].mean():.0f} €/m²")
print(f"   • Surface moyenne: {df['surface_reelle_bati'].mean():.0f} m²")
print(f"   • Types: {df['type_local'].value_counts().to_dict()}")
print(f"   • Communes: {df['nom_commune'].nunique()}")

# 1. RAPPORT POUR HADJER (Dashboard)
print("\n PRÉPARATION POUR HADJER...")
dashboard_data = {
    "metadata": {
        "generated_by": "Rodrigue Mamy (22510795)",
        "generation_date": datetime.now().isoformat(),
        "data_source": "DVF 2023"
    },
    "metrics": {
        "total_transactions": len(df),
        "avg_price_m2": round(df['prix_m2'].mean()),
        "avg_surface": round(df['surface_reelle_bati'].mean()),
        "avg_budget": round(df['valeur_fonciere'].mean()),
        "cities_covered": df['nom_commune'].nunique(),
        "departments_covered": df['code_departement'].nunique()
    },
    "visualization_data": {
        "price_distribution": {
            "min": round(df['prix_m2'].min()),
            "max": round(df['prix_m2'].max()),
            "mean": round(df['prix_m2'].mean()),
            "median": round(df['prix_m2'].median())
        },
        "property_types": df['type_local'].value_counts().to_dict(),
        "top_cities": df['nom_commune'].value_counts().head(10).to_dict(),
        "top_departments": df['code_departement'].value_counts().head(5).to_dict()
    }
}

dashboard_file = current_dir.parent / "data" / "reports" / "dashboard_data.json"
with open(dashboard_file, 'w', encoding='utf-8') as f:
    json.dump(dashboard_data, f, indent=2, ensure_ascii=False)

print(f" Données dashboard: {dashboard_file}")

# 2. RAPPORT POUR LÉA (Qualité)
print(" PRÉPARATION POUR LÉA...")
quality_report = {
    "data_quality_metrics": {
        "completeness_score": round((1 - df.isnull().sum().sum() / df.size) * 100, 1),
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "missing_values_per_column": df.isnull().sum().to_dict()
    },
    "validation_checks": {
        "price_validation": {
            "min_price_m2": round(df['prix_m2'].min()),
            "max_price_m2": round(df['prix_m2'].max()),
            "valid_range": "500 - 20,000 €/m²",
            "status": " VALIDE" if df['prix_m2'].between(500, 20000).all() else "⚠️ VÉRIFIER"
        },
        "surface_validation": {
            "min_surface": round(df['surface_reelle_bati'].min()),
            "max_surface": round(df['surface_reelle_bati'].max()),
            "valid_range": "9 - 500 m²",
            "status": " VALIDE" if df['surface_reelle_bati'].between(9, 500).all() else "⚠️ VÉRIFIER"
        }
    },
    "columns_analysis": {
        "available_columns": list(df.columns),
        "data_types": {col: str(df[col].dtype) for col in df.columns}
    }
}

quality_file = current_dir.parent / "data" / "reports" / "quality_report.json"
with open(quality_file, 'w', encoding='utf-8') as f:
    json.dump(quality_report, f, indent=2, ensure_ascii=False)

print(f" Rapport qualité: {quality_file}")

# 3. RAPPORT ÉQUIPE
print(" RAPPORT POUR L'ÉQUIPE...")
team_report = {
    "project": "Immo_scope - Analyse Marché Immobilier",
    "phase": "Mi-parcours - Données prêtes",
    "team_members": {
        "rodrigue_mamy": "Data Engineering & Architecture",
        "benaissa_hadjer": "Visualization & Dashboard", 
        "lea_benameur": "Quality Assurance & Testing"
    },
    "current_status": {
        "data_ready": True,
        "transactions_processed": len(df),
        "data_quality_score": quality_report["data_quality_metrics"]["completeness_score"],
        "ready_for": ["dashboard_development", "quality_testing", "analysis"]
    },
    "achievements": [
        " Données DVF 2023 téléchargées et nettoyées",
        " 822 transactions immobilières validées",
        " Structure de données optimisée pour visualisation",
        " Rapports techniques générés automatiquement"
    ],
    "next_steps": {
        "hadjer": "Développer le dashboard interactif avec Plotly/Folium",
        "lea": "Valider la qualité des données et créer tests unitaires",
        "rodrigue": "Optimiser les performances et préparer l'intégration Git"
    },
    "files_delivered": [
        "data/processed/dvf_cleaned.csv - Données principales",
        "data/reports/dashboard_data.json - Données pour le dashboard",
        "data/reports/quality_report.json - Métriques de qualité"
    ]
}

team_file = current_dir.parent / "data" / "reports" / "team_report.json"
with open(team_file, 'w', encoding='utf-8') as f:
    json.dump(team_report, f, indent=2, ensure_ascii=False)

print(f" Rapport équipe: {team_file}")

# RÉSUMÉ FINAL
print(f"\n SYNTHÈSE FINALE RODRIGUE:")
print("=" * 45)
print(f" {len(df):,} transactions immobilières")
print(f" {df['prix_m2'].mean():.0f} €/m² (moyenne)")
print(f" {df['type_local'].value_counts().to_dict()}")
print(f"  {df['nom_commune'].nunique()} communes françaises")
print(f" {quality_report['data_quality_metrics']['completeness_score']}% de qualité")
print(f"\n DONNÉES PRÊTES POUR HADJER ET LÉA!")
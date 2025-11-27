# 📁 scripts/start_hadjer.py
"""
SCRIPT DE DÉMARRAGE POUR HADJER
"""
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

print("🎨 HADJER - DÉMARRAGE DU DASHBOARD")
print("=" * 50)

# CHEMIN CORRECT depuis scripts/
current_dir = Path(__file__).parent
project_root = current_dir.parent

# 1. CHARGER LES DONNÉES PRÉPARÉES PAR RODRIGUE
dashboard_file = project_root / "data" / "reports" / "dashboard_data.json"
data_file = project_root / "data" / "processed" / "dvf_cleaned.csv"

print(f"📁 Recherche des données: {dashboard_file}")

if not dashboard_file.exists():
    print("❌ Fichier dashboard_data.json non trouvé!")
    print("💡 Exécute d'abord: python scripts/generate_final_reports.py")
    exit()

print("📊 Chargement des données...")
with open(dashboard_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 2. CHARGER LES DONNÉES COMPLÈTES (si le fichier existe)
if data_file.exists():
    df = pd.read_csv(data_file)
    print(f"✅ Données complètes chargées: {len(df)} transactions")
else:
    df = None
    print("⚠️  Fichier données complètes non trouvé")

# 3. AFFICHER LES MÉTRIQUES
print("\n📈 MÉTRIQUES DISPONIBLES :")
metrics = data['metrics']
print(f"• Transactions : {metrics['total_transactions']}")
print(f"• Prix moyen : {metrics['avg_price_m2']} €/m²")
print(f"• Surface moyenne : {metrics['avg_surface']} m²")
print(f"• Communes : {metrics['cities_covered']}")

# 4. PREMIER GRAPHIQUE - CAMEMBERT TYPES DE BIENS
print("\n🎯 Création du premier graphique...")
types_data = data['visualization_data']['property_types']

fig_pie = px.pie(
    values=list(types_data.values()),
    names=list(types_data.keys()),
    title="🏠 Répartition des types de biens immobiliers",
    color_discrete_sequence=px.colors.qualitative.Set3
)

fig_pie.update_traces(
    textposition='inside',
    textinfo='percent+label',
    hovertemplate="<b>%{label}</b><br>%{value} transactions<br>%{percent}"
)

fig_pie.show()
print("✅ Premier graphique créé !")

# 5. DEUXIÈME GRAPHIQUE - TOP COMMUNES
print("\n🗺️ Création du graphique top communes...")
top_cities = data['visualization_data']['top_cities']

# Prendre les 10 premières communes
cities_names = list(top_cities.keys())[:10]
cities_values = list(top_cities.values())[:10]

fig_bar = px.bar(
    x=cities_values,
    y=cities_names,
    orientation='h',
    title="🏆 Top 10 des communes par nombre de transactions",
    labels={'x': 'Nombre de transactions', 'y': 'Commune'},
    color=cities_values,
    color_continuous_scale='Blues'
)

fig_bar.update_layout(
    yaxis={'categoryorder': 'total ascending'}
)

fig_bar.show()
print("✅ Deuxième graphique créé !")

# 6. TROISIÈME GRAPHIQUE - DISTRIBUTION PRIX (si données complètes disponibles)
if df is not None:
    print("\n💰 Création histogramme prix...")
    
    # Échantillonner pour de meilleures performances
    sample_df = df.sample(min(500, len(df)))
    
    fig_hist = px.histogram(
        sample_df,
        x='prix_m2',
        nbins=20,
        title="📊 Distribution des prix au m²",
        labels={'prix_m2': 'Prix au m² (€)'},
        color_discrete_sequence=['#FF9999']
    )
    
    fig_hist.update_layout(
        xaxis_title="Prix au m² (€)",
        yaxis_title="Nombre de transactions"
    )
    
    fig_hist.show()
    print("✅ Troisième graphique créé !")

print(f"\n🎉 SUCCÈS ! HADJER PEUT MAINTENANT :")
print("1. Modifier ces graphiques dans scripts/start_hadjer.py")
print("2. Créer de nouvelles visualisations")
print("3. Développer dans immo_scope/visualizer.py")
print("4. Personnaliser les couleurs et styles")
# Immo_scope 📊🏠

**Dashboard interactif pour l'analyse des prix immobiliers en France**
*Données DVF (Demandes de Valeurs Foncières) - Analyse 2023*

## 🎯 Description

Immo_scope est un projet de data science qui transforme les données DVF publiques en insights visuels. Notre pipeline automatique télécharge, nettoie, analyse et visualise le marché immobilier français.

## 🚀 Statut du Projet

**✅ PHASE DONNÉES TERMINÉE** - *Prêt pour le développement du dashboard*

### 📊 Résultats Actuels
- **822 transactions** DVF 2023 analysées
- **Prix moyen** : 3,574 €/m²
- **689 communes** françaises couvertes
- **467 Maisons** + **355 Appartements**
- **Qualité données** : 100%

## 🏗️ Architecture du Projet

```
Immo_scope/
├── immo_scope/                 # 📦 Modules Python
│   ├── advanced_data_loader.py # 🔄 DataLoader avancé DVF
│   └── visualizer.py          # 🎨 Visualisations (en développement)
├── scripts/                    # 🛠️ Scripts d'analyse
│   ├── check_results.py       # ✅ Vérification données
│   ├── generate_final_reports.py # 📊 Génération rapports
│   ├── verify_installation.py # 🔍 Test installation
│   └── ...
├── data/                       # 🗃️ Données
│   ├── processed/
│   │   └── dvf_cleaned.csv    # 📈 Données principales
│   └── reports/               # 📋 Rapports automatiques
│       ├── dashboard_data.json # 🎨 Données visualisations
│       ├── quality_report.json # 🔍 Métriques qualité
│       └── team_report.json   # 👥 Rapport équipe
├── notebooks/                  # 🔬 Exploration données
├── roadmap/                   # 📝 Documentation
│   └── README.qmd            # 📋 Rapport mi-parcours
└── requirements.txt           # 📦 Dépendances
```

## ⚡ Fonctionnalités Implémentées

### 🔄 DataLoader Avancé (Rodrigue - ✅ Terminé)
- Téléchargement automatique DVF 2023
- Nettoyage intelligent des données
- Calcul automatique prix au m²
- Validation qualité complète
- Génération rapports JSON

### 📊 Données Livrées
- `dvf_cleaned.csv` - 822 transactions nettoyées
- `dashboard_data.json` - Données structurées pour visualisations
- `quality_report.json` - Métriques qualité complètes
- `team_report.json` - Rapport d'équipe

### 🎨 Visualisations (Hadjer - 🚧 En cours)
*À développer avec les données préparées*

### 🔍 Tests Qualité (Léa - 🔜 Prochain)
*Validation et assurance qualité*

## 🛠️ Installation et Utilisation

```bash
# Cloner le repository
git clone https://github.com/mamyrodriguez7-gif/Immo_scope.git
cd Immo_scope

# Installer les dépendances
pip install -r requirements.txt

# Vérifier l'installation
python scripts/verify_installation.py

# Analyser les données
python scripts/check_results.py

# Générer les rapports
python scripts/generate_final_reports.py
```

## 👥 Équipe & Rôles

### **Rodrigue Mamy** (22510795) - ✅ **Data Engineering**
- Architecture projet & DataLoader
- Traitement données DVF 2023
- Automatisation rapports

### **Benaissa Hadjer** (22506347) - 🚧 **Visualisation**
- Dashboard interactif Plotly/Folium
- Graphiques et analyses visuelles
- Design interface

### **Léa Benameur** (22514472) - 🔜 **Qualité & Tests**
- Validation données DVF
- Tests unitaires et qualité
- Documentation utilisateur

## 📅 Planning - Mi-parcours ✅

**🎯 Prochaines étapes :**
- Dashboard interactif (Hadjer)
- Tests qualité (Léa)
- Intégration finale (Équipe)

## 📈 Résultats & Insights

### 🏠 Répartition des biens
- **57% Maisons** (467 transactions)
- **43% Appartements** (355 transactions)

### 💰 Analyse des prix
- **Prix moyen** : 3,574 €/m²
- **Surface moyenne** : 81 m²
- **Budget moyen** : 289,000 €

### 🗺️ Couverture géographique
- **689 communes** françaises
- Données nationales représentatives

## 🔗 Liens Utiles

- **📂 Repository GitHub** : [github.com/mamyrodriguez7-gif/Immo_scope](https://github.com/mamyrodriguez7-gif/Immo_scope)
- **📊 Données DVF** : [data.gouv.fr](https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncières/)
- **📋 Documentation** : `roadmap/README.qmd`

## 📄 Licence

Ce projet est sous licence **MIT**. Voir le fichier `LICENSE` pour plus de détails.

---

*Dernière mise à jour : Novembre 2024 - Phase données terminée ✅*

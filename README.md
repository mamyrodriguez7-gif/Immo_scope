# Immo_scope 📊🏠

Dashboard interactif pour l'analyse des prix immobiliers en France à partir des données DVF (Demandes de Valeurs Foncières).

## 🎯 Description
**Immo_scope** est un projet de visualisation de données qui permet d'analyser l'évolution des prix immobiliers en France.
Le projet télécharge, nettoie et visualise automatiquement les données DVF publiques.

## 🏗️ Architecture du Projet
```
Immo_scope/
├── immo_scope/              # Module Python principal
│   ├── data_loader.py      # Téléchargement et nettoyage des données DVF
│   └── visualizer.py       # Création des visualisations interactives
├── data/                   # Gestion des données
│   ├── raw/               # Données brutes DVF
│   └── processed/         # Données nettoyées + graphiques HTML
├── notebooks/              # Exploration et analyse des données
├── roadmap/                # Rapport de mi-parcours
│   ├── README.qmd         # Rapport détaillé
│   └── sketches/          # Maquettes des résultats
├── requirements.txt        # Dépendances Python
└── README.md              # Ce fichier
```

## 📊 Fonctionnalités Implémentées

### ✅ DataLoader
- Téléchargement automatique des données DVF
- Nettoyage et traitement des données
- Calcul du prix au m²
- Filtrage des valeurs aberrantes

### ✅ Visualizer
- Histogramme des prix au m²
- Classement des départements par prix
- Relation prix vs surface
- Top communes par transactions

### 📈 Résultats Actuels
- **100 transactions** analysées
- **Prix moyen** : 4 617 €/m²
- **4 visualisations** interactives générées

## 🚀 Installation et Utilisation

```bash
# Cloner le repository
git clone https://github.com/mamyrodriguez7-gif/Immo_scope.git
cd Immo_scope

# Installer les dépendances
pip install -r requirements.txt

# Tester le DataLoader
python -c "from immo_scope.data_loader import DataLoader; loader = DataLoader()"

# Générer les visualisations
python -c "from immo_scope.visualizer import PlotVisualizer; visualizer = PlotVisualizer()"
```

## 👥 Équipe
- **Rodrigue Mamy** (22510795)
- **Benaissa Hadjer** (22506347)
- **Léa Benameur** (22514472)

## 📅 Planning
<img width="2880" height="680" alt="image" src="https://github.com/user-attachments/assets/4e86777f-a86a-449b-989c-02c39b7be5ca" />


- **Mi-parcours** : 25 octobre 2025 ✅
- **Finalisation** : 10 décembre 2025
- **Présentation orale** : 12 décembre 2025

## 🔗 Liens Utiles
- [Données DVF](https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncières/)
- [Documentation Plotly](https://plotly.com/python/)

## 📄 Licence
Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

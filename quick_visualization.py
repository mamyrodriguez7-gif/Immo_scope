# -*- coding: utf-8 -*-
"""
Created on Wed Nov 26 14:36:11 2025

@author: mamyr
"""

# 📁 Fichier : quick_visualization.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def quick_visualization():
    print(" VISUALISATION RAPIDE - RODRIGUE")
    
    try:
        df = pd.read_csv("data/processed/dvf_cleaned.csv")
        
        # Créer une figure avec plusieurs graphiques
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('IMMO_SCOPE - Analyse des Données DVF par Rodrigue', fontsize=16, fontweight='bold')
        
        # 1. Distribution des prix au m²
        axes[0, 0].hist(df['prix_m2'], bins=30, alpha=0.7, edgecolor='black')
        axes[0, 0].set_title('Distribution des Prix au m²')
        axes[0, 0].set_xlabel('Prix (€/m²)')
        axes[0, 0].set_ylabel('Nombre de transactions')
        axes[0, 0].axvline(df['prix_m2'].mean(), color='red', linestyle='--', label=f'Moyenne: {df["prix_m2"].mean():.0f} €')
        axes[0, 0].legend()
        
        # 2. Répartition par type de bien
        if 'type_local' in df.columns:
            type_counts = df['type_local'].value_counts()
            axes[0, 1].pie(type_counts.values, labels=type_counts.index, autopct='%1.1f%%')
            axes[0, 1].set_title('Répartition par Type de Bien')
        
        # 3. Prix vs Surface
        axes[1, 0].scatter(df['surface_reelle_bati'], df['prix_m2'], alpha=0.5)
        axes[1, 0].set_title('Relation Surface vs Prix au m²')
        axes[1, 0].set_xlabel('Surface (m²)')
        axes[1, 0].set_ylabel('Prix (€/m²)')
        
        # 4. Répartition par année
        if 'annee' in df.columns:
            year_counts = df['annee'].value_counts().sort_index()
            axes[1, 1].bar(year_counts.index, year_counts.values)
            axes[1, 1].set_title('Transactions par Année')
            axes[1, 1].set_xlabel('Année')
            axes[1, 1].set_ylabel('Nombre de transactions')
        
        plt.tight_layout()
        plt.savefig('data/reports/quick_visualization.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f" Visualisation sauvegardée: data/reports/quick_visualization.png")
        
    except Exception as e:
        print(f" Erreur visualisation: {e}")

if __name__ == "__main__":
    quick_visualization()
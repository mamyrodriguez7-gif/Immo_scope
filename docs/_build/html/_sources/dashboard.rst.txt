Dashboard Streamlit
===================

Le dashboard a été développé pour permettre une visualisation simple
et interactive des données DVF 2023.

Pages disponibles :
-------------------

- **Accueil** : présentation et indicateurs clés
- **Visualisations** : graphiques interactifs
- **Carte interactive** : localisation des transactions
- **Dashboard complet** : résumé multi-graphique

Lancement du dashboard
----------------------

Dans un terminal :

.. code-block:: bash

   streamlit run streamlit_app.py

Le dashboard charge automatiquement les modules :

- ``Visualizer`` pour les graphiques
- ``MapVisualizer`` pour la carte

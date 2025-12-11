Architecture du projet
======================

Le projet est structuré en trois grandes parties :

1. Data Engineering (Rodrigue)
2. Qualité & Tests Unitaires (Léa)
3. Visualisation & Dashboard (Hadjer)

Organisation du dossier ``immo_scope`` :

.. code-block::

   immo_scope/
      ├── data_loader.py
      ├── visualizer.py
      ├── map_visualizer.py
      ├── __init__.py

Chaque module joue un rôle précis dans le pipeline DVF :
- extraction, nettoyage,
- analyses statistiques,
- construction du dashboard interactif.

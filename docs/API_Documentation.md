Documentation API Immo\_scope (HAX712X)



Cette documentation a été générée à partir des Docstrings du module immo\_scope pour détailler l'interface publique (API) du pipeline de traitement et de visualisation des données DVF.



1\. Module data\_loader.py



Classe DataLoader (Hérite de BaseDataLoader)



Responsabilité : Gère le pipeline de données DVF : téléchargement, nettoyage, calculs et sauvegarde.



Méthode download\_data(year=2023)



Rôle : Télécharge les données DVF pour une année donnée à partir de data.gouv.fr.



Parameters :



year (int) : Année des données à télécharger (par défaut: 2023, cohérent avec le README).



Returns :



Path ou None : Chemin du fichier téléchargé ou None en cas d'erreur.



Méthode load\_and\_clean(file\_path, sample\_size=10000)



Rôle : Charge les données DVF, les nettoie, filtre les valeurs aberrantes et calcule le prix au m² (variable cible).



Parameters :



file\_path (Path) : Chemin vers le fichier de données brutes (csv.gz).



sample\_size (int) : Nombre maximal de lignes à lire pour la performance.



Returns :



pd.DataFrame ou None : DataFrame nettoyé et prêt pour la visualisation.



Méthode save\_processed\_data(df, filename="dvf\_cleaned.csv")



Rôle : Sauvegarde le DataFrame nettoyé dans le répertoire 'processed'.



Parameters :



df (pd.DataFrame) : DataFrame à sauvegarder.



filename (str) : Nom du fichier de sortie.



Returns :



Path : Chemin du fichier sauvegardé.



2\. Module visualizer.py



Classe PlotVisualizer



Responsabilité : Classe regroupant les méthodes pour générer différentes visualisations interactives du marché immobilier à l'aide de Plotly.



Méthode plot\_price\_distribution(df)



Rôle : Crée un histogramme de la distribution des prix au m² pour les transactions.



Parameters :



df (pd.DataFrame) : DataFrame nettoyé contenant la colonne 'prix\_m2'.



Returns :



plotly.graph\_objects.Figure : Figure Plotly affichant la distribution des prix.



Méthode plot\_price\_by\_department(df, top\_n=20)



Rôle : Crée un graphique à barres des prix moyens par département.



Parameters :



df (pd.DataFrame) : DataFrame nettoyé contenant les colonnes 'prix\_m2' et 'code\_departement'.



top\_n (int) : Nombre de départements à afficher.



Returns :



plotly.graph\_objects.Figure : Figure Plotly montrant les prix moyens par département.



Méthode plot\_price\_vs\_surface(df)



Rôle : Crée un nuage de points montrant la relation entre la surface du bien et sa valeur foncière, coloré par le prix au m².



Parameters :



df (pd.DataFrame) : DataFrame nettoyé contenant les colonnes 'surface\_reelle\_bati', 'valeur\_fonciere' et 'prix\_m2'.



Returns :



plotly.graph\_objects.Figure : Figure Plotly montrant la relation prix/surface.



Méthode plot\_property\_types(df)



Rôle : Crée un graphique en camembert pour visualiser la répartition des types de biens.



Parameters :



df (pd.DataFrame) : DataFrame nettoyé contenant la colonne 'type\_local'.



Returns :



plotly.graph\_objects.Figure ou None : Figure Plotly en camembert ou None si la colonne est manquante.



Méthode plot\_commune\_comparison(df, communes=None)



Rôle : Crée un Box Plot pour comparer la distribution des prix au m² entre différentes communes.



Parameters :



df (pd.DataFrame) : DataFrame nettoyé contenant les colonnes 'prix\_m2' et 'nom\_commune'.



communes (list, optional) : Liste des noms de communes à comparer. Par défaut: \['Paris', 'Marseille', 'Lyon', 'Montpellier', 'Bordeaux'].



Returns :



plotly.graph\_objects.Figure ou None : Figure Plotly Box Plot.


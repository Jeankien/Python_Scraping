# Books to Scrape - Scraper Python

## Présentation

Ce projet est un script Python permettant de scraper le site éducatif [Books to Scrape](https://books.toscrape.com/).  
Il extrait les informations suivantes pour chaque livre : titre, prix, disponibilité, note, URL du produit, URL de l'image, code UPC et catégorie.  
Le script peut scraper une catégorie spécifique ou toutes les catégories, enregistrer les données au format CSV, télécharger les images de couverture et analyser les données avec Pandas.

---

## Fonctionnalités

- Scraper une ou plusieurs catégories.
- Gestion automatique de la pagination.
- Enregistrement des données dans des fichiers CSV structurés.
- Téléchargement optionnel des images de couverture.
- Analyse statistique des données :
  - Prix moyen par catégorie
  - Distribution des notes
  - Nombre total de livres
- Création automatique des dossiers de sortie pour CSV et images.
- Mode verbeux pour afficher la progression dans le terminal.

---

## Structure du projet
```
Projet1 - scraping_books/solutions
│
├── script.py # Script principal
├── README.md # Documentation principale
│
├── /csv/ # Fichiers CSV générés
│ ├── category_Travel.csv
│ └── ...
│
└── /images/ # Images téléchargées
├── Travel/
│ ├── <UPC>_<titre>.jpg
│ └── ...
└── ...
```

---

## Utilisation

Le script se lance depuis la ligne de commande :

```bash
python script.py -c <nom_categorie> [options]

Option	            Description
-c, --categories	Obligatoire. Nom ou liste de catégories à scraper. Utilisez "All" pour tout scraper.
-o, --outdir	    Facultatif. Nom du dossier de sortie pour CSV et images.
-i, --images	    Facultatif. Télécharge les images de couverture si présent.
-v, --verbose	    Facultatif. Active le mode verbeux pour suivre la progression.
-a, --analyze       Facultatif. Analyse les données des catégories sélectionnées avec Pandas et affiche: prix moyen, distribution des notes et nombre total de livres.
```

import requests
from scrapy import Selector
import pandas as pd
import csv
import os
import argparse

base_url="https://books.toscrape.com/"
category_url="catalogue/category/"

data= requests.get(base_url)
sel = Selector(text=data.text)
nav = sel.css("ul[class='nav nav-list']").getall()
categories=[]
cat_sel = Selector(text=nav[0])
titles=(cat_sel.css("a::text").getall())
for title in titles:
    categories.append(title.strip().replace(" ","-"))
# categories=[title.replace(" ","-") for title in categories]
#au lieu de faire une autre ligne jai mis dans le append afin que ce soit plus simple

def get_category(cat_title):
    """
    Retourne l'URL complète d'une catégorie spécifique du site "Books to Scrape".
    Args:
        cat_title (str): Nom de la catégorie (ex. "Travel", "Mystery", "Crime").

    Returns:
        str: URL complète de la catégorie demandée.

    Notes:
        - Si la catégorie n'existe pas, la fonction renvoie par défaut la catégorie "Books" qui contient tous les livres.
        - Le site cible est : https://books.toscrape.com/
    """
    title_exist=False
    index=0
    for i in range(1,len(categories)):
        if categories[i].lower() == cat_title.lower().replace(" ","-"):
            title_exist=True
            index=i
            break
    if title_exist:
        title_url="books/"+categories[index].lower()+"_"+str(index+1)
        url=base_url+category_url+title_url
        return url
    else:
        title_url=categories[index].lower()+"_1"
        url=base_url+category_url+title_url
        return url
        

def get_books(cat_title):
    """
    Extrait toutes les informations des livres d'une catégorie donnée.

    Args:
        cat_title (str): Nom de la catégorie à extraire.

    Returns:
        list[list]: Liste contenant les informations de chaque livre, sous la forme :
            [
                [title, price, stock, rating, product_url, image_url, upc, category],
                ...
            ]

    Notes:
        - Gère la pagination automatiquement.
        - Effectue plusieurs requêtes HTTP (une par page et par livre).
        - Peut être relativement lent à cause du scraping détaillé.
    """
    url= get_category(cat_title)
    all_books= requests.get(url)
    all_books.encoding="utf-8"
    sel = Selector(text=all_books.text)
    books_info=[]

    #get nombre de livres et nombre de pages
    nb_books = sel.css("form[class='form-horizontal'] strong::text").get()
    nb_pages=(int(nb_books)//20)+1 #on divise le nombre de livres par 20 car il y a 20 livres par page
    for i in range(nb_pages):
        books = sel.css("article[class='product_pod']").getall()
        for book in books:
            books_info.append([])
            
            #get price
            books_sel = Selector(text=book)
            price=(books_sel.css("p[class='price_color']::text").get())
            price=price[1:]
            
            #get rating
            star=(books_sel.css("p").get())
            rating = star.split('star-rating ') #separe tout ce qui se trouve avant "star-rating " de tout ce qu'il y a apres
            rating = rating[1].split('">\n') #separe tout ce qui se trouve avant '">\n', ce qui dans ce cas sera le rating
            rating=rating[0]
            
            #get product URL
            book_href=(books_sel.css("h3 a").get())
            book_url_relatif = book_href.split('href="')
            book_url_relatif = book_url_relatif[1].split('"')
            book_url_absolu = book_url_relatif[0].replace("../../..", "https://books.toscrape.com/catalogue")
            
            #get image URL
            image_href=(books_sel.css("div[class='image_container'] a").get())
            image_url_relatif = image_href.split('img src="')
            image_url_relatif = image_url_relatif[1].split('"')
            image_url_absolu = image_url_relatif[0].replace("../../../..", "https://books.toscrape.com/")

            #get UPC
            book_data= requests.get(book_url_absolu)
            book_sel = Selector(text=book_data.text)
            UPC=(book_sel.css("table[class='table table-striped'] td::text").getall())
            UPC=UPC[0]

            #get category
            category=(book_sel.css("ul[class='breadcrumb'] li a::text").getall())
            category=category[-1]

            #get title
            title=(book_sel.css("ul[class='breadcrumb'] li[class='active']::text").get())

            #get stock
            stock=(book_sel.css("table[class='table table-striped'] td::text").getall())
            stock=stock[5] #Renvoie "In stock (x available)"
            stock = stock.split('In stock (')
            stock = stock[1].split(' available)')
            stock=stock[0]            

            books_info[-1]=[title,price,stock,rating,book_url_absolu,image_url_absolu,UPC,category]
            
        #Fin de la page precedente, on change l'url a la page suivante (s'il n'y a pas de page suivante, les Selectors ne renverront rien mais ne seront pas utilisés)
        page_url="/page-"+str(i+2)+".html"
        url= get_category(cat_title)+page_url
        all_books= requests.get(url)
        all_books.encoding="utf-8"
        sel = Selector(text=all_books.text)

    return(books_info)


def show_book_infos(cat_title):
    """
    Affiche dans la console les informations de chaque livre d'une catégorie donnée.

    Args:
        cat_title (str): Nom de la catégorie à afficher.
    
    Outputs:
        Listes contenant les informations de chaque livre d'une categorie, sous la forme :
        [title, price, stock, rating, product_url, image_url, upc, category]
    """
    for book in get_books(cat_title):
        print(book)

def save_to_csv(cat_title,output_dir=None):
    """
    Sauvegarde les informations d'une catégorie dans un fichier CSV.

    Args:
        cat_title (str): Nom de la catégorie à sauvegarder.
        output_dir (str, optional): Nom du dossier de sortie (créé s'il n'existe pas).
    """
    data=get_books(cat_title)
    columns = ['Title', 'Price', 'Availability', 'Rating', 'Product URL', 'Image URL', 'UPC', 'Category']

    df = pd.DataFrame(columns=columns)
    for book in data:
        df= pd.concat([df,pd.DataFrame([book], columns=columns)],ignore_index=True)

    filepath=os.path.abspath(__file__) #chemin absolu du script (contient le nom du script)
    path=os.path.dirname(filepath)     #chemin absolu du directoire parent du script

    if output_dir is not None:
        path+="\\"+output_dir
        if not os.path.exists(path):
            os.mkdir(path)

    path+="\\csv\\"
    if not os.path.exists(path):
        os.mkdir(path)

    df.to_csv(path+"category_"+cat_title+".csv",index=False)


def save_to_image_dir(cat_title,output_dir=None):
    """
    Télécharge et sauvegarde les images de couverture d'une catégorie donnée.

    Args:
        cat_title (str): Nom de la catégorie.
        output_dir (str, optional): Nom du dossier de sortie (créé s'il n'existe pas).

    Notes:
        - Les images sont nommées d'après le titre du livre et son UPC sous la forme "UPC_Titre.jpg".
        - Le nom de fichier est nettoyé manuellement pour éviter les caractères interdits (sans utilisation de la classe regex).
        - Si le chemin absolu a creer pour le nouveau fichier jpg est trop long, on raccourci le titre du livre: 
        255 caracteres max --> taille(chemin absolu) + "\" + taille(UPC) + "_" + taille(titre)
        donc taille(titre) doit faire 255-taille(chemin abs)-taille(upc)-2)
    """
    filepath=os.path.abspath(__file__) #chemin absolu du script (contient le nom du script)
    path=os.path.dirname(filepath)     #chemin absolu du directoire parent du script

    if output_dir is not None:
        path+="\\"+output_dir
        if not os.path.exists(path):
            os.mkdir(path)

    path+="\\images\\"
    if not os.path.exists(path):
        os.mkdir(path)

    path+=cat_title
    if not os.path.exists(path):
        os.mkdir(path)

    data=get_books(cat_title)
    char_to_slug=[" ",".","<",">","*",":","/","\\","|",'"',"?"]

    for book in data:
        #book[0] = titre   book[6] = UPC   book[5] = image URL
        slug_title=book[0]
        for c in char_to_slug:
            slug_title=slug_title.replace(c,"-")
        #Si le chemin absolu a cree pour le nouveau fichier jpg est trop long, on raccourci le titre du livre
        #
        if len(slug_title)>255-len(path)-len(book[6])-2: #si le titre est trop long:
            #debug | print(book, slug_title)
            file_path=path+"\\"+book[6] +"_"+ slug_title[:(255-len(path)-len(book[6])-2)] +".jpg"   #raccourcissement du titre
        else:
            file_path=path+"\\"+book[6] +"_"+ slug_title +".jpg"

        jpg_path=book[5]
        img=requests.get(jpg_path)
        if img.status_code == 200:
            with open(file_path, "wb") as file:
                file.write(img.content)
        else:
            print("Failed to download image")


def main():
    """
    Point d'entrée du script.
    
    Utilisation en ligne de commande :
        python script.py -c "Travel" "Poetry" -o output_dir -i -v

    Options :
        -c / --categories : liste de catégories à scraper ou "All" pour tout.
        -o / --outdir     : nom du dossier de sortie.
        -i / --images     : si présent, télécharge les images.
        -v / --verbose    : si présent, affiche les logs d'exécution.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
                        '-c','--categories', 
                        nargs='+', 
                        required=True,
                        help='Choose one or more categories, e.g., --categories cat1 cat2. Use "All" to extract all.'
                        )
    parser.add_argument(
                        '-o','--outdir', 
                        default=None, 
                        help='Choose the name of the output directory'
                        )
    parser.add_argument(
                        '-i','--images', 
                        action='store_true', 
                        help='Save cover images (default: False)'
                        )
    parser.add_argument(
                        '-v','--verbose', 
                        action='store_true', 
                        help='Increase verbosity'
                        )
    args = parser.parse_args()
    if args.categories[0].lower()=="all":
        for category in categories[1:]: #Ne pas prendre "Books" car ca contient tous les livres sans les categories differentes
            if args.verbose:
                print(category)
            save_to_csv(category)
            save_to_image_dir(category)
    else:
        for category in args.categories:
            if args.verbose:
                print("---------------------",category,"---------------------")
                show_book_infos(category)
            save_to_csv(category.capitalize(),args.outdir)
            if args.images:
                save_to_image_dir(category,args.outdir)

if __name__ == '__main__':
    main()

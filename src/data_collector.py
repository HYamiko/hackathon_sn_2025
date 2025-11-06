import requests
from bs4 import BeautifulSoup
import json
import os


URLS_TO_SCRAPE = [
    "https://www.agriculture.bf/2025/09/24/%f0%9d%90%8c%f0%9d%90%a2%f0%9d%90%ac%f0%9d%90%9e-%f0%9d%90%9e%f0%9d%90%a7-oe%f0%9d%90%ae%f0%9d%90%af%f0%9d%90%ab%f0%9d%90%9e-%f0%9d%90%9d%f0%9d%90%ae-%f0%9d%90%a9%f0%9d%90%9a%f0%9d%90%a7%f0%9d%90%a2/",
    "https://www.agriculture.bf/2025/09/11/%f0%9d%90%8f%f0%9d%90%9a%f0%9d%90%a7%f0%9d%90%a2%f0%9d%90%9e%f0%9d%90%ab-%f0%9d%90%9d%f0%9d%90%9e-%f0%9d%90%91%f0%9d%90%9e%f0%9d%90%ac%f0%9d%90%a2%f0%9d%90%a5%f0%9d%90%a2%f0%9d%90%9e%f0%9d%90%a7/",
    "https://www.agriculture.bf/2025/09/08/%f0%9d%90%82%f0%9d%90%a8%f0%9d%90%a8%f0%9d%90%a9%f0%9d%90%9e%f0%9d%90%ab%f0%9d%90%9a%f0%9d%90%ad%f0%9d%90%a2%f0%9d%90%a8%f0%9d%90%a7-%f0%9d%90%ab%f0%9d%90%ae%f0%9d%90%ac%f0%9d%90%ac%f0%9d%90%a8/"
]
DATA_DIR = "../data"
os.makedirs(DATA_DIR, exist_ok=True)

corpus_data = []
source_list = []


def scrape_page(url):
    """Télécharge une page et extrait le texte principal de manière robuste."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # *** ÉTAPE 1 : Supprimer les éléments indésirables ***
        for element in soup.find_all(['script', 'style', 'nav', 'header', 'footer',
                                      'aside', 'iframe', 'noscript']):
            element.decompose()

        # *** ÉTAPE 2 : Chercher le contenu principal dans l'ordre de priorité ***
        main_content = None

        # Essayer les balises sémantiques HTML5
        main_content = soup.find('article') or soup.find('main')

        # Essayer les classes/IDs courants
        if not main_content:
            main_content = soup.find(['div', 'section'],
                                     class_=lambda x: x and any(term in x.lower()
                                                                for term in
                                                                ['content', 'article', 'post', 'entry', 'body']))

        # Essayer par ID
        if not main_content:
            main_content = soup.find(['div', 'section'],
                                     id=lambda x: x and any(term in x.lower()
                                                            for term in ['content', 'article', 'post', 'main']))

        # Fallback : utiliser tout le body
        if not main_content:
            main_content = soup.find('body')
            print(f"AVERTISSEMENT: Utilisation du <body> complet pour {url}")

        # *** ÉTAPE 3 : Extraire le texte ***
        if main_content:
            # Extraire paragraphes, titres, listes
            text_elements = main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])
            page_text = "\n".join([elem.get_text(strip=True) for elem in text_elements
                                   if elem.get_text(strip=True)])
        else:
            page_text = ""

        if not page_text or len(page_text) < 100:
            print(f"⚠️  ATTENTION: Contenu insuffisant pour {url} ({len(page_text)} caractères)")
            # DEBUG : Afficher la structure HTML
            print(f"   Structure disponible: {[tag.name for tag in soup.find_all(limit=20)]}")

        return page_text

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur réseau pour {url}: {e}")
        return None
    except Exception as e:
        print(f"❌ Erreur inattendue pour {url}: {e}")
        return None


# --- Exécution de la collecte ---
for url in URLS_TO_SCRAPE:
    print(f"Collecte de : {url}...")
    content = scrape_page(url)

    if content:
        # Créez le 'chunk' initial (pour l'instant, c'est la page entière)
        data_entry = {
            "id": len(corpus_data) + 1,
            "text": content,
            "source": url,
            "title": url.split('/')[-1]  # Titre basique (sera amélioré plus tard)
        }
        corpus_data.append(data_entry)
        source_list.append(url)

print(f"\nCollecte initiale terminée. {len(corpus_data)} documents bruts collectés.")

# --- Livrables Bruts (pour l'étape suivante) ---
# 1. data/corpus.json
with open(os.path.join(DATA_DIR, "corpus_brut.json"), 'w', encoding='utf-8') as f:
    json.dump(corpus_data, f, ensure_ascii=False, indent=4)

# 2. data/sources.txt
with open(os.path.join(DATA_DIR, "sources_brut.txt"), 'w', encoding='utf-8') as f:
    f.write("\n".join(source_list))

print(f"Livrables bruts sauvegardés dans le dossier '{DATA_DIR}/'.")
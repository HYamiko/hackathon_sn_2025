import requests
from bs4 import BeautifulSoup
import json
import os

# --- Configuration (À adapter) ---
# Listez quelques URLs pour commencer, en respectant robots.txt !
# *Assurez-vous que le contenu est en français et qu'il est bien burkinabè.*
URLS_TO_SCRAPE = [
    "https://www.agriculture.bf/2025/09/24/%f0%9d%90%8c%f0%9d%90%a2%f0%9d%90%ac%f0%9d%90%9e-%f0%9d%90%9e%f0%9d%90%a7-oe%f0%9d%90%ae%f0%9d%90%af%f0%9d%90%ab%f0%9d%90%9e-%f0%9d%90%9d%f0%9d%90%ae-%f0%9d%90%a9%f0%9d%90%9a%f0%9d%90%a7%f0%9d%90%a2/",
    "https://www.agriculture.bf/2025/09/11/%f0%9d%90%8f%f0%9d%90%9a%f0%9d%90%a7%f0%9d%90%a2%f0%9d%90%9e%f0%9d%90%ab-%f0%9d%90%9d%f0%9d%90%9e-%f0%9d%90%91%f0%9d%90%9e%f0%9d%90%ac%f0%9d%90%a2%f0%9d%90%a5%f0%9d%90%a2%f0%9d%90%9e%f0%9d%90%a7/",
    "https://www.agriculture.bf/2025/09/08/%f0%9d%90%82%f0%9d%90%a8%f0%9d%90%a8%f0%9d%90%a9%f0%9d%90%9e%f0%9d%90%ab%f0%9d%90%9a%f0%9d%90%ad%f0%9d%90%a2%f0%9d%90%a8%f0%9d%90%a7-%f0%9d%90%ab%f0%9d%90%ae%f0%9d%90%ac%f0%9d%90%ac%f0%9d%90%a8/"
]
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)  # Crée le dossier data/ s'il n'existe pas

corpus_data = []
source_list = []


def scrape_page(url):
    """Télécharge une page et extrait le texte principal."""
    try:
        # Respect de l'environnement : Utiliser un User-Agent
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Lève une exception pour les codes d'erreur HTTP

        soup = BeautifulSoup(response.text, 'html.parser')

        # *** Logique de Nettoyage/Extraction - C'est la partie la plus critique ! ***
        # Ciblez les balises qui contiennent le corps de l'article (ex: <article>, <main>, <div> avec une classe spécifique)

        # Exemple simple : on prend tout le texte des balises p (paragraphes)
        main_content_tags = soup.find_all('p')

        # Joindre le texte des paragraphes
        page_text = "\n".join([tag.get_text(strip=True) for tag in main_content_tags if tag.get_text(strip=True)])

        if not page_text:
            print(f"ATTENTION: Aucun contenu trouvé pour {url}. À vérifier.")

        return page_text

    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la récupération de {url}: {e}")
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
import json

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
from pathlib import Path
import time


def telecharger_pdfs(url_page, dossier_destination="pdfs_telecharges"):

    Path(dossier_destination).mkdir(parents=True, exist_ok=True)

    print(f" Analyse de la page : {url_page}\n")

    try:
        # Récupérer la page web
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url_page, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        liens_pdf = []

        for lien in soup.find_all('a', href=True):
            href = lien['href']
            if href.lower().endswith('.pdf'):
                url_complete = urljoin(url_page, href)
                liens_pdf.append(url_complete)


        for tag in soup.find_all(['embed', 'object'], src=True):
            src = tag.get('src') or tag.get('data')
            if src and src.lower().endswith('.pdf'):
                url_complete = urljoin(url_page, src)
                liens_pdf.append(url_complete)


        for iframe in soup.find_all('iframe', src=True):
            src = iframe['src']
            if '.pdf' in src.lower():
                url_complete = urljoin(url_page, src)
                liens_pdf.append(url_complete)


        liens_pdf = list(set(liens_pdf))

        if not liens_pdf:
            print(" Aucun PDF trouvé sur cette page.")
            return

        print(f" {len(liens_pdf)} PDF(s) trouvé(s)\n")


        sources_mapping = {}
        for i, url_pdf in enumerate(liens_pdf, 1):
            try:
                print(f" [{i}/{len(liens_pdf)}] Téléchargement : {url_pdf}")


                response_pdf = requests.get(url_pdf, headers=headers, timeout=30, stream=True)
                response_pdf.raise_for_status()


                content_type = response_pdf.headers.get('Content-Type', '')
                if 'pdf' not in content_type.lower():
                    print(f"    Avertissement : Le fichier n'est peut-être pas un PDF (type: {content_type})")


                nom_fichier = extraire_nom_fichier(url_pdf, i)
                chemin_complet = os.path.join(dossier_destination, nom_fichier)
                sources_mapping[nom_fichier] = url_pdf

                with open(chemin_complet, 'wb') as f:
                    for chunk in response_pdf.iter_content(chunk_size=8192):
                        f.write(chunk)

                taille = os.path.getsize(chemin_complet) / (1024 * 1024)  # En Mo
                print(f"   Sauvegardé : {nom_fichier} ({taille:.2f} Mo)\n")


                time.sleep(1)

            except requests.exceptions.RequestException as e:
                print(f"    Erreur lors du téléchargement : {e}\n")
                continue
            except Exception as e:
                print(f"    Erreur inattendue : {e}\n")
                continue

        with open('sources_mapping.json', 'w', encoding='utf-8') as f:
            json.dump(sources_mapping, f, ensure_ascii=False, indent=4)

        print(" Mapping des sources sauvegardé")

        print(f" Téléchargement terminé ! Fichiers dans : {dossier_destination}/")

    except requests.exceptions.RequestException as e:
        print(f" Erreur lors de l'accès à la page : {e}")
    except Exception as e:
        print(f" Erreur inattendue : {e}")


def extraire_nom_fichier(url, numero):

    parsed = urlparse(url)
    nom = os.path.basename(parsed.path)


    if not nom or not nom.endswith('.pdf'):
        nom = f"document_{numero}.pdf"

    nom = nom.replace('%20', '_').replace(' ', '_')

    return nom




if __name__ == "__main__":

    url = "https://www.agriculture.bf/document-library/"
    telecharger_pdfs(url)


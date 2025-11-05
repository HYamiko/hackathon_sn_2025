import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
from pathlib import Path
import time


def telecharger_pdfs(url_page, dossier_destination="pdfs_telecharges"):
    """
    Télécharge tous les PDFs trouvés sur une page web.

    Args:
        url_page: L'URL de la page à scanner
        dossier_destination: Le dossier où sauvegarder les PDFs
    """

    # Créer le dossier de destination s'il n'existe pas
    Path(dossier_destination).mkdir(parents=True, exist_ok=True)

    print(f"🔍 Analyse de la page : {url_page}\n")

    try:
        # Récupérer la page web
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url_page, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Trouver tous les liens PDF
        liens_pdf = []

        # Méthode 1 : Liens <a> pointant vers des .pdf
        for lien in soup.find_all('a', href=True):
            href = lien['href']
            if href.lower().endswith('.pdf'):
                url_complete = urljoin(url_page, href)
                liens_pdf.append(url_complete)

        # Méthode 2 : Balises <embed> ou <object> avec des PDFs
        for tag in soup.find_all(['embed', 'object'], src=True):
            src = tag.get('src') or tag.get('data')
            if src and src.lower().endswith('.pdf'):
                url_complete = urljoin(url_page, src)
                liens_pdf.append(url_complete)

        # Méthode 3 : iframes contenant des PDFs
        for iframe in soup.find_all('iframe', src=True):
            src = iframe['src']
            if '.pdf' in src.lower():
                url_complete = urljoin(url_page, src)
                liens_pdf.append(url_complete)

        # Supprimer les doublons
        liens_pdf = list(set(liens_pdf))

        if not liens_pdf:
            print("❌ Aucun PDF trouvé sur cette page.")
            return

        print(f"✅ {len(liens_pdf)} PDF(s) trouvé(s)\n")

        # Télécharger chaque PDF
        for i, url_pdf in enumerate(liens_pdf, 1):
            try:
                print(f"📥 [{i}/{len(liens_pdf)}] Téléchargement : {url_pdf}")

                # Récupérer le PDF
                response_pdf = requests.get(url_pdf, headers=headers, timeout=30, stream=True)
                response_pdf.raise_for_status()

                # Vérifier que c'est bien un PDF
                content_type = response_pdf.headers.get('Content-Type', '')
                if 'pdf' not in content_type.lower():
                    print(f"   ⚠️  Avertissement : Le fichier n'est peut-être pas un PDF (type: {content_type})")

                # Générer un nom de fichier
                nom_fichier = extraire_nom_fichier(url_pdf, i)
                chemin_complet = os.path.join(dossier_destination, nom_fichier)

                # Sauvegarder le fichier
                with open(chemin_complet, 'wb') as f:
                    for chunk in response_pdf.iter_content(chunk_size=8192):
                        f.write(chunk)

                taille = os.path.getsize(chemin_complet) / (1024 * 1024)  # En Mo
                print(f"   ✓ Sauvegardé : {nom_fichier} ({taille:.2f} Mo)\n")

                # Pause pour éviter de surcharger le serveur
                time.sleep(1)

            except requests.exceptions.RequestException as e:
                print(f"   ❌ Erreur lors du téléchargement : {e}\n")
                continue
            except Exception as e:
                print(f"   ❌ Erreur inattendue : {e}\n")
                continue

        print(f"🎉 Téléchargement terminé ! Fichiers dans : {dossier_destination}/")

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de l'accès à la page : {e}")
    except Exception as e:
        print(f"❌ Erreur inattendue : {e}")


def extraire_nom_fichier(url, numero):
    """Extrait un nom de fichier propre depuis l'URL."""
    # Essayer d'obtenir le nom depuis l'URL
    parsed = urlparse(url)
    nom = os.path.basename(parsed.path)

    # Si pas de nom ou nom invalide, générer un nom
    if not nom or not nom.endswith('.pdf'):
        nom = f"document_{numero}.pdf"

    # Nettoyer le nom (enlever les caractères spéciaux)
    nom = nom.replace('%20', '_').replace(' ', '_')

    return nom


def telecharger_pdfs_recursif(url_page, dossier_destination="pdfs_telecharges", profondeur_max=1):
    """
    Version avancée : explore aussi les liens de la page pour trouver plus de PDFs.

    Args:
        url_page: L'URL de départ
        dossier_destination: Dossier de sauvegarde
        profondeur_max: Nombre de niveaux de liens à explorer (0 = page actuelle uniquement)
    """

    urls_visitees = set()
    pdfs_trouves = set()

    def explorer(url, profondeur):
        if profondeur > profondeur_max or url in urls_visitees:
            return

        urls_visitees.add(url)
        print(f"🔍 Exploration (niveau {profondeur}): {url}")

        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Chercher les PDFs
            for lien in soup.find_all('a', href=True):
                href = lien['href']
                url_complete = urljoin(url, href)

                if url_complete.lower().endswith('.pdf'):
                    pdfs_trouves.add(url_complete)
                elif profondeur < profondeur_max and urlparse(url_complete).netloc == urlparse(url_page).netloc:
                    # Explorer les liens du même domaine
                    explorer(url_complete, profondeur + 1)

            time.sleep(0.5)

        except Exception as e:
            print(f"   Erreur : {e}")

    # Commencer l'exploration
    explorer(url_page, 0)

    print(f"\n✅ {len(pdfs_trouves)} PDF(s) unique(s) trouvé(s)\n")

    # Télécharger tous les PDFs trouvés
    # [Code de téléchargement similaire à telecharger_pdfs]


# ===== UTILISATION =====
if __name__ == "__main__":
    # Exemple simple
    url = "https://www.agriculture.bf/document-library/"
    telecharger_pdfs(url)

    # Exemple avec dossier personnalisé
    # telecharger_pdfs(url, dossier_destination="mes_documents_pdf")

    # Exemple avec exploration récursive (ATTENTION : peut télécharger beaucoup de fichiers)
    # telecharger_pdfs_recursif(url, profondeur_max=2)
import os
import json
from pathlib import Path
import PyPDF2
import pdfplumber

PDF_DIR = "./pdfs_telecharges"  # Dossier contenant les PDFs
DATA_DIR = "../data"
SOURCES_MAPPING_FILE = "../data/sources_mapping.json"

os.makedirs(DATA_DIR, exist_ok=True)

# Structures de données (IDENTIQUES au script web)
corpus_data = []
source_list = []

sources_mapping = {}
if os.path.exists(SOURCES_MAPPING_FILE):
    with open(SOURCES_MAPPING_FILE, 'r', encoding='utf-8') as f:
        sources_mapping = json.load(f)
    print(f" Mapping de sources chargé : {len(sources_mapping)} entrées\n")
else:
    print(f"  Aucun fichier de mapping trouvé ({SOURCES_MAPPING_FILE})")
    print(f"   Les chemins locaux seront utilisés comme sources.\n")

def extract_text_pypdf2(pdf_path):
    """Extraction avec PyPDF2 (rapide mais parfois moins précis)."""
    try:
        text = ""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception as e:
        print(f"   ❌ Erreur PyPDF2: {e}")
        return None


def extract_text_pdfplumber(pdf_path):
    """Extraction avec pdfplumber (plus lent mais plus précis)."""
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception as e:
        print(f"   ❌ Erreur pdfplumber: {e}")
        return None


def extract_pdf_title(pdf_path):
    """Extrait le titre du PDF depuis les métadonnées."""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            metadata = reader.metadata
            if metadata and metadata.get('/Title'):
                return metadata.get('/Title')
    except:
        pass

    # Fallback : utiliser le nom du fichier sans extension
    return os.path.splitext(os.path.basename(pdf_path))[0]


def clean_text(text):
    """Nettoie le texte extrait du PDF."""
    if not text:
        return ""

    # Supprimer les lignes vides multiples
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    text = '\n'.join(lines)

    # Supprimer les caractères de contrôle indésirables
    text = ''.join(char for char in text if char.isprintable() or char in '\n\t')

    # Supprimer les espaces multiples
    text = ' '.join(text.split())

    return text


def process_pdf(pdf_path):
    """
    Traite un fichier PDF et extrait son contenu.


    """
    pdf_name = os.path.basename(pdf_path)
    print(f" Traitement de : {pdf_name}")

    # Essayer d'abord avec pdfplumber (plus fiable)
    content = extract_text_pdfplumber(pdf_path)

    # Si échec, essayer PyPDF2
    if not content or len(content) < 100:
        print(f"   pdfplumber insuffisant, essai avec PyPDF2...")
        content = extract_text_pypdf2(pdf_path)

    # Nettoyer le texte
    if content:
        content = clean_text(content)

    # Vérification de la qualité de l'extraction
    if not content or len(content) < 100:
        print(f"    ATTENTION: Contenu insuffisant ({len(content) if content else 0} caractères)")
        print(f"   Le PDF est peut-être scanné (image) ou protégé.")
        return None

    print(f"   Extrait : {len(content)} caractères")

    return content


# --- Exécution de la collecte (IDENTIQUE au script web) ---
print("=" * 60)
print("EXTRACTION DE TEXTE DEPUIS PDFs")
print("=" * 60 + "\n")

# Trouver tous les fichiers PDF
pdf_files = list(Path(PDF_DIR).glob('**/*.pdf'))

if not pdf_files:
    print(f" Aucun fichier PDF trouvé dans {PDF_DIR}")
else:
    print(f" {len(pdf_files)} fichier(s) PDF trouvé(s)\n")

    # Traiter chaque PDF (BOUCLE IDENTIQUE au script web)
    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"[{i}/{len(pdf_files)}] Collecte de : {pdf_path}...")
        content = process_pdf(str(pdf_path))

        if content:
            # Récupérer la source réelle (URL) depuis le mapping
            pdf_filename = os.path.basename(str(pdf_path))
            real_source = sources_mapping.get(pdf_filename, str(pdf_path))

            data_entry = {
                "id": len(corpus_data) + 1,
                "text": content,
                "source": real_source,  # URL réelle si disponible
                "title": extract_pdf_title(str(pdf_path))
            }
            corpus_data.append(data_entry)
            source_list.append(real_source)

print(f"\nCollecte initiale terminée. {len(corpus_data)} documents bruts collectés.")

# --- Livrables Bruts (IDENTIQUES au script web) ---
# 1. data/corpus_brut.json
with open(os.path.join(DATA_DIR, "corpus_brut.json"), 'w', encoding='utf-8') as f:
    json.dump(corpus_data, f, ensure_ascii=False, indent=4)

# 2. data/sources_brut.txt
with open(os.path.join(DATA_DIR, "sources_brut.txt"), 'w', encoding='utf-8') as f:
    f.write("\n".join(source_list))

print(f"Livrables bruts sauvegardés dans le dossier '{DATA_DIR}/'.")


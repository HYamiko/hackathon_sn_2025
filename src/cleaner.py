import json
import os

DATA_DIR = "../data"
INPUT_FILE = os.path.join(DATA_DIR, "corpus_brut.json")
OUTPUT_FILE = os.path.join(DATA_DIR, "corpus.json")  # Le livrable final attendu

# Taille de chunk recommandée pour le RAG (à ajuster)
# Pour une implémentation rapide, 500 caractères est un bon point de départ.
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50  # Pour éviter de couper une idée au milieu


def chunk_text(text, chunk_size, chunk_overlap):
    """Divise le texte en morceaux (chunks) avec un chevauchement."""
    chunks = []
    # Une méthode simple basée sur les caractères
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        # Déplace le point de départ en utilisant le chevauchement
        start += chunk_size - chunk_overlap
    return chunks


# --- Exécution de la normalisation et segmentation ---
try:
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data_brute = json.load(f)
except FileNotFoundError:
    print(f"Erreur: Le fichier d'entrée {INPUT_FILE} est introuvable. Exécutez d'abord le scraper.")
    exit()

final_corpus = []
chunk_id_counter = 1

for entry in data_brute:
    doc_text = entry.get("text", "")
    source = entry.get("source", "Inconnu")

    # 1. Nettoyage de base (simplifié pour le hackathon)
    # Remplacer les multiples espaces ou sauts de ligne par un seul espace
    cleaned_text = ' '.join(doc_text.split())

    # 2. Segmentation (Chunking)
    chunks = chunk_text(cleaned_text, CHUNK_SIZE, CHUNK_OVERLAP)

    for chunk in chunks:
        final_corpus.append({
            "id": chunk_id_counter,
            "text": chunk,
            "source": source,
            "original_doc_id": entry.get("id")
        })
        chunk_id_counter += 1

print(f"Segmentation terminée. {len(final_corpus)} fragments (chunks) générés pour l'indexation.")

# --- Livrable Final de l'Étape 2 ---
# data/corpus.json
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(final_corpus, f, ensure_ascii=False, indent=4)

print(f"Le fichier de corpus final {OUTPUT_FILE} est prêt pour l'indexation (Étape 3).")
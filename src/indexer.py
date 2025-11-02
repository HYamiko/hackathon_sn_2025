import json
import os
import chromadb
from llama_index.core import Document, VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings

# --- Configuration des chemins et modèles ---
DATA_DIR = "data"
CORPUS_FILE = os.path.join(DATA_DIR, "corpus.json")
CHROMA_DB_PATH = "./chroma_db"
CHROMA_COLLECTION_NAME = "burkina_knowledge_base"
EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

# 1. Préparation des Documents LlamaIndex
print("Chargement des documents du corpus...")
try:
    with open(CORPUS_FILE, 'r', encoding='utf-8') as f:
        corpus_data = json.load(f)
except FileNotFoundError:
    print(f"ERREUR: Le fichier {CORPUS_FILE} est manquant.")
    exit()

documents = []
for entry in corpus_data:
    doc = Document(
        text=entry["text"],
        metadata={"source": entry["source"], "id": entry["id"], "original_doc_id": entry["original_doc_id"]},
        doc_id=f"chunk_{entry['id']}"
    )
    documents.append(doc)

print(f"Nombre de documents chargés : {len(documents)}")

# 2. Configuration de l'Embeddings
try:
    embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL)
    Settings.embed_model = embed_model
    print("Modèle d'embeddings chargé avec succès.")
except Exception as e:
    print(f"ERREUR LORS DU CHARGEMENT DU MODÈLE D'EMBEDDINGS : {e}")
    exit()

# 3. Initialisation de la Base de Données Vectorielle (ChromaDB)
print(f"Initialisation de ChromaDB dans '{CHROMA_DB_PATH}'...")
try:
    db = chromadb.PersistentClient(path=CHROMA_DB_PATH)

    # Supprimer l'ancienne collection si elle existe
    try:
        db.delete_collection(CHROMA_COLLECTION_NAME)
        print(f"Ancienne collection '{CHROMA_COLLECTION_NAME}' supprimée.")
    except:
        pass

    # Créer une nouvelle collection
    chroma_collection = db.create_collection(CHROMA_COLLECTION_NAME)
    print(f"Collection '{CHROMA_COLLECTION_NAME}' créée.")

    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    # ✅ CORRECTION CRITIQUE : Créer un StorageContext
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

except Exception as e:
    print(f"ERREUR LORS DE L'INITIALISATION DE CHROMADB : {e}")
    exit()

# 4. Indexation (Création des vecteurs et stockage)
print(f"Démarrage de l'indexation de {len(documents)} fragments...")
try:
    # ✅ CORRECTION : Passer le storage_context pour forcer le stockage
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,  # ← AJOUT CRUCIAL
        embed_model=embed_model,
        show_progress=True
    )
    print("Indexation terminée. Vérification de la sauvegarde...")

except Exception as e:
    print(f"ERREUR LORS DE L'INDEXATION : {e}")
    import traceback

    traceback.print_exc()
    exit()

# 5. VÉRIFICATION POST-INDEXATION
print("-" * 50)
try:
    # Vérification immédiate
    count_immediate = chroma_collection.count()
    print(f"Comptage immédiat : {count_immediate} fragments")

    # Vérification après reconnexion
    db_recheck = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection_recheck = db_recheck.get_collection(CHROMA_COLLECTION_NAME)
    count_persisted = collection_recheck.count()
    print(f"Comptage après reconnexion : {count_persisted} fragments")

    if count_persisted == len(documents):
        print(
            f"\n✅ SUCCÈS FINAL : Base de connaissances prête avec {count_persisted} fragments dans '{CHROMA_DB_PATH}'.")
        print(f"   Collection : '{CHROMA_COLLECTION_NAME}'")
        print("   Vous pouvez maintenant exécuter le script de requête RAG.")

        # Afficher quelques exemples pour confirmer
        sample = collection_recheck.get(limit=3)
        if sample['ids']:
            print(f"\n   Exemples d'IDs stockés : {sample['ids'][:3]}")
    else:
        print(f"\n❌ ÉCHEC CRITIQUE : Seuls {count_persisted} fragments ont été trouvés au lieu de {len(documents)}.")
        print("   Vérifiez les logs d'erreurs et les permissions du dossier.")

except Exception as e:
    print(f"❌ ERREUR LORS DE LA VÉRIFICATION : {e}")
    import traceback

    traceback.print_exc()

print("-" * 50)
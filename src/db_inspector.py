import chromadb
import os

# --- Configuration RAG ---
CHROMA_DB_PATH = "./chroma_db"
CHROMA_COLLECTION_NAME = "burkina_knowledge_base"


def inspect_chroma_db_client():
    """Utilise le client ChromaDB pour vérifier le nombre de documents et leur contenu."""
    print("Tentative de connexion à la base de données vectorielle ChromaDB...")

    try:
        # 1. Connexion au client ChromaDB
        db = chromadb.PersistentClient(path=CHROMA_DB_PATH)

        # 2. Récupération de la collection (l'Index)
        collection = db.get_collection(CHROMA_COLLECTION_NAME)

        # 3. Comptage des documents
        count = collection.count()
        print("-" * 50)
        print(f"SUCCÈS : Collection '{CHROMA_COLLECTION_NAME}' trouvée.")
        print(f"Nombre total de fragments indexés : {count}")
        print("-" * 50)

        if count == 0:
            print("AVERTISSEMENT : La collection est vide. Ré-exécutez indexer.py.")
            return

        # 4. Récupération d'un échantillon pour vérification du contenu
        print("Récupération de 3 fragments pour aperçu (pour prouver l'indexation)...")

        # On récupère tous les IDs de la collection
        all_ids = collection.get(limit=count, include=[])['ids']

        # On récupère les 3 premiers documents complets (texte et metadata)
        sample_ids = all_ids[:3]

        sample_results = collection.get(
            ids=sample_ids,
            include=['documents', 'metadatas']  # Demande le texte et les métadonnées
        )

        for i in range(len(sample_results['documents'])):
            doc = sample_results['documents'][i]
            meta = sample_results['metadatas'][i]

            print(f"\n[FRAGMENT {i + 1}] Source: {meta.get('source', 'N/A')}")
            print(f"    Extrait : {doc[:150].replace('', ' ')}...")

        print("\n=> L'indexation est CONFIRMÉE. Le problème est dans le Retrieval (Recherche).")

    except Exception as e:
        print(f"ERREUR lors de la connexion ou de la récupération des données Chroma : {e}")
        print("Vérifiez le chemin de la base et le nom de la collection.")


if __name__ == "__main__":
    inspect_chroma_db_client()
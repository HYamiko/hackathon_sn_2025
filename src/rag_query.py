import time
from llama_index.core import VectorStoreIndex, Settings, PromptTemplate
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
# Assurez-vous d'avoir installé les intégrations :
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# --- Configuration RAG ---
CHROMA_COLLECTION_NAME = "burkina_knowledge_base"
EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
LLM_MODEL = "mistral"
REQUEST_TIMEOUT = 360.0  # Augmenté pour la sécurité


QA_PROMPT_TEMPLATE = """Tu es un assistant expert sur le Burkina Faso. Réponds TOUJOURS en français.

Contexte fourni :
{context_str}

Question : {query_str}

Instructions :
- Réponds UNIQUEMENT en français
- Base ta réponse UNIQUEMENT sur le contexte fourni ci-dessus
- Si l'information n'est pas dans le contexte, dis "Je ne trouve pas cette information dans les documents fournis"
- Cite les sources quand c'est pertinent
- Sois précis et concis

Réponse en français :"""


# 1. Connexion au LLM et aux Embeddings
try:
    # La ligne de configuration du LLM (Mistral via Ollama)
    Settings.llm = Ollama(model=LLM_MODEL, request_timeout=REQUEST_TIMEOUT)
    # La ligne de configuration des Embeddings (pour la recherche de similarité)
    Settings.embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL)
except Exception as e:
    print(f"ERREUR FATALE DE CONFIGURATION : {e}")
    print(
        "Vérifiez 1) Qu'Ollama tourne (ollama run mistral) et 2) Que les paquets d'intégration sont installés (pip install llama-index-llms-ollama).")
    exit()

# 2. Récupération de l'Index (Lecture de la base de données)
print("Connexion à l'Index (Base de Données Vectorielle)...")
db = chromadb.PersistentClient(path="./chroma_db")
try:
    chroma_collection = db.get_collection(CHROMA_COLLECTION_NAME)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
except Exception:
    print("ERREUR : Impossible de charger la base. Avez-vous exécuté indexer.py ?")
    exit()

# 3. Création du Retriever (Moteur de Recherche)
# On force le système à récupérer 8 fragments au lieu des 3 par défaut,
# pour augmenter la chance de trouver un fragment pertinent dans un petit corpus.
# Si vous avez un gros corpus (500+ docs), revenez à 3 ou 5.
retriever = index.as_retriever(similarity_top_k=8)

# 4. La Requête (Séparée en deux phases)

question = input("Posez votre question sur le sujet burkinabè : ")
print("\n[PHASE 1 : Récupération des documents] en cours...")

# Exécute la phase de RECHERCHE (Retrieval)
retrieved_nodes = retriever.retrieve(question)

# --- Diagnostic des sources récupérées ---
print(f"--- Diagnostic : {len(retrieved_nodes)} Sources Récupérées ---")
if not retrieved_nodes:
    print("ÉCHEC RÉCUPÉRATION : Aucune source trouvée. Essayez une question plus directe liée aux mots-clés du corpus.")

    # On arrête ici si rien n'est trouvé, car la génération échouera de toute façon
    print("\n--- Réponse de l'Assistant ---\nEmpty Response")
    exit()

# Affichage des fragments pour prouver que la phase de recherche fonctionne
for i, node in enumerate(retrieved_nodes):
    print(f" - Source {i + 1} : {node.metadata.get('source', 'Inconnue')} (Score: {node.score:.4f})")
    print(f"   Extrait : {node.text[:100]}...\n")



qa_prompt = PromptTemplate(QA_PROMPT_TEMPLATE)

# 5. Création du Moteur de Requête (Generation)
# Utilise les fragments récupérés pour générer la réponse
query_engine = index.as_query_engine(
    text_qa_template=qa_prompt,
    similarity_top_k=3
)

print("[PHASE 2 : Génération de la réponse] en cours par Mistral...")

start_time = time.time()

# Exécution de la phase de GÉNÉRATION (Generation)
# LlamaIndex prend les 'retrieved_nodes' et les passe au LLM dans un prompt
response = query_engine.query(question)

end_time = time.time()

# 6. Affichage du Résultat Final
print("\n" + "=" * 50)
print(f"TEMPS DE RÉPONSE TOTAL : {end_time - start_time:.2f} secondes")
print("=" * 50)

print("\n--- Réponse de l'Assistant ---")
if response.response:
    print(response.response)
else:
    print("ERREUR GÉNÉRATION : La réponse est vide. Problème de timeout ou le LLM n'a pas pu synthétiser le contexte.")

# Note: Les sources ont déjà été affichées dans la phase 4 pour le diagnostic.
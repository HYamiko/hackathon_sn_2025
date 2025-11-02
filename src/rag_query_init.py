import time
from llama_index.core import VectorStoreIndex, Settings, PromptTemplate
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# --- Configuration RAG ---
CHROMA_COLLECTION_NAME = "burkina_knowledge_base"
EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
LLM_MODEL = "mistral:7b-instruct-v0.2-q4_K_M"
REQUEST_TIMEOUT = 360.0

# ✅ PROMPT PERSONNALISÉ EN FRANÇAIS
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
print(f"Chargement du modèle : {LLM_MODEL}")
try:
    llm = Ollama(
        model=LLM_MODEL,
        base_url="http://localhost:11434",
        request_timeout=REQUEST_TIMEOUT
    )

    # Test rapide
    test = llm.complete("Réponds en français : Bonjour")
    print(f"✅ LLM actif (test: {test.text[:50]}...)")

    Settings.llm = llm
    Settings.embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL)

except Exception as e:
    print(f"❌ ERREUR : {e}")
    exit()

# 2. Récupération de l'Index
print("\nConnexion à l'Index...")
db = chromadb.PersistentClient(path="./chroma_db")
try:
    chroma_collection = db.get_collection(CHROMA_COLLECTION_NAME)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
    print("✅ Index chargé")
except Exception as e:
    print(f"❌ ERREUR : {e}")
    exit()

# 3. Création du Retriever
retriever = index.as_retriever(similarity_top_k=8)

# 4. La Requête
print("\n" + "=" * 50)
question = input("Posez votre question : ")
print("=" * 50)

print("\n[PHASE 1 : Récupération] en cours...")
retrieved_nodes = retriever.retrieve(question)

print(f"\n📚 {len(retrieved_nodes)} fragments récupérés :")
if not retrieved_nodes:
    print("❌ Aucune source trouvée")
    exit()

for i, node in enumerate(retrieved_nodes):
    print(f"\n  📄 Source {i + 1} : {node.metadata.get('source', 'Inconnue')}")
    print(f"     Score : {node.score:.4f}")
    print(f"     Extrait : {node.text[:200]}...")

# ✅ 5. Création du Query Engine AVEC PROMPT PERSONNALISÉ
qa_prompt = PromptTemplate(QA_PROMPT_TEMPLATE)

query_engine = index.as_query_engine(
    text_qa_template=qa_prompt,
    similarity_top_k=8
)

print(f"\n[PHASE 2 : Génération avec {LLM_MODEL}]...")
print("⏳ Patientez 30-60 secondes...")

start_time = time.time()

try:
    response = query_engine.query(question)
except Exception as e:
    print(f"\n❌ ERREUR : {e}")
    exit()

end_time = time.time()

# 6. Affichage
print("\n" + "=" * 50)
print(f"⏱️  Temps : {end_time - start_time:.2f}s")
print("=" * 50)

print("\n🤖 Réponse :")
print("-" * 50)
if response.response:
    print(response.response)
else:
    print("❌ Réponse vide")
print("-" * 50)

# ✅ BONUS : Afficher les métadonnées des sources utilisées
if hasattr(response, 'source_nodes') and response.source_nodes:
    print("\n📚 Sources utilisées pour cette réponse :")
    for i, node in enumerate(response.source_nodes[:3]):  # Top 3
        print(f"  {i + 1}. {node.metadata.get('source', 'Inconnue')} (score: {node.score:.3f})")
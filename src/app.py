import streamlit as st
import time
import chromadb
# Importation des librairies de la chaîne RAG
from llama_index.core import VectorStoreIndex, Settings, PromptTemplate
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.core.callbacks import CallbackManager, LlamaDebugHandler

# --- I. Configuration Globale ---
CHROMA_COLLECTION_NAME = "burkina_knowledge_base"
EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
LLM_MODEL = "mistral:7b-instruct-v0.2-q4_K_M"  # Modèle choisi par l'utilisateur
REQUEST_TIMEOUT = 360.0
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"  # Modèle de re-classement

# Votre template de prompt pour forcer le français
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
qa_prompt = PromptTemplate(QA_PROMPT_TEMPLATE)


# --- II. Initialisation du Pipeline RAG (Mise en cache pour la vitesse) ---

@st.cache_resource
def setup_rag_pipeline():
    """Initialise le pipeline RAG complet et les composants en cache."""

    # 1. LLM et Embeddings
    Settings.llm = Ollama(model=LLM_MODEL, request_timeout=REQUEST_TIMEOUT)
    Settings.embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL)

    # Configuration du Callback (pour le diagnostic, non affiché directement)
    Settings.callback_manager = CallbackManager([LlamaDebugHandler(print_trace_on_end=False)])

    # 2. Récupération de l'Index ChromaDB
    try:
        db = chromadb.PersistentClient(path="./chroma_db")
        chroma_collection = db.get_collection(CHROMA_COLLECTION_NAME)

        if chroma_collection.count() == 0:
            st.error("ERREUR CRITIQUE : La base de données ChromaDB est vide. Lancez 'indexer.py' d'abord.")
            return None

        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

    except Exception as e:
        st.error(f"Impossible de charger l'Index ChromaDB. Erreur: {e}")
        return None

    # 3. Pipeline de Récupération Avancé

    # A. Multi-Query Retriever
    base_retriever = index.as_retriever(similarity_top_k=8)
    multi_query_retriever = QueryFusionRetriever(
        retrievers=[base_retriever],
        num_queries=3,
        similarity_top_k=8,
        mode="reciprocal_rerank"
    )

    # B. Re-ranker
    rerank_processor = SentenceTransformerRerank(
        model=RERANK_MODEL,
        top_n=3
    )

    # 4. Le Moteur de Requête final
    query_engine = RetrieverQueryEngine(
        retriever=multi_query_retriever,
        node_postprocessors=[rerank_processor],
        response_synthesizer=index.as_query_engine(
            text_qa_template=qa_prompt,
            similarity_top_k=3  # Ne change rien ici, le re-ranker prévaut
        )._response_synthesizer
    )

    return query_engine


# --- III. Interface Streamlit ---

st.set_page_config(
    page_title="Assistant IA Contextuel Burkina (Hackathon 2025)",
    layout="wide"
)

st.title("🇧🇫 Assistant IA Contextuel 100% Open Source")
st.markdown("---")
st.caption(f"**Modèle LLM:** {LLM_MODEL} | **Base de Données:** ChromaDB | **Stratégie:** Multi-Query + Re-ranker")

# Initialisation du pipeline
query_engine = setup_rag_pipeline()

if query_engine:
    # Conteneur pour l'historique de chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Affichage de l'historique
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Champ de saisie pour la question
    if prompt := st.chat_input("Posez votre question sur le sujet burkinabè..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("Recherche des sources et génération de la réponse en cours...")

            try:
                # Exécution de la requête
                response = query_engine.query(prompt)

                # Affichage de la réponse finale
                placeholder.markdown(response.response)
                st.session_state.messages.append({"role": "assistant", "content": response.response})

                # Affichage des sources utilisées (pour le jury)
                with st.expander("🔍 Sources Retrouvées et Re-classées (Diagnostic)"):
                    if response.source_nodes:
                        for i, node in enumerate(response.source_nodes):
                            st.markdown(f"**Re-classement # {i + 1}** | **Score Rerank:** `{node.score:.4f}`")
                            st.markdown(f"**Source:** `{node.metadata.get('source', 'Inconnue')}`")
                            st.caption(node.text)
                            st.markdown("---")
                    else:
                        st.write("Le Re-ranker n'a conservé aucun fragment jugé pertinent pour la synthèse finale.")

            except Exception as e:
                error_message = f"Désolé, une erreur s'est produite (Erreur LLM/Ollama/Timeout). Détails: {e}"
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})

# Affichage d'un avertissement si le pipeline n'est pas initialisé
if not query_engine:
    st.warning(
        "Veuillez résoudre les erreurs listées ci-dessus (Base de données vide/non accessible) pour démarrer l'assistant.")
import streamlit as st
import chromadb
from llama_index.core import VectorStoreIndex, Settings, PromptTemplate
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# --- Configuration Optimisée ---
CHROMA_COLLECTION_NAME = "burkina_knowledge_base"
EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
LLM_MODEL = "mistral"
REQUEST_TIMEOUT = 180.0  # Réduit de 360 à 180

# Prompt simplifié (plus court = plus rapide)
QA_PROMPT_TEMPLATE = """Contexte : {context_str}

Question : {query_str}

Réponds en français, de manière concise, basé uniquement sur le contexte ci-dessus :"""

qa_prompt = PromptTemplate(QA_PROMPT_TEMPLATE)


# --- Pipeline RAG Optimisé ---
@st.cache_resource
def setup_rag_pipeline():
    """Pipeline RAG simplifié et rapide."""

    # 1. Configuration des modèles
    Settings.llm = Ollama(model=LLM_MODEL, request_timeout=REQUEST_TIMEOUT)
    Settings.embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL)

    # 2. Chargement de l'index
    try:
        db = chromadb.PersistentClient(path="./chroma_db")
        chroma_collection = db.get_collection(CHROMA_COLLECTION_NAME)

        if chroma_collection.count() == 0:
            st.error("❌ Base de données vide. Lancez 'indexer.py' d'abord.")
            return None

        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

        st.success(f"✅ {chroma_collection.count()} documents chargés")

    except Exception as e:
        st.error(f"❌ Erreur de chargement : {e}")
        return None

    # 3. Query Engine SIMPLE (sans multi-query ni re-ranker)
    query_engine = index.as_query_engine(
        text_qa_template=qa_prompt,
        similarity_top_k=3,  # Seulement 3 fragments au lieu de 8
        streaming=True  # Active le streaming pour voir la réponse en temps réel
    )

    return query_engine, index


# --- Interface Streamlit ---
st.set_page_config(
    page_title="Assistant IA Burkina (Optimisé)",
    layout="wide"
)

st.title("🇧🇫 Assistant IA Contextuel - Version Rapide")
st.markdown("---")

# Indicateur de performance
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Modèle", LLM_MODEL)
with col2:
    st.metric("Fragments", "3 (optimisé)")
with col3:
    st.metric("Streaming", "✅ Activé")

# Initialisation
result = setup_rag_pipeline()

if result:
    query_engine, index = result

    # Historique de chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Affichage de l'historique
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Champ de saisie
    if prompt := st.chat_input("Posez votre question..."):
        # Ajout de la question
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # Conteneur pour la réponse en streaming
            response_placeholder = st.empty()
            sources_placeholder = st.empty()

            try:
                # Phase 1 : Retrieval (rapide)
                with st.spinner("🔍 Recherche des sources..."):
                    retriever = index.as_retriever(similarity_top_k=3)
                    retrieved_nodes = retriever.retrieve(prompt)

                # Affichage des sources trouvées
                with sources_placeholder.expander("📚 Sources utilisées", expanded=False):
                    for i, node in enumerate(retrieved_nodes):
                        st.markdown(f"**{i + 1}.** {node.metadata.get('source', 'Inconnue')} (score: {node.score:.3f})")
                        st.caption(node.text[:200] + "...")
                        st.markdown("---")

                # Phase 2 : Génération avec streaming
                st.caption("⏳ Génération en cours...")

                streaming_response = query_engine.query(prompt)

                # Affichage mot par mot
                full_response = ""
                for text in streaming_response.response_gen:
                    full_response += text
                    response_placeholder.markdown(full_response + "▌")

                # Réponse finale sans curseur
                response_placeholder.markdown(full_response)

                # Sauvegarde dans l'historique
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response
                })

            except Exception as e:
                error_msg = f"❌ Erreur : {str(e)}"
                response_placeholder.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })

else:
    st.warning("⚠️ Veuillez résoudre les erreurs ci-dessus pour démarrer.")

# Sidebar avec statistiques
with st.sidebar:
    st.header("ℹ️ Informations")
    st.markdown("""
    **Optimisations appliquées :**
    - ✅ Streaming temps réel
    - ✅ 3 fragments au lieu de 8
    - ✅ Pas de multi-query
    - ✅ Pas de re-ranker
    - ✅ Prompt simplifié

    **Temps de réponse attendu :**
    - Recherche : 1-2s
    - Génération : 10-30s
    - Total : ~15-35s

    **Contre ~2 minutes avant !**
    """)

    if st.button("🗑️ Effacer l'historique"):
        st.session_state.messages = []
        st.rerun()
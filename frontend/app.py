import streamlit as st
import requests
import json
import time
from typing import List, Dict

API_BASE_URL = "http://localhost:8000/api/rag"



def check_health() -> bool:
    """Vérifie si l'API est accessible"""
    try:
        response = requests.get(f"{API_BASE_URL}/health/", timeout=5)
        return response.status_code == 200
    except:
        return False


def get_stats() -> Dict:
    """Récupère les statistiques de la base de données"""
    try:
        response = requests.get(f"{API_BASE_URL}/stats/", timeout=10)
        if response.status_code == 200:
            return response.json()
        return {'status': 'error', 'message': 'Erreur API'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}


def retrieve_sources(query: str) -> List[Dict]:
    """Récupère les sources pertinentes"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/retrieve/",
            json={'query': query},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('sources', [])
        return []
    except Exception as e:
        st.error(f"Erreur lors de la récupération des sources : {e}")
        return []


def query_rag(query: str) -> Dict:
    """Exécute une requête RAG complète (non-streaming)"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/query/",
            json={'query': query},
            timeout=180
        )
        if response.status_code == 200:
            return response.json()
        return {'success': False, 'error': 'Erreur API'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def query_rag_stream(query: str):
    """Générateur pour le streaming de réponses"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/query/stream/",
            json={'query': query},
            stream=True,
            timeout=180
        )

        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = json.loads(line[6:])
                    yield data

    except Exception as e:
        yield {'type': 'error', 'data': str(e)}



st.set_page_config(
    page_title="Assistant IA Burkina",
    layout="wide"
)

st.title(" Assistant IA Contextuel - Burkina Faso")
st.markdown("---")

# Vérification de la connexion API
if not check_health():
    st.error(
        "Impossible de se connecter à l'API backend. Assurez-vous que Django est lancé sur http://localhost:8000")
    st.stop()

# Récupération des statistiques
stats = get_stats()

if stats.get('status') == 'ready':
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(" Documents", stats.get('total_documents', 0))
    with col2:
        st.metric(" Modèle", stats.get('model', 'N/A'))
    with col3:
        st.metric(" Top-K", stats.get('similarity_top_k', 3))
    with col4:
        st.metric(" Statut", "Prêt")
else:
    st.error(f" Erreur backend : {stats.get('message', 'Inconnu')}")
    st.stop()

st.markdown("---")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message["role"] == "assistant" and "sources" in message:
            with st.expander(" Sources utilisées", expanded=False):
                for source in message["sources"]:
                    st.markdown(f"**{source['index']}.** {source['source']} (score: {source['score']:.3f})")
                    st.caption(source['text'])
                    st.markdown("---")

if prompt := st.chat_input("Posez votre question sur l'agriculture du Burkina Faso..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        sources_placeholder = st.empty()
        metrics_placeholder = st.empty()


        start_time = time.time()
        retrieval_time = None
        generation_time = None


        try:
            full_response = ""
            sources = []

            with st.spinner("Recherche en cours..."):
                for event in query_rag_stream(prompt):
                    event_type = event.get('type')

                    if event_type == 'sources':
                        retrieval_time = event.get('retrieval_time', 0)
                        sources = event.get('data', [])

                        # Affichage des sources
                        with sources_placeholder.expander("Sources utilisées", expanded=False):
                            for source in sources:
                                st.markdown(f"**{source['index']}.** {source['source']} (score: {source['score']:.3f})")
                                st.caption(source['text'])
                                st.markdown("---")


                        metrics_placeholder.info(
                            f" Recherche terminée en **{retrieval_time:.2f}s** • Génération en cours...")

                    elif event_type == 'token':

                        token = event.get('data', '')
                        full_response += token
                        response_placeholder.markdown(full_response + "▌")

                    elif event_type == 'done':

                        generation_time = event.get('generation_time', 0)
                        total_time = event.get('total_time', 0)


                        response_placeholder.markdown(full_response)


                        col1, col2, col3 = metrics_placeholder.columns(3)
                        with col1:
                            st.metric(" Recherche", f"{retrieval_time:.2f}s")
                        with col2:
                            st.metric(" Génération", f"{generation_time:.2f}s")
                        with col3:
                            st.metric(" Total", f"{total_time:.2f}s")

                    elif event_type == 'error':
                        error_msg = f" Erreur : {event.get('data', 'Inconnue')}"
                        response_placeholder.error(error_msg)
                        full_response = error_msg


            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response,
                "sources": sources
            })

        except Exception as e:
            error_msg = f" Erreur : {str(e)}"
            response_placeholder.error(error_msg)
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg
            })

# Sidebar
with st.sidebar:
    st.header(" Informations")

    st.markdown("**Architecture:**")
    st.markdown("""
    - Backend: Django REST API
    - Frontend: Streamlit
    - LLM: Mistral (Ollama)
    - Vector DB: ChromaDB
    """)

    st.markdown("---")

    st.markdown("**Fonctionnalités:**")
    st.markdown("""
    -  Streaming temps réel
    -  Recherche contextuelle
    -  Sources traçables
    -  API REST complète
    """)

    st.markdown("---")

    if st.button(" Effacer l'historique"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")


    if check_health():
        st.success(" API Backend connectée")
    else:
        st.error(" API Backend déconnectée")
import chromadb
from llama_index.core import VectorStoreIndex, Settings, PromptTemplate
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from django.conf import settings
from typing import Optional, Dict, List, Generator
import logging

logger = logging.getLogger(__name__)


class RAGService:
    """Service pour gérer les opérations RAG"""

    _instance: Optional['RAGService'] = None
    _query_engine = None
    _index = None

    QA_PROMPT_TEMPLATE = """Tu es un assistant expert sur l'agriculture du Burkina Faso. Réponds TOUJOURS en français.

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


    def __new__(cls):
        """Singleton pattern pour éviter de recharger les modèles"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialise le service RAG"""
        if self._query_engine is None:
            self._initialize_pipeline()

    def _initialize_pipeline(self):
        """Initialise le pipeline RAG"""
        try:
            config = settings.RAG_CONFIG


            Settings.llm = Ollama(
                model=config['LLM_MODEL'],
                request_timeout=config['REQUEST_TIMEOUT']
            )
            Settings.embed_model = HuggingFaceEmbedding(
                model_name=config['EMBED_MODEL']
            )


            db = chromadb.PersistentClient(path=config['CHROMA_DB_PATH'])
            chroma_collection = db.get_collection(config['CHROMA_COLLECTION_NAME'])

            if chroma_collection.count() == 0:
                raise ValueError("Base de données Chroma vide")

            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            self._index = VectorStoreIndex.from_vector_store(vector_store=vector_store)


            qa_prompt = PromptTemplate(self.QA_PROMPT_TEMPLATE)
            self._query_engine = self._index.as_query_engine(
                text_qa_template=qa_prompt,
                similarity_top_k=config['SIMILARITY_TOP_K'],
                streaming=True
            )

            logger.info(f"Pipeline RAG initialisé avec {chroma_collection.count()} documents")

        except Exception as e:
            logger.error(f"❌ Erreur d'initialisation RAG : {e}")
            raise

    def get_stats(self) -> Dict:
        """Retourne les statistiques de la base de données"""
        try:
            config = settings.RAG_CONFIG
            db = chromadb.PersistentClient(path=config['CHROMA_DB_PATH'])
            collection = db.get_collection(config['CHROMA_COLLECTION_NAME'])

            return {
                'total_documents': collection.count(),
                'collection_name': config['CHROMA_COLLECTION_NAME'],
                'model': config['LLM_MODEL'],
                'similarity_top_k': config['SIMILARITY_TOP_K'],
                'status': 'ready'
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des stats : {e}")
            return {'status': 'error', 'message': str(e)}

    def retrieve_sources(self, query: str) -> List[Dict]:
        """Récupère les sources pertinentes pour une requête"""
        try:
            config = settings.RAG_CONFIG
            retriever = self._index.as_retriever(
                similarity_top_k=config['SIMILARITY_TOP_K']
            )
            retrieved_nodes = retriever.retrieve(query)

            sources = []
            for i, node in enumerate(retrieved_nodes):
                sources.append({
                    'index': i + 1,
                    'source': node.metadata.get('source', 'Inconnue'),
                    'score': float(node.score),
                    'text': node.text[:200] + "..." if len(node.text) > 200 else node.text,
                    'full_text': node.text
                })

            return sources

        except Exception as e:
            logger.error(f"Erreur lors de la récupération des sources : {e}")
            raise

    def query_streaming(self, query: str) -> Generator[str, None, None]:
        """Génère une réponse en streaming"""
        try:
            streaming_response = self._query_engine.query(query)

            for text in streaming_response.response_gen:
                yield text

        except Exception as e:
            logger.error(f"Erreur lors de la génération : {e}")
            yield f"Erreur : {str(e)}"

    def query(self, query: str) -> Dict:
        """Exécute une requête complète (non-streaming)"""
        try:
            # Récupération des sources
            sources = self.retrieve_sources(query)

            # Génération de la réponse
            response = self._query_engine.query(query)

            return {
                'success': True,
                'answer': str(response),
                'sources': sources,
                'query': query
            }

        except Exception as e:
            logger.error(f"Erreur lors de la requête : {e}")
            return {
                'success': False,
                'error': str(e),
                'query': query
            }
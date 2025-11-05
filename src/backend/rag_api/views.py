from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import StreamingHttpResponse
from .services import RAGService
import json
import logging

logger = logging.getLogger(__name__)


class HealthCheckView(APIView):
    """Vérification de l'état du service"""

    def get(self, request):
        return Response({
            'status': 'ok',
            'service': 'RAG API',
            'version': '1.0.0'
        })


class StatsView(APIView):
    """Statistiques de la base de données"""

    def get(self, request):
        try:
            rag_service = RAGService()
            stats = rag_service.get_stats()
            return Response(stats, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Erreur Stats : {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RetrieveSourcesView(APIView):
    """Récupère les sources pertinentes pour une question"""

    def post(self, request):
        query = request.data.get('query', '').strip()

        if not query:
            return Response(
                {'error': 'Le champ "query" est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            rag_service = RAGService()
            sources = rag_service.retrieve_sources(query)

            return Response({
                'query': query,
                'sources': sources,
                'count': len(sources)
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Erreur Retrieval : {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class QueryView(APIView):
    """Exécute une requête RAG complète (non-streaming)"""

    def post(self, request):
        query = request.data.get('query', '').strip()

        if not query:
            return Response(
                {'error': 'Le champ "query" est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            rag_service = RAGService()
            result = rag_service.query(query)

            if result['success']:
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': result['error']},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            logger.error(f"Erreur Query : {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class QueryStreamView(APIView):
    """Exécute une requête RAG avec streaming de la réponse"""

    def post(self, request):
        query = request.data.get('query', '').strip()

        if not query:
            return Response(
                {'error': 'Le champ "query" est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            import time
            rag_service = RAGService()

            def event_stream():
                """Générateur pour Server-Sent Events"""

                # Mesure du temps de récupération
                retrieval_start = time.time()
                sources = rag_service.retrieve_sources(query)
                retrieval_time = time.time() - retrieval_start

                # Envoi des sources avec le temps
                yield f"data: {json.dumps({'type': 'sources', 'data': sources, 'retrieval_time': retrieval_time})}\n\n"

                # Mesure du temps de génération
                generation_start = time.time()

                # Streaming de la réponse
                for text_chunk in rag_service.query_streaming(query):
                    yield f"data: {json.dumps({'type': 'token', 'data': text_chunk})}\n\n"

                generation_time = time.time() - generation_start

                # Signal de fin avec métriques
                yield f"data: {json.dumps({'type': 'done', 'generation_time': generation_time, 'total_time': retrieval_time + generation_time})}\n\n"

            response = StreamingHttpResponse(
                event_stream(),
                content_type='text/event-stream'
            )
            response['Cache-Control'] = 'no-cache'
            response['X-Accel-Buffering'] = 'no'

            return response

        except Exception as e:
            logger.error(f"Erreur Query Stream : {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
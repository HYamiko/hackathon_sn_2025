
from django.urls import path
from .views import (
    HealthCheckView,
    StatsView,
    RetrieveSourcesView,
    QueryView,
    QueryStreamView
)

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health'),
    path('stats/', StatsView.as_view(), name='stats'),
    path('retrieve/', RetrieveSourcesView.as_view(), name='retrieve_sources'),
    path('query/', QueryView.as_view(), name='query'),
    path('query/stream/', QueryStreamView.as_view(), name='query_stream'),
]




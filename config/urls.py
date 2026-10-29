from django.contrib import admin
from django.urls import include, path

from solicitacoes import api

# "/" é a landing page (servida pelo WhiteNoise a partir de landing/, ver settings.py)
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/solicitacoes/", api.criar_solicitacao, name="api-criar-solicitacao"),
    path("painel/", include("solicitacoes.urls")),
]

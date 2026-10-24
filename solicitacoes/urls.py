from django.urls import path

from . import api

urlpatterns = [
    path("api/solicitacoes/", api.criar_solicitacao, name="api-criar-solicitacao"),
]

from django.contrib.auth import views as auth_views
from django.urls import path

from . import api, views
from .forms import LoginComBloqueioForm

urlpatterns = [
    path("", views.lista, name="lista"),
    path("solicitacoes/<int:pk>/", views.atendimento, name="atendimento"),
    path("api/solicitacoes/", api.criar_solicitacao, name="api-criar-solicitacao"),
    path(
        "entrar/",
        auth_views.LoginView.as_view(authentication_form=LoginComBloqueioForm),
        name="login",
    ),
    path("sair/", auth_views.LogoutView.as_view(), name="logout"),
]

from django.contrib import admin

from .models import Solicitacao


@admin.register(Solicitacao)
class SolicitacaoAdmin(admin.ModelAdmin):
    list_display = ["nome", "cidade", "uf", "servico", "status", "atendente", "criada_em"]
    list_filter = ["status", "servico", "agricultor_familiar", "uf"]
    search_fields = ["nome", "email", "cidade", "telefone"]

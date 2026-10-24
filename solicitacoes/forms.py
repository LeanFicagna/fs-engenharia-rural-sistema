from django import forms

from .models import Solicitacao


class SolicitacaoPublicaForm(forms.ModelForm):
    """Validação do formulário enviado pela landing page."""

    class Meta:
        model = Solicitacao
        fields = ["nome", "email", "cidade", "uf", "telefone", "mensagem"]

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.cache import cache
from django.core.exceptions import ValidationError

from .models import Solicitacao


class SolicitacaoPublicaForm(forms.ModelForm):
    """Validação do formulário enviado pela landing page."""

    class Meta:
        model = Solicitacao
        fields = ["nome", "email", "cidade", "uf", "telefone", "mensagem"]


MAX_TENTATIVAS_LOGIN = 5
BLOQUEIO_LOGIN_SEGUNDOS = 15 * 60


class LoginComBloqueioForm(AuthenticationForm):
    """Login que bloqueia o usuário por 15 minutos após 5 senhas erradas seguidas."""

    error_messages = {
        **AuthenticationForm.error_messages,
        "bloqueado": "Muitas tentativas erradas. Tente de novo em 15 minutos.",
    }

    def clean(self):
        usuario = (self.cleaned_data.get("username") or "").strip().lower()
        chave = f"login-falhas:{usuario}"
        falhas = cache.get(chave, 0)
        if falhas >= MAX_TENTATIVAS_LOGIN:
            raise ValidationError(self.error_messages["bloqueado"], code="bloqueado")

        try:
            cleaned_data = super().clean()
        except ValidationError:
            # O prazo recomeça a cada erro: o bloqueio dura 15 min após a última tentativa
            cache.set(chave, falhas + 1, BLOQUEIO_LOGIN_SEGUNDOS)
            raise

        cache.delete(chave)
        return cleaned_data


class AtendimentoForm(forms.ModelForm):
    """Campos que a equipe atualiza durante o atendimento."""

    class Meta:
        model = Solicitacao
        fields = ["status", "agricultor_familiar", "servico", "atendente", "observacoes"]
        widgets = {"observacoes": forms.Textarea(attrs={"rows": 4, "cols": 60})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["atendente"].queryset = self.fields["atendente"].queryset.filter(is_active=True)

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Usuário ou e-mail"

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


class CadastroUsuarioForm(UserCreationForm):
    """Cadastro de usuário da equipe feito pelo administrador.

    Reaproveita o UserCreationForm do Django: confirmação de senha, validadores de
    AUTH_PASSWORD_VALIDATORS e senha salva com hash. O e-mail vira o nome de usuário do login.
    """

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ["first_name", "email"]
        labels = {"first_name": "Nome", "email": "E-mail"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["email"].required = True
        self.fields["first_name"].widget.attrs["autofocus"] = True

    def clean_email(self) -> str:
        email = self.cleaned_data["email"].strip().lower()
        User = self._meta.model
        if User.objects.filter(username__iexact=email).exists() or User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Já existe um usuário com este e-mail.")
        # Definido antes da validação da senha, para o validador de similaridade comparar com ele
        self.instance.username = email
        return email

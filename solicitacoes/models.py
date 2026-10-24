from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

UFS = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA",
    "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
]

telefone_validator = RegexValidator(
    r"^\(\d{2}\) \d{5}-\d{4}$", "Use o formato (99) 99999-9999."
)


class Solicitacao(models.Model):
    class Status(models.TextChoices):
        NOVA = "nova", "Nova"
        EM_ATENDIMENTO = "em_atendimento", "Em atendimento"
        CONCLUIDA = "concluida", "Concluída"
        CANCELADA = "cancelada", "Cancelada"

    class Servico(models.TextChoices):
        CREDITO_RURAL = "credito_rural", "Crédito rural"
        GEORREFERENCIAMENTO = "georreferenciamento", "Georreferenciamento"
        TOPOGRAFIA = "topografia", "Topografia"
        REGULARIZACAO_FUNDIARIA = "regularizacao_fundiaria", "Regularização fundiária"
        REGULARIZACAO_AMBIENTAL = "regularizacao_ambiental", "Regularização ambiental"
        OUTRO = "outro", "Outro"

    # Dados do formulário da landing page
    nome = models.CharField(max_length=120)
    email = models.EmailField()
    cidade = models.CharField(max_length=100)
    uf = models.CharField("UF", max_length=2, choices=[(uf, uf) for uf in UFS])
    telefone = models.CharField(max_length=15, validators=[telefone_validator])
    mensagem = models.TextField(max_length=2000)

    # Preenchidos pela equipe durante o atendimento
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOVA)
    agricultor_familiar = models.BooleanField(null=True, blank=True)
    servico = models.CharField("serviço", max_length=30, choices=Servico.choices, blank=True)
    atendente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="solicitacoes",
    )
    observacoes = models.TextField("observações", blank=True)

    # Pedidos importados da planilha guardam a data original do envio
    criada_em = models.DateTimeField(default=timezone.now)
    # Identifica a linha da planilha de onde veio o pedido, para não importar duas vezes
    chave_planilha = models.CharField(max_length=400, unique=True, null=True, blank=True, editable=False)
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-criada_em"]
        verbose_name = "solicitação"
        verbose_name_plural = "solicitações"

    def __str__(self) -> str:
        return f"{self.nome} ({self.cidade}/{self.uf})"

import json

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import SolicitacaoPublicaForm

# Nome do campo no JSON da landing page -> campo do modelo
CAMPOS_DO_SITE = {
    "name": "nome",
    "email": "email",
    "city": "cidade",
    "uf": "uf",
    "phone": "telefone",
    "message": "mensagem",
}


# Sem CSRF: o envio vem de outro domínio (o site), sem sessão
@csrf_exempt
@require_POST
def criar_solicitacao(request: HttpRequest) -> JsonResponse:
    # A landing manda JSON como text/plain para evitar o preflight de CORS,
    # então o corpo é lido como JSON independente do Content-Type
    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"erro": "JSON inválido."}, status=400)
    if not isinstance(payload, dict):
        return JsonResponse({"erro": "JSON inválido."}, status=400)

    # Honeypot preenchido = bot
    if payload.get("website"):
        return JsonResponse({"erro": "Envio recusado."}, status=400)

    dados = {campo: payload.get(chave, "") for chave, campo in CAMPOS_DO_SITE.items()}
    form = SolicitacaoPublicaForm(dados)
    if not form.is_valid():
        erros = {
            chave: list(form.errors[campo])
            for chave, campo in CAMPOS_DO_SITE.items()
            if campo in form.errors
        }
        return JsonResponse({"erros": erros}, status=400)

    solicitacao = form.save()
    return JsonResponse({"id": solicitacao.id}, status=201)

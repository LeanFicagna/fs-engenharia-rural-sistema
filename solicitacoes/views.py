from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import AtendimentoForm
from .models import Solicitacao
from .planilha import ErroPlanilha, importar_da_planilha


@login_required
def lista(request: HttpRequest) -> HttpResponse:
    status = request.GET.get("status", "")
    cidade = request.GET.get("cidade", "").strip()

    solicitacoes = Solicitacao.objects.select_related("atendente")
    if status:
        solicitacoes = solicitacoes.filter(status=status)
    if cidade:
        solicitacoes = solicitacoes.filter(cidade__icontains=cidade)

    cidades = Solicitacao.objects.order_by("cidade").values_list("cidade", flat=True).distinct()
    return render(
        request,
        "solicitacoes/lista.html",
        {
            "solicitacoes": solicitacoes,
            "status_escolhido": status,
            "cidade_escolhida": cidade,
            "opcoes_status": Solicitacao.Status.choices,
            "cidades": cidades,
        },
    )


@login_required
def atendimento(request: HttpRequest, pk: int) -> HttpResponse:
    solicitacao = get_object_or_404(Solicitacao, pk=pk)

    if request.method == "POST":
        form = AtendimentoForm(request.POST, instance=solicitacao)
        if form.is_valid():
            form.save()
            messages.success(request, f"Atendimento de {solicitacao.nome} atualizado.")
            return redirect("lista")
    else:
        # Quem abre um pedido sem atendente já aparece sugerido
        initial = {} if solicitacao.atendente else {"atendente": request.user}
        form = AtendimentoForm(instance=solicitacao, initial=initial)

    return render(
        request,
        "solicitacoes/atendimento.html",
        {"solicitacao": solicitacao, "form": form},
    )


@login_required
@require_POST
def importar_planilha(request: HttpRequest) -> HttpResponse:
    try:
        resultado = importar_da_planilha()
    except ErroPlanilha as erro:
        messages.error(request, str(erro))
        return redirect("lista")

    messages.success(
        request,
        f"Planilha importada: {resultado.criadas} nova(s), {resultado.ja_importadas} já estavam no painel.",
    )
    for aviso in resultado.invalidas:
        messages.warning(request, f"Ignorada — {aviso}")
    return redirect("lista")

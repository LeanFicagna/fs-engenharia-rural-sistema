from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AtendimentoForm
from .models import Solicitacao


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

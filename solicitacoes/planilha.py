"""Importa para o painel os pedidos que a landing page registra na planilha do Google."""

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone as dt_timezone
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from django.conf import settings
from django.utils import timezone

from .forms import SolicitacaoPublicaForm
from .models import Solicitacao

# O Apps Script devolve a data no formato do JavaScript:
# "Wed Oct 14 2026 11:29:26 GMT-0300 (Horário Padrão de Brasília)"
DATA_JAVASCRIPT = re.compile(
    r"^\w{3} (\w{3}) (\d{1,2}) (\d{4}) (\d{2}):(\d{2}):(\d{2}) GMT([+-])(\d{2})(\d{2})"
)
MESES = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
}


class ErroPlanilha(Exception):
    pass


@dataclass
class ResultadoImportacao:
    criadas: int = 0
    ja_importadas: int = 0
    invalidas: list[str] = field(default_factory=list)


def buscar_linhas() -> list[dict]:
    if not settings.PLANILHA_URL or not settings.PLANILHA_TOKEN:
        raise ErroPlanilha("Configure PLANILHA_URL e PLANILHA_TOKEN no arquivo .env.")

    endereco = f"{settings.PLANILHA_URL}?{urlencode({'token': settings.PLANILHA_TOKEN})}"
    try:
        with urlopen(endereco, timeout=30) as resposta:
            dados = json.load(resposta)
    except (URLError, TimeoutError, ValueError) as erro:
        # Não inclui o endereço na mensagem: ele carrega o token
        raise ErroPlanilha(f"Não foi possível ler a planilha ({type(erro).__name__}).") from erro

    if not isinstance(dados, dict) or not dados.get("ok"):
        motivo = dados.get("error", "resposta inesperada") if isinstance(dados, dict) else "resposta inesperada"
        raise ErroPlanilha(f"A planilha recusou a leitura: {motivo}.")
    return dados.get("solicitacoes", [])


def converter_data(texto: str) -> datetime | None:
    encontrado = DATA_JAVASCRIPT.match(texto)
    if encontrado:
        mes, dia, ano, hora, minuto, segundo, sinal, fuso_h, fuso_m = encontrado.groups()
        if mes not in MESES:
            return None
        deslocamento = timedelta(hours=int(fuso_h), minutes=int(fuso_m))
        fuso = dt_timezone(deslocamento if sinal == "+" else -deslocamento)
        return datetime(int(ano), MESES[mes], int(dia), int(hora), int(minuto), int(segundo), tzinfo=fuso)

    # Caso o script passe a mandar a data em ISO 8601
    try:
        data = datetime.fromisoformat(texto)
    except ValueError:
        return None
    return data if timezone.is_aware(data) else timezone.make_aware(data)


def importar_da_planilha() -> ResultadoImportacao:
    resultado = ResultadoImportacao()

    for linha in buscar_linhas():
        data_texto = str(linha.get("data", "")).strip()
        email = str(linha.get("email", "")).strip().lower()
        # Data do envio + e-mail identificam a linha mesmo que linhas sejam apagadas na planilha
        chave = f"{data_texto}|{email}"

        if Solicitacao.objects.filter(chave_planilha=chave).exists():
            resultado.ja_importadas += 1
            continue

        form = SolicitacaoPublicaForm({campo: linha.get(campo, "") for campo in SolicitacaoPublicaForm.Meta.fields})
        if not form.is_valid():
            erros = "; ".join(f"{campo}: {' '.join(msgs)}" for campo, msgs in form.errors.items())
            resultado.invalidas.append(f"Linha {linha.get('id', '?')}: {erros}")
            continue

        solicitacao = form.save(commit=False)
        solicitacao.chave_planilha = chave
        solicitacao.criada_em = converter_data(data_texto) or timezone.now()
        solicitacao.save()
        resultado.criadas += 1

    return resultado

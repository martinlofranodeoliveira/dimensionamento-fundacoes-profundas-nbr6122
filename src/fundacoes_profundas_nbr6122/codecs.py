"""Codec JSON canônico RFC 8259 para fundações profundas NBR 6122:2022.

Garante ausência estrita de ponto flutuante IEEE-754, rejeição de BOM,
verificação de chaves duplicadas e limitação de profundidade estrutural.
"""

from __future__ import annotations

import json
from enum import Enum
from fractions import Fraction
from typing import Any

from fundacoes_profundas_nbr6122.models import (
    CamadaSoloSPT,
    DadosProjetoFundacaoProfunda,
    EfeitoGrupoEstacas,
    GeometriaEstaca,
    ResultadoProjetoFundacaoProfunda,
    SolicitacaoCarga,
    TipoProcessoExecutivo,
    TipoSecaoTransversal,
)


def _rejeitar_float(valor: str) -> None:
    raise ValueError(
        f"Ponto flutuante IEEE-754 ({valor}) não é permitido. "
        "Utilize inteiros ou strings numéricas fracionárias/decimais exatas."
    )


def _rejeitar_chaves_duplicadas(pares: list[tuple[str, Any]]) -> dict[str, Any]:
    resultado: dict[str, Any] = {}
    for chave, valor in pares:
        if chave in resultado:
            raise ValueError(f"Chave duplicada encontrada no JSON: '{chave}'")
        resultado[chave] = valor
    return resultado


def _verificar_profundidade(obj: Any, profundidade: int = 1, limite: int = 32) -> None:
    if profundidade > limite:
        raise ValueError(
            f"Profundidade da estrutura JSON ({profundidade}) excede o limite máximo permitido de {limite}."
        )
    if isinstance(obj, dict):
        for v in obj.values():
            _verificar_profundidade(v, profundidade + 1, limite)
    elif isinstance(obj, list):
        for elem in obj:
            _verificar_profundidade(elem, profundidade + 1, limite)


def _para_fracao(val: Any) -> Fraction:
    if isinstance(val, (int, str)):
        return Fraction(val)
    if isinstance(val, Fraction):
        return val
    raise ValueError(f"Tipo inválido para conversão fracionária: {type(val).__name__} ({val})")


def _serializar_valor(val: Any) -> Any:
    if isinstance(val, Fraction):
        if val.denominator == 1:
            return val.numerator
        return f"{val.numerator}/{val.denominator}"
    if isinstance(val, Enum):
        return val.value
    if isinstance(val, tuple):
        return [_serializar_valor(x) for x in val]
    if isinstance(val, list):
        return [_serializar_valor(x) for x in val]
    if isinstance(val, dict):
        return {k: _serializar_valor(v) for k, v in val.items()}
    return val


def carregar_projeto_fundacao_json(conteudo: str) -> DadosProjetoFundacaoProfunda:
    """Carrega e valida o projeto de fundação profunda a partir de JSON canônico RFC 8259."""
    if conteudo.startswith(("\ufeff", "\xef\xbb\xbf")):
        raise ValueError("Byte Order Mark (BOM) detectado. O arquivo deve ser codificado em UTF-8 puro.")

    try:
        dados = json.loads(
            conteudo,
            object_pairs_hook=_rejeitar_chaves_duplicadas,
            parse_float=_rejeitar_float,
        )
    except json.JSONDecodeError as err:
        raise ValueError(f"Erro de decodificação JSON: {err}") from err

    _verificar_profundidade(dados)

    if not isinstance(dados, dict):
        raise ValueError("O JSON raiz do projeto deve ser um objeto dicionário.")

    identificacao = str(dados.get("identificacao_projeto") or dados.get("nome_projeto") or "Projeto de Fundação Profunda")

    # Processo executivo
    proc_str = str(dados.get("processo_executivo") or dados.get("tipo_estaca") or "ESTACA_HELICE_CONTINUA").upper().strip()
    try:
        processo = TipoProcessoExecutivo(proc_str)
    except ValueError:
        processo = TipoProcessoExecutivo.ESTACA_HELICE_CONTINUA

    # Geometria
    geo_raw = dados.get("geometria")
    if not isinstance(geo_raw, dict):
        raise ValueError("O campo 'geometria' deve ser um objeto JSON.")

    tipo_sec_str = str(geo_raw.get("tipo_secao", "CIRCULAR")).upper().strip()
    try:
        tipo_secao = TipoSecaoTransversal(tipo_sec_str)
    except ValueError:
        tipo_secao = TipoSecaoTransversal.CIRCULAR

    dim = _para_fracao(geo_raw.get("diametro_ou_lado_m") or geo_raw.get("diametro_m") or geo_raw.get("lado_m") or "2/5")
    comp = _para_fracao(geo_raw.get("comprimento_fuste_m") or geo_raw.get("comprimento_m") or 12)
    fck = _para_fracao(geo_raw.get("fck_concreto_mpa") or 30)
    larg = _para_fracao(geo_raw.get("largura_b_m") or 0)
    cota = _para_fracao(geo_raw.get("cota_arrasamento_m") or 0)
    taxa_arm = _para_fracao(geo_raw.get("taxa_armadura_adotada") or Fraction(5, 1000))

    geometria = GeometriaEstaca(
        tipo_secao=tipo_secao,
        diametro_ou_lado_m=dim,
        comprimento_fuste_m=comp,
        fck_concreto_mpa=fck,
        largura_b_m=larg,
        cota_arrasamento_m=cota,
        taxa_armadura_adotada=taxa_arm,
    )

    # Perfil estratigráfico (camadas de solo)
    camadas_raw = dados.get("perfil_solo") or dados.get("camadas_solo") or []
    if not isinstance(camadas_raw, list) or not camadas_raw:
        raise ValueError("O campo 'perfil_solo' deve ser uma lista não vazia de camadas.")

    camadas_list: list[CamadaSoloSPT] = []
    for c in camadas_raw:
        if not isinstance(c, dict):
            raise ValueError("Cada camada de solo deve ser um objeto JSON.")
        topo_c = _para_fracao(c.get("profundidade_topo_m", 0))
        base_c = _para_fracao(c.get("profundidade_base_m", 1))
        tipo_s = str(c.get("tipo_solo", "SILTE")).upper().strip()
        nspt = int(c.get("nspt_medio") or c.get("nspt") or 10)
        camadas_list.append(CamadaSoloSPT(topo_c, base_c, tipo_s, nspt))

    # Solicitações
    sol_raw = dados.get("solicitacao") or dados.get("esforcos") or {}
    if not isinstance(sol_raw, dict):
        raise ValueError("O campo 'solicitacao' deve ser um objeto JSON.")

    normal_kn = _para_fracao(sol_raw.get("forca_normal_compressao_kn") or sol_raw.get("carga_normal_kn") or 500)
    tracao_kn = _para_fracao(sol_raw.get("forca_tracao_kn") or 0)
    momento_knm = _para_fracao(sol_raw.get("momento_fletor_knm") or 0)
    horiz_kn = _para_fracao(sol_raw.get("forca_horizontal_kn") or 0)

    solicitacao = SolicitacaoCarga(
        forca_normal_compressao_kn=normal_kn,
        forca_tracao_kn=tracao_kn,
        momento_fletor_knm=momento_knm,
        forca_horizontal_kn=horiz_kn,
    )

    # Efeito de grupo opcional
    grp_raw = dados.get("grupo") or {}
    num_estacas = int(grp_raw.get("numero_estacas_bloco", 1))
    espacamento = _para_fracao(grp_raw.get("espacamento_entre_eixos_m") or 0)
    grupo = EfeitoGrupoEstacas(numero_estacas_bloco=num_estacas, espacamento_entre_eixos_m=espacamento)

    prova_carga = bool(dados.get("possui_prova_carga", False))
    responsavel = str(dados.get("responsavel_tecnico", "Engenharia Geotécnica"))

    return DadosProjetoFundacaoProfunda(
        identificacao_projeto=identificacao,
        processo_executivo=processo,
        geometria=geometria,
        perfil_solo=tuple(camadas_list),
        solicitacao=solicitacao,
        grupo=grupo,
        possui_prova_carga=prova_carga,
        responsavel_tecnico=responsavel,
    )


def exportar_resultado_json(resultado: ResultadoProjetoFundacaoProfunda) -> str:
    """Serializa o resultado em JSON canônico RFC 8259 determinístico."""
    dados: dict[str, Any] = {
        "normas_referencia": [
            "ABNT NBR 6122:2022",
            "ABNT NBR 6118:2023",
        ],
        "identificacao_projeto": resultado.identificacao_projeto,
        "processo_executivo": resultado.processo_executivo.value,
        "geometria": {
            "tipo_secao": resultado.geometria.tipo_secao.value,
            "diametro_ou_lado_m": _serializar_valor(resultado.geometria.diametro_ou_lado_m),
            "comprimento_fuste_m": _serializar_valor(resultado.geometria.comprimento_fuste_m),
            "fck_concreto_mpa": _serializar_valor(resultado.geometria.fck_concreto_mpa),
            "taxa_armadura_adotada": _serializar_valor(resultado.geometria.taxa_armadura_adotada),
        },
        "solicitacao": {
            "forca_normal_compressao_kn": _serializar_valor(resultado.solicitacao.forca_normal_compressao_kn),
            "forca_tracao_kn": _serializar_valor(resultado.solicitacao.forca_tracao_kn),
            "momento_fletor_knm": _serializar_valor(resultado.solicitacao.momento_fletor_knm),
            "forca_horizontal_kn": _serializar_valor(resultado.solicitacao.forca_horizontal_kn),
        },
        "capacidade_geotecnica_aoki_velloso": {
            "metodo": resultado.aoki_velloso.metodo,
            "resistencia_ponta_kn": _serializar_valor(resultado.aoki_velloso.resistencia_ponta_kn),
            "resistencia_lateral_kn": _serializar_valor(resultado.aoki_velloso.resistencia_lateral_kn),
            "resistencia_total_ultima_kn": _serializar_valor(resultado.aoki_velloso.resistencia_total_ultima_kn),
            "capacidade_admissivel_kn": _serializar_valor(resultado.aoki_velloso.capacidade_admissivel_kn),
        },
        "capacidade_geotecnica_decourt_quaresma": {
            "metodo": resultado.decourt_quaresma.metodo,
            "resistencia_ponta_kn": _serializar_valor(resultado.decourt_quaresma.resistencia_ponta_kn),
            "resistencia_lateral_kn": _serializar_valor(resultado.decourt_quaresma.resistencia_lateral_kn),
            "resistencia_total_ultima_kn": _serializar_valor(resultado.decourt_quaresma.resistencia_total_ultima_kn),
            "capacidade_admissivel_kn": _serializar_valor(resultado.decourt_quaresma.capacidade_admissivel_kn),
        },
        "capacidade_admissivel_adotada_kn": _serializar_valor(resultado.capacidade_admissivel_adotada_kn),
        "fator_seguranca_geotecnico_adotado": _serializar_valor(resultado.fator_seguranca_geotecnico_adotado),
        "verificacao_estrutural_fuste": {
            "area_secao_concreto_m2": _serializar_valor(resultado.estrutural.area_secao_concreto_m2),
            "perimetro_fuste_m": _serializar_valor(resultado.estrutural.perimetro_fuste_m),
            "resistencia_calculo_concreto_kpa": _serializar_valor(resultado.estrutural.resistencia_calculo_concreto_kpa),
            "area_armadura_minima_cm2": _serializar_valor(resultado.estrutural.area_armadura_minima_cm2),
            "area_armadura_adotada_cm2": _serializar_valor(resultado.estrutural.area_armadura_adotada_cm2),
            "forca_normal_admissivel_estrutural_kn": _serializar_valor(
                resultado.estrutural.forca_normal_admissivel_estrutural_kn
            ),
            "tensao_trabalho_concreto_kpa": _serializar_valor(resultado.estrutural.tensao_trabalho_concreto_kpa),
            "aprovado_estruturalmente": resultado.estrutural.aprovado_estruturalmente,
        },
        "efeito_grupo": {
            "eficiencia_grupo": _serializar_valor(resultado.eficiencia_grupo),
            "capacidade_admissivel_bloco_kn": _serializar_valor(resultado.capacidade_admissivel_bloco_kn),
        },
        "aprovado_geotecnicamente": resultado.aprovado_geotecnicamente,
        "conformidade_geral": resultado.conformidade_geral,
        "alertas_tecnicos": list(resultado.alertas_tecnicos),
    }

    return json.dumps(dados, ensure_ascii=False, indent=2, sort_keys=True)


decodificar_json_projeto = carregar_projeto_fundacao_json


def codificar_json_projeto(
    arg1: Any,
    arg2: ResultadoProjetoFundacaoProfunda | None = None,
) -> str:
    """Codifica resultado em JSON RFC 8259, aceitando (resultado) ou (dados, resultado)."""
    if isinstance(arg1, ResultadoProjetoFundacaoProfunda):
        return exportar_resultado_json(arg1)
    if arg2 is not None and isinstance(arg2, ResultadoProjetoFundacaoProfunda):
        return exportar_resultado_json(arg2)
    raise ValueError("ResultadoProjetoFundacaoProfunda não fornecido para codificação JSON.")

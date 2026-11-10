"""Exportadores técnicos: memorial descritivo, CSV sanitizado e ZIP determinístico.

Conforme normas ABNT NBR 6122:2022 e ABNT NBR 6118:2023.
Padrão de engenharia LOFRANO TECNOLOGIA.
"""

from __future__ import annotations

import csv
import io
import os
import zipfile
from fractions import Fraction
from typing import Any, Optional

from fundacoes_profundas_nbr6122.codecs import exportar_resultado_json
from fundacoes_profundas_nbr6122.models import ResultadoProjetoFundacaoProfunda


def _fmt(val: Fraction, casas: int = 2) -> str:
    """Formata fração para string decimal com número fixo de casas sem ponto flutuante IEEE-754."""
    num = val.numerator
    den = val.denominator
    if den == 1:
        return f"{num}.0" if casas > 0 else str(num)
    inteiro = num // den
    resto = abs(num % den)
    fator = 10**casas
    frac_parte = (resto * fator + den // 2) // den
    return f"{inteiro}.{frac_parte:0{casas}d}"


def _sanitizar_campo_csv(val: str) -> str:
    """Sanitiza strings contra injeção de fórmulas de planilhas eletrônicas."""
    if val and val[0] in ("=", "+", "-", "@", "\t", "\r"):
        return f"'{val}"
    return val


def gerar_memorial_fundacao_texto(res: ResultadoProjetoFundacaoProfunda) -> str:
    """Gera memorial técnico descritivo completo da fundação profunda."""
    linhas: list[str] = []
    w = 84
    linhas.append("=" * w)
    linhas.append("           LOFRANO TECNOLOGIA - ENGENHARIA GEOTÉCNICA E ESTRUTURAL")
    linhas.append("      MEMORIAL DE CÁLCULO DE FUNDAÇÕES PROFUNDAS - ABNT NBR 6122:2022")
    linhas.append("=" * w)
    linhas.append(f"Projeto / Obra:           {res.identificacao_projeto}")
    linhas.append(f"Processo Executivo:       {res.processo_executivo.value}")
    linhas.append(f"Tipo de Seção:            {res.geometria.tipo_secao.value}")
    linhas.append(f"Diâmetro / Lado:          {_fmt(res.geometria.diametro_ou_lado_m, 2)} m")
    linhas.append(f"Comprimento do Fuste:     {_fmt(res.geometria.comprimento_fuste_m, 2)} m")
    linhas.append(f"fck do Concreto:          {_fmt(res.geometria.fck_concreto_mpa, 1)} MPa")
    linhas.append("-" * w)

    st_geo = "APROVADO (R_adm >= N_atuante)" if res.aprovado_geotecnicamente else "REPROVADO (CARGA EXCESSIVA)"
    st_est = "CONFORME (N_adm >= N_atuante)" if res.estrutural.aprovado_estruturalmente else "REPROVADO (FUSTE SOBRECARREGADO)"
    st_glo = "CONFORME NBR 6122 / NBR 6118" if res.conformidade_geral else "PENDÊNCIAS TÉCNICAS / RISCO"

    linhas.append("1. AÇÕES E ESFORÇOS SOLICITANTES (CABEÇA DA FUNDAÇÃO)")
    linhas.append(f"  * Carga Normal de Compressão (Nk):  {_fmt(res.solicitacao.forca_normal_compressao_kn, 2)} kN")
    if res.solicitacao.forca_tracao_kn > Fraction(0, 1):
        linhas.append(f"  * Força de Tração / Arrancamento:   {_fmt(res.solicitacao.forca_tracao_kn, 2)} kN")
    if res.solicitacao.momento_fletor_knm > Fraction(0, 1):
        linhas.append(f"  * Momento Fletor Solicitante:       {_fmt(res.solicitacao.momento_fletor_knm, 2)} kNm")
    if res.solicitacao.forca_horizontal_kn > Fraction(0, 1):
        linhas.append(f"  * Força Horizontal Solicitante:     {_fmt(res.solicitacao.forca_horizontal_kn, 2)} kN")
    linhas.append("-" * w)

    linhas.append("2. CAPACIDADE DE CARGA GEOTÉCNICA - MÉTODO AOKI-VELLOSO (1975)")
    av = res.aoki_velloso
    linhas.append(f"  * Resistência de Ponta (Rp):        {_fmt(av.resistencia_ponta_kn, 2)} kN")
    linhas.append(f"  * Resistência Lateral (Rl):         {_fmt(av.resistencia_lateral_kn, 2)} kN")
    linhas.append(f"  * Resistência Última Total (Rult):  {_fmt(av.resistencia_total_ultima_kn, 2)} kN")
    linhas.append(f"  * Carga Admissível Geotécnica (Ra): {_fmt(av.capacidade_admissivel_kn, 2)} kN (FS = {_fmt(res.fator_seguranca_geotecnico_adotado, 1)})")
    linhas.append("-" * w)

    linhas.append("3. CAPACIDADE DE CARGA GEOTÉCNICA - MÉTODO DÉCOURT-QUARESMA (1978/1996)")
    dq = res.decourt_quaresma
    linhas.append(f"  * Resistência de Ponta (Rp):        {_fmt(dq.resistencia_ponta_kn, 2)} kN")
    linhas.append(f"  * Resistência Lateral (Rl):         {_fmt(dq.resistencia_lateral_kn, 2)} kN")
    linhas.append(f"  * Resistência Última Total (Rult):  {_fmt(dq.resistencia_total_ultima_kn, 2)} kN")
    linhas.append(f"  * Carga Admissível Geotécnica (Ra): {_fmt(dq.capacidade_admissivel_kn, 2)} kN (FS = {_fmt(res.fator_seguranca_geotecnico_adotado, 1)})")
    linhas.append("-" * w)

    linhas.append("4. CARGA ADMISSÍVEL ADOTADA E EFEITO DE GRUPO")
    linhas.append(f"  * Carga Admissível Isolada Adotada: {_fmt(res.capacidade_admissivel_adotada_kn, 2)} kN (Critério Conservador)")
    linhas.append(f"  * Eficiência do Bloco (Grupo):      {_fmt(res.eficiencia_grupo * 100, 1)}%")
    linhas.append(f"  * Capacidade Admissível do Bloco:   {_fmt(res.capacidade_admissivel_bloco_kn, 2)} kN")
    linhas.append(f"  * Status da Segurança Geotécnica:   {st_geo}")
    linhas.append("-" * w)

    linhas.append("5. VERIFICAÇÃO ESTRUTURAL DO FUSTE DE CONCRETO (NBR 6118 / NBR 6122)")
    es = res.estrutural
    linhas.append(f"  * Área da Seção de Concreto (Ac):   {_fmt(es.area_secao_concreto_m2, 4)} m² ({_fmt(es.area_secao_concreto_m2 * 10000, 1)} cm²)")
    linhas.append(f"  * Perímetro do Fuste (U):           {_fmt(es.perimetro_fuste_m, 3)} m")
    linhas.append(f"  * Tensão de Trabalho no Concreto:   {_fmt(es.tensao_trabalho_concreto_kpa / 1000, 2)} MPa")
    linhas.append(f"  * Área de Aço Mínima (As,min):      {_fmt(es.area_armadura_minima_cm2, 2)} cm²")
    linhas.append(f"  * Área de Aço Efetiva Adotada (As): {_fmt(es.area_armadura_adotada_cm2, 2)} cm²")
    linhas.append(f"  * Carga Admissível Estrutural (Nad):{_fmt(es.forca_normal_admissivel_estrutural_kn, 2)} kN")
    linhas.append(f"  * Status da Verificação Estrutural: {st_est}")
    linhas.append("-" * w)

    linhas.append(f"STATUS GLOBAL DE CONFORMIDADE:        {st_glo}")

    if res.alertas_tecnicos:
        linhas.append("-" * w)
        linhas.append("6. RECOMENDAÇÕES E ALERTAS TÉCNICOS NORMATIVOS")
        for alerta in res.alertas_tecnicos:
            linhas.append(f"  [ALERTA] {alerta}")

    linhas.append("=" * w)
    linhas.append("Emitido via Lofrano Tecnologia - Conforme ABNT NBR 6122:2022 e ABNT NBR 6118:2023")
    linhas.append("=" * w)

    return "\n".join(linhas)


def gerar_csv_resumo_fundacao(res: ResultadoProjetoFundacaoProfunda) -> str:
    """Gera resumo técnico tabular em CSV sanitizado contra injeção de fórmulas."""
    saida = io.StringIO()
    writer = csv.writer(saida, delimiter=";", lineterminator="\n")

    writer.writerow([
        _sanitizar_campo_csv("modulo"),
        _sanitizar_campo_csv("parametro"),
        _sanitizar_campo_csv("valor"),
        _sanitizar_campo_csv("unidade"),
        _sanitizar_campo_csv("observacao"),
    ])

    linhas = [
        ("SOLICITACAO", "carga_normal_compressao", _fmt(res.solicitacao.forca_normal_compressao_kn, 2), "kN", "Esforço característico atuante"),
        ("GEOMETRIA", "diametro_lado", _fmt(res.geometria.diametro_ou_lado_m, 2), "m", f"Seção {res.geometria.tipo_secao.value}"),
        ("GEOMETRIA", "comprimento_fuste", _fmt(res.geometria.comprimento_fuste_m, 2), "m", "Profundidade de embutimento"),
        ("GEOTECNIA_AOKI", "resistencia_ponta", _fmt(res.aoki_velloso.resistencia_ponta_kn, 2), "kN", "Aoki-Velloso (1975)"),
        ("GEOTECNIA_AOKI", "resistencia_lateral", _fmt(res.aoki_velloso.resistencia_lateral_kn, 2), "kN", "Aoki-Velloso (1975)"),
        ("GEOTECNIA_AOKI", "resistencia_total", _fmt(res.aoki_velloso.resistencia_total_ultima_kn, 2), "kN", "Carga última"),
        ("GEOTECNIA_AOKI", "capacidade_admissivel", _fmt(res.aoki_velloso.capacidade_admissivel_kn, 2), "kN", f"FS = {_fmt(res.fator_seguranca_geotecnico_adotado, 1)}"),
        ("GEOTECNIA_DECOURT", "resistencia_ponta", _fmt(res.decourt_quaresma.resistencia_ponta_kn, 2), "kN", "Décourt-Quaresma (1978/1996)"),
        ("GEOTECNIA_DECOURT", "resistencia_lateral", _fmt(res.decourt_quaresma.resistencia_lateral_kn, 2), "kN", "Décourt-Quaresma (1978/1996)"),
        ("GEOTECNIA_DECOURT", "resistencia_total", _fmt(res.decourt_quaresma.resistencia_total_ultima_kn, 2), "kN", "Carga última"),
        ("GEOTECNIA_DECOURT", "capacidade_admissivel", _fmt(res.decourt_quaresma.capacidade_admissivel_kn, 2), "kN", f"FS = {_fmt(res.fator_seguranca_geotecnico_adotado, 1)}"),
        ("CAPACIDADE_ADOTADA", "carga_admissivel_estaca", _fmt(res.capacidade_admissivel_adotada_kn, 2), "kN", "Menor valor entre métodos"),
        ("CAPACIDADE_ADOTADA", "capacidade_bloco", _fmt(res.capacidade_admissivel_bloco_kn, 2), "kN", f"Eficiência {res.eficiencia_grupo}"),
        ("ESTRUTURAL_FUSTE", "fck_concreto", _fmt(res.geometria.fck_concreto_mpa, 1), "MPa", "Classe do concreto"),
        ("ESTRUTURAL_FUSTE", "capacidade_estrutural_admissivel", _fmt(res.estrutural.forca_normal_admissivel_estrutural_kn, 2), "kN", "NBR 6118 / NBR 6122"),
        ("ESTRUTURAL_FUSTE", "area_aco_adotada", _fmt(res.estrutural.area_armadura_adotada_cm2, 2), "cm2", "Armadura longitudinal"),
        ("CONFORMIDADE", "status_geotecnico", "APROVADO" if res.aprovado_geotecnicamente else "REPROVADO", "status", "Segurança geotécnica"),
        ("CONFORMIDADE", "status_estrutural", "APROVADO" if res.estrutural.aprovado_estruturalmente else "REPROVADO", "status", "Segurança do fuste"),
        ("CONFORMIDADE", "status_geral", "CONFORME" if res.conformidade_geral else "PENDENCIAS", "status", "Conformidade global"),
    ]

    for mod, param, val, un, obs in linhas:
        writer.writerow([
            _sanitizar_campo_csv(mod),
            _sanitizar_campo_csv(param),
            _sanitizar_campo_csv(val),
            _sanitizar_campo_csv(un),
            _sanitizar_campo_csv(obs),
        ])

    return saida.getvalue()


def gerar_pacote_zip_fundacao(
    res: ResultadoProjetoFundacaoProfunda,
    caminho_zip: str,
    svg_conteudo: Optional[str] = None,
) -> None:
    """Gera pacote determinístico ZIP com O_EXCL, evitando sobrescrita acidental."""
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_BINARY", 0)
    fd = os.open(caminho_zip, flags, 0o644)
    fixed_time = (2026, 1, 1, 0, 0, 0)

    try:
        with open(fd, "wb", closefd=True) as f_out:
            with zipfile.ZipFile(f_out, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
                # 1. Memorial descritivo em texto
                txt = gerar_memorial_fundacao_texto(res).encode("utf-8")
                zi_txt = zipfile.ZipInfo(filename="memorial_fundacao_profunda.txt", date_time=fixed_time)
                zf.writestr(zi_txt, txt)

                # 2. Dados em JSON canônico
                js = exportar_resultado_json(res).encode("utf-8")
                zi_js = zipfile.ZipInfo(filename="dados_fundacao_profunda.json", date_time=fixed_time)
                zf.writestr(zi_js, js)

                # 3. Resumo tabular em CSV sanitizado
                csv_data = gerar_csv_resumo_fundacao(res).encode("utf-8")
                zi_csv = zipfile.ZipInfo(filename="resumo_fundacao_profunda.csv", date_time=fixed_time)
                zf.writestr(zi_csv, csv_data)

                # 4. Diagrama vetorial SVG se fornecido
                if svg_conteudo is not None:
                    zi_svg = zipfile.ZipInfo(filename="painel_fundacao_profunda.svg", date_time=fixed_time)
                    zf.writestr(zi_svg, svg_conteudo.encode("utf-8"))
    except Exception:
        if os.path.exists(caminho_zip):
            try:
                os.remove(caminho_zip)
            except OSError:
                pass
        raise


def exportar_memorial_descritivo(arg1: Any, arg2: Optional[ResultadoProjetoFundacaoProfunda] = None) -> str:
    """Exporta memorial descritivo aceitando (resultado) ou (dados, resultado)."""
    if isinstance(arg1, ResultadoProjetoFundacaoProfunda):
        return gerar_memorial_fundacao_texto(arg1)
    if arg2 is not None and isinstance(arg2, ResultadoProjetoFundacaoProfunda):
        return gerar_memorial_fundacao_texto(arg2)
    raise ValueError("ResultadoProjetoFundacaoProfunda não fornecido para memorial descritivo.")


def exportar_csv_resumo(arg1: Any, arg2: Optional[ResultadoProjetoFundacaoProfunda] = None) -> str:
    """Exporta resumo em CSV aceitando (resultado) ou (dados, resultado)."""
    if isinstance(arg1, ResultadoProjetoFundacaoProfunda):
        return gerar_csv_resumo_fundacao(arg1)
    if arg2 is not None and isinstance(arg2, ResultadoProjetoFundacaoProfunda):
        return gerar_csv_resumo_fundacao(arg2)
    raise ValueError("ResultadoProjetoFundacaoProfunda não fornecido para CSV.")


def gerar_pacote_completo_zip(arg1: Any, arg2: Any, arg3: Optional[str] = None) -> None:
    """Gera pacote ZIP aceitando (res, caminho) ou (dados, res, caminho)."""
    if isinstance(arg1, ResultadoProjetoFundacaoProfunda):
        gerar_pacote_zip_fundacao(arg1, str(arg2))
    elif isinstance(arg2, ResultadoProjetoFundacaoProfunda) and arg3 is not None:
        gerar_pacote_zip_fundacao(arg2, str(arg3))
    else:
        raise ValueError("Parâmetros inválidos para geração de pacote ZIP.")

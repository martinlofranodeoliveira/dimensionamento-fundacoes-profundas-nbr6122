"""Interface de Linha de Comando (CLI) para dimensionamento de fundações profundas NBR 6122:2022.

Desenvolvido por LOFRANO TECNOLOGIA.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from fundacoes_profundas_nbr6122 import __version__
from fundacoes_profundas_nbr6122.calculator import dimensionar_projeto_fundacao_profunda
from fundacoes_profundas_nbr6122.codecs import codificar_json_projeto, decodificar_json_projeto
from fundacoes_profundas_nbr6122.constants import (
    TABELA_FATORES_ESTACAS,
    TABELA_SOLOS,
)
from fundacoes_profundas_nbr6122.exporters import (
    exportar_csv_resumo,
    exportar_memorial_descritivo,
    gerar_pacote_completo_zip,
)
from fundacoes_profundas_nbr6122.svg_generator import gerar_painel_svg

EXEMPLO_HELICE = """{
  "identificacao_projeto": "Edifício Residencial Jardins - Bloco B",
  "processo_executivo": "ESTACA_HELICE_CONTINUA",
  "responsavel_tecnico": "Eng. Martin Lofrano de Oliveira - CREA/SP",
  "geometria": {
    "tipo_secao": "CIRCULAR",
    "diametro_ou_lado_m": "0.50",
    "comprimento_fuste_m": "14.0",
    "fck_concreto_mpa": 30,
    "cota_arrasamento_m": 0,
    "taxa_armadura_adotada": "0.005"
  },
  "solicitacao": {
    "forca_normal_compressao_kn": "850.0",
    "forca_tracao_kn": 0,
    "momento_fletor_knm": 0,
    "forca_horizontal_kn": 0
  },
  "perfil_solo": [
    {
      "profundidade_topo_m": 0,
      "profundidade_base_m": 3,
      "tipo_solo": "ARGILA_SILTOSA",
      "nspt_medio": 4
    },
    {
      "profundidade_topo_m": 3,
      "profundidade_base_m": 8,
      "tipo_solo": "SILTE_ARENOSO",
      "nspt_medio": 9
    },
    {
      "profundidade_topo_m": 8,
      "profundidade_base_m": 12,
      "tipo_solo": "AREIA_SILTOSA",
      "nspt_medio": 18
    },
    {
      "profundidade_topo_m": 12,
      "profundidade_base_m": 18,
      "tipo_solo": "AREIA",
      "nspt_medio": 28
    }
  ],
  "grupo": {
    "numero_estacas_bloco": 1,
    "espacamento_entre_eixos_m": 0
  },
  "possui_prova_carga": false
}"""

EXEMPLO_PRE_MOLDADA = """{
  "identificacao_projeto": "Galpão Logístico Bandeirantes",
  "processo_executivo": "ESTACA_PRE_MOLDADA_CONCRETO",
  "responsavel_tecnico": "Eng. Martin Lofrano de Oliveira - CREA/SP",
  "geometria": {
    "tipo_secao": "QUADRADA",
    "diametro_ou_lado_m": "0.35",
    "comprimento_fuste_m": "11.0",
    "fck_concreto_mpa": 35,
    "cota_arrasamento_m": 0,
    "taxa_armadura_adotada": "0.006"
  },
  "solicitacao": {
    "forca_normal_compressao_kn": "650.0",
    "forca_tracao_kn": 0,
    "momento_fletor_knm": 0,
    "forca_horizontal_kn": 0
  },
  "perfil_solo": [
    {
      "profundidade_topo_m": 0,
      "profundidade_base_m": 4,
      "tipo_solo": "SILTE_ARGILOSO",
      "nspt_medio": 5
    },
    {
      "profundidade_topo_m": 4,
      "profundidade_base_m": 9,
      "tipo_solo": "AREIA_ARGILOSA",
      "nspt_medio": 14
    },
    {
      "profundidade_topo_m": 9,
      "profundidade_base_m": 15,
      "tipo_solo": "AREIA",
      "nspt_medio": 24
    }
  ],
  "grupo": {
    "numero_estacas_bloco": 2,
    "espacamento_entre_eixos_m": "1.05"
  },
  "possui_prova_carga": true
}"""

EXEMPLO_TUBULAO = """{
  "identificacao_projeto": "Viaduto de Acesso Rodoviário",
  "processo_executivo": "TUBULAO_A_CEU_ABERTO",
  "responsavel_tecnico": "Eng. Martin Lofrano de Oliveira - CREA/SP",
  "geometria": {
    "tipo_secao": "CIRCULAR",
    "diametro_ou_lado_m": "1.20",
    "comprimento_fuste_m": "8.0",
    "fck_concreto_mpa": 25,
    "cota_arrasamento_m": 0,
    "taxa_armadura_adotada": "0.004"
  },
  "solicitacao": {
    "forca_normal_compressao_kn": "2200.0",
    "forca_tracao_kn": 0,
    "momento_fletor_knm": 0,
    "forca_horizontal_kn": 0
  },
  "perfil_solo": [
    {
      "profundidade_topo_m": 0,
      "profundidade_base_m": 3,
      "tipo_solo": "ARGILA",
      "nspt_medio": 6
    },
    {
      "profundidade_topo_m": 3,
      "profundidade_base_m": 6,
      "tipo_solo": "SILTE_ARGILOSO",
      "nspt_medio": 15
    },
    {
      "profundidade_topo_m": 6,
      "profundidade_base_m": 12,
      "tipo_solo": "AREIA",
      "nspt_medio": 35
    }
  ],
  "grupo": {
    "numero_estacas_bloco": 1,
    "espacamento_entre_eixos_m": 0
  },
  "possui_prova_carga": false
}"""


def criar_parser() -> argparse.ArgumentParser:
    """Cria e configura o analisador de argumentos da CLI."""
    parser = argparse.ArgumentParser(
        prog="fundacoes-profundas-nbr6122",
        description="Dimensionamento analítico determinístico de fundações profundas conforme ABNT NBR 6122:2022.",
        add_help=False,
    )

    parser.add_argument(
        "-a",
        "--ajuda",
        action="help",
        help="Exibe esta mensagem de ajuda e encerra.",
    )
    parser.add_argument(
        "-v",
        "--versao",
        action="version",
        version=f"%(prog)s {__version__} (LOFRANO TECNOLOGIA)",
        help="Exibe a versão do programa e encerra.",
    )

    subparsers = parser.add_subparsers(dest="comando", help="Comando a ser executado")

    # Subcomando 'calcular'
    parser_calc = subparsers.add_parser(
        "calcular",
        help="Executa o dimensionamento da fundação a partir de arquivo JSON.",
        add_help=False,
    )
    parser_calc.add_argument(
        "-a",
        "--ajuda",
        action="help",
        help="Exibe a ajuda do subcomando calcular.",
    )
    parser_calc.add_argument(
        "entrada",
        nargs="?",
        type=str,
        help="Caminho do arquivo JSON de entrada (ou '-' para entrada padrão stdin).",
    )
    parser_calc.add_argument(
        "-o",
        "--saida",
        type=str,
        help="Caminho do arquivo JSON de saída dos resultados.",
    )
    parser_calc.add_argument(
        "--memorial",
        type=str,
        help="Gera memorial técnico descritivo em formato texto/markdown.",
    )
    parser_calc.add_argument(
        "--csv",
        type=str,
        help="Gera planilha técnica resumida em formato CSV sanitizado.",
    )
    parser_calc.add_argument(
        "--svg",
        type=str,
        help="Gera painel visual esquemático de engenharia em formato vetorial SVG.",
    )
    parser_calc.add_argument(
        "--pacote-zip",
        type=str,
        help="Gera arquivo compactado ZIP determinístico com todos os artefatos de saída.",
    )

    # Subcomando 'catalogo'
    subparsers.add_parser(
        "catalogo",
        help="Exibe tabelas geotécnicas de solos (Aoki/Décourt) e fatores executivos de estacas.",
    )

    # Subcomando 'gerar-exemplo'
    parser_ex = subparsers.add_parser(
        "gerar-exemplo",
        help="Gera arquivo JSON de exemplo pronto para edição e cálculo.",
        add_help=False,
    )
    parser_ex.add_argument(
        "-a",
        "--ajuda",
        action="help",
        help="Exibe a ajuda do subcomando gerar-exemplo.",
    )
    parser_ex.add_argument(
        "-t",
        "--tipo",
        choices=["estaca-helice", "estaca-pre-moldada", "tubulao"],
        default="estaca-helice",
        help="Tipo de fundação a gerar no exemplo (estaca-helice, estaca-pre-moldada ou tubulao).",
    )
    parser_ex.add_argument(
        "-o",
        "--saida",
        type=str,
        help="Caminho de destino do arquivo JSON de exemplo (se omitido, imprime no stdout).",
    )

    return parser


def comando_catalogo() -> int:
    """Exibe catálogo normativo de solos e fatores executivos da NBR 6122."""
    print("=" * 80)
    print("CATÁLOGO GEOTÉCNICO DE FUNDAÇÕES PROFUNDAS (ABNT NBR 6122:2022)")
    print("=" * 80)
    print("\n1. COEFICIENTES GEOTÉCNICOS DE SOLOS (MÉTODOS SEMIEMPÍRICOS):")
    print(f"{'Tipo de Solo':<18} | {'K Aoki (MPa)':<14} | {'alpha Aoki (%)':<15} | {'C Décourt (kPa)'}")
    print("-" * 80)
    for solo_id, p in TABELA_SOLOS.items():
        k_mpa = f"{float(p.k_aoki_velloso_kpa) / 1000:.2f} MPa"
        alpha_pct = f"{float(p.alpha_aoki_velloso) * 100:.1f} %"
        c_kpa = f"{float(p.c_decourt_quaresma_kpa):.0f} kPa"
        print(f"{solo_id:<18} | {k_mpa:<14} | {alpha_pct:<15} | {c_kpa}")

    print("\n2. FATORES DE ESTACA POR PROCESSO EXECUTIVO:")
    print(f"{'Processo Executivo':<30} | {'F1 Aoki':<10} | {'F2 Aoki':<10} | {'alpha DQ':<10} | {'beta DQ'}")
    print("-" * 80)
    for proc_id, f in TABELA_FATORES_ESTACAS.items():
        f1 = f"{float(f.f1_aoki):.2f}"
        f2 = f"{float(f.f2_aoki):.2f}"
        ad = f"{float(f.alpha_decourt):.2f}"
        bd = f"{float(f.beta_decourt):.2f}"
        print(f"{proc_id:<30} | {f1:<10} | {f2:<10} | {ad:<10} | {bd}")

    print("\n3. DIRETRIZES DE SEGURANÇA E NORMAS:")
    print(" - Fator de Segurança Geotécnico Global (sem prova de carga): FS = 2,0")
    print(" - Fator de Segurança com Prova de Carga Estática: FS = 1,6")
    print(" - Atrito lateral médio limitado normativamente a 120 kPa (Décourt-Quaresma)")
    print(" - Armadura longitudinal mínima: 0,40% da seção de concreto (NBR 6118 / NBR 6122)")
    print("=" * 80)
    return 0


def comando_gerar_exemplo(tipo: str, saida: str | None) -> int:
    """Gera um arquivo JSON de exemplo pronto para dimensionamento."""
    mapa = {
        "estaca-helice": EXEMPLO_HELICE,
        "estaca-pre-moldada": EXEMPLO_PRE_MOLDADA,
        "tubulao": EXEMPLO_TUBULAO,
    }
    conteudo = mapa.get(tipo, EXEMPLO_HELICE)

    if saida:
        path = Path(saida)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(conteudo, encoding="utf-8")
        print(f"Exemplo '{tipo}' gerado com sucesso em: {saida}")
    else:
        print(conteudo)
    return 0


def comando_calcular(
    entrada: str | None,
    saida: str | None,
    memorial: str | None,
    csv: str | None,
    svg: str | None,
    pacote_zip: str | None,
) -> int:
    """Executa o cálculo analítico de dimensionamento."""
    if not entrada or entrada == "-":
        texto = sys.stdin.read()
    else:
        path_in = Path(entrada)
        if not path_in.exists():
            print(f"Erro: Arquivo de entrada não encontrado: {entrada}", file=sys.stderr)
            return 1
        texto = path_in.read_text(encoding="utf-8")

    try:
        dados = decodificar_json_projeto(texto)
        resultado = dimensionar_projeto_fundacao_profunda(dados)
    except Exception as exc:
        print(f"Erro durante o processamento do dimensionamento: {exc}", file=sys.stderr)
        return 1

    json_res = codificar_json_projeto(resultado)

    if saida:
        path_out = Path(saida)
        path_out.parent.mkdir(parents=True, exist_ok=True)
        path_out.write_text(json_res, encoding="utf-8")
        print(f"Resultados exportados em JSON: {saida}")
    else:
        if not memorial and not csv and not svg and not pacote_zip:
            print(json_res)

    if memorial:
        path_mem = Path(memorial)
        path_mem.parent.mkdir(parents=True, exist_ok=True)
        txt_mem = exportar_memorial_descritivo(resultado)
        path_mem.write_text(txt_mem, encoding="utf-8")
        print(f"Memorial descritivo gerado: {memorial}")

    if csv:
        path_csv = Path(csv)
        path_csv.parent.mkdir(parents=True, exist_ok=True)
        txt_csv = exportar_csv_resumo(resultado)
        path_csv.write_text(txt_csv, encoding="utf-8")
        print(f"Planilha CSV gerada: {csv}")

    if svg:
        path_svg = Path(svg)
        path_svg.parent.mkdir(parents=True, exist_ok=True)
        txt_svg = gerar_painel_svg(resultado)
        path_svg.write_text(txt_svg, encoding="utf-8")
        print(f"Painel vetorial SVG gerado: {svg}")

    if pacote_zip:
        path_zip = Path(pacote_zip)
        path_zip.parent.mkdir(parents=True, exist_ok=True)
        gerar_pacote_completo_zip(resultado, str(path_zip))
        print(f"Pacote ZIP determinístico gerado: {pacote_zip}")

    return 0


def main(args: list[str] | None = None) -> int:
    """Ponto de entrada principal da CLI."""
    parser = criar_parser()
    parsed = parser.parse_args(args)

    if not parsed.comando:
        parser.print_help()
        return 0

    if parsed.comando == "catalogo":
        return comando_catalogo()

    if parsed.comando == "gerar-exemplo":
        return comando_gerar_exemplo(parsed.tipo, parsed.saida)

    if parsed.comando == "calcular":
        return comando_calcular(
            entrada=parsed.entrada,
            saida=parsed.saida,
            memorial=parsed.memorial,
            csv=parsed.csv,
            svg=parsed.svg,
            pacote_zip=parsed.pacote_zip,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())

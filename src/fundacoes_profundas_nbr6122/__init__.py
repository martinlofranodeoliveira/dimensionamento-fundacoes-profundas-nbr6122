"""Pacote de dimensionamento de fundações profundas conforme ABNT NBR 6122:2022 e NBR 6118:2023.

Desenvolvido por LOFRANO TECNOLOGIA sob rigoroso padrão de integridade matemática:
- Aritmética 100% exata com frações racionais (fractions.Fraction)
- Zero float em grandezas geotécnicas, mecânicas, tensões e dimensões
- Sem dependências externas em tempo de execução (apenas biblioteca padrão Python)
- Codecs JSON estritos conforme RFC 8259
"""

from .constants import (
    COEFICIENTE_RUDIGER_CONCRETO,
    FATOR_SEGURANCA_GEOTECNICO_COM_PROVA_CARGA,
    FATOR_SEGURANCA_GEOTECNICO_COMPRESSAO,
    FATOR_SEGURANCA_GEOTECNICO_TRACAO,
    FYK_ACO_CA50_MPA,
    GAMMA_ACO,
    GAMMA_CONCRETO,
    LIMITE_SUPERIOR_ATRITO_LATERAL_KPA,
    PI_FRAC,
    TABELA_FATORES_ESTACAS,
    TABELA_SOLOS,
    TAXA_ARMADURA_LONGITUDINAL_MINIMA,
    FatoresTipoEstaca,
    ParametrosSolo,
)
from .models import (
    CamadaSoloSPT,
    DadosProjetoFundacaoProfunda,
    EfeitoGrupoEstacas,
    GeometriaEstaca,
    ResultadoCapacidadeMetodo,
    ResultadoEstruturalFuste,
    ResultadoProjetoFundacaoProfunda,
    SolicitacaoCarga,
    TipoProcessoExecutivo,
    TipoSecaoTransversal,
)
from .calculator import (
    calcular_capacidade_aoki_velloso,
    calcular_capacidade_decourt_quaresma,
    calcular_eficiencia_grupo,
    calcular_geometria_secao,
    calcular_verificacao_estrutural_fuste,
    dimensionar_projeto_fundacao_profunda,
    processar_perfil_estratigrafico,
)
from .codecs import (
    carregar_projeto_fundacao_json,
    codificar_json_projeto,
    decodificar_json_projeto,
    exportar_resultado_json,
)
from .exporters import (
    exportar_csv_resumo,
    exportar_memorial_descritivo,
    gerar_csv_resumo_fundacao,
    gerar_memorial_fundacao_texto,
    gerar_pacote_completo_zip,
    gerar_pacote_zip_fundacao,
)
from .svg_generator import gerar_painel_svg

__version__ = "1.0.0"
__author__ = "LOFRANO TECNOLOGIA"

__all__ = [
    "__version__",
    "__author__",
    # Constantes
    "PI_FRAC",
    "ParametrosSolo",
    "TABELA_SOLOS",
    "FatoresTipoEstaca",
    "TABELA_FATORES_ESTACAS",
    "FATOR_SEGURANCA_GEOTECNICO_COMPRESSAO",
    "FATOR_SEGURANCA_GEOTECNICO_COM_PROVA_CARGA",
    "FATOR_SEGURANCA_GEOTECNICO_TRACAO",
    "LIMITE_SUPERIOR_ATRITO_LATERAL_KPA",
    "GAMMA_CONCRETO",
    "GAMMA_ACO",
    "FYK_ACO_CA50_MPA",
    "TAXA_ARMADURA_LONGITUDINAL_MINIMA",
    "COEFICIENTE_RUDIGER_CONCRETO",
    # Modelos
    "TipoProcessoExecutivo",
    "TipoSecaoTransversal",
    "CamadaSoloSPT",
    "GeometriaEstaca",
    "SolicitacaoCarga",
    "EfeitoGrupoEstacas",
    "ResultadoCapacidadeMetodo",
    "ResultadoEstruturalFuste",
    "DadosProjetoFundacaoProfunda",
    "ResultadoProjetoFundacaoProfunda",
    # Calculadora
    "calcular_geometria_secao",
    "processar_perfil_estratigrafico",
    "calcular_capacidade_aoki_velloso",
    "calcular_capacidade_decourt_quaresma",
    "calcular_verificacao_estrutural_fuste",
    "calcular_eficiencia_grupo",
    "dimensionar_projeto_fundacao_profunda",
    # Codecs e exportadores
    "carregar_projeto_fundacao_json",
    "decodificar_json_projeto",
    "exportar_resultado_json",
    "codificar_json_projeto",
    "gerar_memorial_fundacao_texto",
    "exportar_memorial_descritivo",
    "gerar_csv_resumo_fundacao",
    "exportar_csv_resumo",
    "gerar_pacote_zip_fundacao",
    "gerar_pacote_completo_zip",
    "gerar_painel_svg",
]

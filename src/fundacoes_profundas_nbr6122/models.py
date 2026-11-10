"""Modelos de dados e estruturas tipadas para fundações profundas (NBR 6122:2022).

Todos os campos utilizam frações exatas (`fractions.Fraction`) e inteiros,
garantindo Zero-Float estrito.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction
from typing import Tuple


class TipoProcessoExecutivo(str, Enum):
    """Método ou tecnologia executiva de fundação profunda conforme NBR 6122."""
    ESTACA_FRANKI = "ESTACA_FRANKI"
    ESTACA_PRE_MOLDADA_CONCRETO = "ESTACA_PRE_MOLDADA_CONCRETO"
    ESTACA_HELICE_CONTINUA = "ESTACA_HELICE_CONTINUA"
    ESTACA_ESCAVADA_BENTONITA = "ESTACA_ESCAVADA_BENTONITA"
    ESTACA_ESCAVADA_SEM_FLUIDO = "ESTACA_ESCAVADA_SEM_FLUIDO"
    ESTACA_RAIZ = "ESTACA_RAIZ"
    ESTACA_METALICA = "ESTACA_METALICA"
    TUBULAO_A_CEU_ABERTO = "TUBULAO_A_CEU_ABERTO"


class TipoSecaoTransversal(str, Enum):
    """Geometria da seção transversal do fuste."""
    CIRCULAR = "CIRCULAR"
    QUADRADA = "QUADRADA"
    RETANGULAR = "RETANGULAR"


@dataclass(frozen=True)
class CamadaSoloSPT:
    """Estrato do perfil geotécnico com índice de resistência à penetração SPT."""
    profundidade_topo_m: Fraction
    profundidade_base_m: Fraction
    tipo_solo: str
    nspt_medio: int


@dataclass(frozen=True)
class GeometriaEstaca:
    """Parâmetros geométricos e de materiais da estaca ou tubulão."""
    tipo_secao: TipoSecaoTransversal
    diametro_ou_lado_m: Fraction
    comprimento_fuste_m: Fraction
    fck_concreto_mpa: Fraction = Fraction(30, 1)
    largura_b_m: Fraction = Fraction(0, 1)
    cota_arrasamento_m: Fraction = Fraction(0, 1)
    taxa_armadura_adotada: Fraction = Fraction(5, 1000)  # 0.5%


@dataclass(frozen=True)
class SolicitacaoCarga:
    """Ações e esforços característicos atuantes na cabeça da fundação."""
    forca_normal_compressao_kn: Fraction
    forca_tracao_kn: Fraction = Fraction(0, 1)
    momento_fletor_knm: Fraction = Fraction(0, 1)
    forca_horizontal_kn: Fraction = Fraction(0, 1)


@dataclass(frozen=True)
class EfeitoGrupoEstacas:
    """Parâmetros do bloco de coroamento e efeito de grupo."""
    numero_estacas_bloco: int = 1
    espacamento_entre_eixos_m: Fraction = Fraction(0, 1)


@dataclass(frozen=True)
class ResultadoCapacidadeMetodo:
    """Resultados de capacidade de carga para um método semiempírico específico."""
    metodo: str
    resistencia_ponta_kn: Fraction
    resistencia_lateral_kn: Fraction
    resistencia_total_ultima_kn: Fraction
    capacidade_admissivel_kn: Fraction


@dataclass(frozen=True)
class ResultadoEstruturalFuste:
    """Verificação estrutural do concreto e armadura conforme NBR 6118 / NBR 6122."""
    area_secao_concreto_m2: Fraction
    perimetro_fuste_m: Fraction
    resistencia_calculo_concreto_kpa: Fraction
    area_armadura_minima_cm2: Fraction
    area_armadura_adotada_cm2: Fraction
    forca_normal_admissivel_estrutural_kn: Fraction
    tensao_trabalho_concreto_kpa: Fraction
    aprovado_estruturalmente: bool


@dataclass(frozen=True)
class DadosProjetoFundacaoProfunda:
    """Dados de entrada consolidados do projeto de fundação profunda."""
    identificacao_projeto: str
    processo_executivo: TipoProcessoExecutivo
    geometria: GeometriaEstaca
    perfil_solo: Tuple[CamadaSoloSPT, ...]
    solicitacao: SolicitacaoCarga
    grupo: EfeitoGrupoEstacas = EfeitoGrupoEstacas()
    possui_prova_carga: bool = False
    responsavel_tecnico: str = "Engenharia Geotécnica"


@dataclass(frozen=True)
class ResultadoProjetoFundacaoProfunda:
    """Relatório e resultados consolidados do dimensionamento."""
    identificacao_projeto: str
    processo_executivo: TipoProcessoExecutivo
    geometria: GeometriaEstaca
    solicitacao: SolicitacaoCarga
    aoki_velloso: ResultadoCapacidadeMetodo
    decourt_quaresma: ResultadoCapacidadeMetodo
    capacidade_admissivel_adotada_kn: Fraction
    fator_seguranca_geotecnico_adotado: Fraction
    estrutural: ResultadoEstruturalFuste
    eficiencia_grupo: Fraction
    capacidade_admissivel_bloco_kn: Fraction
    aprovado_geotecnicamente: bool
    conformidade_geral: bool
    alertas_tecnicos: Tuple[str, ...]

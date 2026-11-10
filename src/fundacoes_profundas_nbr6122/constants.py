"""Constantes geotécnicas e parâmetros normativos conforme ABNT NBR 6122:2022 e NBR 6118:2023.

Aritmética 100% exata com frações racionais (fractions.Fraction) e inteiros,
garantindo Zero-Float estrito em todas as grandezas mecânicas, tensões e capacidades.
"""

from fractions import Fraction
from typing import NamedTuple


# Aproximação racional de pi de alta precisão (355/113 ~= 3.14159292...)
PI_FRAC = Fraction(355, 113)

# 1. Coeficientes Geotécnicos de Solos (Métodos Aoki-Velloso e Décourt-Quaresma)
class ParametrosSolo(NamedTuple):
    """Parâmetros semiempíricos de resistência de solos para fundações profundas."""
    nome: str
    k_aoki_velloso_kpa: Fraction      # K em kPa (Aoki-Velloso)
    alpha_aoki_velloso: Fraction      # alpha lateral (Aoki-Velloso)
    c_decourt_quaresma_kpa: Fraction  # C de ponta em kPa (Décourt-Quaresma)


TABELA_SOLOS = {
    "AREIA": ParametrosSolo(
        nome="Areia",
        k_aoki_velloso_kpa=Fraction(1000, 1),   # 1.0 MPa
        alpha_aoki_velloso=Fraction(14, 1000),  # 1.4%
        c_decourt_quaresma_kpa=Fraction(200, 1),# 200 kPa
    ),
    "AREIA_SILTOSA": ParametrosSolo(
        nome="Areia Siltosa",
        k_aoki_velloso_kpa=Fraction(800, 1),    # 0.8 MPa
        alpha_aoki_velloso=Fraction(20, 1000),  # 2.0%
        c_decourt_quaresma_kpa=Fraction(150, 1),# 150 kPa
    ),
    "AREIA_ARGILOSA": ParametrosSolo(
        nome="Areia Argilosa",
        k_aoki_velloso_kpa=Fraction(600, 1),    # 0.6 MPa
        alpha_aoki_velloso=Fraction(30, 1000),  # 3.0%
        c_decourt_quaresma_kpa=Fraction(130, 1),# 130 kPa
    ),
    "SILTE": ParametrosSolo(
        nome="Silte",
        k_aoki_velloso_kpa=Fraction(400, 1),    # 0.4 MPa
        alpha_aoki_velloso=Fraction(30, 1000),  # 3.0%
        c_decourt_quaresma_kpa=Fraction(120, 1),# 120 kPa
    ),
    "SILTE_ARENOSO": ParametrosSolo(
        nome="Silte Arenoso",
        k_aoki_velloso_kpa=Fraction(500, 1),    # 0.5 MPa
        alpha_aoki_velloso=Fraction(24, 1000),  # 2.4%
        c_decourt_quaresma_kpa=Fraction(120, 1),# 120 kPa
    ),
    "SILTE_ARGILOSO": ParametrosSolo(
        nome="Silte Argiloso",
        k_aoki_velloso_kpa=Fraction(300, 1),    # 0.3 MPa
        alpha_aoki_velloso=Fraction(28, 1000),  # 2.8%
        c_decourt_quaresma_kpa=Fraction(250, 1),# 250 kPa
    ),
    "ARGILA": ParametrosSolo(
        nome="Argila",
        k_aoki_velloso_kpa=Fraction(200, 1),    # 0.2 MPa
        alpha_aoki_velloso=Fraction(60, 1000),  # 6.0%
        c_decourt_quaresma_kpa=Fraction(400, 1),# 400 kPa
    ),
    "ARGILA_ARENOSA": ParametrosSolo(
        nome="Argila Arenosa",
        k_aoki_velloso_kpa=Fraction(350, 1),    # 0.35 MPa
        alpha_aoki_velloso=Fraction(24, 1000),  # 2.4%
        c_decourt_quaresma_kpa=Fraction(300, 1),# 300 kPa
    ),
    "ARGILA_SILTOSA": ParametrosSolo(
        nome="Argila Siltosa",
        k_aoki_velloso_kpa=Fraction(250, 1),    # 0.25 MPa
        alpha_aoki_velloso=Fraction(30, 1000),  # 3.0%
        c_decourt_quaresma_kpa=Fraction(350, 1),# 350 kPa
    ),
}


# 2. Fatores Executivos de Estacas (Aoki-Velloso F1/F2 e Décourt-Quaresma alfa/beta)
class FatoresTipoEstaca(NamedTuple):
    """Fatores de redução e ponderação conforme processo executivo da estaca."""
    nome: str
    f1_aoki: Fraction      # F1 ponta (Aoki-Velloso)
    f2_aoki: Fraction      # F2 lateral (Aoki-Velloso)
    alpha_decourt: Fraction# alpha ponta (Décourt-Quaresma)
    beta_decourt: Fraction # beta lateral (Décourt-Quaresma)


TABELA_FATORES_ESTACAS = {
    "ESTACA_FRANKI": FatoresTipoEstaca(
        nome="Estaca Franki",
        f1_aoki=Fraction(5, 2),        # 2.50
        f2_aoki=Fraction(5, 1),        # 5.00
        alpha_decourt=Fraction(1, 1),  # 1.00
        beta_decourt=Fraction(1, 1),   # 1.00
    ),
    "ESTACA_PRE_MOLDADA_CONCRETO": FatoresTipoEstaca(
        nome="Estaca Pré-moldada de Concreto",
        f1_aoki=Fraction(7, 4),        # 1.75
        f2_aoki=Fraction(7, 2),        # 3.50
        alpha_decourt=Fraction(1, 1),  # 1.00
        beta_decourt=Fraction(1, 1),   # 1.00
    ),
    "ESTACA_HELICE_CONTINUA": FatoresTipoEstaca(
        nome="Estaca Hélice Contínua Monitorada",
        f1_aoki=Fraction(2, 1),        # 2.00
        f2_aoki=Fraction(4, 1),        # 4.00
        alpha_decourt=Fraction(3, 10), # 0.30
        beta_decourt=Fraction(1, 1),   # 1.00
    ),
    "ESTACA_ESCAVADA_BENTONITA": FatoresTipoEstaca(
        nome="Estaca Escavada com Fluido Estabilizante",
        f1_aoki=Fraction(3, 1),        # 3.00
        f2_aoki=Fraction(6, 1),        # 6.00
        alpha_decourt=Fraction(1, 2),  # 0.50
        beta_decourt=Fraction(4, 5),   # 0.80
    ),
    "ESTACA_ESCAVADA_SEM_FLUIDO": FatoresTipoEstaca(
        nome="Estaca Escavada a Trado (Sem Fluido)",
        f1_aoki=Fraction(7, 2),        # 3.50
        f2_aoki=Fraction(7, 1),        # 7.00
        alpha_decourt=Fraction(1, 2),  # 0.50
        beta_decourt=Fraction(13, 20), # 0.65
    ),
    "ESTACA_RAIZ": FatoresTipoEstaca(
        nome="Estaca Raiz Injetada",
        f1_aoki=Fraction(3, 2),        # 1.50
        f2_aoki=Fraction(3, 1),        # 3.00
        alpha_decourt=Fraction(1, 1),  # 1.00
        beta_decourt=Fraction(3, 2),   # 1.50
    ),
    "ESTACA_METALICA": FatoresTipoEstaca(
        nome="Estaca Metálica (Perfil / Tubo)",
        f1_aoki=Fraction(7, 4),        # 1.75
        f2_aoki=Fraction(7, 2),        # 3.50
        alpha_decourt=Fraction(1, 1),  # 1.00
        beta_decourt=Fraction(1, 1),   # 1.00
    ),
    "TUBULAO_A_CEU_ABERTO": FatoresTipoEstaca(
        nome="Tubulão a Céu Aberto",
        f1_aoki=Fraction(3, 1),        # 3.00
        f2_aoki=Fraction(6, 1),        # 6.00 (despreza fuste se revestido)
        alpha_decourt=Fraction(1, 2),  # 0.50
        beta_decourt=Fraction(1, 2),   # 0.50
    ),
}

# 3. Fatores de Segurança Normativos conforme Tabela 4 da NBR 6122:2022
FATOR_SEGURANCA_GEOTECNICO_COMPRESSAO = Fraction(2, 1)        # FS = 2.0 (sem prova de carga)
FATOR_SEGURANCA_GEOTECNICO_COM_PROVA_CARGA = Fraction(8, 5)   # FS = 1.6 (com prova de carga)
FATOR_SEGURANCA_GEOTECNICO_TRACAO = Fraction(5, 2)            # FS = 2.5 (arrancamento)

# Limite normativo máximo para atrito lateral médio no Décourt-Quaresma (kPa)
LIMITE_SUPERIOR_ATRITO_LATERAL_KPA = Fraction(120, 1)         # 120 kPa

# 4. Parâmetros Estruturais de Concreto (NBR 6118:2023 / NBR 6122:2022)
GAMMA_CONCRETO = Fraction(14, 10)                             # gamma_c = 1.40
GAMMA_ACO = Fraction(115, 100)                                # gamma_s = 1.15
FYK_ACO_CA50_MPA = Fraction(500, 1)                           # 500 MPa = 500.000 kPa
TAXA_ARMADURA_LONGITUDINAL_MINIMA = Fraction(4, 1000)         # 0.4% da área de concreto
COEFICIENTE_RUDIGER_CONCRETO = Fraction(85, 100)              # 0.85

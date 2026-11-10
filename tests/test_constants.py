"""Testes unitários para as constantes geotécnicas da NBR 6122:2022."""

from fractions import Fraction
import unittest

from fundacoes_profundas_nbr6122.constants import (
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
)


class TestConstantes(unittest.TestCase):
    def test_solos_cadastrados(self):
        solos_esperados = {
            "AREIA", "AREIA_SILTOSA", "AREIA_ARGILOSA",
            "SILTE", "SILTE_ARENOSO", "SILTE_ARGILOSO",
            "ARGILA", "ARGILA_ARENOSA", "ARGILA_SILTOSA"
        }
        self.assertEqual(set(TABELA_SOLOS.keys()), solos_esperados)

    def test_parametros_solo_areia(self):
        s = TABELA_SOLOS["AREIA"]
        self.assertEqual(s.k_aoki_velloso_kpa, Fraction(1000, 1))
        self.assertEqual(s.alpha_aoki_velloso, Fraction(14, 1000))
        self.assertEqual(s.c_decourt_quaresma_kpa, Fraction(200, 1))

    def test_parametros_solo_argila(self):
        s = TABELA_SOLOS["ARGILA"]
        self.assertEqual(s.k_aoki_velloso_kpa, Fraction(200, 1))
        self.assertEqual(s.alpha_aoki_velloso, Fraction(60, 1000))
        self.assertEqual(s.c_decourt_quaresma_kpa, Fraction(400, 1))

    def test_processos_executivos_cadastrados(self):
        processos_esperados = {
            "ESTACA_FRANKI", "ESTACA_PRE_MOLDADA_CONCRETO", "ESTACA_HELICE_CONTINUA",
            "ESTACA_ESCAVADA_BENTONITA", "ESTACA_ESCAVADA_SEM_FLUIDO",
            "ESTACA_RAIZ", "ESTACA_METALICA", "TUBULAO_A_CEU_ABERTO"
        }
        self.assertEqual(set(TABELA_FATORES_ESTACAS.keys()), processos_esperados)

    def test_fatores_helice_continua(self):
        f = TABELA_FATORES_ESTACAS["ESTACA_HELICE_CONTINUA"]
        self.assertEqual(f.f1_aoki, Fraction(2, 1))
        self.assertEqual(f.f2_aoki, Fraction(4, 1))
        self.assertEqual(f.alpha_decourt, Fraction(3, 10))
        self.assertEqual(f.beta_decourt, Fraction(1, 1))

    def test_fatores_seguranca_geotecnicos(self):
        self.assertEqual(FATOR_SEGURANCA_GEOTECNICO_COMPRESSAO, Fraction(2, 1))
        self.assertEqual(FATOR_SEGURANCA_GEOTECNICO_COM_PROVA_CARGA, Fraction(8, 5))
        self.assertEqual(FATOR_SEGURANCA_GEOTECNICO_TRACAO, Fraction(5, 2))

    def test_fatores_estruturais_concreto_e_aco(self):
        self.assertEqual(GAMMA_CONCRETO, Fraction(14, 10))
        self.assertEqual(GAMMA_ACO, Fraction(115, 100))
        self.assertEqual(FYK_ACO_CA50_MPA, Fraction(500, 1))
        self.assertEqual(TAXA_ARMADURA_LONGITUDINAL_MINIMA, Fraction(4, 1000))
        self.assertEqual(COEFICIENTE_RUDIGER_CONCRETO, Fraction(85, 100))

    def test_pi_racional_precisao(self):
        self.assertEqual(PI_FRAC, Fraction(355, 113))
        # Diferença absoluta menor que 3e-7 em relação a 3.14159265
        diff = abs(float(PI_FRAC) - 3.1415926535)
        self.assertLess(diff, 1e-6)


if __name__ == "__main__":
    unittest.main()

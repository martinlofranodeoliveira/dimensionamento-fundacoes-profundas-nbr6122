"""Testes unitários para as estruturas de dados e modelos tipados."""

from fractions import Fraction
import unittest

from fundacoes_profundas_nbr6122.models import (
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


class TestModelos(unittest.TestCase):
    def test_enums_processo_executivo(self):
        self.assertEqual(TipoProcessoExecutivo.ESTACA_HELICE_CONTINUA.value, "ESTACA_HELICE_CONTINUA")
        self.assertEqual(TipoProcessoExecutivo.ESTACA_PRE_MOLDADA_CONCRETO.value, "ESTACA_PRE_MOLDADA_CONCRETO")
        self.assertEqual(TipoProcessoExecutivo.TUBULAO_A_CEU_ABERTO.value, "TUBULAO_A_CEU_ABERTO")

    def test_enums_tipo_secao(self):
        self.assertEqual(TipoSecaoTransversal.CIRCULAR.value, "CIRCULAR")
        self.assertEqual(TipoSecaoTransversal.QUADRADA.value, "QUADRADA")
        self.assertEqual(TipoSecaoTransversal.RETANGULAR.value, "RETANGULAR")

    def test_camada_solo_spt(self):
        c = CamadaSoloSPT(
            profundidade_topo_m=Fraction(0, 1),
            profundidade_base_m=Fraction(4, 1),
            tipo_solo="AREIA_SILTOSA",
            nspt_medio=12,
        )
        self.assertEqual(c.profundidade_topo_m, Fraction(0, 1))
        self.assertEqual(c.profundidade_base_m, Fraction(4, 1))
        self.assertEqual(c.nspt_medio, 12)

    def test_geometria_estaca(self):
        g = GeometriaEstaca(
            tipo_secao=TipoSecaoTransversal.CIRCULAR,
            diametro_ou_lado_m=Fraction(1, 2),
            comprimento_fuste_m=Fraction(12, 1),
            fck_concreto_mpa=Fraction(30, 1),
        )
        self.assertEqual(g.diametro_ou_lado_m, Fraction(1, 2))
        self.assertEqual(g.comprimento_fuste_m, Fraction(12, 1))

    def test_solicitacao_carga(self):
        s = SolicitacaoCarga(
            forca_normal_compressao_kn=Fraction(750, 1),
            forca_tracao_kn=Fraction(50, 1),
            momento_fletor_knm=Fraction(25, 1),
            forca_horizontal_kn=Fraction(15, 1),
        )
        self.assertEqual(s.forca_normal_compressao_kn, Fraction(750, 1))
        self.assertEqual(s.forca_tracao_kn, Fraction(50, 1))

    def test_resultado_capacidade_metodo(self):
        res = ResultadoCapacidadeMetodo(
            metodo="Aoki-Velloso",
            resistencia_ponta_kn=Fraction(300, 1),
            resistencia_lateral_kn=Fraction(700, 1),
            resistencia_total_ultima_kn=Fraction(1000, 1),
            capacidade_admissivel_kn=Fraction(500, 1),
        )
        self.assertEqual(res.resistencia_total_ultima_kn, Fraction(1000, 1))
        self.assertEqual(res.capacidade_admissivel_kn, Fraction(500, 1))

    def test_resultado_estrutural_fuste(self):
        est = ResultadoEstruturalFuste(
            area_secao_concreto_m2=Fraction(1, 5),
            perimetro_fuste_m=Fraction(8, 5),
            resistencia_calculo_concreto_kpa=Fraction(21428, 1),
            area_armadura_minima_cm2=Fraction(8, 1),
            area_armadura_adotada_cm2=Fraction(10, 1),
            forca_normal_admissivel_estrutural_kn=Fraction(2500, 1),
            tensao_trabalho_concreto_kpa=Fraction(3500, 1),
            aprovado_estruturalmente=True,
        )
        self.assertTrue(est.aprovado_estruturalmente)
        self.assertEqual(est.area_secao_concreto_m2, Fraction(1, 5))


if __name__ == "__main__":
    unittest.main()

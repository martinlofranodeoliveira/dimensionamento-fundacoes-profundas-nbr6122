"""Testes unitários do motor de cálculo geotécnico e estrutural NBR 6122 / NBR 6118."""

import unittest
from fractions import Fraction

from fundacoes_profundas_nbr6122.calculator import (
    calcular_capacidade_aoki_velloso,
    calcular_capacidade_decourt_quaresma,
    calcular_eficiencia_grupo,
    calcular_geometria_secao,
    calcular_verificacao_estrutural_fuste,
    dimensionar_projeto_fundacao_profunda,
    processar_perfil_estratigrafico,
)
from fundacoes_profundas_nbr6122.constants import (
    FATOR_SEGURANCA_GEOTECNICO_COM_PROVA_CARGA,
    FATOR_SEGURANCA_GEOTECNICO_COMPRESSAO,
    TABELA_FATORES_ESTACAS,
    TABELA_SOLOS,
)
from fundacoes_profundas_nbr6122.models import (
    CamadaSoloSPT,
    DadosProjetoFundacaoProfunda,
    EfeitoGrupoEstacas,
    GeometriaEstaca,
    SolicitacaoCarga,
    TipoProcessoExecutivo,
    TipoSecaoTransversal,
)


class TestCalculator(unittest.TestCase):
    """Testes exatos do motor de cálculo determinístico e analítico."""

    def test_geometria_secao_circular(self):
        geo = GeometriaEstaca(
            tipo_secao=TipoSecaoTransversal.CIRCULAR,
            diametro_ou_lado_m=Fraction(1, 2),  # 0.5m
            comprimento_fuste_m=Fraction(12, 1),
            fck_concreto_mpa=Fraction(30, 1),
        )
        area, perimetro = calcular_geometria_secao(geo)
        # r = 0.25 = 1/4 m -> Area = (355/113) * (1/16) = 355/1808 m²
        self.assertEqual(area, Fraction(355, 1808))
        # Perímetro = 2 * (355/113) * (1/4) = 355/226 m
        self.assertEqual(perimetro, Fraction(355, 226))

    def test_geometria_secao_quadrada(self):
        geo = GeometriaEstaca(
            tipo_secao=TipoSecaoTransversal.QUADRADA,
            diametro_ou_lado_m=Fraction(7, 20),  # 0.35m
            comprimento_fuste_m=Fraction(10, 1),
            fck_concreto_mpa=Fraction(35, 1),
        )
        area, perimetro = calcular_geometria_secao(geo)
        self.assertEqual(area, Fraction(49, 400))
        self.assertEqual(perimetro, Fraction(7, 5))

    def test_geometria_secao_retangular(self):
        geo = GeometriaEstaca(
            tipo_secao=TipoSecaoTransversal.RETANGULAR,
            diametro_ou_lado_m=Fraction(2, 5),  # 0.40m
            largura_b_m=Fraction(3, 5),         # 0.60m
            comprimento_fuste_m=Fraction(10, 1),
            fck_concreto_mpa=Fraction(25, 1),
        )
        area, perimetro = calcular_geometria_secao(geo)
        self.assertEqual(area, Fraction(6, 25))
        self.assertEqual(perimetro, Fraction(2, 1))

    def test_geometria_dimensao_invalida(self):
        geo = GeometriaEstaca(
            tipo_secao=TipoSecaoTransversal.CIRCULAR,
            diametro_ou_lado_m=Fraction(0, 1),
            comprimento_fuste_m=Fraction(10, 1),
            fck_concreto_mpa=Fraction(25, 1),
        )
        with self.assertRaises(ValueError):
            calcular_geometria_secao(geo)

    def test_processar_perfil_estratigrafico(self):
        perfil = (
            CamadaSoloSPT(Fraction(0, 1), Fraction(4, 1), "ARGILA_SILTOSA", 5),
            CamadaSoloSPT(Fraction(4, 1), Fraction(10, 1), "SILTE_ARENOSO", 12),
            CamadaSoloSPT(Fraction(10, 1), Fraction(18, 1), "AREIA", 25),
        )
        trechos, solo_ponta, nspt_ponta = processar_perfil_estratigrafico(
            perfil=perfil,
            cota_topo=Fraction(0, 1),
            comprimento_fuste=Fraction(12, 1),
        )
        # Deve ter 3 trechos: [0-4], [4-10], [10-12]
        self.assertEqual(len(trechos), 3)
        self.assertEqual(trechos[0][2], Fraction(4, 1))
        self.assertEqual(trechos[1][2], Fraction(6, 1))
        self.assertEqual(trechos[2][2], Fraction(2, 1))
        # Ponta aos 12m está na camada AREIA
        self.assertEqual(solo_ponta.nome, "Areia")
        self.assertEqual(nspt_ponta, 25)

    def test_processar_perfil_com_fuste_alem_da_base(self):
        perfil = (
            CamadaSoloSPT(Fraction(0, 1), Fraction(5, 1), "ARGILA", 4),
            CamadaSoloSPT(Fraction(5, 1), Fraction(10, 1), "AREIA", 20),
        )
        # Fuste de 15m (ultrapassa a base do perfil aos 10m)
        trechos, solo_ponta, nspt_ponta = processar_perfil_estratigrafico(
            perfil=perfil,
            cota_topo=Fraction(0, 1),
            comprimento_fuste=Fraction(15, 1),
        )
        self.assertEqual(len(trechos), 2)
        self.assertEqual(solo_ponta.nome, "Areia")
        self.assertEqual(nspt_ponta, 20)

    def test_processar_perfil_erros(self):
        with self.assertRaises(ValueError):
            processar_perfil_estratigrafico(
                perfil=(),
                cota_topo=Fraction(0, 1),
                comprimento_fuste=Fraction(10, 1),
            )
        perfil = (CamadaSoloSPT(Fraction(0, 1), Fraction(5, 1), "AREIA", 10),)
        with self.assertRaises(ValueError):
            processar_perfil_estratigrafico(
                perfil=perfil,
                cota_topo=Fraction(0, 1),
                comprimento_fuste=Fraction(0, 1),
            )

    def test_capacidade_aoki_velloso(self):
        fatores = TABELA_FATORES_ESTACAS["ESTACA_HELICE_CONTINUA"]
        area_ponta = Fraction(1, 5)
        perimetro = Fraction(8, 5)
        trechos = [
            (TABELA_SOLOS["ARGILA"], 6, Fraction(5, 1)),
            (TABELA_SOLOS["AREIA"], 20, Fraction(5, 1)),
        ]
        solo_ponta = TABELA_SOLOS["AREIA"]
        nspt_ponta = 25
        fs_geo = FATOR_SEGURANCA_GEOTECNICO_COMPRESSAO  # 2.0

        res = calcular_capacidade_aoki_velloso(
            fatores=fatores,
            area_ponta_m2=area_ponta,
            perimetro_m=perimetro,
            trechos_fuste=trechos,
            camada_ponta=solo_ponta,
            nspt_ponta=nspt_ponta,
            fs_geotecnico=fs_geo,
        )
        self.assertGreater(res.resistencia_ponta_kn, Fraction(0, 1))
        self.assertGreater(res.resistencia_lateral_kn, Fraction(0, 1))
        self.assertEqual(res.resistencia_total_ultima_kn, res.resistencia_ponta_kn + res.resistencia_lateral_kn)
        self.assertEqual(res.capacidade_admissivel_kn, res.resistencia_total_ultima_kn / fs_geo)

    def test_capacidade_decourt_quaresma(self):
        fatores = TABELA_FATORES_ESTACAS["ESTACA_HELICE_CONTINUA"]
        area_ponta = Fraction(1, 5)
        perimetro = Fraction(8, 5)
        trechos = [
            (TABELA_SOLOS["ARGILA"], 6, Fraction(5, 1)),
            (TABELA_SOLOS["AREIA"], 20, Fraction(5, 1)),
        ]
        solo_ponta = TABELA_SOLOS["AREIA"]
        nspt_ponta = 25
        fs_geo = FATOR_SEGURANCA_GEOTECNICO_COMPRESSAO

        res = calcular_capacidade_decourt_quaresma(
            fatores=fatores,
            area_ponta_m2=area_ponta,
            perimetro_m=perimetro,
            trechos_fuste=trechos,
            camada_ponta=solo_ponta,
            nspt_ponta=nspt_ponta,
            fs_geotecnico=fs_geo,
        )
        self.assertGreater(res.resistencia_ponta_kn, Fraction(0, 1))
        self.assertGreater(res.resistencia_lateral_kn, Fraction(0, 1))
        self.assertEqual(res.resistencia_total_ultima_kn, res.resistencia_ponta_kn + res.resistencia_lateral_kn)
        self.assertEqual(res.capacidade_admissivel_kn, res.resistencia_total_ultima_kn / fs_geo)

    def test_verificacao_estrutural_fuste_aprovado(self):
        geo = GeometriaEstaca(
            tipo_secao=TipoSecaoTransversal.CIRCULAR,
            diametro_ou_lado_m=Fraction(1, 2),  # 50cm
            comprimento_fuste_m=Fraction(12, 1),
            fck_concreto_mpa=Fraction(30, 1),
            taxa_armadura_adotada=Fraction(5, 1000),  # 0.5%
        )
        area, perimetro = calcular_geometria_secao(geo)
        res = calcular_verificacao_estrutural_fuste(
            geometria=geo,
            processo=TipoProcessoExecutivo.ESTACA_HELICE_CONTINUA,
            area_concreto_m2=area,
            perimetro_m=perimetro,
            forca_normal_atuante_kn=Fraction(800, 1),
        )
        self.assertTrue(res.aprovado_estruturalmente)
        self.assertGreater(res.forca_normal_admissivel_estrutural_kn, Fraction(800, 1))
        self.assertGreater(res.area_armadura_adotada_cm2, Fraction(0, 1))

    def test_verificacao_estrutural_fuste_reprovado_por_sobrecarga(self):
        geo = GeometriaEstaca(
            tipo_secao=TipoSecaoTransversal.CIRCULAR,
            diametro_ou_lado_m=Fraction(3, 10),  # 30cm
            comprimento_fuste_m=Fraction(10, 1),
            fck_concreto_mpa=Fraction(20, 1),
        )
        area, perimetro = calcular_geometria_secao(geo)
        res = calcular_verificacao_estrutural_fuste(
            geometria=geo,
            processo=TipoProcessoExecutivo.ESTACA_HELICE_CONTINUA,
            area_concreto_m2=area,
            perimetro_m=perimetro,
            forca_normal_atuante_kn=Fraction(5000, 1),  # Carga absurda
        )
        self.assertFalse(res.aprovado_estruturalmente)

    def test_eficiencia_grupo(self):
        d = Fraction(1, 2)  # 0.50m
        # n = 1 -> 1.00
        g1 = EfeitoGrupoEstacas(1, Fraction(0, 1))
        self.assertEqual(calcular_eficiencia_grupo(g1, d), Fraction(1, 1))

        # n = 4, s = 2.0m (4D >= 3D) -> 1.00
        g4_largo = EfeitoGrupoEstacas(4, Fraction(2, 1))
        self.assertEqual(calcular_eficiencia_grupo(g4_largo, d), Fraction(1, 1))

        # n = 4, s = 1.3m (2.6D: entre 2.5D e 3D) -> 0.90
        g4_medio = EfeitoGrupoEstacas(4, Fraction(13, 10))
        self.assertEqual(calcular_eficiencia_grupo(g4_medio, d), Fraction(9, 10))

        # n = 4, s = 1.1m (2.2D: entre 2.0D e 2.5D) -> 0.80
        g4_justo = EfeitoGrupoEstacas(4, Fraction(11, 10))
        self.assertEqual(calcular_eficiencia_grupo(g4_justo, d), Fraction(8, 10))

        # n = 4, s = 0.8m (< 2D) -> 0.70
        g4_critico = EfeitoGrupoEstacas(4, Fraction(4, 5))
        self.assertEqual(calcular_eficiencia_grupo(g4_critico, d), Fraction(7, 10))

    def test_dimensionar_projeto_completo(self):
        dados = DadosProjetoFundacaoProfunda(
            identificacao_projeto="Teste de Carga Edifício",
            processo_executivo=TipoProcessoExecutivo.ESTACA_HELICE_CONTINUA,
            geometria=GeometriaEstaca(
                tipo_secao=TipoSecaoTransversal.CIRCULAR,
                diametro_ou_lado_m=Fraction(1, 2),
                comprimento_fuste_m=Fraction(12, 1),
                fck_concreto_mpa=Fraction(30, 1),
            ),
            perfil_solo=(
                CamadaSoloSPT(Fraction(0, 1), Fraction(4, 1), "ARGILA_SILTOSA", 4),
                CamadaSoloSPT(Fraction(4, 1), Fraction(8, 1), "SILTE_ARENOSO", 8),
                CamadaSoloSPT(Fraction(8, 1), Fraction(14, 1), "AREIA", 22),
            ),
            solicitacao=SolicitacaoCarga(forca_normal_compressao_kn=Fraction(700, 1)),
            grupo=EfeitoGrupoEstacas(numero_estacas_bloco=1, espacamento_entre_eixos_m=Fraction(0, 1)),
            possui_prova_carga=False,
            responsavel_tecnico="Engenharia Lofrano",
        )
        res = dimensionar_projeto_fundacao_profunda(dados)
        self.assertEqual(res.identificacao_projeto, "Teste de Carga Edifício")
        self.assertIn("Aoki-Velloso", res.aoki_velloso.metodo)
        self.assertIn("Décourt-Quaresma", res.decourt_quaresma.metodo)
        self.assertEqual(res.fator_seguranca_geotecnico_adotado, Fraction(2, 1))
        self.assertEqual(
            res.capacidade_admissivel_adotada_kn,
            min(res.aoki_velloso.capacidade_admissivel_kn, res.decourt_quaresma.capacidade_admissivel_kn),
        )
        self.assertTrue(isinstance(res.conformidade_geral, bool))


if __name__ == "__main__":
    unittest.main()

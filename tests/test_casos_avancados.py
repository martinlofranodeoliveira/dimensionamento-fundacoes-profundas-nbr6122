"""Testes de casos geotécnicos avançados: estacas raiz, tubulões, prova de carga e grupos."""

import unittest
from fractions import Fraction

from fundacoes_profundas_nbr6122.calculator import (
    calcular_verificacao_estrutural_fuste,
    dimensionar_projeto_fundacao_profunda,
)
from fundacoes_profundas_nbr6122.constants import (
    FATOR_SEGURANCA_GEOTECNICO_COM_PROVA_CARGA,
    FATOR_SEGURANCA_GEOTECNICO_COMPRESSAO,
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


class TestCasosAvancados(unittest.TestCase):
    """Casos especiais e envoltórias complexas da ABNT NBR 6122:2022."""

    def test_estaca_raiz_com_fator_executivo_090(self):
        geo = GeometriaEstaca(
            tipo_secao=TipoSecaoTransversal.CIRCULAR,
            diametro_ou_lado_m=Fraction(31, 100),  # 31cm
            comprimento_fuste_m=Fraction(10, 1),
            fck_concreto_mpa=Fraction(30, 1),
            taxa_armadura_adotada=Fraction(1, 100),  # 1%
        )
        dados = DadosProjetoFundacaoProfunda(
            identificacao_projeto="Reforço de Fundação - Estaca Raiz",
            processo_executivo=TipoProcessoExecutivo.ESTACA_RAIZ,
            geometria=geo,
            perfil_solo=(
                CamadaSoloSPT(Fraction(0, 1), Fraction(5, 1), "ARGILA", 5),
                CamadaSoloSPT(Fraction(5, 1), Fraction(12, 1), "AREIA", 25),
            ),
            solicitacao=SolicitacaoCarga(forca_normal_compressao_kn=Fraction(350, 1)),
            grupo=EfeitoGrupoEstacas(numero_estacas_bloco=1, espacamento_entre_eixos_m=Fraction(0, 1)),
            possui_prova_carga=False,
            responsavel_tecnico="Eng. Lofrano",
        )
        res = dimensionar_projeto_fundacao_profunda(dados)
        self.assertEqual(res.processo_executivo, TipoProcessoExecutivo.ESTACA_RAIZ)
        self.assertTrue(res.aprovado_geotecnicamente)
        self.assertTrue(res.estrutural.aprovado_estruturalmente)
        self.assertTrue(res.conformidade_geral)

    def test_beneficio_prova_de_carga_fator_seguranca_1_6(self):
        # Projeto com prova de carga estática normatizada
        geo = GeometriaEstaca(
            tipo_secao=TipoSecaoTransversal.CIRCULAR,
            diametro_ou_lado_m=Fraction(1, 2),
            comprimento_fuste_m=Fraction(12, 1),
            fck_concreto_mpa=Fraction(30, 1),
        )
        perfil = (
            CamadaSoloSPT(Fraction(0, 1), Fraction(6, 1), "ARGILA_SILTOSA", 6),
            CamadaSoloSPT(Fraction(6, 1), Fraction(15, 1), "AREIA", 20),
        )
        # 1. Sem prova de carga (FS = 2.0)
        d_sem = DadosProjetoFundacaoProfunda(
            identificacao_projeto="Sem Prova de Carga",
            processo_executivo=TipoProcessoExecutivo.ESTACA_HELICE_CONTINUA,
            geometria=geo,
            perfil_solo=perfil,
            solicitacao=SolicitacaoCarga(forca_normal_compressao_kn=Fraction(700, 1)),
            grupo=EfeitoGrupoEstacas(1, Fraction(0, 1)),
            possui_prova_carga=False,
        )
        res_sem = dimensionar_projeto_fundacao_profunda(d_sem)

        # 2. Com prova de carga (FS = 1.6 = 8/5)
        d_com = DadosProjetoFundacaoProfunda(
            identificacao_projeto="Com Prova de Carga",
            processo_executivo=TipoProcessoExecutivo.ESTACA_HELICE_CONTINUA,
            geometria=geo,
            perfil_solo=perfil,
            solicitacao=SolicitacaoCarga(forca_normal_compressao_kn=Fraction(700, 1)),
            grupo=EfeitoGrupoEstacas(1, Fraction(0, 1)),
            possui_prova_carga=True,
        )
        res_com = dimensionar_projeto_fundacao_profunda(d_com)

        self.assertEqual(res_sem.fator_seguranca_geotecnico_adotado, FATOR_SEGURANCA_GEOTECNICO_COMPRESSAO)
        self.assertEqual(res_com.fator_seguranca_geotecnico_adotado, FATOR_SEGURANCA_GEOTECNICO_COM_PROVA_CARGA)
        # Capacidade admissível com prova de carga deve ser 25% maior (2.0 / 1.6 = 1.25)
        self.assertGreater(res_com.capacidade_admissivel_adotada_kn, res_sem.capacidade_admissivel_adotada_kn)
        self.assertEqual(
            res_com.capacidade_admissivel_adotada_kn * Fraction(16, 10),
            res_sem.capacidade_admissivel_adotada_kn * Fraction(20, 10),
        )

    def test_alerta_ponta_em_solo_mole(self):
        # Ponta de estaca terminando em camada com N_SPT < 5
        geo = GeometriaEstaca(
            tipo_secao=TipoSecaoTransversal.CIRCULAR,
            diametro_ou_lado_m=Fraction(2, 5),
            comprimento_fuste_m=Fraction(5, 1),
            fck_concreto_mpa=Fraction(25, 1),
        )
        perfil = (
            CamadaSoloSPT(Fraction(0, 1), Fraction(10, 1), "ARGILA_MOLE", 3),
        )
        dados = DadosProjetoFundacaoProfunda(
            identificacao_projeto="Estaca em Solo Mole",
            processo_executivo=TipoProcessoExecutivo.ESTACA_ESCAVADA_SEM_FLUIDO,
            geometria=geo,
            perfil_solo=perfil,
            solicitacao=SolicitacaoCarga(forca_normal_compressao_kn=Fraction(200, 1)),
            grupo=EfeitoGrupoEstacas(1, Fraction(0, 1)),
            possui_prova_carga=False,
        )
        res = dimensionar_projeto_fundacao_profunda(dados)
        self.assertTrue(any("N_SPT na cota de ponta é baixo" in alerta for alerta in res.alertas_tecnicos))

    def test_alerta_espacamento_reduzido_bloco(self):
        # Bloco de 3 estacas com s = 1.0m quando D = 0.50m (s = 2.0D < 2.5D)
        geo = GeometriaEstaca(
            tipo_secao=TipoSecaoTransversal.CIRCULAR,
            diametro_ou_lado_m=Fraction(1, 2),  # 0.50m -> 2.5D = 1.25m
            comprimento_fuste_m=Fraction(10, 1),
            fck_concreto_mpa=Fraction(30, 1),
        )
        perfil = (
            CamadaSoloSPT(Fraction(0, 1), Fraction(12, 1), "AREIA", 20),
        )
        dados = DadosProjetoFundacaoProfunda(
            identificacao_projeto="Bloco de 3 Estacas Justas",
            processo_executivo=TipoProcessoExecutivo.ESTACA_HELICE_CONTINUA,
            geometria=geo,
            perfil_solo=perfil,
            solicitacao=SolicitacaoCarga(forca_normal_compressao_kn=Fraction(1000, 1)),
            grupo=EfeitoGrupoEstacas(3, Fraction(1, 1)),  # s = 1.0m < 1.25m
            possui_prova_carga=False,
        )
        res = dimensionar_projeto_fundacao_profunda(dados)
        self.assertTrue(any("Espaçamento entre estacas inferior ao mínimo recomendado" in a for a in res.alertas_tecnicos))
        self.assertEqual(res.eficiencia_grupo, Fraction(8, 10))


if __name__ == "__main__":
    unittest.main()

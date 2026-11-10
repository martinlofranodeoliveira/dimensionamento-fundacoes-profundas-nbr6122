"""Testes unitários do gerador vetorial SVG para fundações profundas NBR 6122."""

import unittest
from fractions import Fraction
import xml.etree.ElementTree as ET

from fundacoes_profundas_nbr6122.calculator import dimensionar_projeto_fundacao_profunda
from fundacoes_profundas_nbr6122.models import (
    CamadaSoloSPT,
    DadosProjetoFundacaoProfunda,
    EfeitoGrupoEstacas,
    GeometriaEstaca,
    SolicitacaoCarga,
    TipoProcessoExecutivo,
    TipoSecaoTransversal,
)
from fundacoes_profundas_nbr6122.svg_generator import gerar_painel_svg


class TestSVGGenerator(unittest.TestCase):
    """Testa a conformidade do SVG gerado no padrão visual 1440x900."""

    def setUp(self):
        self.dados_conforme = DadosProjetoFundacaoProfunda(
            identificacao_projeto="Ponte Estaiada - Pilar Central",
            processo_executivo=TipoProcessoExecutivo.ESTACA_HELICE_CONTINUA,
            geometria=GeometriaEstaca(
                tipo_secao=TipoSecaoTransversal.CIRCULAR,
                diametro_ou_lado_m=Fraction(6, 10),  # 60cm
                comprimento_fuste_m=Fraction(15, 1),
                fck_concreto_mpa=Fraction(35, 1),
            ),
            perfil_solo=(
                CamadaSoloSPT(Fraction(0, 1), Fraction(5, 1), "ARGILA_SILTOSA", 6),
                CamadaSoloSPT(Fraction(5, 1), Fraction(10, 1), "SILTE_ARENOSO", 14),
                CamadaSoloSPT(Fraction(10, 1), Fraction(20, 1), "AREIA", 28),
            ),
            solicitacao=SolicitacaoCarga(forca_normal_compressao_kn=Fraction(900, 1)),
            grupo=EfeitoGrupoEstacas(numero_estacas_bloco=1, espacamento_entre_eixos_m=Fraction(0, 1)),
            possui_prova_carga=False,
            responsavel_tecnico="Eng. Martin Lofrano",
        )
        self.resultado_conforme = dimensionar_projeto_fundacao_profunda(self.dados_conforme)

    def test_gerar_svg_estrutura_e_dimensoes(self):
        svg_conteudo = gerar_painel_svg(self.resultado_conforme)
        self.assertIn('<svg xmlns="http://www.w3.org/2000/svg"', svg_conteudo)
        self.assertIn('viewBox="0 0 1440 900"', svg_conteudo)
        self.assertIn('width="1440"', svg_conteudo)
        self.assertIn('height="900"', svg_conteudo)
        self.assertIn("Ponte Estaiada - Pilar Central", svg_conteudo)
        self.assertIn("ABNT NBR 6122:2022", svg_conteudo)
        self.assertIn("CONFORME NBR 6122", svg_conteudo)

        # Valida conformidade XML bem-formado
        root = ET.fromstring(svg_conteudo)
        self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")

    def test_gerar_svg_projeto_com_pendencias(self):
        dados_pendencia = DadosProjetoFundacaoProfunda(
            identificacao_projeto="Pilar Sobrecarga Extrema",
            processo_executivo=TipoProcessoExecutivo.ESTACA_PRE_MOLDADA_CONCRETO,
            geometria=GeometriaEstaca(
                tipo_secao=TipoSecaoTransversal.QUADRADA,
                diametro_ou_lado_m=Fraction(1, 4),  # 25cm
                comprimento_fuste_m=Fraction(6, 1),
                fck_concreto_mpa=Fraction(25, 1),
            ),
            perfil_solo=(
                CamadaSoloSPT(Fraction(0, 1), Fraction(8, 1), "ARGILA_MOLE", 2),
            ),
            solicitacao=SolicitacaoCarga(forca_normal_compressao_kn=Fraction(3000, 1)),
            grupo=EfeitoGrupoEstacas(numero_estacas_bloco=1, espacamento_entre_eixos_m=Fraction(0, 1)),
            possui_prova_carga=False,
            responsavel_tecnico="Eng. Martin Lofrano",
        )
        res_pendencia = dimensionar_projeto_fundacao_profunda(dados_pendencia)
        svg_conteudo = gerar_painel_svg(res_pendencia)
        self.assertIn("PENDÊNCIAS TÉCNICAS", svg_conteudo)
        self.assertFalse(res_pendencia.conformidade_geral)


if __name__ == "__main__":
    unittest.main()

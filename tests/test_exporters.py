"""Testes unitários dos exportadores (Memorial Descritivo, CSV Sanitizado, Pacote ZIP)."""

import os
import tempfile
import unittest
import zipfile
from fractions import Fraction

from fundacoes_profundas_nbr6122.calculator import dimensionar_projeto_fundacao_profunda
from fundacoes_profundas_nbr6122.exporters import (
    _sanitizar_campo_csv,
    exportar_csv_resumo,
    exportar_memorial_descritivo,
    gerar_csv_resumo_fundacao,
    gerar_memorial_fundacao_texto,
    gerar_pacote_completo_zip,
    gerar_pacote_zip_fundacao,
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


class TestExporters(unittest.TestCase):
    """Testes dos exportadores técnicos conforme padrões de engenharia."""

    def setUp(self):
        self.dados = DadosProjetoFundacaoProfunda(
            identificacao_projeto="Edifício Lofrano Tower",
            processo_executivo=TipoProcessoExecutivo.ESTACA_HELICE_CONTINUA,
            geometria=GeometriaEstaca(
                tipo_secao=TipoSecaoTransversal.CIRCULAR,
                diametro_ou_lado_m=Fraction(1, 2),
                comprimento_fuste_m=Fraction(14, 1),
                fck_concreto_mpa=Fraction(30, 1),
            ),
            perfil_solo=(
                CamadaSoloSPT(Fraction(0, 1), Fraction(4, 1), "ARGILA_SILTOSA", 5),
                CamadaSoloSPT(Fraction(4, 1), Fraction(10, 1), "SILTE_ARENOSO", 12),
                CamadaSoloSPT(Fraction(10, 1), Fraction(16, 1), "AREIA", 25),
            ),
            solicitacao=SolicitacaoCarga(forca_normal_compressao_kn=Fraction(850, 1)),
            grupo=EfeitoGrupoEstacas(numero_estacas_bloco=1, espacamento_entre_eixos_m=Fraction(0, 1)),
            possui_prova_carga=False,
            responsavel_tecnico="Eng. Martin Lofrano",
        )
        self.resultado = dimensionar_projeto_fundacao_profunda(self.dados)

    def test_memorial_descritivo_texto(self):
        txt = gerar_memorial_fundacao_texto(self.resultado)
        self.assertIn("LOFRANO TECNOLOGIA", txt)
        self.assertIn("ABNT NBR 6122:2022", txt)
        self.assertIn("Edifício Lofrano Tower", txt)
        self.assertIn("ESTACA_HELICE_CONTINUA", txt)
        self.assertIn("AOKI-VELLOSO", txt)
        self.assertIn("DÉCOURT-QUARESMA", txt)

        # Teste alias
        txt_alias = exportar_memorial_descritivo(self.resultado)
        self.assertEqual(txt, txt_alias)

    def test_csv_resumo_e_sanitizacao(self):
        csv_txt = gerar_csv_resumo_fundacao(self.resultado)
        self.assertIn("modulo;parametro;valor;unidade;observacao", csv_txt)
        self.assertIn("GEOMETRIA", csv_txt)
        self.assertIn("GEOTECNIA_AOKI", csv_txt)
        self.assertIn("GEOTECNIA_DECOURT", csv_txt)
        self.assertIn("ESTRUTURAL_FUSTE", csv_txt)

        # Teste sanitização anti-fórmula
        self.assertEqual(_sanitizar_campo_csv("=SOMA(A1:A10)"), "'=SOMA(A1:A10)")
        self.assertEqual(_sanitizar_campo_csv("+123"), "'+123")
        self.assertEqual(_sanitizar_campo_csv("-456"), "'-456")
        self.assertEqual(_sanitizar_campo_csv("@cmd"), "'@cmd")
        self.assertEqual(_sanitizar_campo_csv("\ttab"), "'\ttab")
        self.assertEqual(_sanitizar_campo_csv("Texto normal"), "Texto normal")

        # Teste alias
        csv_alias = exportar_csv_resumo(self.resultado)
        self.assertEqual(csv_txt, csv_alias)

    def test_pacote_zip_determinista(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = os.path.join(tmpdir, "pacote_teste.zip")
            svg_conteudo = "<svg><rect width='100' height='100'/></svg>"
            gerar_pacote_zip_fundacao(self.resultado, zip_path, svg_conteudo=svg_conteudo)

            self.assertTrue(os.path.exists(zip_path))
            with zipfile.ZipFile(zip_path, "r") as zf:
                nomes = zf.namelist()
                self.assertIn("memorial_fundacao_profunda.txt", nomes)
                self.assertIn("dados_fundacao_profunda.json", nomes)
                self.assertIn("resumo_fundacao_profunda.csv", nomes)
                self.assertIn("painel_fundacao_profunda.svg", nomes)

                # Verifica timestamp determinístico (2026, 1, 1, 0, 0, 0)
                for info in zf.infolist():
                    self.assertEqual(info.date_time, (2026, 1, 1, 0, 0, 0))

            # Verifica proteção O_EXCL contra sobrescrita
            with self.assertRaises(FileExistsError):
                gerar_pacote_zip_fundacao(self.resultado, zip_path)

    def test_pacote_zip_alias(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = os.path.join(tmpdir, "pacote_alias.zip")
            gerar_pacote_completo_zip(self.resultado, zip_path)
            self.assertTrue(os.path.exists(zip_path))


if __name__ == "__main__":
    unittest.main()

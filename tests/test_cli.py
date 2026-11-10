"""Testes unitários da interface de linha de comando (CLI) fundacoes-profundas-nbr6122."""

import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

from fundacoes_profundas_nbr6122.cli import main


class TestCLI(unittest.TestCase):
    """Testa a robustez, subcomandos e tratamento de erros da CLI."""

    def executar_cli(self, args: list[str]) -> tuple[int, str, str]:
        out_buf = io.StringIO()
        err_buf = io.StringIO()
        codigo = 0
        antigo_argv = sys.argv
        sys.argv = ["fundacoes-profundas-nbr6122"] + args
        try:
            with redirect_stdout(out_buf), redirect_stderr(err_buf):
                try:
                    res = main(args)
                    if isinstance(res, int):
                        codigo = res
                except SystemExit as e:
                    codigo = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
        finally:
            sys.argv = antigo_argv
        return codigo, out_buf.getvalue(), err_buf.getvalue()

    def test_cli_versao(self):
        codigo, out, _ = self.executar_cli(["--versao"])
        self.assertEqual(codigo, 0)
        self.assertIn("1.0.0", out)
        self.assertIn("LOFRANO TECNOLOGIA", out)

    def test_cli_ajuda(self):
        codigo, out, _ = self.executar_cli(["--ajuda"])
        self.assertEqual(codigo, 0)
        self.assertIn("NBR 6122:2022", out)
        self.assertIn("calcular", out)
        self.assertIn("catalogo", out)
        self.assertIn("gerar-exemplo", out)

    def test_cli_catalogo(self):
        codigo, out, _ = self.executar_cli(["catalogo"])
        self.assertEqual(codigo, 0)
        self.assertIn("CATÁLOGO GEOTÉCNICO DE FUNDAÇÕES PROFUNDAS", out)
        self.assertIn("COEFICIENTES GEOTÉCNICOS DE SOLOS", out)
        self.assertIn("Aoki", out)
        self.assertIn("Décourt", out)

    def test_cli_gerar_exemplo(self):
        for tipo in ["estaca-helice", "estaca-pre-moldada", "tubulao"]:
            codigo, out, _ = self.executar_cli(["gerar-exemplo", "-t", tipo])
            self.assertEqual(codigo, 0)
            self.assertIn("identificacao_projeto", out)
            self.assertIn("geometria", out)
            self.assertIn("perfil_solo", out)

    def test_cli_gerar_exemplo_arquivo(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            caminho = os.path.join(tmpdir, "exemplo_gerado.json")
            codigo, out, _ = self.executar_cli(["gerar-exemplo", "-t", "estaca-helice", "-o", caminho])
            self.assertEqual(codigo, 0)
            self.assertTrue(os.path.exists(caminho))

    def test_cli_calcular_arquivo_e_exportadores(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            arq_entrada = os.path.join(tmpdir, "entrada.json")
            arq_saida = os.path.join(tmpdir, "saida.json")
            arq_memorial = os.path.join(tmpdir, "memorial.txt")
            arq_csv = os.path.join(tmpdir, "resumo.csv")
            arq_svg = os.path.join(tmpdir, "painel.svg")
            arq_zip = os.path.join(tmpdir, "pacote.zip")

            # Gera exemplo válido
            self.executar_cli(["gerar-exemplo", "-t", "estaca-helice", "-o", arq_entrada])

            # Executa cálculo com todos os exportadores
            codigo, out, _ = self.executar_cli([
                "calcular",
                arq_entrada,
                "-o", arq_saida,
                "--memorial", arq_memorial,
                "--csv", arq_csv,
                "--svg", arq_svg,
                "--pacote-zip", arq_zip,
            ])
            self.assertEqual(codigo, 0)
            self.assertTrue(os.path.exists(arq_saida))
            self.assertTrue(os.path.exists(arq_memorial))
            self.assertTrue(os.path.exists(arq_csv))
            self.assertTrue(os.path.exists(arq_svg))
            self.assertTrue(os.path.exists(arq_zip))
            self.assertIn("Resultados exportados em JSON", out)

    def test_cli_calcular_arquivo_inexistente(self):
        codigo, _, err = self.executar_cli(["calcular", "arquivo_fantasma_123.json"])
        self.assertNotEqual(codigo, 0)
        self.assertIn("não encontrado", err)

    def test_cli_calcular_entrada_com_float(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            arq_invalido = os.path.join(tmpdir, "com_float.json")
            with open(arq_invalido, "w", encoding="utf-8") as f:
                f.write('{"fck_concreto_mpa": 30.5}')
            codigo, _, err = self.executar_cli(["calcular", arq_invalido])
            self.assertNotEqual(codigo, 0)
            self.assertIn("Ponto flutuante IEEE-754", err)

    def test_cli_sem_comando(self):
        codigo, out, _ = self.executar_cli([])
        self.assertEqual(codigo, 0)
        self.assertIn("NBR 6122:2022", out)


if __name__ == "__main__":
    unittest.main()

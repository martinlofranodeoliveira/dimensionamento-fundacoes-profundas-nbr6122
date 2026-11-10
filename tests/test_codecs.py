"""Testes unitários dos codecs JSON RFC 8259 estritos (Zero-Float, Anti-BOM, Profundidade)."""

import json
import unittest
from fractions import Fraction

from fundacoes_profundas_nbr6122.calculator import dimensionar_projeto_fundacao_profunda
from fundacoes_profundas_nbr6122.codecs import (
    carregar_projeto_fundacao_json,
    codificar_json_projeto,
    decodificar_json_projeto,
    exportar_resultado_json,
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


class TestCodecs(unittest.TestCase):
    """Garante conformidade estrita com RFC 8259 e regras de robustez LOFRANO TECNOLOGIA."""

    def setUp(self):
        self.json_valido = """{
  "identificacao_projeto": "Edifício Residencial Horizonte",
  "processo_executivo": "ESTACA_HELICE_CONTINUA",
  "geometria": {
    "tipo_secao": "CIRCULAR",
    "diametro_ou_lado_m": "1/2",
    "comprimento_fuste_m": 12,
    "fck_concreto_mpa": 30,
    "cota_arrasamento_m": 0,
    "taxa_armadura_adotada": "1/200"
  },
  "solicitacao": {
    "forca_normal_compressao_kn": 800,
    "forca_tracao_kn": 0,
    "momento_fletor_knm": 0,
    "forca_horizontal_kn": 0
  },
  "perfil_solo": [
    {
      "profundidade_topo_m": 0,
      "profundidade_base_m": 4,
      "tipo_solo": "ARGILA_SILTOSA",
      "nspt_medio": 5
    },
    {
      "profundidade_topo_m": 4,
      "profundidade_base_m": 14,
      "tipo_solo": "AREIA",
      "nspt_medio": 22
    }
  ],
  "grupo": {
    "numero_estacas_bloco": 1,
    "espacamento_entre_eixos_m": 0
  },
  "possui_prova_carga": false,
  "responsavel_tecnico": "Eng. Martin Lofrano"
}"""

    def test_carregar_json_valido(self):
        dados = carregar_projeto_fundacao_json(self.json_valido)
        self.assertEqual(dados.identificacao_projeto, "Edifício Residencial Horizonte")
        self.assertEqual(dados.processo_executivo, TipoProcessoExecutivo.ESTACA_HELICE_CONTINUA)
        self.assertEqual(dados.geometria.diametro_ou_lado_m, Fraction(1, 2))
        self.assertEqual(dados.geometria.comprimento_fuste_m, Fraction(12, 1))
        self.assertEqual(len(dados.perfil_solo), 2)
        self.assertEqual(dados.solicitacao.forca_normal_compressao_kn, Fraction(800, 1))

    def test_rejeitar_ponto_flutuante_float(self):
        # Número com ponto flutuante no JSON numérico
        json_com_float = self.json_valido.replace('"diametro_ou_lado_m": "1/2"', '"diametro_ou_lado_m": 0.50')
        with self.assertRaises(ValueError) as ctx:
            carregar_projeto_fundacao_json(json_com_float)
        self.assertIn("Ponto flutuante IEEE-754", str(ctx.exception))

    def test_rejeitar_bom(self):
        # UTF-8 BOM \xef\xbb\xbf ou \ufeff
        json_bom = "\ufeff" + self.json_valido
        with self.assertRaises(ValueError) as ctx:
            carregar_projeto_fundacao_json(json_bom)
        self.assertIn("Byte Order Mark (BOM)", str(ctx.exception))

        json_bom_bytes = "\xef\xbb\xbf" + self.json_valido
        with self.assertRaises(ValueError) as ctx:
            carregar_projeto_fundacao_json(json_bom_bytes)
        self.assertIn("Byte Order Mark (BOM)", str(ctx.exception))

    def test_rejeitar_chaves_duplicadas(self):
        json_duplicado = """{
  "identificacao_projeto": "Projeto A",
  "identificacao_projeto": "Projeto B",
  "processo_executivo": "ESTACA_HELICE_CONTINUA",
  "geometria": {
    "tipo_secao": "CIRCULAR",
    "diametro_ou_lado_m": 1,
    "comprimento_fuste_m": 10,
    "fck_concreto_mpa": 25
  },
  "solicitacao": {
    "forca_normal_compressao_kn": 500
  },
  "perfil_solo": [
    {"profundidade_topo_m": 0, "profundidade_base_m": 10, "tipo_solo": "AREIA", "nspt_medio": 15}
  ]
}"""
        with self.assertRaises(ValueError) as ctx:
            carregar_projeto_fundacao_json(json_duplicado)
        self.assertIn("Chave duplicada encontrada", str(ctx.exception))

    def test_rejeitar_profundidade_excessiva(self):
        # Estrutura com aninhamento maior que 32 níveis
        d = {"chave": 1}
        for _ in range(35):
            d = {"sub": d}
        json_profundo = json.dumps(d)
        with self.assertRaises(ValueError) as ctx:
            carregar_projeto_fundacao_json(json_profundo)
        self.assertIn("limite máximo permitido de 32", str(ctx.exception))

    def test_exportar_e_roundtrip_resultado(self):
        dados = carregar_projeto_fundacao_json(self.json_valido)
        res = dimensionar_projeto_fundacao_profunda(dados)
        saida_json = exportar_resultado_json(res)
        self.assertIsInstance(saida_json, str)
        parsed = json.loads(saida_json)
        self.assertIn("normas_referencia", parsed)
        self.assertIn("capacidade_geotecnica_aoki_velloso", parsed)
        self.assertIn("capacidade_geotecnica_decourt_quaresma", parsed)
        self.assertIn("verificacao_estrutural_fuste", parsed)

    def test_aliases_decodificar_codificar(self):
        dados = decodificar_json_projeto(self.json_valido)
        res = dimensionar_projeto_fundacao_profunda(dados)
        texto_1 = codificar_json_projeto(res)
        texto_2 = codificar_json_projeto(dados, res)
        self.assertEqual(texto_1, texto_2)
        with self.assertRaises(ValueError):
            codificar_json_projeto("invalido")


if __name__ == "__main__":
    unittest.main()

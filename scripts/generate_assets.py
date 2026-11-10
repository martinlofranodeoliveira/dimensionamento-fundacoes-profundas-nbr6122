"""Script de automação para geração de painéis SVG e imagens PNG (1440x900).

Utiliza Chrome headless para renderização de alta fidelidade visual.
Desenvolvido por LOFRANO TECNOLOGIA.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

# Adiciona diretório src ao path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from fundacoes_profundas_nbr6122.calculator import dimensionar_projeto_fundacao_profunda
from fundacoes_profundas_nbr6122.codecs import decodificar_json_projeto
from fundacoes_profundas_nbr6122.svg_generator import gerar_painel_svg


def encontrar_binario_navegador() -> str | None:
    """Busca executável do Google Chrome ou Chromium disponível no sistema."""
    candidatos = [
        "google-chrome",
        "google-chrome-stable",
        "chromium",
        "chromium-browser",
    ]
    for c in candidatos:
        path = shutil.which(c)
        if path:
            return path
    return None


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    docs_dir = repo_root / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    json_exemplo = repo_root / "examples" / "estaca_helice_edificio.json"
    if not json_exemplo.exists():
        print(f"Erro: Exemplo não encontrado em {json_exemplo}", file=sys.stderr)
        return 1

    conteudo = json_exemplo.read_text(encoding="utf-8")
    dados = decodificar_json_projeto(conteudo)
    resultado = dimensionar_projeto_fundacao_profunda(dados)

    svg_conteudo = gerar_painel_svg(resultado)
    svg_path = docs_dir / "painel_exemplo.svg"
    svg_path.write_text(svg_conteudo, encoding="utf-8")
    print(f"Painel vetorial gerado com sucesso em: {svg_path}")

    png_path = docs_dir / "exemplo.png"
    nav = encontrar_binario_navegador()

    if not nav:
        print("Aviso: Navegador headless não encontrado no sistema. Fallback visual.", file=sys.stderr)
        return 0

    cmd = [
        nav,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--window-size=1440,900",
        f"--screenshot={png_path.resolve()}",
        str(svg_path.resolve()),
    ]
    print(f"Executando renderização via: {' '.join(cmd)}")
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if proc.returncode != 0:
        print(f"Erro ao renderizar screenshot com {nav}: {proc.stderr}", file=sys.stderr)
        return proc.returncode

    if png_path.exists() and png_path.stat().st_size > 0:
        print(f"Imagem renderizada com sucesso: {png_path} ({png_path.stat().st_size} bytes)")
        return 0
    else:
        print("Erro: Arquivo PNG não foi gerado ou está vazio.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

"""Verificador de integridade de distribuição do pacote (sdist e wheel).

Garante que todos os arquivos críticos e metadados estão presentes nos artefatos de release.
Desenvolvido por LOFRANO TECNOLOGIA.
"""

from __future__ import annotations

import sys
import tarfile
import zipfile
from pathlib import Path


def verificar_distribuicao() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    dist_dir = repo_root / "dist"

    if not dist_dir.exists():
        print(f"Erro: Diretório 'dist' não encontrado em {dist_dir}", file=sys.stderr)
        return 1

    sdists = list(dist_dir.glob("*.tar.gz"))
    wheels = list(dist_dir.glob("*.whl"))

    if not sdists:
        print("Erro: Nenhum pacote sdist (.tar.gz) encontrado em dist/", file=sys.stderr)
        return 1
    if not wheels:
        print("Erro: Nenhum pacote wheel (.whl) encontrado em dist/", file=sys.stderr)
        return 1

    sdist_path = sdists[0]
    wheel_path = wheels[0]

    print(f"Verificando sdist: {sdist_path.name}")
    with tarfile.open(sdist_path, "r:gz") as tar:
        membros = tar.getnames()
        obrigatorios_sdist = [
            "pyproject.toml",
            "LICENSE",
            "README.md",
            "src/fundacoes_profundas_nbr6122/__init__.py",
            "src/fundacoes_profundas_nbr6122/calculator.py",
            "src/fundacoes_profundas_nbr6122/models.py",
            "src/fundacoes_profundas_nbr6122/constants.py",
            "src/fundacoes_profundas_nbr6122/codecs.py",
            "src/fundacoes_profundas_nbr6122/exporters.py",
            "src/fundacoes_profundas_nbr6122/svg_generator.py",
            "src/fundacoes_profundas_nbr6122/cli.py",
            "src/fundacoes_profundas_nbr6122/py.typed",
        ]
        for ob in obrigatorios_sdist:
            encontrado = any(m.endswith(ob) for m in membros)
            if not encontrado:
                print(f"Erro: Arquivo obrigatório '{ob}' ausente no sdist!", file=sys.stderr)
                return 1

    print(f"Verificando wheel: {wheel_path.name}")
    with zipfile.ZipFile(wheel_path, "r") as whl:
        arquivos_whl = whl.namelist()
        obrigatorios_whl = [
            "fundacoes_profundas_nbr6122/__init__.py",
            "fundacoes_profundas_nbr6122/calculator.py",
            "fundacoes_profundas_nbr6122/models.py",
            "fundacoes_profundas_nbr6122/constants.py",
            "fundacoes_profundas_nbr6122/codecs.py",
            "fundacoes_profundas_nbr6122/exporters.py",
            "fundacoes_profundas_nbr6122/svg_generator.py",
            "fundacoes_profundas_nbr6122/cli.py",
            "fundacoes_profundas_nbr6122/py.typed",
        ]
        for ob in obrigatorios_whl:
            if ob not in arquivos_whl:
                print(f"Erro: Arquivo obrigatório '{ob}' ausente no wheel!", file=sys.stderr)
                return 1

    print("Distribuição verificada com sucesso: 100% dos arquivos obrigatórios presentes.")
    return 0


if __name__ == "__main__":
    sys.exit(verificar_distribuicao())

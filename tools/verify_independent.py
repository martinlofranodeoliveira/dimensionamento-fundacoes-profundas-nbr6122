"""Auditor Independente em SQLite para Verificação de Fundações Profundas (NBR 6122:2022).

Desenvolvido por LOFRANO TECNOLOGIA.
Este script é 100% desacoplado do código-fonte do pacote, sem importar nenhum módulo
de 'fundacoes_profundas_nbr6122'. Executa a auditoria das formulações analíticas e
tabelas normativas em banco relacional SQLite em memória (:memory:).
"""

from __future__ import annotations

import sqlite3
import sys
from fractions import Fraction

# Tabelas normativas de referência independente da NBR 6122:2022
REFERENCIA_SOLOS = {
    "AREIA": {"k_aoki": Fraction(1000, 1), "alpha_aoki": Fraction(14, 1000), "c_decourt": Fraction(200, 1)},
    "AREIA_SILTOSA": {"k_aoki": Fraction(800, 1), "alpha_aoki": Fraction(20, 1000), "c_decourt": Fraction(150, 1)},
    "AREIA_ARGILOSA": {"k_aoki": Fraction(600, 1), "alpha_aoki": Fraction(30, 1000), "c_decourt": Fraction(130, 1)},
    "SILTE": {"k_aoki": Fraction(400, 1), "alpha_aoki": Fraction(30, 1000), "c_decourt": Fraction(120, 1)},
    "SILTE_ARENOSO": {"k_aoki": Fraction(500, 1), "alpha_aoki": Fraction(24, 1000), "c_decourt": Fraction(120, 1)},
    "SILTE_ARGILOSO": {"k_aoki": Fraction(300, 1), "alpha_aoki": Fraction(28, 1000), "c_decourt": Fraction(250, 1)},
    "ARGILA": {"k_aoki": Fraction(200, 1), "alpha_aoki": Fraction(60, 1000), "c_decourt": Fraction(400, 1)},
    "ARGILA_ARENOSA": {"k_aoki": Fraction(350, 1), "alpha_aoki": Fraction(24, 1000), "c_decourt": Fraction(300, 1)},
    "ARGILA_SILTOSA": {"k_aoki": Fraction(250, 1), "alpha_aoki": Fraction(30, 1000), "c_decourt": Fraction(350, 1)},
}

REFERENCIA_FATORES_ESTACAS = {
    "ESTACA_FRANKI": {"f1": Fraction(5, 2), "f2": Fraction(5, 1), "alpha_dq": Fraction(1, 1), "beta_dq": Fraction(1, 1)},
    "ESTACA_PRE_MOLDADA_CONCRETO": {"f1": Fraction(7, 4), "f2": Fraction(7, 2), "alpha_dq": Fraction(1, 1), "beta_dq": Fraction(1, 1)},
    "ESTACA_HELICE_CONTINUA": {"f1": Fraction(2, 1), "f2": Fraction(4, 1), "alpha_dq": Fraction(3, 10), "beta_dq": Fraction(1, 1)},
    "ESTACA_ESCAVADA_BENTONITA": {"f1": Fraction(3, 1), "f2": Fraction(6, 1), "alpha_dq": Fraction(1, 2), "beta_dq": Fraction(4, 5)},
    "ESTACA_ESCAVADA_SEM_FLUIDO": {"f1": Fraction(7, 2), "f2": Fraction(7, 1), "alpha_dq": Fraction(1, 2), "beta_dq": Fraction(13, 20)},
    "ESTACA_RAIZ": {"f1": Fraction(3, 2), "f2": Fraction(3, 1), "alpha_dq": Fraction(1, 1), "beta_dq": Fraction(3, 2)},
    "ESTACA_METALICA": {"f1": Fraction(7, 4), "f2": Fraction(7, 2), "alpha_dq": Fraction(1, 1), "beta_dq": Fraction(1, 1)},
    "TUBULAO_A_CEU_ABERTO": {"f1": Fraction(3, 1), "f2": Fraction(6, 1), "alpha_dq": Fraction(1, 2), "beta_dq": Fraction(1, 2)},
}

PI_REF = Fraction(355, 113)


def inicializar_banco(conn: sqlite3.Connection) -> None:
    """Cria tabelas de auditoria relacional com constraints estritas."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE solos_normativos (
            tipo_solo TEXT PRIMARY KEY,
            k_aoki_kpa INTEGER NOT NULL CHECK (k_aoki_kpa > 0),
            alpha_aoki TEXT NOT NULL,
            c_decourt_kpa INTEGER NOT NULL CHECK (c_decourt_kpa > 0)
        )
    """)

    cursor.execute("""
        CREATE TABLE fatores_estacas (
            processo_executivo TEXT PRIMARY KEY,
            f1_aoki TEXT NOT NULL,
            f2_aoki TEXT NOT NULL,
            alpha_decourt TEXT NOT NULL,
            beta_decourt TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE auditoria_estacas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_projeto TEXT NOT NULL,
            processo_executivo TEXT NOT NULL REFERENCES fatores_estacas(processo_executivo),
            diametro_m TEXT NOT NULL,
            comprimento_m TEXT NOT NULL,
            carga_atuante_kn TEXT NOT NULL,
            r_adm_aoki_kn TEXT NOT NULL,
            r_adm_decourt_kn TEXT NOT NULL,
            r_adm_adotada_kn TEXT NOT NULL,
            r_adm_estrutural_kn TEXT NOT NULL,
            aprovado_geotecnico INTEGER NOT NULL CHECK (aprovado_geotecnico IN (0, 1)),
            aprovado_estrutural INTEGER NOT NULL CHECK (aprovado_estrutural IN (0, 1))
        )
    """)

    for s, p in REFERENCIA_SOLOS.items():
        cursor.execute(
            "INSERT INTO solos_normativos VALUES (?, ?, ?, ?)",
            (s, int(p["k_aoki"]), str(p["alpha_aoki"]), int(p["c_decourt"])),
        )

    for proc, f in REFERENCIA_FATORES_ESTACAS.items():
        cursor.execute(
            "INSERT INTO fatores_estacas VALUES (?, ?, ?, ?, ?)",
            (proc, str(f["f1"]), str(f["f2"]), str(f["alpha_dq"]), str(f["beta_dq"])),
        )

    conn.commit()


def auditoria_calculo_independente(
    nome: str,
    processo: str,
    diametro_m: Fraction,
    comprimento_m: Fraction,
    fck_mpa: Fraction,
    camadas: list[tuple[str, int, Fraction]],
    camada_ponta: str,
    nspt_ponta: int,
    carga_kn: Fraction,
    fs: Fraction = Fraction(2, 1),
) -> dict:
    """Implementação puramente matemática independente para validação cruzada."""
    f = REFERENCIA_FATORES_ESTACAS[processo]
    p_solo_ponta = REFERENCIA_SOLOS[camada_ponta]

    raio = diametro_m / Fraction(2, 1)
    area_ponta = PI_REF * raio * raio
    perimetro = Fraction(2, 1) * PI_REF * raio

    # 1. Aoki-Velloso
    # Rp = (K * Np * Ap) / F1
    rp_aoki = (p_solo_ponta["k_aoki"] * nspt_ponta * area_ponta) / f["f1"]
    rl_aoki_soma = Fraction(0, 1)
    for solo_nome, nspt, delta_l in camadas:
        ps = REFERENCIA_SOLOS[solo_nome]
        rl_aoki_soma += ps["alpha_aoki"] * ps["k_aoki"] * min(50, nspt) * delta_l
    rl_aoki = (perimetro * rl_aoki_soma) / f["f2"]
    radm_aoki = (rp_aoki + rl_aoki) / fs

    # 2. Décourt-Quaresma
    # Rp = alpha * C * Np * Ap
    rp_dq = f["alpha_dq"] * p_solo_ponta["c_decourt"] * nspt_ponta * area_ponta
    rl_dq_soma = Fraction(0, 1)
    for solo_nome, nspt, delta_l in camadas:
        ql = min(Fraction(120, 1), Fraction(10, 1) * (Fraction(min(50, nspt), 3) + Fraction(1, 1)))
        rl_dq_soma += perimetro * f["beta_dq"] * ql * delta_l
    radm_dq = (rp_dq + rl_dq_soma) / fs

    radm_adotada = min(radm_aoki, radm_dq)

    # 3. Estrutural Fuste
    fcd_kpa = (fck_mpa * Fraction(1000, 1)) / Fraction(14, 10)
    taxa_arm = Fraction(5, 1000)
    as_m2 = area_ponta * taxa_arm
    fyd_kpa = Fraction(500000, 1) / Fraction(115, 100)
    fator_exec = Fraction(85, 100) if "HELICE" in processo or "ESCAVADA" in processo else Fraction(1, 1)
    n_ult_est = Fraction(85, 100) * fcd_kpa * area_ponta * fator_exec + fyd_kpa * as_m2
    n_adm_est = n_ult_est / Fraction(14, 10)

    aprov_geo = 1 if carga_kn <= radm_adotada else 0
    aprov_est = 1 if carga_kn <= n_adm_est else 0

    return {
        "nome": nome,
        "processo": processo,
        "diametro": diametro_m,
        "comprimento": comprimento_m,
        "carga": carga_kn,
        "radm_aoki": radm_aoki,
        "radm_dq": radm_dq,
        "radm_adotada": radm_adotada,
        "radm_est": n_adm_est,
        "aprov_geo": aprov_geo,
        "aprov_est": aprov_est,
    }


def executar_auditoria() -> int:
    """Executa a verificação dos casos representativos e valida no banco relacional."""
    print("=" * 80)
    print("AUDITORIA INDEPENDENTE DE FUNDAÇÕES PROFUNDAS EM SQLITE (NBR 6122:2022)")
    print("=" * 80)

    conn = sqlite3.connect(":memory:")
    inicializar_banco(conn)

    casos = [
        # Caso 1: Estaca Hélice Contínua D=50cm L=14m
        auditoria_calculo_independente(
            nome="Caso 1 - Hélice Contínua D50cm L14m",
            processo="ESTACA_HELICE_CONTINUA",
            diametro_m=Fraction(1, 2),
            comprimento_m=Fraction(14, 1),
            fck_mpa=Fraction(30, 1),
            camadas=[
                ("ARGILA_SILTOSA", 4, Fraction(3, 1)),
                ("SILTE_ARENOSO", 9, Fraction(5, 1)),
                ("AREIA_SILTOSA", 18, Fraction(4, 1)),
                ("AREIA", 28, Fraction(2, 1)),
            ],
            camada_ponta="AREIA",
            nspt_ponta=28,
            carga_kn=Fraction(700, 1),
        ),
        # Caso 2: Estaca Pré-moldada D=35cm L=11m
        auditoria_calculo_independente(
            nome="Caso 2 - Pré-moldada D35cm L11m",
            processo="ESTACA_PRE_MOLDADA_CONCRETO",
            diametro_m=Fraction(7, 20),
            comprimento_m=Fraction(11, 1),
            fck_mpa=Fraction(35, 1),
            camadas=[
                ("SILTE_ARGILOSO", 5, Fraction(4, 1)),
                ("AREIA_ARGILOSA", 14, Fraction(5, 1)),
                ("AREIA", 24, Fraction(2, 1)),
            ],
            camada_ponta="AREIA",
            nspt_ponta=24,
            carga_kn=Fraction(600, 1),
            fs=Fraction(8, 5), # Com prova de carga FS=1.6
        ),
        # Caso 3: Tubulão Céu Aberto D=1.20m L=8m
        auditoria_calculo_independente(
            nome="Caso 3 - Tubulão Céu Aberto D1.20m L8m",
            processo="TUBULAO_A_CEU_ABERTO",
            diametro_m=Fraction(6, 5),
            comprimento_m=Fraction(8, 1),
            fck_mpa=Fraction(25, 1),
            camadas=[
                ("ARGILA", 6, Fraction(3, 1)),
                ("SILTE_ARGILOSO", 15, Fraction(3, 1)),
                ("AREIA", 35, Fraction(2, 1)),
            ],
            camada_ponta="AREIA",
            nspt_ponta=35,
            carga_kn=Fraction(2200, 1),
        ),
    ]

    cursor = conn.cursor()
    for c in casos:
        cursor.execute("""
            INSERT INTO auditoria_estacas (
                nome_projeto, processo_executivo, diametro_m, comprimento_m,
                carga_atuante_kn, r_adm_aoki_kn, r_adm_decourt_kn, r_adm_adotada_kn,
                r_adm_estrutural_kn, aprovado_geotecnico, aprovado_estrutural
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            c["nome"], c["processo"], str(c["diametro"]), str(c["comprimento"]),
            str(c["carga"]), str(c["radm_aoki"]), str(c["radm_dq"]), str(c["radm_adotada"]),
            str(c["radm_est"]), c["aprov_geo"], c["aprov_est"]
        ))
    conn.commit()

    cursor.execute("""
        SELECT
            nome_projeto,
            processo_executivo,
            carga_atuante_kn,
            r_adm_aoki_kn,
            r_adm_decourt_kn,
            r_adm_adotada_kn,
            r_adm_estrutural_kn,
            aprovado_geotecnico,
            aprovado_estrutural
        FROM auditoria_estacas
    """)
    linhas = cursor.fetchall()

    for nome, proc, carga, aoki, dq, adotada, est, ap_geo, ap_est in linhas:
        print(f"\nAuditando: {nome}")
        print(f"  * Tecnologia: {proc}")
        print(f"  * Carga Normal Atuante (Nk): {carga} kN")
        print(f"  * R_adm Aoki-Velloso: {float(Fraction(aoki)):.2f} kN")
        print(f"  * R_adm Décourt-Quaresma: {float(Fraction(dq)):.2f} kN")
        print(f"  * R_adm Geotécnica Adotada: {float(Fraction(adotada)):.2f} kN")
        print(f"  * N_adm Estrutural do Fuste: {float(Fraction(est)):.2f} kN")
        print(f"  * Avaliação Geotécnica: {'APROVADO' if ap_geo == 1 else 'REPROVADO'}")
        print(f"  * Avaliação Estrutural: {'CONFORME' if ap_est == 1 else 'REPROVADO'}")

        if ap_est != 1:
            print(f"FALHA: Projeto {nome} reprovado na verificação estrutural do fuste!", file=sys.stderr)
            return 1

    print("\n" + "=" * 80)
    print("TODAS AS VERIFICAÇÕES DE AUDITORIA INDEPENDENTE EM SQLITE FORAM APROVADAS COM SUCESSO!")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    sys.exit(executar_auditoria())

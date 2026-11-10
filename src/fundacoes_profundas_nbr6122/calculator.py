"""Motor de cálculo analítico e determinístico de fundações profundas NBR 6122:2022.

Implementa os métodos semiempíricos de Aoki-Velloso (1975) e Décourt-Quaresma (1978/1996),
verificação estrutural do fuste conforme NBR 6118 / NBR 6122 e efeito de grupo de estacas.
Aritmética estritamente racional e inteira (Zero-Float).
"""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from fundacoes_profundas_nbr6122.constants import (
    COEFICIENTE_RUDIGER_CONCRETO,
    FATOR_SEGURANCA_GEOTECNICO_COM_PROVA_CARGA,
    FATOR_SEGURANCA_GEOTECNICO_COMPRESSAO,
    FYK_ACO_CA50_MPA,
    GAMMA_ACO,
    GAMMA_CONCRETO,
    LIMITE_SUPERIOR_ATRITO_LATERAL_KPA,
    PI_FRAC,
    TABELA_FATORES_ESTACAS,
    TABELA_SOLOS,
    TAXA_ARMADURA_LONGITUDINAL_MINIMA,
    FatoresTipoEstaca,
    ParametrosSolo,
)
from fundacoes_profundas_nbr6122.models import (
    CamadaSoloSPT,
    DadosProjetoFundacaoProfunda,
    EfeitoGrupoEstacas,
    GeometriaEstaca,
    ResultadoCapacidadeMetodo,
    ResultadoEstruturalFuste,
    ResultadoProjetoFundacaoProfunda,
    TipoProcessoExecutivo,
    TipoSecaoTransversal,
)


def calcular_geometria_secao(geometria: GeometriaEstaca) -> Tuple[Fraction, Fraction]:
    """Calcula a área da seção transversal (m²) e o perímetro do fuste (m)."""
    dim1 = geometria.diametro_ou_lado_m
    if dim1 <= Fraction(0, 1):
        raise ValueError(f"Dimensão da seção transversal deve ser positiva: {dim1}")

    if geometria.tipo_secao == TipoSecaoTransversal.CIRCULAR:
        raio = dim1 / Fraction(2, 1)
        area_m2 = PI_FRAC * raio * raio
        perimetro_m = Fraction(2, 1) * PI_FRAC * raio
    elif geometria.tipo_secao == TipoSecaoTransversal.QUADRADA:
        area_m2 = dim1 * dim1
        perimetro_m = Fraction(4, 1) * dim1
    elif geometria.tipo_secao == TipoSecaoTransversal.RETANGULAR:
        dim2 = geometria.largura_b_m if geometria.largura_b_m > Fraction(0, 1) else dim1
        area_m2 = dim1 * dim2
        perimetro_m = Fraction(2, 1) * (dim1 + dim2)
    else:
        # Fallback circular
        raio = dim1 / Fraction(2, 1)
        area_m2 = PI_FRAC * raio * raio
        perimetro_m = Fraction(2, 1) * PI_FRAC * raio

    return area_m2, perimetro_m


def processar_perfil_estratigrafico(
    perfil: Tuple[CamadaSoloSPT, ...],
    cota_topo: Fraction,
    comprimento_fuste: Fraction,
) -> Tuple[List[Tuple[ParametrosSolo, int, Fraction]], ParametrosSolo, int]:
    """Segmenta o perfil de solo ao longo do comprimento cravado e determina o SPT da ponta."""
    if not perfil:
        raise ValueError("Perfil geotécnico não pode ser vazio.")
    if comprimento_fuste <= Fraction(0, 1):
        raise ValueError(f"Comprimento do fuste deve ser positivo: {comprimento_fuste}")

    z_inicio = cota_topo
    z_fim = cota_topo + comprimento_fuste

    trechos: List[Tuple[ParametrosSolo, int, Fraction]] = []
    camada_ponta_param: ParametrosSolo | None = None
    nspt_ponta = 1

    for c in perfil:
        if c.profundidade_base_m <= z_inicio:
            continue
        if c.profundidade_topo_m >= z_fim:
            continue

        topo_efetivo = max(z_inicio, c.profundidade_topo_m)
        base_efetiva = min(z_fim, c.profundidade_base_m)
        comprimento_trecho = base_efetiva - topo_efetivo

        if comprimento_trecho > Fraction(0, 1):
            param = TABELA_SOLOS.get(c.tipo_solo.upper())
            if param is None:
                # Fallback para silte médio
                param = TABELA_SOLOS["SILTE"]
            trechos.append((param, max(1, c.nspt_medio), comprimento_trecho))

        # Camada que contém a ponta
        if c.profundidade_topo_m <= z_fim <= c.profundidade_base_m:
            param = TABELA_SOLOS.get(c.tipo_solo.upper())
            camada_ponta_param = param if param is not None else TABELA_SOLOS["SILTE"]
            nspt_ponta = max(1, c.nspt_medio)

    if camada_ponta_param is None:
        # Pega a última camada do perfil
        ultima = perfil[-1]
        param = TABELA_SOLOS.get(ultima.tipo_solo.upper())
        camada_ponta_param = param if param is not None else TABELA_SOLOS["SILTE"]
        nspt_ponta = max(1, ultima.nspt_medio)

    # Limite normativo conservador para N_spt de ponta (máx 50)
    nspt_ponta = min(50, nspt_ponta)

    return trechos, camada_ponta_param, nspt_ponta


def calcular_capacidade_aoki_velloso(
    fatores: FatoresTipoEstaca,
    area_ponta_m2: Fraction,
    perimetro_m: Fraction,
    trechos_fuste: List[Tuple[ParametrosSolo, int, Fraction]],
    camada_ponta: ParametrosSolo,
    nspt_ponta: int,
    fs_geotecnico: Fraction,
) -> ResultadoCapacidadeMetodo:
    """Calcula a capacidade de carga última e admissível pelo método de Aoki-Velloso (1975)."""
    # 1. Resistência de Ponta: R_p = (K * N_p * A_p) / F1
    # K em kPa, A_p em m² -> R_p em kN
    k_ponta = camada_ponta.k_aoki_velloso_kpa
    r_ponta_kn = (k_ponta * nspt_ponta * area_ponta_m2) / fatores.f1_aoki

    # 2. Resistência Lateral: R_l = (U / F2) * sum(alpha_i * K_i * N_s,i * Delta_L_i)
    soma_lateral_kpa_m = Fraction(0, 1)
    for solo, nspt, delta_l in trechos_fuste:
        # N_s limitado normativamente a 50
        ns = min(50, nspt)
        soma_lateral_kpa_m += solo.alpha_aoki_velloso * solo.k_aoki_velloso_kpa * ns * delta_l

    r_lateral_kn = (perimetro_m * soma_lateral_kpa_m) / fatores.f2_aoki

    r_total_ultima_kn = r_ponta_kn + r_lateral_kn
    r_admissivel_kn = r_total_ultima_kn / fs_geotecnico

    return ResultadoCapacidadeMetodo(
        metodo="Aoki-Velloso (1975)",
        resistencia_ponta_kn=r_ponta_kn,
        resistencia_lateral_kn=r_lateral_kn,
        resistencia_total_ultima_kn=r_total_ultima_kn,
        capacidade_admissivel_kn=r_admissivel_kn,
    )


def calcular_capacidade_decourt_quaresma(
    fatores: FatoresTipoEstaca,
    area_ponta_m2: Fraction,
    perimetro_m: Fraction,
    trechos_fuste: List[Tuple[ParametrosSolo, int, Fraction]],
    camada_ponta: ParametrosSolo,
    nspt_ponta: int,
    fs_geotecnico: Fraction,
) -> ResultadoCapacidadeMetodo:
    """Calcula a capacidade de carga última e admissível pelo método de Décourt-Quaresma (1978/1996)."""
    # 1. Resistência de Ponta: R_p = alpha * C * N_p * A_p
    # C em kPa, A_p em m² -> R_p em kN
    c_ponta = camada_ponta.c_decourt_quaresma_kpa
    r_ponta_kn = fatores.alpha_decourt * c_ponta * nspt_ponta * area_ponta_m2

    # 2. Resistência Lateral: q_l = beta * 10 * (N_s / 3 + 1) [kPa]
    # Limitado a 120 kPa normativo
    soma_lateral_kn = Fraction(0, 1)
    for solo, nspt, delta_l in trechos_fuste:
        ns = min(50, nspt)
        q_l_base = Fraction(10, 1) * (Fraction(ns, 3) + Fraction(1, 1))
        q_l_efetivo = min(LIMITE_SUPERIOR_ATRITO_LATERAL_KPA, q_l_base)
        q_l_com_beta = fatores.beta_decourt * q_l_efetivo
        soma_lateral_kn += perimetro_m * q_l_com_beta * delta_l

    r_total_ultima_kn = r_ponta_kn + soma_lateral_kn
    r_admissivel_kn = r_total_ultima_kn / fs_geotecnico

    return ResultadoCapacidadeMetodo(
        metodo="Décourt-Quaresma (1978/1996)",
        resistencia_ponta_kn=r_ponta_kn,
        resistencia_lateral_kn=soma_lateral_kn,
        resistencia_total_ultima_kn=r_total_ultima_kn,
        capacidade_admissivel_kn=r_admissivel_kn,
    )


def calcular_verificacao_estrutural_fuste(
    geometria: GeometriaEstaca,
    processo: TipoProcessoExecutivo,
    area_concreto_m2: Fraction,
    perimetro_m: Fraction,
    forca_normal_atuante_kn: Fraction,
) -> ResultadoEstruturalFuste:
    """Verifica a resistência estrutural do fuste de concreto armado conforme NBR 6118 / NBR 6122."""
    # Fator de minoração executiva conforme item 8.2 da NBR 6122
    if processo in (
        TipoProcessoExecutivo.ESTACA_HELICE_CONTINUA,
        TipoProcessoExecutivo.ESTACA_ESCAVADA_BENTONITA,
        TipoProcessoExecutivo.ESTACA_ESCAVADA_SEM_FLUIDO,
    ):
        fator_min_exec = Fraction(85, 100)  # 0.85
    elif processo == TipoProcessoExecutivo.ESTACA_RAIZ:
        fator_min_exec = Fraction(90, 100)  # 0.90
    else:
        fator_min_exec = Fraction(1, 1)     # 1.00 (pré-moldada / franki)

    # Resistência de cálculo do concreto: f_cd = f_ck / 1.4 (em kPa: 1 MPa = 1000 kPa)
    fck_kpa = geometria.fck_concreto_mpa * Fraction(1000, 1)
    fcd_kpa = fck_kpa / GAMMA_CONCRETO

    # Armadura longitudinal mínima: 0.4% a 0.5% da seção
    taxa_armadura = max(TAXA_ARMADURA_LONGITUDINAL_MINIMA, geometria.taxa_armadura_adotada)
    area_armadura_m2 = area_concreto_m2 * taxa_armadura
    area_armadura_cm2 = area_armadura_m2 * Fraction(10000, 1)
    area_minima_cm2 = area_concreto_m2 * TAXA_ARMADURA_LONGITUDINAL_MINIMA * Fraction(10000, 1)

    # Resistência de cálculo do aço: f_yd = f_yk / 1.15 (500 MPa = 500.000 kPa)
    fyd_kpa = (FYK_ACO_CA50_MPA * Fraction(1000, 1)) / GAMMA_ACO

    # Capacidade normal admissível estrutural em serviço:
    # N_adm = [ (0.85 * fcd * Ac * fator_min_exec) + (fyd * As) ] / 1.4
    capacidade_ultima_estrutural_kn = (
        COEFICIENTE_RUDIGER_CONCRETO * fcd_kpa * area_concreto_m2 * fator_min_exec
        + fyd_kpa * area_armadura_m2
    )
    capacidade_admissivel_estrutural_kn = capacidade_ultima_estrutural_kn / Fraction(14, 10)

    tensao_trabalho_kpa = forca_normal_atuante_kn / area_concreto_m2
    aprovado = forca_normal_atuante_kn <= capacidade_admissivel_estrutural_kn

    return ResultadoEstruturalFuste(
        area_secao_concreto_m2=area_concreto_m2,
        perimetro_fuste_m=perimetro_m,
        resistencia_calculo_concreto_kpa=fcd_kpa,
        area_armadura_minima_cm2=area_minima_cm2,
        area_armadura_adotada_cm2=area_armadura_cm2,
        forca_normal_admissivel_estrutural_kn=capacidade_admissivel_estrutural_kn,
        tensao_trabalho_concreto_kpa=tensao_trabalho_kpa,
        aprovado_estruturalmente=aprovado,
    )


def calcular_eficiencia_grupo(grupo: EfeitoGrupoEstacas, diametro_m: Fraction) -> Fraction:
    """Calcula a eficiência do bloco de estacas considerando o espaçamento entre eixos."""
    n = grupo.numero_estacas_bloco
    if n <= 1:
        return Fraction(1, 1)

    s = grupo.espacamento_entre_eixos_m
    if s <= Fraction(0, 1):
        # Espaçamento padrão normativo s = 2.5 * D
        s = Fraction(5, 2) * diametro_m

    razao = s / diametro_m
    if razao >= Fraction(3, 1):
        # Para s >= 3D a NBR 6122 considera eficiência plena (1.00)
        return Fraction(1, 1)
    elif razao >= Fraction(5, 2):
        # Para 2.5D <= s < 3D, eficiência conservadora de 90%
        return Fraction(9, 10)
    elif razao >= Fraction(2, 1):
        # Para 2.0D <= s < 2.5D, eficiência de 80%
        return Fraction(8, 10)
    else:
        # Espaçamento crítico (< 2D)
        return Fraction(7, 10)


def dimensionar_projeto_fundacao_profunda(
    dados: DadosProjetoFundacaoProfunda,
) -> ResultadoProjetoFundacaoProfunda:
    """Executa o dimensionamento geotécnico e estrutural completo da fundação profunda."""
    alertas: List[str] = []

    # 1. Geometria da Seção
    area_m2, perimetro_m = calcular_geometria_secao(dados.geometria)

    # 2. Processamento do Perfil de Solo e Fatores de Estaca
    fatores = TABELA_FATORES_ESTACAS.get(dados.processo_executivo.value)
    if fatores is None:
        raise ValueError(f"Processo executivo não reconhecido: {dados.processo_executivo}")

    trechos_fuste, camada_ponta, nspt_ponta = processar_perfil_estratigrafico(
        perfil=dados.perfil_solo,
        cota_topo=dados.geometria.cota_arrasamento_m,
        comprimento_fuste=dados.geometria.comprimento_fuste_m,
    )

    # Fator de segurança geotécnico
    fs_geo = (
        FATOR_SEGURANCA_GEOTECNICO_COM_PROVA_CARGA
        if dados.possui_prova_carga
        else FATOR_SEGURANCA_GEOTECNICO_COMPRESSAO
    )

    # 3. Capacidade de Carga Geotécnica pelos dois métodos consagrados
    res_aoki = calcular_capacidade_aoki_velloso(
        fatores=fatores,
        area_ponta_m2=area_m2,
        perimetro_m=perimetro_m,
        trechos_fuste=trechos_fuste,
        camada_ponta=camada_ponta,
        nspt_ponta=nspt_ponta,
        fs_geotecnico=fs_geo,
    )

    res_decourt = calcular_capacidade_decourt_quaresma(
        fatores=fatores,
        area_ponta_m2=area_m2,
        perimetro_m=perimetro_m,
        trechos_fuste=trechos_fuste,
        camada_ponta=camada_ponta,
        nspt_ponta=nspt_ponta,
        fs_geotecnico=fs_geo,
    )

    # Capacidade admissível geotécnica adotada (menor valor entre Aoki e Décourt por segurança)
    cap_adm_adotada = min(res_aoki.capacidade_admissivel_kn, res_decourt.capacidade_admissivel_kn)

    # 4. Verificação Estrutural do Fuste
    res_estrutural = calcular_verificacao_estrutural_fuste(
        geometria=dados.geometria,
        processo=dados.processo_executivo,
        area_concreto_m2=area_m2,
        perimetro_m=perimetro_m,
        forca_normal_atuante_kn=dados.solicitacao.forca_normal_compressao_kn,
    )

    # 5. Efeito de Grupo
    eficiencia = calcular_eficiencia_grupo(dados.grupo, dados.geometria.diametro_ou_lado_m)
    num_estacas = max(1, dados.grupo.numero_estacas_bloco)
    cap_bloco = cap_adm_adotada * num_estacas * eficiencia

    # 6. Avaliação de Conformidade e Alertas
    aprovado_geo = dados.solicitacao.forca_normal_compressao_kn <= cap_bloco
    conformidade = aprovado_geo and res_estrutural.aprovado_estruturalmente

    if not aprovado_geo:
        alertas.append(
            f"Capacidade geotécnica insuficiente: Força atuante ({dados.solicitacao.forca_normal_compressao_kn} kN) "
            f"excede a carga admissível de projeto ({cap_bloco} kN)."
        )

    if not res_estrutural.aprovado_estruturalmente:
        alertas.append(
            f"Resistência estrutural do fuste insuficiente: Carga atuante ({dados.solicitacao.forca_normal_compressao_kn} kN) "
            f"excede o limite estrutural admissível de cálculo ({res_estrutural.forca_normal_admissivel_estrutural_kn} kN)."
        )

    if dados.grupo.numero_estacas_bloco > 1 and dados.grupo.espacamento_entre_eixos_m < Fraction(5, 2) * dados.geometria.diametro_ou_lado_m:
        alertas.append(
            "Espaçamento entre estacas inferior ao mínimo recomendado de 2,5 vezes o diâmetro (NBR 6122 Item 8.3)."
        )

    if nspt_ponta < 5:
        alertas.append(
            f"Atenção: N_SPT na cota de ponta é baixo ({nspt_ponta}). Avaliar aprofundamento até estrato mais resistente."
        )

    return ResultadoProjetoFundacaoProfunda(
        identificacao_projeto=dados.identificacao_projeto,
        processo_executivo=dados.processo_executivo,
        geometria=dados.geometria,
        solicitacao=dados.solicitacao,
        aoki_velloso=res_aoki,
        decourt_quaresma=res_decourt,
        capacidade_admissivel_adotada_kn=cap_adm_adotada,
        fator_seguranca_geotecnico_adotado=fs_geo,
        estrutural=res_estrutural,
        eficiencia_grupo=eficiencia,
        capacidade_admissivel_bloco_kn=cap_bloco,
        aprovado_geotecnicamente=aprovado_geo,
        conformidade_geral=conformidade,
        alertas_tecnicos=tuple(alertas),
    )

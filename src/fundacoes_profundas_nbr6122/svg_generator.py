"""Gerador de diagramas vetoriais SVG (1440x900) para Fundações Profundas NBR 6122.

Painel técnico profissional no padrão de engenharia visual da Lofrano Tecnologia.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any

from fundacoes_profundas_nbr6122.exporters import _fmt
from fundacoes_profundas_nbr6122.models import ResultadoProjetoFundacaoProfunda


def gerar_painel_svg(
    arg1: Any,
    arg2: ResultadoProjetoFundacaoProfunda | None = None,
) -> str:
    """Gera painel vetorial SVG 1440x900 com perfil geotécnico e dimensionamento da estaca."""
    res: ResultadoProjetoFundacaoProfunda = (
        arg2 if arg2 is not None and isinstance(arg2, ResultadoProjetoFundacaoProfunda) else arg1
    )

    cor_fundo = "#0f172a"
    cor_card = "#1e293b"
    cor_borda = "#334155"
    cor_texto = "#f8fafc"
    cor_texto_mut = "#94a3b8"
    cor_ciano = "#06b6d4"
    cor_azul = "#3b82f6"
    cor_laranja = "#f97316"
    cor_verde = "#10b981"
    cor_vermelho = "#ef4444"
    cor_amarelo = "#eab308"

    status_cor = cor_verde if res.conformidade_geral else cor_vermelho
    status_texto = "CONFORME NBR 6122" if res.conformidade_geral else "PENDÊNCIAS TÉCNICAS"

    svg_linhas = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 900" width="1440" height="900" style="background:{cor_fundo}; font-family:-apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, Helvetica, Arial, sans-serif;">',
        '<defs>',
        '  <linearGradient id="gradHeader" x1="0" y1="0" x2="1" y2="0">',
        f'    <stop offset="0%" stop-color="{cor_azul}" stop-opacity="0.8"/>',
        f'    <stop offset="100%" stop-color="{cor_ciano}" stop-opacity="0.8"/>',
        '  </linearGradient>',
        '  <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">',
        '    <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.4"/>',
        '  </filter>',
        '</defs>',
        f'<rect width="1440" height="900" fill="{cor_fundo}"/>',
    ]

    # Header Topo
    svg_linhas.extend([
        f'<rect x="30" y="24" width="1380" height="76" rx="12" fill="{cor_card}" stroke="{cor_borda}" stroke-width="1.5" filter="url(#shadow)"/>',
        f'<text x="56" y="52" fill="{cor_ciano}" font-size="13" font-weight="700" letter-spacing="1.5">LOFRANO TECNOLOGIA • ENGENHARIA GEOTÉCNICA E ESTRUTURAL</text>',
        f'<text x="56" y="78" fill="{cor_texto}" font-size="20" font-weight="700">Fundações Profundas — {res.identificacao_projeto} (ABNT NBR 6122:2022)</text>',
        f'<rect x="1170" y="40" width="220" height="44" rx="8" fill="{status_cor}" fill-opacity="0.15" stroke="{status_cor}" stroke-width="1.5"/>',
        f'<circle cx="1192" cy="62" r="6" fill="{status_cor}"/>',
        f'<text x="1208" y="67" fill="{status_cor}" font-size="13" font-weight="700">{status_texto}</text>',
    ])

    # Coluna Esquerda: Cartões de Dados (x: 30, w: 420)
    # Card 1: Geometria e Ações
    svg_linhas.extend([
        f'<rect x="30" y="116" width="420" height="230" rx="10" fill="{cor_card}" stroke="{cor_borda}" stroke-width="1.2" filter="url(#shadow)"/>',
        f'<text x="50" y="144" fill="{cor_ciano}" font-size="14" font-weight="700">1. GEOMETRIA E CARREGAMENTO</text>',
        f'<line x1="50" y1="154" x2="430" y2="154" stroke="{cor_borda}" stroke-width="1"/>',
        f'<text x="50" y="180" fill="{cor_texto_mut}" font-size="13">Processo Executivo:</text>',
        f'<text x="430" y="180" text-anchor="end" fill="{cor_texto}" font-size="13" font-weight="600">{res.processo_executivo.value}</text>',
        f'<text x="50" y="206" fill="{cor_texto_mut}" font-size="13">Tipo de Seção / Diâmetro:</text>',
        f'<text x="430" y="206" text-anchor="end" fill="{cor_texto}" font-size="13">{res.geometria.tipo_secao.value} ({_fmt(res.geometria.diametro_ou_lado_m, 2)} m)</text>',
        f'<text x="50" y="232" fill="{cor_texto_mut}" font-size="13">Comprimento do Fuste:</text>',
        f'<text x="430" y="232" text-anchor="end" fill="{cor_texto}" font-size="13">{_fmt(res.geometria.comprimento_fuste_m, 2)} m</text>',
        f'<text x="50" y="258" fill="{cor_texto_mut}" font-size="13">Carga Normal de Compressão (Nk):</text>',
        f'<text x="430" y="258" text-anchor="end" fill="{cor_laranja}" font-size="15" font-weight="700">{_fmt(res.solicitacao.forca_normal_compressao_kn, 2)} kN</text>',
        f'<text x="50" y="290" fill="{cor_texto_mut}" font-size="11" font-style="italic">Dimensionamento conforme critérios de ruptura e serviço.</text>',
    ])

    # Card 2: Capacidade Geotécnica Comparativa
    svg_linhas.extend([
        f'<rect x="30" y="362" width="420" height="230" rx="10" fill="{cor_card}" stroke="{cor_borda}" stroke-width="1.2" filter="url(#shadow)"/>',
        f'<text x="50" y="390" fill="{cor_ciano}" font-size="14" font-weight="700">2. CAPACIDADE DE CARGA GEOTÉCNICA</text>',
        f'<line x1="50" y1="400" x2="430" y2="400" stroke="{cor_borda}" stroke-width="1"/>',
        f'<text x="50" y="426" fill="{cor_texto_mut}" font-size="13">Aoki-Velloso (R_adm):</text>',
        f'<text x="430" y="426" text-anchor="end" fill="{cor_texto}" font-size="13">{_fmt(res.aoki_velloso.capacidade_admissivel_kn, 2)} kN (Rp: {_fmt(res.aoki_velloso.resistencia_ponta_kn, 0)} | Rl: {_fmt(res.aoki_velloso.resistencia_lateral_kn, 0)})</text>',
        f'<text x="50" y="452" fill="{cor_texto_mut}" font-size="13">Décourt-Quaresma (R_adm):</text>',
        f'<text x="430" y="452" text-anchor="end" fill="{cor_texto}" font-size="13">{_fmt(res.decourt_quaresma.capacidade_admissivel_kn, 2)} kN (Rp: {_fmt(res.decourt_quaresma.resistencia_ponta_kn, 0)} | Rl: {_fmt(res.decourt_quaresma.resistencia_lateral_kn, 0)})</text>',
        f'<text x="50" y="478" fill="{cor_texto_mut}" font-size="13">Fator de Segurança Geotécnico:</text>',
        f'<text x="430" y="478" text-anchor="end" fill="{cor_texto}" font-size="13">FS = {_fmt(res.fator_seguranca_geotecnico_adotado, 1)}</text>',
        f'<text x="50" y="508" fill="{cor_texto_mut}" font-size="13">Capacidade Adotada por Estaca:</text>',
        f'<text x="430" y="508" text-anchor="end" fill="{cor_verde}" font-size="15" font-weight="700">{_fmt(res.capacidade_admissivel_adotada_kn, 2)} kN</text>',
        f'<text x="50" y="534" fill="{cor_texto_mut}" font-size="13">Capacidade do Bloco de Coroamento:</text>',
        f'<text x="430" y="534" text-anchor="end" fill="{cor_ciano}" font-size="15" font-weight="700">{_fmt(res.capacidade_admissivel_bloco_kn, 2)} kN</text>',
    ])

    # Card 3: Verificação Estrutural do Fuste
    st_fuste_cor = cor_verde if res.estrutural.aprovado_estruturalmente else cor_vermelho
    st_fuste_txt = "FUSTE APROVADO" if res.estrutural.aprovado_estruturalmente else "FUSTE REPROVADO"

    svg_linhas.extend([
        f'<rect x="30" y="608" width="420" height="254" rx="10" fill="{cor_card}" stroke="{cor_borda}" stroke-width="1.2" filter="url(#shadow)"/>',
        f'<text x="50" y="636" fill="{cor_ciano}" font-size="14" font-weight="700">3. SEGURANÇA ESTRUTURAL DO FUSTE</text>',
        f'<line x1="50" y1="646" x2="430" y2="646" stroke="{cor_borda}" stroke-width="1"/>',
        f'<text x="50" y="672" fill="{cor_texto_mut}" font-size="13">Classe do Concreto (fck):</text>',
        f'<text x="430" y="672" text-anchor="end" fill="{cor_texto}" font-size="13" font-weight="600">{_fmt(res.geometria.fck_concreto_mpa, 1)} MPa</text>',
        f'<text x="50" y="698" fill="{cor_texto_mut}" font-size="13">Área de Aço Adotada (As):</text>',
        f'<text x="430" y="698" text-anchor="end" fill="{cor_texto}" font-size="13">{_fmt(res.estrutural.area_armadura_adotada_cm2, 2)} cm² (Mín: {_fmt(res.estrutural.area_armadura_minima_cm2, 2)} cm²)</text>',
        f'<text x="50" y="724" fill="{cor_texto_mut}" font-size="13">Tensão de Trabalho no Concreto:</text>',
        f'<text x="430" y="724" text-anchor="end" fill="{cor_texto}" font-size="13">{_fmt(res.estrutural.tensao_trabalho_concreto_kpa / 1000, 2)} MPa</text>',
        f'<text x="50" y="750" fill="{cor_texto_mut}" font-size="13">Carga Normal Estrutural Admissível:</text>',
        f'<text x="430" y="750" text-anchor="end" fill="{st_fuste_cor}" font-size="14" font-weight="700">{_fmt(res.estrutural.forca_normal_admissivel_estrutural_kn, 2)} kN</text>',
        f'<rect x="50" y="770" width="380" height="32" rx="6" fill="{st_fuste_cor}" fill-opacity="0.15" stroke="{st_fuste_cor}" stroke-width="1"/>',
        f'<text x="240" y="791" text-anchor="middle" fill="{st_fuste_cor}" font-size="12" font-weight="700">{st_fuste_txt}</text>',
        f'<text x="50" y="830" fill="{cor_texto_mut}" font-size="11">Minoração executiva do concreto aplicada conforme NBR 6122.</text>',
    ])

    # Área Central: Desenho Esquemático do Perfil Geotécnico e Fuste (x: 474, w: 490, h: 746)
    svg_linhas.extend([
        f'<rect x="474" y="116" width="490" height="746" rx="10" fill="{cor_card}" stroke="{cor_borda}" stroke-width="1.2" filter="url(#shadow)"/>',
        f'<text x="494" y="144" fill="{cor_ciano}" font-size="14" font-weight="700">PERFIL ESTRATIGRÁFICO E FUSTE DA ESTACA</text>',
        f'<line x1="494" y1="154" x2="944" y2="154" stroke="{cor_borda}" stroke-width="1"/>',
        # Nível do terreno (cota 0.00)
        '<line x1="500" y1="200" x2="938" y2="200" stroke="#94a3b8" stroke-width="2" stroke-dasharray="8,4"/>',
        '<text x="510" y="192" fill="#94a3b8" font-size="11">Cota do Terreno (0.00 m)</text>',
        # Bloco de Coroamento no topo
        '<rect x="630" y="170" width="180" height="60" rx="4" fill="#334155" stroke="#94a3b8" stroke-width="2"/>',
        '<text x="720" y="205" text-anchor="middle" fill="#f8fafc" font-size="12" font-weight="700">BLOCO DE COROAMENTO</text>',
        # Vetor de Carga Vertical Nk atuando no bloco
        f'<path d="M 720 125 L 720 165" stroke="{cor_laranja}" stroke-width="4"/>',
        f'<polygon points="714,160 726,160 720,170" fill="{cor_laranja}"/>',
        f'<text x="735" y="145" fill="{cor_laranja}" font-size="12" font-weight="700">Nk = {_fmt(res.solicitacao.forca_normal_compressao_kn, 0)} kN</text>',
        # Fuste da estaca
        '<rect x="700" y="230" width="40" height="480" fill="#64748b" stroke="#cbd5e1" stroke-width="2"/>',
        '<text x="750" y="470" fill="#cbd5e1" font-size="12" font-weight="600">FUSTE</text>',
        f'<text x="750" y="490" fill="{cor_texto_mut}" font-size="11">D = {_fmt(res.geometria.diametro_ou_lado_m, 2)} m</text>',
        f'<text x="750" y="510" fill="{cor_texto_mut}" font-size="11">L = {_fmt(res.geometria.comprimento_fuste_m, 2)} m</text>',
        # Bulbo / Ponta da estaca
        f'<ellipse cx="720" cy="710" rx="30" ry="20" fill="#475569" stroke="{cor_laranja}" stroke-width="2"/>',
        f'<text x="720" y="745" text-anchor="middle" fill="{cor_laranja}" font-size="11" font-weight="700">PONTA DA ESTACA</text>',
        # Setas de atrito lateral
        '<path d="M 685 300 L 695 300 M 690 295 L 695 300 L 690 305" stroke="#38bdf8" stroke-width="2"/>',
        '<path d="M 685 450 L 695 450 M 690 445 L 695 450 L 690 455" stroke="#38bdf8" stroke-width="2"/>',
        '<path d="M 685 600 L 695 600 M 690 595 L 695 600 L 690 605" stroke="#38bdf8" stroke-width="2"/>',
        '<path d="M 755 300 L 745 300 M 750 295 L 745 300 L 750 305" stroke="#38bdf8" stroke-width="2"/>',
        '<path d="M 755 450 L 745 450 M 750 445 L 745 450 L 750 455" stroke="#38bdf8" stroke-width="2"/>',
        '<path d="M 755 600 L 745 600 M 750 595 L 745 600 L 750 605" stroke="#38bdf8" stroke-width="2"/>',
        '<text x="580" y="470" fill="#38bdf8" font-size="11" font-weight="600">Atrito Lateral (Rl)</text>',
        # Reação de ponta
        '<path d="M 720 780 L 720 735" stroke="#f97316" stroke-width="3"/>',
        '<polygon points="715,745 725,745 720,735" fill="#f97316"/>',
        '<text x="720" y="805" text-anchor="middle" fill="#f97316" font-size="11" font-weight="600">Reação de Ponta (Rp)</text>',
    ])

    # Coluna Direita: Especificações e Alertas (x: 988, w: 422)
    svg_linhas.extend([
        f'<rect x="988" y="116" width="422" height="746" rx="10" fill="{cor_card}" stroke="{cor_borda}" stroke-width="1.2" filter="url(#shadow)"/>',
        f'<text x="1008" y="144" fill="{cor_ciano}" font-size="14" font-weight="700">MEMÓRIA TÉCNICA E RECOMENDAÇÕES</text>',
        f'<line x1="1008" y1="154" x2="1390" y2="154" stroke="{cor_borda}" stroke-width="1"/>',
        f'<rect x="1008" y="170" width="382" height="210" rx="8" fill="#0f172a" stroke="{cor_azul}" stroke-width="1.2"/>',
        f'<text x="1024" y="196" fill="{cor_azul}" font-size="13" font-weight="700">MÉTODO COMPARATIVO AOKI X DÉCOURT</text>',
        f'<line x1="1024" y1="206" x2="1374" y2="206" stroke="{cor_borda}" stroke-width="1"/>',
        f'<text x="1024" y="230" fill="{cor_texto_mut}" font-size="12">Ponta Aoki-Velloso:</text>',
        f'<text x="1374" y="230" text-anchor="end" fill="{cor_texto}" font-size="12">{_fmt(res.aoki_velloso.resistencia_ponta_kn, 1)} kN</text>',
        f'<text x="1024" y="254" fill="{cor_texto_mut}" font-size="12">Lateral Aoki-Velloso:</text>',
        f'<text x="1374" y="254" text-anchor="end" fill="{cor_texto}" font-size="12">{_fmt(res.aoki_velloso.resistencia_lateral_kn, 1)} kN</text>',
        f'<text x="1024" y="278" fill="{cor_texto_mut}" font-size="12">Ponta Décourt-Quaresma:</text>',
        f'<text x="1374" y="278" text-anchor="end" fill="{cor_texto}" font-size="12">{_fmt(res.decourt_quaresma.resistencia_ponta_kn, 1)} kN</text>',
        f'<text x="1024" y="302" fill="{cor_texto_mut}" font-size="12">Lateral Décourt-Quaresma:</text>',
        f'<text x="1374" y="302" text-anchor="end" fill="{cor_texto}" font-size="12">{_fmt(res.decourt_quaresma.resistencia_lateral_kn, 1)} kN</text>',
        f'<text x="1024" y="330" fill="{cor_texto_mut}" font-size="12">Critério de Adotação:</text>',
        f'<text x="1374" y="330" text-anchor="end" fill="{cor_verde}" font-size="12" font-weight="700">Menor Valor (Envoltória Mínima)</text>',
        f'<text x="1024" y="356" fill="{cor_texto_mut}" font-size="11" font-style="italic">Preserva margem de segurança contra heterogeneidade do solo.</text>',
    ])

    # Caixa de Alertas
    if res.alertas_tecnicos:
        svg_linhas.extend([
            f'<rect x="1008" y="400" width="382" height="280" rx="8" fill="#7f1d1d" fill-opacity="0.3" stroke="{cor_vermelho}" stroke-width="1"/>',
            f'<text x="1024" y="426" fill="{cor_vermelho}" font-size="12" font-weight="700">ALERTAS E RECOMENDAÇÕES NORMATIVAS:</text>',
        ])
        y_alerta = 450
        for al in res.alertas_tecnicos[:5]:
            texto_curto = al if len(al) <= 52 else al[:49] + "..."
            svg_linhas.append(f'<text x="1024" y="{y_alerta}" fill="#fca5a5" font-size="11">• {texto_curto}</text>')
            y_alerta += 24
    else:
        svg_linhas.extend([
            f'<rect x="1008" y="400" width="382" height="150" rx="8" fill="#065f46" fill-opacity="0.3" stroke="{cor_verde}" stroke-width="1"/>',
            f'<text x="1024" y="426" fill="{cor_verde}" font-size="12" font-weight="700">STATUS NORMATIVO PLENO:</text>',
            f'<text x="1024" y="454" fill="#a7f3d0" font-size="11">• Capacidade geotécnica superior à carga solicitante.</text>',
            f'<text x="1024" y="478" fill="#a7f3d0" font-size="11">• Fuste de concreto dimensionado conforme NBR 6118.</text>',
            f'<text x="1024" y="502" fill="#a7f3d0" font-size="11">• Armadura longitudinal atende aos requisitos mínimos da NBR 6122.</text>',
        ])

    # Rodapé
    svg_linhas.extend([
        f'<text x="720" y="885" text-anchor="middle" fill="{cor_texto_mut}" font-size="11">Lofrano Tecnologia • Engenharia de Fundações e Geotecnia • São Paulo, Brasil • 2026</text>',
        '</svg>',
    ])

    return "\n".join(svg_linhas)

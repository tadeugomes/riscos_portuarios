"""Emendas do relatório diagramado (revisão de 30/10/2026).

Cada emenda:
  pag      página do PDF (1 = primeira)
  area     (x0, y0, x1, y1) em pontos; todo o texto com centro dentro dela é substituído
  antigo   trechos que PRECISAM existir na área antes da emenda (trava contra emenda no lugar errado)
  blocos   conteúdo novo, em ordem: ("b", markup) item com marcador; ("p", markup) parágrafo;
           ("h", texto, estilo, x) título de uma linha; ("col2", itens) lista numerada em duas colunas
  limite   linha de base máxima permitida para a última linha composta
  numeros  {"texto no PDF": "chave em numeros_referencia.json"} conferidos contra a base
  motivo   texto da nota de prova
Markup: **negrito** usa o estilo de rótulo do parágrafo.
"""

N = "numeros"
B, P, H = "b", "p", "h"

EMENDAS = [
    # ------------------------------------------------------------------ p. 22
    dict(pag=22, area=(130, 712, 525, 762), antigo=["57 pares de comparação"],
         blocos=[(P, "Para avaliar a evolução percebida dos riscos entre horizontes temporais, foi "
                     "estruturado um pipeline estatístico de dispersão com os 76 pares de comparação "
                     "entre curto e longo prazo, um para cada variável do questionário.", dict(x1=137, x2=137))],
         limite=760, numeros={"76 pares": "n_pares_temporais"},
         motivo="O questionário tem 76 variáveis, todas com respostas de curto e longo prazo. A base de 57 "
                "pares resultou de falha no pareamento automático (19 variáveis não casadas, entre elas 12 "
                "tecnológicas), não de critério metodológico. A análise foi refeita com os 76 pares."),
    # ------------------------------------------------------------------ p. 34
    dict(pag=34, area=(130, 112, 525, 162), antigo=["6 riscos imediatos críticos"],
         blocos=[(B, "Os participantes da pesquisa apontam 9 riscos imediatos críticos (pelo menos 40% "
                     "das respostas nos níveis 4-5), liderados por instabilidade política, excesso "
                     "regulatório e conflitos geoeconômicos.")],
         limite=160, numeros={"9 riscos": "n_criticos_imediatos_ge40"},
         motivo="São 9 riscos com pelo menos 40% em níveis 4-5 no horizonte imediato (inclui 5.4 e 5.16, "
                "com 41,6%, e 1.6, com 40,0%). Critério ≥40% alinhado às seções 4.2.1 e 4.3.1."),
    dict(pag=34, area=(130, 172, 525, 237), antigo=["78% das variáveis", "+0,56", "delta 0,00"],
         blocos=[(B, "73,7% das variáveis (56 de 76) permanecem crônicas em curto e longo prazo. "
                     "Geopolítica (+0,57) e Ambiental (+0,53) lideram a piora temporal, enquanto "
                     "Tecnologia tem leve alta (+0,19), expondo uma lacuna entre pressão climática "
                     "crescente e maturidade digital.")],
         limite=235, numeros={"73,7%": "pct_cronicos", "56 de 76": "quadrantes.cronicos",
                              "+0,57": "por_dimensao.Geopolítica.delta_medio",
                              "+0,53": "por_dimensao.Ambiental.delta_medio",
                              "+0,19": "por_dimensao.Tecnológica.delta_medio"},
         motivo="78% não corresponde a nenhuma base. Com 76 pares: 56 crônicas (73,7%). A geopolítica "
                "(+0,57) passa a ter a maior piora; tecnologia +0,19, não 0,00."),
    dict(pag=34, area=(130, 336, 525, 401), antigo=["13 dos 20", "(-0,05)"],
         blocos=[(B, "**Econômica:** 12 dos 20 riscos imediatos com maior avaliação pertencem a esta "
                     "dimensão, com média de 40,3% das respostas em níveis altos; o delta temporal (0,00) "
                     "indica estabilidade na percepção sobre a dimensão. Variação considerando as "
                     "respostas para o período de 2025 a 2035.")],
         limite=400, numeros={"(0,00)": "por_dimensao.Econômica.delta_medio",
                              "12 dos 20": "top20.economicos", "40,3%": "top20.media_economicos"},
         motivo="Entre os 20 maiores riscos imediatos (Gráfico 5) há 12 econômicos, não 13. Os 39% eram a "
                "média dos 20 riscos de todas as dimensões; a média dos 12 econômicos é 40,3%. Delta 0,00 com 76 pares."),
    dict(pag=34, area=(130, 411, 525, 446), antigo=["+0,56", "cinco variáveis"],
         blocos=[(B, "**Ambiental:** Aumento médio de +0,53 e nove variáveis com salto de +1,0 ponto, "
                     "puxadas por eventos climáticos extremos e gestão de resíduos.")],
         limite=445, numeros={"+0,53": "por_dimensao.Ambiental.delta_medio",
                              "nove variáveis": "por_dimensao.Ambiental.pioras_1"},
         motivo="Delta ambiental com 76 pares: +0,53. São 9 variáveis com +1,0 (o próprio capítulo 6 lista 9), não cinco."),
    dict(pag=34, area=(130, 456, 525, 536), antigo=["+0,40"],
         blocos=[(B, "**Geopolítica:** Embora apresente menor diversidade de riscos, observa-se elevada "
                     "relevância atribuída a eventos geopolíticos, especialmente aos conflitos "
                     "geoeconômicos e a ameaças de natureza biológica. O aumento médio de +0,57 entre "
                     "curto e longo prazo indica intensificação da influência de fatores externos sobre o "
                     "ambiente operacional e estratégico dos portos.")],
         limite=535, numeros={"+0,57": "por_dimensao.Geopolítica.delta_medio"},
         motivo="Com as 7 variáveis geopolíticas (eram 5), o delta é +0,57, o maior entre as dimensões."),
    dict(pag=34, area=(130, 546, 525, 641), antigo=["+0,08"],
         blocos=[(B, "**Social:** Riscos de direitos humanos e pressões trabalhistas mantêm-se em nível "
                     "moderado, com leve aumento (+0,07) ao longo do horizonte temporal. Esse comportamento "
                     "indica que a mitigação desses riscos depende de ações coordenadas de capacitação, "
                     "voltadas ao fortalecimento de práticas laborais, à conformidade normativa e à "
                     "disseminação de padrões institucionais de responsabilidade social no setor portuário.")],
         limite=640, numeros={"+0,07": "por_dimensao.Social.delta_medio"},
         motivo="Delta social com 15 variáveis: +0,07. Corrigido também o ponto final duplicado."),
    dict(pag=34, area=(130, 651, 525, 701), antigo=["Disrupções em infraestruturas críticas digitais", "(delta 0,00)"],
         blocos=[(B, "**Tecnológica:** Falta de segurança computacional e escassez de mão de obra "
                     "qualificada em tecnologia (41,6% cada) estão entre os nove riscos prioritários, com "
                     "leve piora temporal (delta +0,19).")],
         limite=700, numeros={"+0,19": "por_dimensao.Tecnológica.delta_medio", "41,6%": "pct.5.4"},
         motivo="Disrupções em infraestruturas críticas (1.7) é variável da dimensão Econômica. Os riscos "
                "tecnológicos entre os críticos são 5.4 e 5.16 (41,6%). Delta tecnológico com 16 variáveis: +0,19."),
    # ------------------------------------------------------------------ p. 35 (Tabela 6)
    dict(pag=35, area=(150, 134, 270, 158), antigo=["13/20"],
         blocos=[(P, "12/20 maiores riscos imediatos;\nmédias >2,5", dict(tabela=(156.39, 268)))],
         limite=158, numeros={"12/20": "top20.economicos"}, motivo="12 dos 20 maiores riscos imediatos são econômicos."),
    dict(pag=35, area=(385, 134, 505, 158), antigo=["(delta -0,05)"],
         blocos=[(P, "Estável em patamar crítico\n(delta 0,00)", dict(tabela=(390.14, 500)))],
         limite=158, numeros={"0,00": "por_dimensao.Econômica.delta_medio"}, motivo="Delta econômico com 21 variáveis: 0,00."),
    dict(pag=35, area=(150, 177, 270, 201), antigo=["+0,56", "5 variáveis"],
         blocos=[(P, "Delta médio +0,53; 9 variáveis\npioram +1 ponto", dict(tabela=(156.39, 268)))],
         limite=201, numeros={"+0,53": "por_dimensao.Ambiental.delta_medio", "9 variáveis": "por_dimensao.Ambiental.pioras_1"},
         motivo="Delta ambiental +0,53; 9 variáveis com +1,0."),
    dict(pag=35, area=(385, 201, 505, 225), antigo=["+0,40"],
         blocos=[(P, "Maior piora (delta +0,57) e\nalta interdependência", dict(tabela=(390.14, 500)))],
         limite=225, numeros={"+0,57": "por_dimensao.Geopolítica.delta_medio"}, motivo="Delta geopolítico +0,57, o maior."),
    dict(pag=35, area=(385, 224, 505, 248), antigo=["+0,08"],
         blocos=[(P, "Leve alta (+0,07) mantendo\nvigilância contínua", dict(tabela=(390.14, 500)))],
         limite=248, numeros={"+0,07": "por_dimensao.Social.delta_medio"}, motivo="Delta social +0,07."),
    dict(pag=35, area=(150, 248, 270, 272), antigo=["Disrupções digitais 44,8%"],
         blocos=[(P, "Segurança computacional\n41,6% em níveis altos", dict(tabela=(156.39, 268)))],
         limite=272, numeros={"41,6%": "pct.5.4"},
         motivo="Os 44,8% são da variável 1.7 (Econômica). O maior risco tecnológico imediato é 5.4 (41,6%, empatado com 5.16)."),
    dict(pag=35, area=(385, 248, 505, 272), antigo=["Estabilidade (delta 0,00)"],
         blocos=[(P, "Leve piora (delta +0,19) e\nvulnerabilidade latente", dict(tabela=(390.14, 500)))],
         limite=272, numeros={"+0,19": "por_dimensao.Tecnológica.delta_medio"}, motivo="Delta tecnológico +0,19."),
    # ------------------------------------------------------------------ p. 38 (quadro)
    dict(pag=38, area=(130, 684, 520, 798), antigo=["6 riscos críticos", "(>40%", "todos"],
         blocos=[("box38", None)], limite=797,
         numeros={"9 riscos críticos": "n_criticos_imediatos_ge40", "50,4%": "pct.1.15", "46,4%": "pct.1.16",
                  "45,6%": "pct.1.14", "44,8%": "pct.1.7", "41,6%": "pct.5.16", "40,0%": "pct.1.6"},
         motivo="O Gráfico 5 mostra 9 riscos com pelo menos 40%: faltavam 5.4 e 5.16 (Tecnológica, 41,6%) e "
                "1.6 (cadeias de suprimentos, 40,0%). A afirmação 'todos concentrados nas dimensões Econômica "
                "e Geopolítica' é falsa. Percentuais com uma casa, como no Gráfico 5."),
    # ------------------------------------------------------------------ p. 39
    dict(pag=39, area=(130, 97, 525, 131), antigo=["com 13 dos riscos analisados e média de 39%"],
         blocos=[(B, "**Dimensão Econômica:** Apresenta a maior concentração de riscos críticos, com 12 "
                     "dos 20 maiores riscos e média de 40,3% de percepção de risco alto.")],
         limite=130, numeros={"12": "top20.economicos", "40,3%": "top20.media_economicos"},
         motivo="12 dos 20 maiores riscos imediatos são econômicos, com média de 40,3%."),
    # ------------------------------------------------------------------ p. 40 e 42 (quadros)
    dict(pag=40, area=(130, 127, 515, 156), antigo=["(>40%", "todos con"],
         blocos=[(P, "Foram identificados **14 riscos críticos** (pelo menos 40% em níveis altos): "
                     "10 econômicos, 3 tecnológicos e 1 geopolítico:",
                  dict(x1=136.38, x2=136.38, normal="l10", bold="blk10", leading=12, direita=510, justificar=False))],
         limite=153, numeros={"14 riscos": "curto_ge40.total", "10 econômicos": "curto_ge40.Econômica",
                              "3 tecnológicos": "curto_ge40.Tecnológica", "1 geopolítico": "curto_ge40.Geopolítica"},
         motivo="A lista inclui 40,0% (logo o critério é ≥40%) e tem 3 riscos tecnológicos: não estão 'todos' "
                "nas dimensões Econômica e Geopolítica."),
    dict(pag=42, area=(110, 131, 500, 159), antigo=["(>40%", "todos con"],
         blocos=[(P, "Foram identificados 31 riscos críticos (pelo menos 40% em níveis altos): 13 econômicos, "
                     "6 tecnológicos, 5 ambientais, 4 sociais e 3 geopolíticos:",
                  dict(x1=115.57, x2=115.57, normal="l10", bold="l10b", leading=12, direita=496, justificar=False))],
         limite=156, numeros={"31 riscos": "longo_ge40.total", "13 econômicos": "longo_ge40.Econômica",
                              "6 tecnológicos": "longo_ge40.Tecnológica", "5 ambientais": "longo_ge40.Ambiental",
                              "4 sociais": "longo_ge40.Social", "3 geopolíticos": "longo_ge40.Geopolítica"},
         motivo="Os 31 riscos com pelo menos 40% estão nas cinco dimensões, não 'todos' na Econômica e Geopolítica."),
    # ------------------------------------------------------------------ p. 44
    dict(pag=44, area=(130, 606, 525, 731), antigo=["r = 0,63", "+0,19 ponto", "74% dos riscos"],
         blocos=[(B, "**Correlação moderada (r = 0,57):** Indica que a hierarquia de riscos tende a se "
                     "manter, mas com mudanças significativas em casos específicos"),
                 (B, "**Delta médio de +0,22 ponto:** Sugere uma leve piora geral dos riscos ao longo do tempo", 15),
                 (B, "**73,7% dos riscos são crônicos:** 56 das 76 variáveis permanecem em níveis elevados "
                     "em ambos os horizontes temporais.", 15)],
         limite=730, numeros={"0,57": "correlacao_medianas", "+0,22": "delta_medio_geral",
                              "73,7%": "pct_cronicos", "56 das 76": "quadrantes.cronicos"},
         motivo="Recalculado com 76 pares (correlação de Pearson entre medianas de curto e longo prazo; delta médio das medianas)."),
    # ------------------------------------------------------------------ p. 45
    dict(pag=45, area=(130, 97, 525, 176), antigo=["42 variáveis", "11 variáveis"],
         blocos=[(B, "**Quadrante 1 - Riscos Crônicos (alto x alto):** 56 variáveis, principalmente "
                     "econômicas, tecnológicas e sociais"),
                 (B, "**Quadrante 2 - Riscos Emergentes (baixo x alto):** 16 variáveis, metade delas "
                     "ambientais", 15)],
         limite=174, numeros={"56 variáveis": "quadrantes.cronicos", "16 variáveis": "quadrantes.emergentes"},
         motivo="Quadrantes com 76 pares: 56 crônicas (21 econômicas, 13 tecnológicas, 11 sociais), 16 "
                "emergentes (8 ambientais), 4 controladas, 0 em melhoria. São os números do próprio Gráfico 8."),
    dict(pag=45, area=(130, 546, 525, 761), antigo=["+0,56", "-0,05", "+0,40", "+0,08", "0,00"],
         blocos=[(B, "**Ambiental:** Piora temporal de +0,53, com 9 variáveis aumentando +1,0 ponto"),
                 (B, "**Econômica:** Relativa estabilidade (delta 0,00), com riscos mantidos em níveis elevados", 15),
                 (B, "**Geopolítica:** Maior piora temporal (delta +0,57), com 4 variáveis aumentando +1,0 ponto", 15),
                 (B, "**Social:** Variação leve (delta +0,07), com preocupações consistentes sobre direitos humanos", 15),
                 (B, "**Tecnológica:** Leve piora (delta +0,19), com 3 variáveis aumentando +1,0 ponto", 15)],
         limite=760, numeros={"+0,53": "por_dimensao.Ambiental.delta_medio", "9 variáveis": "por_dimensao.Ambiental.pioras_1",
                              "0,00": "por_dimensao.Econômica.delta_medio", "+0,57": "por_dimensao.Geopolítica.delta_medio",
                              "4 variáveis": "por_dimensao.Geopolítica.pioras_1", "+0,07": "por_dimensao.Social.delta_medio",
                              "+0,19": "por_dimensao.Tecnológica.delta_medio", "3 variáveis": "por_dimensao.Tecnológica.pioras_1"},
         motivo="Deltas por dimensão com 76 pares. A ambiental tinha 9 variáveis com +1,0 (não 5)."),
    # ------------------------------------------------------------------ p. 46
    dict(pag=46, area=(130, 98, 525, 161), antigo=["desafios ambientais que mostram o maior"],
         blocos=[(P, "A ausência de riscos em melhoria (Quadrante 4 vazio) e a predominância de riscos "
                     "crônicos destacam a necessidade de ações preventivas e mitigatórias contínuas, "
                     "especialmente para os desafios geopolíticos e ambientais, que mostram o maior "
                     "agravamento temporal.", dict(x1=137, x2=137))],
         limite=160, numeros={}, motivo="Com 76 pares, a geopolítica (+0,57) e a ambiental (+0,53) têm as maiores pioras."),
    dict(pag=46, area=(130, 203, 525, 281), antigo=["57 variáveis de risco"],
         blocos=[(P, "O Gráfico 9 apresenta a evolução das médias das 23 variáveis com média igual ou superior "
                     "a 3,0 no curto prazo (2026-2027), conectando cada uma ao seu valor no longo prazo (até "
                     "2035). Cada linha corresponde a uma variável, identificada pelo código e pelo rótulo "
                     "central.", dict(x1=137, x2=137))],
         limite=280, numeros={"23 variáveis": "grafico9_n"},
         motivo="O Gráfico 9 não mostrava 57 variáveis: mostrava 18 (média de curto prazo ≥3,0 dentro da base de 57). "
                "Regerado com as 23 variáveis da base completa (inclui 5.16, 5.4, 1.13, 5.15 e 4.9); texto descreve o que o gráfico mostra."),
    # ------------------------------------------------------------------ p. 47 (seções 4.5.1.1 a 4.5.1.3)
    dict(pag=47, area=(118, 140, 525, 792),
         antigo=["(16 variáveis)", "(4 variáveis)", "11 variáveis", "infraestruturas críticas", "42 variáveis (74% do total)"],
         blocos=[(B, "**Ambiental (17 variáveis):** Segunda maior piora, delta médio de +0,53"),
                 (B, "**Econômica (21 variáveis):** Menor variação, com delta médio de 0,00"),
                 (B, "**Geopolítica (7 variáveis):** Maior piora, com delta médio de +0,57"),
                 (B, "**Social (15 variáveis):** Piora leve, com delta médio de +0,07"),
                 (B, "**Tecnológica (16 variáveis):** Piora leve, com delta médio de +0,19."),
                 (H, "4.5.1.2 Principais Padrões Identificados", "h_az", 125.0, 15),
                 (H, "Pioras Críticas (+1,0 ponto) - 18 variáveis:", "h_pt", 137.0, 15),
                 (B, "**Ambiental (9 variáveis):** Mudanças climáticas, aumento do nível do mar, poluição, "
                     "espécies exóticas, resíduos, desmatamento, ruídos, patógenos, produtos perigosos;", 15),
                 (B, "**Geopolítica (4 variáveis):** Terrorismo, liberação de contaminantes, alterações em "
                     "sistemas terrestres, migração forçada;"),
                 (B, "**Tecnológica (3 variáveis):** Tecnologias avançadas, censura e vigilância adversa, "
                     "navios autônomos;"),
                 (B, "**Econômica (1 variável):** Risco de competitividade portuária;"),
                 (B, "**Social (1 variável):** Ameaças aos direitos humanos."),
                 (H, "Melhoria Significativa (-1,0 ponto) - 1 variável:", "h_pt", 137.0, 15),
                 (B, "**Econômica:** Falhas, interrupções ou disrupções em cadeias de suprimentos relevantes", 15),
                 (H, "Estabilidade (57 variáveis, 53 em níveis elevados):", "h_pt", 137.0, 15),
                 (B, "Predominância de riscos econômicos mantidos em mediana 3,0-4,0", 15),
                 (B, "Riscos tecnológicos: 13 de 16 estáveis em mediana 3,0"),
                 (B, "Riscos sociais com variações mínimas (14 de 15 estáveis)."),
                 (H, "4.5.1.3 Análise Estatística Geral (Mediana ≥ 3,0 no Curto Prazo)", "h_az", 125.0, 15),
                 (B, "**Total analisado:** 56 variáveis (73,7% do total)", 15),
                 (B, "**Delta médio geral:** 0,02 (equilíbrio geral)"),
                 (B, "**Desvio padrão:** 0,23 (baixa variabilidade)"),
                 (B, "**Variáveis com piora:** 2 (4%)"),
                 (B, "**Variáveis com melhoria:** 1 (2%)"),
                 (B, "**Variáveis estáveis:** 53 (95%).")],
         limite=790,
         numeros={"(17 variáveis)": "por_dimensao.Ambiental.n", "(21 variáveis)": "por_dimensao.Econômica.n",
                  "(7 variáveis)": "por_dimensao.Geopolítica.n", "(15 variáveis)": "por_dimensao.Social.n",
                  "(16 variáveis)": "por_dimensao.Tecnológica.n", "18 variáveis": "n_pioras_1",
                  "(9 variáveis)": "por_dimensao.Ambiental.pioras_1", "(4 variáveis)": "por_dimensao.Geopolítica.pioras_1",
                  "(3 variáveis)": "por_dimensao.Tecnológica.pioras_1", "57 variáveis": "estaveis",
                  "53 em níveis": "subconjunto_mediana_curto_ge3.estaveis", "13 de 16": "por_dimensao.Tecnológica.estaveis",
                  "14 de 15": "por_dimensao.Social.estaveis", "56 variáveis": "subconjunto_mediana_curto_ge3.n",
                  "(73,7% do total)": "subconjunto_mediana_curto_ge3.pct", "0,02": "subconjunto_mediana_curto_ge3.delta_medio",
                  "0,23": "subconjunto_mediana_curto_ge3.desvio", "piora: 2": "subconjunto_mediana_curto_ge3.pioras",
                  "melhoria: 1": "subconjunto_mediana_curto_ge3.melhorias", "estáveis: 53": "subconjunto_mediana_curto_ge3.estaveis"},
         motivo="Seção inteira recalculada com 76 pares. Erros da versão anterior: título dizia 11 pioras e "
                "a lista somava 12; a melhoria de -1,0 é da variável 1.6 (cadeias de suprimentos), não de "
                "infraestruturas críticas (1.7); 42/57 = 73,7% aparecia como 74% sem denominador."),
    # ------------------------------------------------------------------ p. 48 (4.5.1.4 e 4.5.1.5)
    dict(pag=48, area=(118, 140, 525, 792),
         antigo=["Falhas em infraestruturas críticas", "40 variáveis permaneceram", "Foco em Dois Pontos"],
         blocos=[(B, "**Cadeias de suprimentos (Econômica):** 4,00 para 3,00 (-1,00)."),
                 (H, "Mudanças Significativas de Piora:", "h_pt", 133.0, 15),
                 (B, "**Mudanças climáticas (Ambiental):** 3,00 para 4,00 (+1,00);", 15),
                 (B, "**Competitividade portuária (Econômica):** 3,00 para 4,00 (+1,00)."),
                 (H, "Estabilidade Generalizada:", "h_pt", 133.0, 15),
                 (B, "**53 variáveis permaneceram inalteradas, indicando percepção consolidada de risco**", 15),
                 (B, "**Econômica:** 19 variáveis estáveis em níveis elevados (3,0-4,0)"),
                 (B, "**Social e Tecnológica:** Todas as variáveis (11 e 13) estáveis em mediana 3,0"),
                 (B, "**Ambiental:** 7 variáveis estáveis em mediana 3,0"),
                 (B, "**Geopolítica:** 3 variáveis estáveis, com medianas entre 3,0 e 4,0."),
                 (H, "4.5.1.5 Implicações Estratégicas", "h_az", 121.0, 15),
                 (P, "**Os dados revelam um cenário de alta estabilidade percebida:** 95% das variáveis com "
                     "risco elevado mantiveram-se inalteradas entre os horizontes temporais. Este padrão sugere:",
                  dict(x1=133, x2=133, bold="h_pt", gap=15)),
                 (P, "**1. Consolidação da Percepção de Risco:** Os stakeholders possuem visões bem "
                     "estabelecidas sobre os riscos portuários; **2. Foco em Três Pontos Críticos:** Apenas "
                     "três variáveis mostraram mudança significativa, permitindo ação focada; **3. Prioridade "
                     "para Mudanças Climáticas e Competitividade Portuária:** São as duas variáveis com piora "
                     "significativa e exigem atenção estratégica; **4. Oportunidade nas Cadeias de "
                     "Suprimentos:** A melhoria identificada pode ser alavancada como caso de sucesso. A "
                     "estabilidade predominante indica, na percepção dos gestores, que as estratégias de "
                     "gestão de riscos atuais são adequadas para manter os níveis de risco, mas insuficientes "
                     "para reduzi-los significativamente.", dict(x1=133, x2=133, gap=15))],
         limite=790,
         numeros={"53 variáveis": "subconjunto_mediana_curto_ge3.estaveis",
                  "19 variáveis": "subconjunto_mediana_curto_ge3.estaveis_por_dim.Econômica",
                  "(11 e 13)": "subconjunto_mediana_curto_ge3.estaveis_por_dim.Social|Tecnológica",
                  "7 variáveis": "subconjunto_mediana_curto_ge3.estaveis_por_dim.Ambiental",
                  "3 variáveis": "subconjunto_mediana_curto_ge3.estaveis_por_dim.Geopolítica",
                  "95%": "subconjunto_mediana_curto_ge3.pct_estaveis"},
         motivo="A melhoria (-1,0) é da variável 1.6 (cadeias de suprimentos), não 1.7. Com 76 pares há duas "
                "pioras entre as variáveis de risco elevado (2.3 e 1.13) e 53 estáveis. Os itens 2 a 4 das "
                "implicações foram ajustados a esses fatos."),
    # ------------------------------------------------------------------ p. 53
    dict(pag=53, area=(130, 113, 525, 131), antigo=["19 variáveis com médias superiores a 2.5"],
         blocos=[("linha", "A dimensão econômica apresenta 21 variáveis com médias superiores a 2,5", 137.0)],
         limite=131, numeros={"21 variáveis": "eco_media_curto_gt25"},
         motivo="As 21 variáveis econômicas têm média de curto prazo acima de 2,5. Decimal com vírgula."),
    # ------------------------------------------------------------------ p. 54
    dict(pag=54, area=(130, 172, 525, 191), antigo=["Delta médio de -0,05"],
         blocos=[(B, "**Delta médio de 0,00:** Menor variação média entre as dimensões")],
         limite=190, numeros={"0,00": "por_dimensao.Econômica.delta_medio"},
         motivo="Com 21 variáveis, o delta econômico é 0,00; não há dimensão com melhoria média."),
    dict(pag=54, area=(130, 322, 525, 356), antigo=["Falhas em infraestruturas críticas digitais"],
         blocos=[(B, "**Melhoria Significativa:** Falhas em cadeias de suprimentos apresentam melhoria de "
                     "-1,0 ponto")],
         limite=355, numeros={}, motivo="A variável com -1,0 é 1.6 (cadeias de suprimentos); 1.7 ficou estável."),
    # ------------------------------------------------------------------ p. 82
    dict(pag=82, area=(130, 172, 525, 191), antigo=["Delta médio de +0,56"],
         blocos=[(B, "**Delta médio de +0,53:** Segunda maior piora, após a geopolítica (+0,57)")],
         limite=190, numeros={"+0,53": "por_dimensao.Ambiental.delta_medio", "+0,57": "por_dimensao.Geopolítica.delta_medio"},
         motivo="Com 17 variáveis ambientais, delta +0,53; a geopolítica (+0,57) passa à frente."),
    dict(pag=82, area=(130, 307, 525, 341), antigo=["Evolui de mediana 2,0 para"],
         blocos=[(B, "**Mudanças Climáticas como Principal Risco:** Evolui de mediana 3,0 para 4,0, "
                     "tornando-se crítica")],
         limite=340, numeros={}, motivo="Variável 2.3: mediana 3,0 no curto prazo e 4,0 no longo prazo (não 2,0)."),
    # ------------------------------------------------------------------ p. 106
    dict(pag=106, area=(130, 172, 525, 221), antigo=["+0,40", "2 variáveis com piora crítica"],
         blocos=[(B, "**Delta médio de +0,57:** Maior piora entre as dimensões"),
                 (B, "**4 variáveis com piora crítica (+1,0 ponto):** Terrorismo, contaminantes, sistemas "
                     "terrestres e migração forçada")],
         limite=219, numeros={"+0,57": "por_dimensao.Geopolítica.delta_medio",
                              "4 variáveis": "por_dimensao.Geopolítica.pioras_1"},
         motivo="Com 7 variáveis geopolíticas (3.2 e 3.7 estavam fora), delta +0,57 e 4 pioras de +1,0."),
    # ------------------------------------------------------------------ p. 142
    dict(pag=142, area=(130, 172, 525, 266), antigo=["+0,20", "Ataques cibernéticos"],
         blocos=[(B, "**Delta médio de +0,19:** Piora moderada em comparação com outras dimensões"),
                 (B, "**3 variáveis com piora crítica (+1,0 ponto):** Consequências adversas de tecnologias "
                     "avançadas, práticas de censura e vigilância adversa e riscos associados à introdução "
                     "de navios autônomos")],
         limite=264, numeros={"+0,19": "por_dimensao.Tecnológica.delta_medio",
                              "3 variáveis": "por_dimensao.Tecnológica.pioras_1"},
         motivo="O questionário não tem variável 'ataques cibernéticos e ransomware'. As 3 variáveis "
                "tecnológicas com +1,0 são 5.2, 5.3 e 5.9 (todas estavam fora da base de 57)."),
    # ------------------------------------------------------------------ p. 162
    dict(pag=162, area=(130, 187, 525, 611), antigo=["Seis riscos imediatos", "acima", "+0,56", "Treze"],
         blocos=[(B, "**Nove riscos imediatos críticos** foram identificados com pelo menos 40% das respostas "
                     "em níveis altos (4-5): instabilidade política (50,4%), excesso regulatório e conflitos "
                     "geoeconômicos (46,4% cada), aumento de impostos e corrupção (45,6% cada), disrupções em "
                     "infraestruturas críticas (44,8%), falta de segurança computacional e escassez de mão de "
                     "obra em tecnologia (41,6% cada) e falhas em cadeias de suprimentos (40,0%)."),
                 (B, "**Cronicidade elevada dos riscos:** 73,7% das variáveis (56 de 76) "
                     "permanecem crônicas em curto e longo prazo, indicando que a maioria dos desafios "
                     "identificados não é transitória, mas sim estrutural e persistente."),
                 (B, "**Divergência temporal preocupante:** A divergência temporal observada evidencia um "
                     "descompasso estrutural entre a intensificação dos riscos e a capacidade de resposta do "
                     "sistema, uma vez que as dimensões geopolítica (+0,57) e ambiental (+0,53) apresentam a "
                     "maior deterioração ao longo do tempo, a ambiental ligada a pressões cumulativas das "
                     "mudanças climáticas e da degradação ambiental sobre as operações, enquanto a dimensão tecnológica tem apenas leve alta (delta +0,19), indicando "
                     "que a maturidade digital não evolui no mesmo ritmo das exigências impostas por esses "
                     "riscos. Essa assimetria revela limitações na adoção e integração de tecnologias voltadas "
                     "ao monitoramento ambiental, à análise preditiva, à gestão de dados e ao apoio à tomada de "
                     "decisão, reduzindo o potencial da tecnologia como vetor de resiliência, adaptação e "
                     "mitigação. No contexto portuário, essa lacuna amplia a vulnerabilidade sistêmica, "
                     "compromete a capacidade de antecipação e resposta a eventos extremos e tende a impactar "
                     "negativamente a sustentabilidade operacional, regulatória e competitiva no médio e longo prazo."),
                 (B, "**Concentração econômica de riscos:** Doze dos vinte maiores riscos imediatos são "
                     "econômicos, com média de 40,3% das respostas em níveis altos, configurando um "
                     "cenário de vulnerabilidade sistêmica.")],
         limite=610,
         numeros={"Nove riscos": "n_criticos_imediatos_ge40", "50,4%": "pct.1.15", "46,4%": "pct.3.3",
                  "45,6%": "pct.1.19", "44,8%": "pct.1.7", "41,6%": "pct.5.4", "40,0%": "pct.1.6",
                  "73,7%": "pct_cronicos", "56 de 76": "quadrantes.cronicos",
                  "+0,57": "por_dimensao.Geopolítica.delta_medio", "+0,53": "por_dimensao.Ambiental.delta_medio",
                  "+0,19": "por_dimensao.Tecnológica.delta_medio", "Doze": "top20.economicos",
                  "40,3%": "top20.media_economicos"},
         motivo="Seis riscos 'acima de 40%' incluía um de 40,0% e omitia Corrupção (45,6%) e os dois "
                "tecnológicos (41,6%); a lista não coincidia com a da seção 4.1.1. 73,7% sem denominador. "
                "Deltas e contagem do top 20 corrigidos."),
    # ------------------------------------------------------------------ p. 163
    dict(pag=163, area=(130, 518, 525, 596), antigo=["A estabilidade", "percebida no eixo tecnológico"],
         blocos=[(P, "O risco cibernético e de falhas digitais reflete a crescente digitalização dos portos "
                     "brasileiros sem que haja, em muitos casos, maturidade equivalente em governança de TI, "
                     "redundância de sistemas e cibersegurança. A piora apenas leve no eixo tecnológico "
                     "(+0,19), diante do agravamento ambiental (+0,53), sugere não ausência de risco, mas "
                     "possível subavaliação relativa.", dict(x1=137.12, x2=137.12))],
         limite=595, numeros={"+0,19": "por_dimensao.Tecnológica.delta_medio",
                              "+0,53": "por_dimensao.Ambiental.delta_medio"},
         motivo="O eixo tecnológico não é estável com 76 pares (+0,19)."),
    dict(pag=163, area=(130, 638, 525, 716), antigo=["O dado de que 73,7% dos riscos permanecem"],
         blocos=[(P, "O dado de que 73,7% dos riscos (56 de 76 variáveis) permanecem crônicos no curto e "
                     "longo prazo é um forte indicativo de que não se trata apenas de percepção conjuntural. "
                     "Riscos crônicos são, por definição, estruturais. Eles derivam de características "
                     "persistentes do ambiente econômico, institucional e regulatório brasileiro, e não de "
                     "eventos isolados.", dict(x1=137.12, x2=137.12))],
         limite=715, numeros={"73,7%": "pct_cronicos", "56 de 76": "quadrantes.cronicos"},
         motivo="Denominador explicitado."),
]

# Trechos sem correção no PDF limpo: dependem de decisão do autor. Viram notas na prova.
# Trechos sinalizados anteriormente (pp. 82, 106 e 142) foram retirados da prova a pedido do autor.
SINALIZACOES = []

IMAGENS = [
    dict(pag=45, xref=687, arquivo="quarto/assets/graficos_agrupados/matriz_riscos_quadrantes.png",
         motivo="Figura 1 regerada: 56 / 16 / 4 / 0 (eram 42 / 11 / 4 / 0). Eixos corrigidos para curto × "
                "longo prazo (eram 'Probabilidade' × 'Impacto', que não correspondem ao cálculo) e grafia 'Crônicos'."),
    dict(pag=46, xref=701, arquivo="quarto/assets/graficos_agrupados/slopegraph_centro_conectores_cor_unica.png",
         motivo="Gráfico 9 regerado com as 23 variáveis de média ≥3,0 no curto prazo (o original tinha 18, "
                "por usar a base de 57). Decimais com vírgula."),
]

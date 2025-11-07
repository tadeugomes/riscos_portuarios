#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Atualiza o capítulo de interconexão com slopegraphs individuais por dimensão

from pathlib import Path

# Caminhos
CAPITULO_FILE = "quarto/interconexao-riscos.qmd"
SLOPEGRAPHS_DIR = "quarto/assets/slopegraphs_por_dimensao"

# Conteúdo a ser adicionado após o slopegraph existente
NOVO_CONTEUDO = """

## Análise Temporal por Dimensão de Risco

Para uma análise mais detalhada da evolução temporal dos riscos, foram gerados slopegraphs individuais para cada dimensão. Esses gráficos permitem visualizar como as percepções de risco específicas de cada área se comportam entre o curto e longo prazo.

### Riscos Econômicos

![Evolução Temporal dos Riscos Econômicos](assets/slopegraphs_por_dimensao/slopegraph_econômica.png){#fig-slopegraph-economicos}

A dimensão econômica apresenta 19 variáveis com médias superiores a 2.5 no curto prazo, demonstrando a preocupação significativa com fatores financeiros e de mercado. Os slopegraphs revelam as trajetórias individuais de cada risco econômico, permitindo identificar quais tendências apresentam maior ou menor resiliência temporal.

### Riscos Ambientais

![Evolução Temporal dos Riscos Ambientais](assets/slopegraphs_por_dimensao/slopegraph_ambiental.png){#fig-slopegraph-ambientais}

Os riscos ambientais totalizam 16 variáveis relevantes, refletindo a crescente conscientização sobre questões sustentáveis no setor portuário. A análise temporal mostra como as percepções sobre impactos ambientais evoluem, indicando possíveis mudanças nas prioridades de mitigação ao longo do tempo.

### Riscos Geopolíticos

![Evolução Temporal dos Riscos Geopolíticos](assets/slopegraphs_por_dimensao/slopegraph_geopolítica.png){#fig-slopegraph-geopoliticos}

Embora com menor número de variáveis (5), os riscos geopolíticos demonstram alta relevância, com trajetórias temporais distintas que refletem a volatilidade do cenário internacional e seu impacto direto nas operações portuárias.

### Riscos Sociais

![Evolução Temporal dos Riscos Sociais](assets/slopegraphs_por_dimensao/slopegraph_social.png){#fig-slopegraph-sociais}

A dimensão social compreende 13 variáveis críticas, abrangendo desde direitos humanos até questões trabalhistas e participação comunitária. Os slopegraphs sociais revelam como as percepções sobre impacto social evoluem, indicando áreas que demandam atenção contínua.

### Riscos Tecnológicos

![Evolução Temporal dos Riscos Tecnológicos](assets/slopegraphs_por_dimensao/slopegraph_tecnologica.png){#fig-slopegraph-tecnologicos}

Os riscos tecnológicos, embora numericamente menores (4 variáveis), apresentam trajetórias significativas que refletem o rápido avanço tecnológico e seus impactos transformadores no setor portuário.

### Insights Comparativos

A análise comparativa dos slopegraphs por dimensão revela padrões importantes:

- **Dinâmicas Distintas**: Cada dimensão apresenta padrões temporais únicos, refletindo suas características específicas e fatores influenciadores
- **Prioridades Evolutivas**: Algumas dimensões mostram tendências de aumento de preocupação, enquanto outras apresentam maior estabilidade temporal
- **Interconexões Temporais**: As trajetórias individuais revelam como riscos de diferentes dimensões podem influenciar-se mutuamente ao longo do tempo
- **Foco Estratégico**: A análise temporal por dimensão permite identificar áreas que requerem intervenções imediatas versus aquelas que demandam planejamento de longo prazo

Essa abordagem detalhada complementa a análise agregada, fornecendo uma visão granular essencial para o desenvolvimento de estratégias de mitigação específicas e contextualizadas para cada dimensão de risco.
"""

def atualizar_capitulo():
    """Atualiza o capítulo com os novos slopegraphs individuais."""
    
    # Verificar se o arquivo do capítulo existe
    capitulo_path = Path(CAPITULO_FILE)
    if not capitulo_path.exists():
        print(f"Erro: Arquivo {CAPITULO_FILE} não encontrado!")
        return False
    
    # Ler o conteúdo atual
    with open(capitulo_path, 'r', encoding='utf-8') as f:
        conteudo_atual = f.read()
    
    # Verificar se o conteúdo já foi adicionado
    if "Análise Temporal por Dimensão de Risco" in conteudo_atual:
        print("O conteúdo dos slopegraphs individuais já foi adicionado ao capítulo.")
        return True
    
    # Encontrar o ponto de inserção (após a seção do slopegraph completo)
    # Procuramos pelo final da seção do slopegraph principal
    ponto_insercao = conteudo_atual.find("A estabilidade predominante indica que as estratégias de gestão de riscos atuais são adequadas para manter os níveis de risco, mas insuficientes para reduzi-los significativamente.")
    
    if ponto_insercao == -1:
        print("Não foi possível encontrar o ponto de inserção no capítulo.")
        return False
    
    # Calcular posição final
    pos_final = ponto_insercao + len("A estabilidade predominante indica que as estratégias de gestão de riscos atuais são adequadas para manter os níveis de risco, mas insuficientes para reduzi-los significativamente.")
    
    # Inserir novo conteúdo
    novo_conteudo = conteudo_atual[:pos_final] + NOVO_CONTEUDO + conteudo_atual[pos_final:]
    
    # Salvar arquivo atualizado
    with open(capitulo_path, 'w', encoding='utf-8') as f:
        f.write(novo_conteudo)
    
    print(f"Capítulo atualizado com sucesso! Conteúdo adicionado em {CAPITULO_FILE}")
    return True

def main():
    """Função principal."""
    print("=== ATUALIZANDO CAPÍTULO COM SLOPEGRAPHS INDIVIDUAIS ===")
    
    # Verificar se os slopegraphs foram gerados
    slopegraphs_dir = Path(SLOPEGRAPHS_DIR)
    if not slopegraphs_dir.exists():
        print(f"Erro: Diretório {SLOPEGRAPHS_DIR} não encontrado!")
        print("Execute primeiro: python gerar_slopegraph_por_dimensao.py")
        return
    
    # Listar arquivos gerados
    arquivos = list(slopegraphs_dir.glob("*.png"))
    print(f"Slopegraphs encontrados: {len(arquivos)}")
    for arquivo in arquivos:
        print(f"  - {arquivo.name}")
    
    # Atualizar capítulo
    if atualizar_capitulo():
        print("\n✅ Capítulo atualizado com sucesso!")
        print("Os slopegraphs individuais por dimensão foram integrados ao capítulo de interconexão.")
    else:
        print("\n❌ Falha ao atualizar o capítulo.")

if __name__ == "__main__":
    main()

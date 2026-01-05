# Planilha de Estatísticas de Riscos Portuários

## Overview

Este projeto gerou uma planilha Excel completa com estatísticas detalhadas dos riscos portuários, utilizando os mesmos cálculos implementados para construir os gráficos existentes.

## Arquivos Gerados

### 1. Planilha Principal
- **Arquivo**: `outputs/estatisticas_riscos_portuarios.xlsx`
- **Estrutura**:
  - **Resumo_Geral**: Estatísticas agregadas por dimensão e período temporal
  - **Dados_Detalhados**: Todas as variáveis com estatísticas completas (média, mediana, moda, desvio padrão)
  - **Frequencias**: Distribuição detalhada por nível de risco (1-5)
  - **Metadados**: Informações sobre a análise e metodologia
  - **Info_Dimensoes**: Detalhes específicos por dimensão

### 2. Relatórios de Validação
- **Arquivo**: `outputs/relatorio_validacao_estatisticas.txt`
- **Conteúdo**: Validação inicial dos dados gerados

- **Arquivo**: `outputs/relatorio_validacao_completa.txt`
- **Conteúdo**: Validação completa contra os cálculos originais dos gráficos

### 3. Scripts Gerados
- **`gerar_planilha_estatisticas.py`**: Script principal para geração da planilha
- **`validar_planilha_contra_graficos.py`**: Script de validação da consistência dos dados

## Estrutura dos Dados

### Dimensões Analisadas
1. **Econômica** (22 variáveis únicas)
2. **Ambiental** (17 variáveis únicas)
3. **Geopolítica** (7 variáveis únicas)
4. **Social** (15 variáveis únicas)
5. **Tecnológica** (16 variáveis únicas)

### Períodos Temporais
- **Imediato 2025**: Análise de riscos imediatos
- **Curto Prazo 2026-2027**: Projeção de médio prazo
- **Longo Prazo até 2035**: Projeção de longo prazo

### Estatísticas Calculadas
- **Média**: Média aritmética das respostas (escala 1-5)
- **Mediana**: Valor central das respostas
- **Moda**: Valor mais frequente
- **Desvio Padrão**: Dispersão dos dados
- **Percentual Risco Alto**: % de respostas 4-5
- **Percentual Risco Baixo**: % de respostas 1-2
- **Nível de Risco**: Classificação (Baixo, Moderado, Alto, Crítico)

## Resultados Principais

### Estatísticas Gerais
- **Total de Respondentes**: 125
- **Total de Variáveis Analisadas**: 77
- **Total de Registros Detalhados**: 229
- **Total de Registros de Frequência**: 1.145

### Principais Descobertas
- **Dimensão com mais riscos críticos**: Econômica (9 riscos críticos)
- **Dimensão com maior média geral**: Econômica (média 3.00)
- **Dimensão com menor média geral**: Ambiental (média 2.65)
- **Período com maior concentração de riscos**: Imediato 2025

## Como Usar

### 1. Para Gerar a Planilha
```bash
python gerar_planilha_estatisticas.py
```

### 2. Para Validar os Dados
```bash
python validar_planilha_contra_graficos.py
```

### 3. Para Abrir a Planilha
- Abra o arquivo `outputs/estatisticas_riscos_portuarios.xlsx`
- Navegue entre as abas conforme necessário:
  - Use **Resumo_Geral** para visão geral
  - Use **Dados_Detalhados** para análise específica
  - Use **Frequencias** para distribuição detalhada

## Metodologia

### Cálculos Utilizados
A planilha utiliza exatamente os mesmos cálculos implementados na classe `AnalisadorRiscosLikert`:

1. **Análise de Frequências**: Método `analisar_frequencias_likert()`
2. **Classificação de Risco**: Método `classificar_nivel_risco()`
3. **Mapeamento Temporal**: Método `mapear_variaveis_por_dimensao()`

### Consistência Validada
- **Agregações**: 96.7% de consistência matemática
- **Frequências**: 92.8% de consistência
- **Escala**: Todos os valores dentro da escala Likert (1-5)

## Recomendações de Uso

### Para Análise Estratégica
1. Focar nas variáveis classificadas como "Risco Crítico"
2. Monitorar tendências temporais entre os períodos
3. Comparar dimensões para priorização de recursos

### Para Relatórios
1. Utilizar aba **Resumo_Geral** para executivos
2. Usar **Dados_Detalhados** para análises técnicas
3. Referenciar **Metadados** para metodologia

### Para Validação
1. Consultar relatórios de validação gerados
2. Verificar consistência com gráficos existentes
3. Confirmar agregações matemáticas

## Controle de Versão

- **Versão**: 1.0
- **Data de Geração**: 13/11/2025
- **Fonte de Dados**: questionario.xlsx
- **Total de Respondentes**: 125

## Suporte

Para dúvidas ou problemas:
1. Verifique os relatórios de validação
2. Confirme se o arquivo `questionario.xlsx` está atualizado
3. Execute os scripts em ambiente Python 3.8+ com pandas instalado

---

**Nota**: Esta planilha foi gerada automaticamente e validada contra os cálculos originais utilizados nos gráficos do projeto de análise de riscos portuários.

# Análise de Riscos Portuários - Escala Likert

## Overview

Este projeto implementa uma análise completa de dados de risco portuário coletados através de escala Likert (1-5), organizados por 5 dimensões principais:

- **Econômica** (prefixo 1.x)
- **Ambiental** (prefixo 2.x) 
- **Geopolítica** (prefixo 3.x)
- **Social** (prefixo 4.x)
- **Tecnológica** (prefixo 5.x)

## Classificação de Risco

- **1**: Raríssima
- **2**: Baixa
- **3**: Moderada
- **4**: Alta
- **5**: Muito Alta

## Horizontes Temporais

- **Imediato (2025)**
- **Curto prazo (2026-2027)**
- **Longo prazo (até 2035)**

## Arquivos do Projeto

### Principal
- `analise_likert_riscos.py` - Script completo de análise e geração de gráficos
- `test_analise_likert.py` - Script de teste simplificado

### Apoio
- `data_processor.py` - Processamento de dados (dashboard existente)
- `app.py` - Dashboard web interativo
- `requirements.txt` - Dependências Python

## Como Usar

### 1. Setup do Ambiente

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar (Windows)
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### 2. Executar Análise Completa

```bash
python analise_likert_riscos.py
```

### 3. Executar Teste Simplificado

```bash
python test_analise_likert.py
```

## Funcionalidades

### Análises Estatísticas Apropriadas para Dados Likert

✅ **Medidas de Tendência Central:**
- Mediana
- Moda
- Percentis (25º, 50º, 75º)

✅ **Medidas de Dispersão:**
- Frequências absolutas e relativas
- Amplitude interquartil (IQR)
- Análise de consenso

✅ **Análises NÃO Utilizadas (inapropriadas para Likert):**
- ❌ Média aritmética
- ❌ Desvio padrão
- ❌ Coeficiente de variação

### Tipos de Gráficos Gerados

1. **Gráficos de Frequência Individual**
   - Barras para cada categoria (1-5)
   - Cores por nível de risco
   - Percentuais e medianas

2. **Gráficos Comparativos por Dimensão**
   - Todas as variáveis da dimensão
   - Ordenação por nível de risco
   - Classificação visual (crítico/alto/moderado/baixo)

3. **Box Plots Modificados**
   - Apenas mediana e quartis
   - Sem média/desvio padrão
   - Linhas de referência

4. **Gráficos de Evolução Temporal**
   - Mesma variável nos 3 períodos
   - Tendências de medianas
   - Percentuais de risco alto

### Estrutura de Saída

```
outputs/
├── graficos_economicos/
│   ├── imediato_2025/
│   │   ├── frequencias/
│   │   ├── comparativos/
│   │   └── boxplots/
│   ├── curto_prazo_2026_2027/
│   └── longo_prazo_2035/
├── graficos_ambientais/
├── graficos_geopoliticos/
├── graficos_sociais/
├── graficos_tecnologicos/
└── relatorio_consolidado.txt
```

### Classificação de Riscos

- **RISCO CRÍTICO**: Mediana ≥ 4.0 E >50% respostas em 4-5
- **RISCO ALTO**: Mediana ≥ 3.5 E >40% respostas em 4-5
- **RISCO MODERADO-ALTO**: Mediana ≥ 3.0 E >30% respostas em 4-5
- **RISCO MODERADO**: Mediana ≥ 2.0
- **RISCO BAIXO**: Mediana < 2.0

### Relatórios Gerados

1. **Relatórios por Dimensão**
   - Estatísticas completas
   - Top 10 riscos críticos
   - Análise por período
   - Recomendações específicas

2. **Relatório Consolidado**
   - Comparação entre dimensões
   - Sumário executivo
   - Recomendações estratégicas
   - Próximos passos

## Cores Utilizadas

| Nível | Cor | Nome |
|-------|------|------|
| 1 | #90EE90 | Raríssima |
| 2 | #228B22 | Baixa |
| 3 | #FFD700 | Moderada |
| 4 | #FF8C00 | Alta |
| 5 | #DC143C | Muito Alta |

## Abordagem Estatística

Este projeto utiliza **apenas métodos estatísticos apropriados para dados categóricos ordinais (Likert)**:

✅ **Correto:**
- Mediana como medida de tendência central
- Percentis e quartis
- Frequências e proporções
- Testes não paramétricos

❌ **Incorreto (evitado):**
- Média aritmética (pressupõe intervalos iguais)
- Desvio padrão (requer dados contínuos)
- Coeficientes de correlação de Pearson

## Exemplo de Uso

```python
from analise_likert_riscos import AnalisadorRiscosLikert

# Criar analisador
analisador = AnalisadorRiscosLikert('questionario.xlsx')

# Executar análise completa
analisador.executar_analise_completa()

# Acessar resultados
mapeamento = analisador.mapear_variaveis_por_dimensao()
stats = analisador.analisar_frequencias_likert(dados_coluna)
```

## Considerações Técnicas

- **Tratamento de dados nulos**: Automático na análise
- **Validação de dados**: Conversão para numérico com tratamento de erros
- **Logging**: Registro detalhado do processo
- **Gerenciamento de memória**: Fechamento adequado de gráficos
- **Codificação**: UTF-8 para suporte a caracteres especiais

## Requisitos

- Python 3.8+
- pandas
- numpy
- matplotlib
- seaborn
- openpyxl

## Notas Importantes

1. **Escala Likert é categórica ordinal**, não numérica contínua
2. **Média não é apropriada** para dados Likert
3. **Mediana é a melhor medida** de tendência central
4. **Análises devem respeitar** a natureza ordinal dos dados
5. **Interpretação deve considerar** o contexto específico de cada variável

## Suporte

Para dúvidas ou problemas, verifique:
1. Se o arquivo `questionario.xlsx` existe no diretório
2. Se as dependências estão instaladas corretamente
3. Se o ambiente virtual está ativado
4. Os logs de execução para identificar erros específicos

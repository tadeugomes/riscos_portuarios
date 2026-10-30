# Revisão do PDF diagramado (30/10/2026)

Corrige a análise temporal do relatório "Riscos Globais Portuários Brasil", que usava 57 pares curto × longo prazo em vez dos 76 do questionário (19 variáveis não eram pareadas por falha de correspondência textual; a 5.16 tinha "áréa" na coluna de longo prazo).

## Como rodar

```
python validacao/numeros_referencia.py      # recalcula a base de referência a partir de questionario.xlsx
python gerar_figuras_revisao_76.py           # regera Gráfico 9 e Figura 1 (matriz)
python revisao_pdf/corrigir_relatorio.py     # aplica as emendas ao PDF diagramado
```

Requisitos extras: `pymupdf`, `pyphen`, `fonttools` (apenas para inspeção).

## Saídas

- `RELATORIO DE RISCO GLOBAL COMPLETO-DIGITAL - CORRIGIDO.pdf`: versão limpa.
- `RELATORIO DE RISCO GLOBAL COMPLETO-DIGITAL - PROVA.pdf`: original com destaques (amarelo = emenda, vermelho = figura substituída, laranja = trecho a verificar sem emenda) e nota explicando cada caso.
- `revisao_pdf/relatorio_verificacao.txt`: registro das verificações.

## Verificações automáticas (o script aborta se qualquer uma falhar)

1. O trecho antigo esperado precisa estar na área antes da emenda.
2. Cada caractere novo é renderizado na fonte embutida da sua sequência e comparado com o glifo .notdef.
3. O texto composto precisa caber no limite vertical declarado da área.
4. Cada número citado no texto novo é conferido contra `validacao/numeros_referencia.json`.
5. No arquivo gravado, todo o texto fora das áreas emendadas é comparado linha a linha com o original.
6. O texto extraído de cada área emendada precisa ser igual ao texto composto (garante busca e cópia corretas).

## Arquivos

- `motor.py`: composição tipográfica com as fontes do próprio PDF (justificação, hifenização pt-BR, marcadores, faixas de título).
- `emendas.py`: todas as emendas, com área, texto antigo esperado, texto novo, números conferidos e justificativa.
- `corrigir_relatorio.py`: execução, verificações e geração da prova.

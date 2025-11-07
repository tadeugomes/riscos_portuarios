#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Lista todas as variáveis para entender a estrutura

import pandas as pd

# Carregar dados
df = pd.read_excel("questionario.xlsx")

# Encontrar colunas de curto prazo
curto_cols = [c for c in df.columns if '[Curto prazo' in c]

print("=== VARIÁVEIS DE CURTO PRAZO ===")
for i, col in enumerate(curto_cols, 1):
    print(f"{i:2d}: {col}")

print(f"\nTotal: {len(curto_cols)} variáveis")

# Mostrar os primeiros caracteres de cada variável
print("\n=== PREFIXOS ===")
prefixos = set()
for col in curto_cols:
    # Extrair o prefixo numérico
    import re
    match = re.match(r'^(\d+(?:\.\d+)?)', col)
    if match:
        prefixos.add(match.group(1))

for prefixo in sorted(prefixos):
    print(f"- {prefixo}")

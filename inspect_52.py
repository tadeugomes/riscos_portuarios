from analise_likert_riscos import AnalisadorRiscosLikert
from pathlib import Path

analisador = AnalisadorRiscosLikert()
analisador.carregar_dados()
cols = [c for c in analisador.dados_brutos.columns if str(c).startswith('5.2')]
for c in cols:
    print(repr(c))
    print('len:', len(c))

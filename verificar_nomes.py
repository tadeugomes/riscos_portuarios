from analise_likert_riscos import AnalisadorRiscosLikert

analisador = AnalisadorRiscosLikert()
analisador.carregar_dados()
mapeamento = analisador.mapear_variaveis_por_dimensao()
dados_sociais = mapeamento.get('Social', {})
dados_imediato = dados_sociais.get('imediato_2025', [])

print('Nomes das variáveis no período Imediato 2025:')
for i, variavel in enumerate(dados_imediato):
    print(f'{i+1}: "{variavel}"')
    
print(f'\nTotal de variáveis: {len(dados_imediato)}')

# Verificar formato específico da variável 4.3
print('\n' + '='*50)
print('ANÁLISE ESPECÍFICA DA VARIÁVEL 4.3:')
for variavel in dados_imediato:
    if variavel.startswith('4.3'):
        print(f'Nome completo: "{variavel}"')
        print(f'Contém "[Imediato (2025)]": {"[Imediato (2025)]" in variavel}')
        print(f'Contém "[Imediato_2025_]": {"[Imediato_2025_]" in variavel}')
        print(f'Contém "Imediato": {"Imediato" in variavel}')
        break

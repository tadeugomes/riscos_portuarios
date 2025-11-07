"""
Teste simplificado para verificar a análise Likert
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from analise_likert_riscos import AnalisadorRiscosLikert

def test_analise_simplificada():
    """Teste simplificado para verificar funcionamento"""
    
    print("TESTE SIMPLIFICADO - ANÁLISE LIKERT")
    print("=" * 50)
    
    try:
        # Criar analisador
        analisador = AnalisadorRiscosLikert()
        
        # Carregar dados
        print("1. Carregando dados...")
        analisador.carregar_dados()
        print(f"   Dados carregados: {analisador.dados_brutos.shape}")
        
        # Mapear variáveis
        print("2. Mapeando variáveis...")
        mapeamento = analisador.mapear_variaveis_por_dimensao()
        
        # Mostrar resumo
        print("\nRESUMO DO MAPEAMENTO:")
        for dimensao, periodos in mapeamento.items():
            total_vars = sum(len(vars) for vars in periodos.values())
            print(f"   {dimensao}: {total_vars} variáveis totais")
            for periodo, vars in periodos.items():
                print(f"     {periodo}: {len(vars)} variáveis")
        
        # Criar pasta de saída
        print("3. Criando estrutura de pastas...")
        os.makedirs('outputs/teste', exist_ok=True)
        
        # Testar com uma variável de cada dimensão
        print("4. Testando geração de gráficos...")
        
        for dimensao, periodos in mapeamento.items():
            for periodo, variaveis in periodos.items():
                if variaveis:  # Se houver variáveis neste período
                    # Pegar a primeira variável como teste
                    variavel_teste = variaveis[0]
                    dados_teste = analisador.dados_brutos[variavel_teste]
                    
                    print(f"\n   Testando: {dimensao} - {variavel_teste}")
                    
                    # Análise de frequências
                    stats = analisador.analisar_frequencias_likert(dados_teste)
                    if stats:
                        print(f"      Total respostas: {stats['total_respostas']}")
                        print(f"      Mediana: {stats['mediana']:.2f}")
                        print(f"      Percentual risco alto: {stats['percentual_risco_alto']:.1f}%")
                        
                        # Gerar gráfico de teste
                        caminho_grafico = f'outputs/teste/grafico_teste_{dimensao.lower()}.png'
                        titulo = f"Teste - {dimensao} - {variavel_teste}"
                        
                        sucesso = analisador.gerar_grafico_frequencia(
                            dados_teste, titulo, caminho_grafico, variavel_teste
                        )
                        
                        if sucesso:
                            print(f"      ✓ Gráfico salvo: {caminho_grafico}")
                        else:
                            print(f"      ✗ Erro ao gerar gráfico")
                    else:
                        print(f"      ✗ Sem dados válidos para análise")
                    
                    break  # Testar apenas um período por dimensão
        
        print("\n" + "=" * 50)
        print("TESTE CONCLUÍDO!")
        print("Verifique a pasta 'outputs/teste/' para os gráficos gerados.")
        
    except Exception as e:
        print(f"ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_analise_simplificada()

#!/usr/bin/env python3
"""
Script para gerar gráficos agrupados temporais para todas as variáveis sociais
"""

import sys
import os
import shutil
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analise_likert_riscos import criar_grafico_agrupado_temporal, carregar_dados
import pandas as pd

def gerar_todos_graficos_sociais():
    """Gera gráficos agrupados para todas as variáveis sociais (4.1 a 4.15)"""
    
    # Carregar dados
    df = carregar_dados()
    if df is None:
        print("Erro: Não foi possível carregar os dados")
        return
    
    # Definir variáveis sociais com seus nomes exatos no Excel
    variaveis_sociais = [
        '4.1', '4.2', '4.3', '4.5', '4.6', '4.7', '4.8', 
        '4.10', '4.11', '4.12', '4.13', '4.14', '4.15'
    ]
    
    print("Gerando graficos agrupados para variaveis sociais...")
    
    for var in variaveis_sociais:
        print(f"\nProcessando variável {var}...")
        
        # Gerar gráfico usando a função que já funciona
        try:
            sucesso = criar_grafico_agrupado_temporal(
                df, var, 
                output_dir='outputs/teste',
                nome_arquivo=f'grafico_agrupado_{var.replace(".", "_")}_temporal.png'
            )
            
            if sucesso:
                print(f"  OK Grafico {var} gerado com sucesso")
                origem = f'outputs/teste/grafico_agrupado_{var.replace(".", "_")}_temporal.png'
                destinos = [
                    f'quarto/assets/graficos_agrupados/grafico_agrupado_{var.replace(".", "_")}_temporal.png',
                    f'quarto/assets/social/grafico_agrupado_{var.replace(".", "_")}_temporal.png',
                ]
                if os.path.exists(origem):
                    for destino in destinos:
                        os.makedirs(os.path.dirname(destino), exist_ok=True)
                        shutil.copy2(origem, destino)
                        print(f"  Copiado para {destino}")
            else:
                print(f"  ERRO: Falha ao gerar grafico {var}")
                
        except Exception as e:
            print(f"  ERRO: Excecao ao processar variavel {var}: {str(e)}")
    
    print("\nProcessamento concluido!")
    print(f"Total de variaveis processadas: {len(variaveis_sociais)}")

if __name__ == "__main__":
    gerar_todos_graficos_sociais()

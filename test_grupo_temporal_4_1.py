#!/usr/bin/env python3
"""
Script de teste para gerar gráfico agrupado temporal para variável 4.1
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import re
from analise_likert_riscos import AnalisadorRiscosLikert

def gerar_grafico_teste_4_1():
    """
    Gera gráfico agrupado temporal específico para variável 4.1
    """
    print("Gerando gráfico de teste para variável 4.1...")
    
    # Inicializar analisador
    analisador = AnalisadorRiscosLikert()
    
    # Carregar dados
    analisador.carregar_dados()
    
    # Mapear variáveis
    mapeamento = analisador.mapear_variaveis_por_dimensao()
    
    # Obter dados da dimensão Social
    dados_sociais = mapeamento.get('Social', {})
    
    # Coletar dados para variável 4.1
    dados_4_1_periodos = {}
    
    for periodo, variaveis in dados_sociais.items():
        for variavel in variaveis:
            if variavel.startswith('4.1 Ameaças aos direitos humanos'):
                dados_4_1_periodos[periodo] = analisador.dados_brutos[variavel]
                print(f"Encontrada variável 4.1 para período {periodo}: {variavel}")
                break
    
    # Criar pasta de teste se não existir
    os.makedirs('outputs/teste', exist_ok=True)
    
    # Gerar gráfico agrupado
    caminho_grafico = 'outputs/teste/grafico_agrupado_4_1_temporal.png'
    
    sucesso = analisador.gerar_grafico_barras_agrupado_temporal(
        dados_4_1_periodos, 
        '4.1 Ameaças aos direitos humanos e/ou às liberdades individuais ou de grupo. [Imediato (2025)]',
        caminho_grafico
    )
    
    if sucesso:
        print(f"✅ Gráfico gerado com sucesso: {caminho_grafico}")
        
        # Exibir estatísticas
        print("\n📊 Estatísticas por período:")
        for periodo, dados in dados_4_1_periodos.items():
            stats = analisador.analisar_frequencias_likert(dados)
            if stats:
                print(f"\n{periodo}:")
                print(f"  Total de respostas: {stats['total_respostas']}")
                print(f"  Mediana: {stats['mediana']:.2f}")
                print(f"  Percentual risco alto (4-5): {stats['percentual_risco_alto']:.1f}%")
                print(f"  Distribuição: {stats['frequencias_absolutas']}")
        
        return caminho_grafico
    else:
        print("❌ Erro ao gerar gráfico")
        return None

if __name__ == "__main__":
    gerar_grafico_teste_4_1()

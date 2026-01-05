#!/usr/bin/env python3
"""
Script para testar geração dos gráficos 1.12 e 1.13 com títulos corretos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analise_likert_riscos import AnalisadorRiscosLikert, carregar_dados
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def testar_graficos_especificos():
    """Testa geração dos gráficos 1.12 e 1.13"""
    
    # Carregar dados
    df = carregar_dados()
    if df is None:
        print("Erro: Não foi possível carregar os dados")
        return
    
    # Criar analisador
    analisador = AnalisadorRiscosLikert()
    analisador.dados_brutos = df
    
    # Mapear variáveis
    mapeamento = analisador.mapear_variaveis_por_dimensao()
    
    # Variáveis para testar
    variaveis_teste = ['1.12', '1.13']
    
    for variavel in variaveis_teste:
        print(f"\nTestando variável {variavel}...")
        
        # Encontrar dados da variável por período
        dados_periodos = {}
        nome_completo_variavel = None
        
        # Procurar a variável em todos os períodos da dimensão econômica
        if 'Economica' in mapeamento:
            for periodo, variaveis in mapeamento['Economica'].items():
                for var in variaveis:
                    if var.startswith(variavel):
                        dados_periodos[periodo] = df[var]
                        if nome_completo_variavel is None:
                            nome_completo_variavel = var
                        break
        
        if not dados_periodos:
            print(f"  ERRO: Variável {variavel} não encontrada nos dados")
            continue
        
        print(f"  Nome completo: {nome_completo_variavel}")
        print(f"  Label sucinto: {analisador.gerar_label_sucinto(nome_completo_variavel)}")
        
        # Gerar gráfico
        nome_arquivo = f'teste_grafico_{variavel.replace(".", "_")}_temporal.png'
        caminho_completo = os.path.join('outputs/teste', nome_arquivo)
        
        sucesso = analisador.gerar_grafico_barras_agrupado_temporal(
            dados_periodos, nome_completo_variavel, caminho_completo
        )
        
        if sucesso:
            print(f"  OK: Gráfico {variavel} gerado com sucesso em {caminho_completo}")
        else:
            print(f"  ERRO: Falha ao gerar gráfico {variavel}")

if __name__ == "__main__":
    testar_graficos_especificos()

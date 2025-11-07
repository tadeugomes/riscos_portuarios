#!/usr/bin/env python3
"""
Script para gerar gráficos agrupados temporais para todas as variáveis geopolíticas
"""

import sys
import os
import shutil
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analise_likert_riscos import AnalisadorRiscosLikert, carregar_dados
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def criar_grafico_agrupado_temporal_geopolitico(df, variavel, output_dir='outputs', nome_arquivo=None):
    """
    Função personalizada para criar gráfico agrupado temporal para dimensão geopolítica
    
    Args:
        df: DataFrame com os dados
        variavel: Código da variável (ex: '3.1')
        output_dir: Diretório para salvar o gráfico
        nome_arquivo: Nome do arquivo (opcional)
        
    Returns:
        True se sucesso, False se erro
    """
    try:
        # Criar analisador temporário
        analisador = AnalisadorRiscosLikert()
        analisador.dados_brutos = df
        
        # Mapear variáveis por período
        mapeamento = analisador.mapear_variaveis_por_dimensao()
        
        # Encontrar dados da variável por período
        dados_periodos = {}
        nome_completo_variavel = None
        
        # Procurar a variável em todos os períodos da dimensão geopolítica
        if 'Geopolitica' in mapeamento:
            for periodo, variaveis in mapeamento['Geopolitica'].items():
                for var in variaveis:
                    if var.startswith(variavel):
                        dados_periodos[periodo] = df[var]
                        if nome_completo_variavel is None:
                            nome_completo_variavel = var
                        break
        
        if not dados_periodos:
            logger.warning(f"Variável {variavel} não encontrada nos dados")
            return False
        
        # Gerar nome do arquivo se não fornecido
        if nome_arquivo is None:
            nome_arquivo = f'grafico_agrupado_{variavel.replace(".", "_")}_temporal.png'
        
        # Caminho completo
        caminho_completo = os.path.join(output_dir, nome_arquivo)
        
        # Criar diretório se não existir
        os.makedirs(output_dir, exist_ok=True)
        
        # Gerar gráfico usando o método da classe
        sucesso = analisador.gerar_grafico_barras_agrupado_temporal(
            dados_periodos, nome_completo_variavel, caminho_completo
        )
        
        return sucesso
        
    except Exception as e:
        logger.error(f"Erro ao criar gráfico agrupado para {variavel}: {e}")
        return False

def gerar_todos_graficos_geopoliticos():
    """Gera gráficos agrupados para todas as variáveis geopolíticas (3.1 a 3.x)"""
    
    # Carregar dados
    df = carregar_dados()
    if df is None:
        print("Erro: Não foi possível carregar os dados")
        return
    
    # Definir variáveis geopolíticas com seus nomes exatos no Excel
    # Baseado na estrutura do projeto, variáveis geopolíticas começam com "3."
    # Total de 22 variáveis geopolíticas encontradas
    variaveis_geopoliticas = [
        '3.1', '3.2', '3.3', '3.4', '3.5', '3.6', '3.7', '3.8', '3.9', '3.10',
        '3.11', '3.12', '3.13', '3.14', '3.15', '3.16', '3.17', '3.18', '3.19', '3.20',
        '3.21', '3.22'
    ]
    
    print("Gerando graficos agrupados para variaveis geopoliticas...")
    
    for var in variaveis_geopoliticas:
        print(f"\nProcessando variável {var}...")
        
        # Gerar gráfico usando a função que já funciona
        try:
            sucesso = criar_grafico_agrupado_temporal_geopolitico(
                df, var, 
                output_dir='outputs/teste',
                nome_arquivo=f'grafico_agrupado_{var.replace(".", "_")}_temporal.png'
            )
            
            if sucesso:
                print(f"  OK Grafico {var} gerado com sucesso")
                origem = f'outputs/teste/grafico_agrupado_{var.replace(".", "_")}_temporal.png'
                destinos = [
                    f'quarto/assets/graficos_agrupados/grafico_agrupado_{var.replace(".", "_")}_temporal.png',
                    f'quarto/assets/geopoliticos/grafico_agrupado_{var.replace(".", "_")}_temporal.png',
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
    print(f"Total de variaveis processadas: {len(variaveis_geopoliticas)}")

if __name__ == "__main__":
    gerar_todos_graficos_geopoliticos()

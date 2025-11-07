#!/usr/bin/env python3
"""
Script para gerar gráficos agrupados temporais para todas as variáveis econômicas
"""

import sys
import os
import shutil
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analise_likert_riscos import AnalisadorRiscosLikert, carregar_dados
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def criar_grafico_agrupado_temporal_economico(df, variavel, output_dir='outputs', nome_arquivo=None):
    """
    Função personalizada para criar gráfico agrupado temporal para dimensão econômica
    
    Args:
        df: DataFrame com os dados
        variavel: Código da variável (ex: '1.1')
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

def gerar_todos_graficos_economicos():
    """Gera gráficos agrupados para todas as variáveis econômicas (1.1 a 1.x)"""
    
    # Carregar dados
    df = carregar_dados()
    if df is None:
        print("Erro: Não foi possível carregar os dados")
        return
    
    # Definir variáveis econômicas com seus nomes exatos no Excel
    # Baseado na estrutura do projeto, variáveis econômicas começam com "1."
    # Total de 21 variáveis econômicas encontradas (1.1 a 1.21)
    variaveis_economicas = [
        '1.1', '1.2', '1.3', '1.4', '1.5', '1.6', '1.7', '1.8', '1.9', '1.10',
        '1.11', '1.12', '1.13', '1.14', '1.15', '1.16', '1.17', '1.18', '1.19', '1.20',
        '1.21'
    ]
    
    print("Gerando gráficos agrupados para variáveis econômicas...")
    
    for var in variaveis_economicas:
        print(f"\nProcessando variável {var}...")
        
        # Gerar gráfico usando função personalizada para dimensão econômica
        try:
            sucesso = criar_grafico_agrupado_temporal_economico(
                df, var, 
                output_dir='outputs/teste',
                nome_arquivo=f'grafico_agrupado_{var.replace(".", "_")}_temporal.png'
            )
            
            if sucesso:
                print(f"  OK Gráfico {var} gerado com sucesso")
                origem = f'outputs/teste/grafico_agrupado_{var.replace(".", "_")}_temporal.png'
                destinos = [
                    f'quarto/assets/graficos_agrupados/grafico_agrupado_{var.replace(".", "_")}_temporal.png',
                    f'quarto/assets/economicos/grafico_agrupado_{var.replace(".", "_")}_temporal.png',
                ]
                if os.path.exists(origem):
                    for destino in destinos:
                        os.makedirs(os.path.dirname(destino), exist_ok=True)
                        shutil.copy2(origem, destino)
                        print(f"  Copiado para {destino}")
            else:
                print(f"  ERRO: Falha ao gerar gráfico {var}")
                
        except Exception as e:
            print(f"  ERRO: Exceção ao processar variável {var}: {str(e)}")
    
    print("\nProcessamento concluído!")
    print(f"Total de variáveis processadas: {len(variaveis_economicas)}")

if __name__ == "__main__":
    gerar_todos_graficos_economicos()

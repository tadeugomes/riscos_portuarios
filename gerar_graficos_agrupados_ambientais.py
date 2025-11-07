#!/usr/bin/env python3
"""
Script para gerar gráficos agrupados temporais para todas as variáveis ambientais
"""

import sys
import os
import shutil
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analise_likert_riscos import AnalisadorRiscosLikert, carregar_dados
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def criar_grafico_agrupado_temporal_ambiental(df, variavel, output_dir='outputs', nome_arquivo=None):
    """
    Função personalizada para criar gráfico agrupado temporal para dimensão ambiental
    
    Args:
        df: DataFrame com os dados
        variavel: Código da variável (ex: '2.1')
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
        
        # Procurar a variável em todos os períodos da dimensão ambiental
        if 'Ambiental' in mapeamento:
            for periodo, variaveis in mapeamento['Ambiental'].items():
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

def gerar_todos_graficos_ambientais():
    """Gera gráficos agrupados para todas as variáveis ambientais (2.1 a 2.x)"""
    
    # Carregar dados
    df = carregar_dados()
    if df is None:
        print("Erro: Não foi possível carregar os dados")
        return
    
    # Definir variáveis ambientais com seus nomes exatos no Excel
    # Baseado na estrutura do projeto, variáveis ambientais começam com "2."
    # Total de 52 variáveis ambientais encontradas
    variaveis_ambientais = [
        '2.1', '2.2', '2.3', '2.4', '2.5', '2.6', '2.7', '2.8', '2.9', '2.10',
        '2.11', '2.12', '2.13', '2.14', '2.15', '2.16', '2.17', '2.18', '2.19', '2.20',
        '2.21', '2.22', '2.23', '2.24', '2.25', '2.26', '2.27', '2.28', '2.29', '2.30',
        '2.31', '2.32', '2.33', '2.34', '2.35', '2.36', '2.37', '2.38', '2.39', '2.40',
        '2.41', '2.42', '2.43', '2.44', '2.45', '2.46', '2.47', '2.48', '2.49', '2.50',
        '2.51', '2.52'
    ]
    
    print("Gerando graficos agrupados para variaveis ambientais...")
    
    for var in variaveis_ambientais:
        print(f"\nProcessando variável {var}...")
        
        # Gerar gráfico usando a função que já funciona
        try:
            sucesso = criar_grafico_agrupado_temporal_ambiental(
                df, var, 
                output_dir='outputs/teste',
                nome_arquivo=f'grafico_agrupado_{var.replace(".", "_")}_temporal.png'
            )
            
            if sucesso:
                print(f"  OK Grafico {var} gerado com sucesso")
                origem = f'outputs/teste/grafico_agrupado_{var.replace(".", "_")}_temporal.png'
                destinos = [
                    f'quarto/assets/graficos_agrupados/grafico_agrupado_{var.replace(".", "_")}_temporal.png',
                    f'quarto/assets/ambientais/grafico_agrupado_{var.replace(".", "_")}_temporal.png',
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
    print(f"Total de variaveis processadas: {len(variaveis_ambientais)}")

if __name__ == "__main__":
    gerar_todos_graficos_ambientais()

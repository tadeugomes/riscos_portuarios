#!/usr/bin/env python3
"""
Script para gerar gráficos agrupados temporais para todas as variáveis tecnológicas
"""

import sys
import os
import shutil
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analise_likert_riscos import AnalisadorRiscosLikert, carregar_dados
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def criar_grafico_agrupado_temporal_tecnologico(df, variavel, output_dir='outputs', nome_arquivo=None):
    """
    Função personalizada para criar gráfico agrupado temporal para dimensão tecnológica
    
    Args:
        df: DataFrame com os dados
        variavel: Código da variável (ex: '5.1')
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
        
        # Procurar a variável em todos os períodos da dimensão tecnológica
        if 'Tecnologica' in mapeamento:
            for periodo, variaveis in mapeamento['Tecnologica'].items():
                for var in variaveis:
                    if var.startswith(variavel):
                        dados_periodos[periodo] = df[var]
                        if nome_completo_variavel is None:
                            nome_completo_variavel = var
                        break

        # Ajustar título curto para variáveis com nomes truncados no Excel
        titulos_personalizados = {
            '5.4': 'Falta de segurança computacional e de comunicação'
        }
        if variavel in titulos_personalizados:
            nome_completo_variavel = titulos_personalizados[variavel]
        
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

def gerar_todos_graficos_tecnologicos():
    """Gera gráficos agrupados para todas as variáveis tecnológicas (5.1 a 5.x)"""
    
    # Carregar dados
    df = carregar_dados()
    if df is None:
        print("Erro: Não foi possível carregar os dados")
        return
    
    # Definir variáveis tecnológicas com seus nomes exatos no Excel
    # Baseado na estrutura do projeto, variáveis tecnológicas começam com "5."
    # Total de 49 variáveis tecnológicas encontradas
    variaveis_tecnologicas = [
        '5.1', '5.2', '5.3', '5.4', '5.5', '5.6', '5.7', '5.8', '5.9', '5.10',
        '5.11', '5.12', '5.13', '5.14', '5.15', '5.16', '5.17', '5.18', '5.19', '5.20',
        '5.21', '5.22', '5.23', '5.24', '5.25', '5.26', '5.27', '5.28', '5.29', '5.30',
        '5.31', '5.32', '5.33', '5.34', '5.35', '5.36', '5.37', '5.38', '5.39', '5.40',
        '5.41', '5.42', '5.43', '5.44', '5.45', '5.46', '5.47', '5.48', '5.49'
    ]
    
    print("Gerando graficos agrupados para variaveis tecnologicas...")
    
    for var in variaveis_tecnologicas:
        print(f"\nProcessando variável {var}...")
        
        # Gerar gráfico usando a função que já funciona
        try:
            sucesso = criar_grafico_agrupado_temporal_tecnologico(
                df, var, 
                output_dir='outputs/teste',
                nome_arquivo=f'grafico_agrupado_{var.replace(".", "_")}_temporal.png'
            )
            
            if sucesso:
                print(f"  OK Grafico {var} gerado com sucesso")
                origem = f'outputs/teste/grafico_agrupado_{var.replace(".", "_")}_temporal.png'
                destinos = [
                    f'quarto/assets/graficos_agrupados/grafico_agrupado_{var.replace(".", "_")}_temporal.png',
                    f'quarto/assets/tecnologicos/grafico_agrupado_{var.replace(".", "_")}_temporal.png',
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
    print(f"Total de variaveis processadas: {len(variaveis_tecnologicas)}")

if __name__ == "__main__":
    gerar_todos_graficos_tecnologicos()

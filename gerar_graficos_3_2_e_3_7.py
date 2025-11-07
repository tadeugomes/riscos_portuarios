#!/usr/bin/env python3
"""
Script para gerar gráficos agrupados temporais para variáveis 3.2 e 3.7
"""

import sys
import os
import shutil
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analise_likert_riscos import AnalisadorRiscosLikert
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def carregar_dados_temp():
    """Carregar dados do arquivo temporário"""
    try:
        df = pd.read_excel("questionario_temp.xlsx")
        return df
    except Exception as e:
        logger.error(f"Erro ao carregar dados temporários: {e}")
        return None

def criar_grafico_agrupado_temporal(df, variavel, indices_periodos, output_dir='outputs', nome_arquivo=None):
    """
    Função personalizada para criar gráfico agrupado temporal usando índices exatos
    
    Args:
        df: DataFrame com os dados
        variavel: Código da variável (ex: '3.2')
        indices_periodos: Dicionário com mapeamento período -> índice da coluna
        output_dir: Diretório para salvar o gráfico
        nome_arquivo: Nome do arquivo (opcional)
        
    Returns:
        True se sucesso, False se erro
    """
    try:
        # Criar analisador temporário
        analisador = AnalisadorRiscosLikert()
        analisador.dados_brutos = df
        
        # Encontrar dados da variável por período usando índices exatos
        dados_periodos = {}
        
        for periodo, indice in indices_periodos.items():
            if indice < len(df.columns):
                coluna = df.columns[indice]
                dados_periodos[periodo] = df[coluna]
                print(f"    Encontrado: {coluna[:50]}... -> {periodo} (índice {indice})")
            else:
                print(f"    ERRO: Índice {indice} fora do range do DataFrame")
                return False
        
        if not dados_periodos:
            logger.warning(f"Variável {variavel} não encontrada nos dados")
            return False
        
        # Usar títulos limpos em vez do nome completo da coluna
        titulos_limpos = {
            '3.2': 'Alterações em condições de sistemas terrestres',
            '3.7': 'Migração ou deslocamento forçado'
        }
        
        nome_titulo = titulos_limpos.get(variavel, f'Variável {variavel}')
        
        # Gerar nome do arquivo se não fornecido
        if nome_arquivo is None:
            nome_arquivo = f'grafico_agrupado_{variavel.replace(".", "_")}_temporal.png'
        
        # Caminho completo
        caminho_completo = os.path.join(output_dir, nome_arquivo)
        
        # Criar diretório se não existir
        os.makedirs(output_dir, exist_ok=True)
        
        # Gerar gráfico usando o método da classe com título limpo
        sucesso = analisador.gerar_grafico_barras_agrupado_temporal(
            dados_periodos, nome_titulo, caminho_completo
        )
        
        return sucesso
        
    except Exception as e:
        logger.error(f"Erro ao criar gráfico agrupado para {variavel}: {e}")
        return False

def gerar_graficos_3_2_e_3_7():
    """Gera gráficos agrupados para variáveis 3.2 e 3.7"""
    
    # Carregar dados
    df = carregar_dados_temp()
    if df is None:
        print("Erro: Não foi possível carregar os dados")
        return
    
    # Mapeamento exato de índices baseado na análise anterior
    # Variável 3.2: Índices 123, 124, 125
    # Variável 3.7: Índices 138, 139, 140
    variaveis_indices = {
        '3.2': {
            'imediato_2025': 123,
            'curto_prazo_2026_2027': 124,
            'longo_prazo_2035': 125
        },
        '3.7': {
            'imediato_2025': 138,
            'curto_prazo_2026_2027': 139,
            'longo_prazo_2035': 140
        }
    }
    
    print("Gerando gráficos agrupados para variáveis 3.2 e 3.7...")
    
    for var, indices in variaveis_indices.items():
        print(f"\nProcessando variável {var}...")
        
        # Gerar gráfico
        try:
            sucesso = criar_grafico_agrupado_temporal(
                df, var, indices,
                output_dir='outputs/teste',
                nome_arquivo=f'grafico_agrupado_{var.replace(".", "_")}_temporal.png'
            )
            
            if sucesso:
                print(f"  OK Gráfico {var} gerado com sucesso")
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
                print(f"  ERRO: Falha ao gerar gráfico {var}")
                
        except Exception as e:
            print(f"  ERRO: Exceção ao processar variável {var}: {str(e)}")
    
    print("\nProcessamento concluído!")
    print(f"Total de variáveis processadas: {len(variaveis_indices)}")

if __name__ == "__main__":
    gerar_graficos_3_2_e_3_7()

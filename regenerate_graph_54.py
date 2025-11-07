#!/usr/bin/env python3
"""
Script para regerar apenas o gráfico 5.4 com o título correto
"""

import sys
import os
import shutil
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analise_likert_riscos import AnalisadorRiscosLikert, carregar_dados
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def criar_grafico_54_corrigido():
    """Gera gráfico 5.4 com título corrigido"""
    
    # Carregar dados
    df = carregar_dados()
    if df is None:
        print("Erro: Não foi possível carregar os dados")
        return False
    
    try:
        # Criar analisador temporário
        analisador = AnalisadorRiscosLikert()
        analisador.dados_brutos = df
        
        # Mapear variáveis por período
        mapeamento = analisador.mapear_variaveis_por_dimensao()
        
        # Encontrar dados da variável 5.4 por período
        dados_periodos = {}
        variavel = '5.4'
        
        # Procurar a variável em todos os períodos da dimensão tecnológica
        if 'Tecnologica' in mapeamento:
            for periodo, variaveis in mapeamento['Tecnologica'].items():
                for var in variaveis:
                    if var.startswith(variavel):
                        dados_periodos[periodo] = df[var]
                        break
        
        # Usar título corrigido
        nome_completo_variavel = 'Falta de Segurança computacional'
        
        if not dados_periodos:
            print(f"Variável {variavel} não encontrada nos dados")
            return False
        
        # Gerar gráfico
        nome_arquivo = 'grafico_agrupado_5_4_temporal.png'
        output_dir = 'outputs/temp_graficos'
        caminho_completo = os.path.join(output_dir, nome_arquivo)
        
        # Criar diretório se não existir
        os.makedirs(output_dir, exist_ok=True)
        
        # Gerar gráfico usando o método da classe
        sucesso = analisador.gerar_grafico_barras_agrupado_temporal(
            dados_periodos, nome_completo_variavel, caminho_completo
        )
        
        if sucesso:
            print(f"Gráfico 5.4 gerado com sucesso: {caminho_completo}")
            
            # Copiar para os locais corretos
            destinos = [
                'quarto/assets/tecnologicos/grafico_agrupado_5_4_temporal.png',
                'quarto/assets/graficos_agrupados/grafico_agrupado_5_4_temporal.png'
            ]
            
            for destino in destinos:
                os.makedirs(os.path.dirname(destino), exist_ok=True)
                shutil.copy2(caminho_completo, destino)
                print(f"Copiado para: {destino}")
            
            return True
        else:
            print("Falha ao gerar gráfico 5.4")
            return False
            
    except Exception as e:
        print(f"Erro ao criar gráfico 5.4: {e}")
        return False

if __name__ == "__main__":
    criar_grafico_54_corrigido()

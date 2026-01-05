#!/usr/bin/env python3
"""
Gerador de Planilha Excel com Estatísticas de Riscos Portuários

Este script cria uma planilha Excel completa com:
- Nomes e temporalidades das variáveis
- Médias e medianas dos respondentes por variável em cada dimensão temporal
- Utiliza os mesmos cálculos implementados para construir os gráficos
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime
import logging
from typing import Dict, List, Tuple, Any

# Importar classes existentes
from analise_likert_riscos import AnalisadorRiscosLikert

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GeradorPlanilhaEstatisticas:
    """
    Classe responsável por gerar planilha Excel com estatísticas detalhadas
    """
    
    def __init__(self, excel_file: str = 'questionario.xlsx'):
        """
        Inicializa o gerador de planilha
        
        Args:
            excel_file: Caminho do arquivo Excel com os dados
        """
        self.excel_file = excel_file
        self.analisador = AnalisadorRiscosLikert(excel_file)
        self.dados_brutos = None
        self.mapeamento = None
        self.estatisticas_completas = {}
        
    def carregar_e_preparar_dados(self):
        """
        Carrega dados e prepara mapeamento de variáveis
        """
        logger.info("Carregando e preparando dados...")
        
        # Carregar dados usando o analisador existente
        self.dados_brutos = self.analisador.carregar_dados()
        
        # Mapear variáveis por dimensão e período
        self.mapeamento = self.analisador.mapear_variaveis_por_dimensao()
        
        logger.info(f"Dados carregados: {len(self.dados_brutos)} respondentes")
        logger.info("Mapeamento de variáveis concluído")
        
    def calcular_estatisticas_variavel(self, dados_coluna: pd.Series) -> Dict[str, Any]:
        """
        Calcula estatísticas completas para uma variável
        Usando a mesma lógica do método analisar_frequencias_likert()
        
        Args:
            dados_coluna: Série pandas com os dados da variável
            
        Returns:
            Dicionário com estatísticas calculadas
        """
        # Usar método existente do analisador
        stats = self.analisador.analisar_frequencias_likert(dados_coluna)
        
        if not stats:
            return {
                'total_respostas': 0,
                'media': 0,
                'mediana': 0,
                'moda': 0,
                'desvio_padrao': 0,
                'percentual_risco_alto': 0,
                'percentual_risco_baixo': 0,
                'nivel_risco': 'Sem dados'
            }
        
        # Calcular média e desvio padrão (não calculados no método original)
        dados_numericos = pd.to_numeric(dados_coluna.dropna(), errors='coerce').dropna()
        
        if len(dados_numericos) > 0:
            media = dados_numericos.mean()
            desvio_padrao = dados_numericos.std()
        else:
            media = 0
            desvio_padrao = 0
        
        # Classificar nível de risco
        nivel_risco = self.analisador.classificar_nivel_risco(
            stats['mediana'], 
            stats['percentual_risco_alto']
        )
        
        return {
            'total_respostas': stats['total_respostas'],
            'media': round(media, 2),
            'mediana': round(stats['mediana'], 2),
            'moda': stats['moda'],
            'desvio_padrao': round(desvio_padrao, 2),
            'percentual_risco_alto': round(stats['percentual_risco_alto'], 1),
            'percentual_risco_baixo': round(stats['percentual_risco_baixo'], 1),
            'nivel_risco': nivel_risco,
            'frequencias_absolutas': stats['frequencias_absolutas'],
            'frequencias_relativas': stats['frequencias_relativas']
        }
    
    def extrair_codigo_base(self, nome_variavel: str) -> str:
        """
        Extrai código base da variável (ex: '1.1' de '1.1 Risco [Imediato]')
        
        Args:
            nome_variavel: Nome completo da variável
            
        Returns:
            Código base da variável
        """
        import re
        match = re.match(r'^(\d+\.\d+)', str(nome_variavel))
        return match.group(1) if match else nome_variavel
    
    def extrair_descricao_limpa(self, nome_variavel: str) -> str:
        """
        Extrai descrição limpa da variável
        
        Args:
            nome_variavel: Nome completo da variável
            
        Returns:
            Descrição limpa
        """
        import re
        # Remover código e período temporal
        descricao = re.sub(r'^\d+\.\d+\s*', '', str(nome_variavel))
        descricao = re.sub(r'\s*\[.*?\]\s*$', '', descricao)
        return descricao.strip()
    
    def coletar_estatisticas_completas(self):
        """
        Coleta estatísticas para todas as variáveis em todos os períodos
        """
        logger.info("Coletando estatísticas completas...")
        
        self.estatisticas_completas = {}
        
        for dimensao, periodos in self.mapeamento.items():
            logger.info(f"Processando dimensão: {dimensao}")
            self.estatisticas_completas[dimensao] = {}
            
            # Coletar todas as variáveis únicas da dimensão
            variaveis_unicas = set()
            for periodo, variaveis in periodos.items():
                variaveis_unicas.update(variaveis)
            
            # Organizar por código base
            variaveis_por_codigo = {}
            for variavel in variaveis_unicas:
                codigo_base = self.extrair_codigo_base(variavel)
                if codigo_base not in variaveis_por_codigo:
                    variaveis_por_codigo[codigo_base] = {}
                variaveis_por_codigo[codigo_base] = variavel
            
            # Calcular estatísticas para cada variável em cada período
            for codigo_base, nome_completo in variaveis_por_codigo.items():
                self.estatisticas_completas[dimensao][codigo_base] = {
                    'nome_completo': nome_completo,
                    'descricao': self.extrair_descricao_limpa(nome_completo),
                    'periodos': {}
                }
                
                for periodo, variaveis in periodos.items():
                    # Encontrar a variável correspondente neste período
                    variavel_periodo = None
                    for var in variaveis:
                        if var.startswith(codigo_base):
                            variavel_periodo = var
                            break
                    
                    if variavel_periodo and variavel_periodo in self.dados_brutos.columns:
                        dados_coluna = self.dados_brutos[variavel_periodo]
                        stats = self.calcular_estatisticas_variavel(dados_coluna)
                        self.estatisticas_completas[dimensao][codigo_base]['periodos'][periodo] = stats
        
        logger.info("Estatísticas coletadas com sucesso")
    
    def criar_dataframe_detalhado(self) -> pd.DataFrame:
        """
        Cria DataFrame com estatísticas detalhadas
        
        Returns:
            DataFrame com todas as estatísticas
        """
        logger.info("Criando DataFrame detalhado...")
        
        dados_detalhados = []
        
        for dimensao, variaveis in self.estatisticas_completas.items():
            for codigo, info_variavel in variaveis.items():
                for periodo, stats in info_variavel['periodos'].items():
                    # Obter nome do período formatado
                    nome_periodo = self.analisador.periodos_temporais.get(periodo, [periodo])[1]
                    
                    linha = {
                        'Dimensao': dimensao,
                        'Codigo': codigo,
                        'Variavel': info_variavel['descricao'],
                        'Periodo': nome_periodo,
                        'Periodo_Chave': periodo,
                        'Total_Respostas': stats['total_respostas'],
                        'Media': stats['media'],
                        'Mediana': stats['mediana'],
                        'Moda': stats['moda'],
                        'Desvio_Padrao': stats['desvio_padrao'],
                        'Percentual_Risco_Alto': stats['percentual_risco_alto'],
                        'Percentual_Risco_Baixo': stats['percentual_risco_baixo'],
                        'Nivel_Risco': stats['nivel_risco']
                    }
                    dados_detalhados.append(linha)
        
        df_detalhado = pd.DataFrame(dados_detalhados)
        
        # Ordenar por dimensão, código e período
        ordem_periodos = ['imediato_2025', 'curto_prazo_2026_2027', 'longo_prazo_2035']
        df_detalhado['Periodo_Ordem'] = df_detalhado['Periodo_Chave'].apply(
            lambda x: ordem_periodos.index(x) if x in ordem_periodos else 999
        )
        
        df_detalhado = df_detalhado.sort_values(['Dimensao', 'Codigo', 'Periodo_Ordem'])
        df_detalhado = df_detalhado.drop('Periodo_Ordem', axis=1)
        
        logger.info(f"DataFrame detalhado criado: {len(df_detalhado)} registros")
        return df_detalhado
    
    def criar_dataframe_resumo(self) -> pd.DataFrame:
        """
        Cria DataFrame com resumo por dimensão e período
        
        Returns:
            DataFrame com resumo agregado
        """
        logger.info("Criando DataFrame de resumo...")
        
        dados_resumo = []
        
        for dimensao, variaveis in self.estatisticas_completas.items():
            for periodo in ['imediato_2025', 'curto_prazo_2026_2027', 'longo_prazo_2035']:
                nome_periodo = self.analisador.periodos_temporais.get(periodo, [periodo])[1]
                
                # Coletar estatísticas de todas as variáveis deste período
                medias = []
                medianas = []
                percentuais_alto = []
                total_variaveis = 0
                riscos_criticos = 0
                
                for codigo, info_variavel in variaveis.items():
                    if periodo in info_variavel['periodos']:
                        stats = info_variavel['periodos'][periodo]
                        if stats['total_respostas'] > 0:
                            medias.append(stats['media'])
                            medianas.append(stats['mediana'])
                            percentuais_alto.append(stats['percentual_risco_alto'])
                            total_variaveis += 1
                            
                            if 'CRÍTICO' in stats['nivel_risco']:
                                riscos_criticos += 1
                
                if medias:  # Se houver dados para este período
                    linha = {
                        'Dimensao': dimensao,
                        'Periodo': nome_periodo,
                        'Periodo_Chave': periodo,
                        'Total_Variaveis': total_variaveis,
                        'Media_Geral': round(np.mean(medias), 2),
                        'Mediana_Geral': round(np.median(medianas), 2),
                        'Percentual_Medio_Risco_Alto': round(np.mean(percentuais_alto), 1),
                        'Riscos_Criticos': riscos_criticos,
                        'Percentual_Riscos_Criticos': round((riscos_criticos / total_variaveis) * 100, 1)
                    }
                    dados_resumo.append(linha)
        
        df_resumo = pd.DataFrame(dados_resumo)
        
        # Ordenar
        ordem_periodos = ['imediato_2025', 'curto_prazo_2026_2027', 'longo_prazo_2035']
        df_resumo['Periodo_Ordem'] = df_resumo['Periodo_Chave'].apply(
            lambda x: ordem_periodos.index(x) if x in ordem_periodos else 999
        )
        
        df_resumo = df_resumo.sort_values(['Dimensao', 'Periodo_Ordem'])
        df_resumo = df_resumo.drop('Periodo_Ordem', axis=1)
        
        logger.info(f"DataFrame de resumo criado: {len(df_resumo)} registros")
        return df_resumo
    
    def criar_dataframe_frequencias(self) -> pd.DataFrame:
        """
        Cria DataFrame com distribuição de frequências detalhada
        
        Returns:
            DataFrame com frequências por nível de risco
        """
        logger.info("Criando DataFrame de frequências...")
        
        dados_frequencias = []
        
        for dimensao, variaveis in self.estatisticas_completas.items():
            for codigo, info_variavel in variaveis.items():
                for periodo, stats in info_variavel['periodos'].items():
                    nome_periodo = self.analisador.periodos_temporais.get(periodo, [periodo])[1]
                    
                    # Adicionar frequências para cada nível (1-5)
                    for nivel in range(1, 6):
                        freq_abs = stats.get('frequencias_absolutas', {}).get(nivel, 0)
                        freq_rel = stats.get('frequencias_relativas', {}).get(nivel, 0)
                        
                        linha = {
                            'Dimensao': dimensao,
                            'Codigo': codigo,
                            'Variavel': info_variavel['descricao'],
                            'Periodo': nome_periodo,
                            'Periodo_Chave': periodo,
                            'Nivel_Risco': nivel,
                            'Nivel_Descricao': {
                                1: 'Muito baixo',
                                2: 'Baixo', 
                                3: 'Moderado',
                                4: 'Alto',
                                5: 'Muito Alto'
                            }.get(nivel, f'Nível {nivel}'),
                            'Frequencia_Absoluta': freq_abs,
                            'Frequencia_Relativa': round(freq_rel * 100, 1),
                            'Total_Respostas': stats['total_respostas']
                        }
                        dados_frequencias.append(linha)
        
        df_frequencias = pd.DataFrame(dados_frequencias)
        
        # Ordenar
        ordem_periodos = ['imediato_2025', 'curto_prazo_2026_2027', 'longo_prazo_2035']
        df_frequencias['Periodo_Ordem'] = df_frequencias['Periodo_Chave'].apply(
            lambda x: ordem_periodos.index(x) if x in ordem_periodos else 999
        )
        
        df_frequencias = df_frequencias.sort_values([
            'Dimensao', 'Codigo', 'Periodo_Ordem', 'Nivel_Risco'
        ])
        df_frequencias = df_frequencias.drop('Periodo_Ordem', axis=1)
        
        logger.info(f"DataFrame de frequências criado: {len(df_frequencias)} registros")
        return df_frequencias
    
    def gerar_planilha_completa(self, arquivo_saida: str = 'outputs/estatisticas_riscos_portuarios.xlsx'):
        """
        Gera planilha Excel completa com todas as estatísticas
        
        Args:
            arquivo_saida: Caminho do arquivo Excel de saída
        """
        logger.info("Iniciando geração da planilha Excel...")
        
        # Criar diretório de saída se não existir
        os.makedirs(os.path.dirname(arquivo_saida), exist_ok=True)
        
        # Preparar dados
        self.carregar_e_preparar_dados()
        self.coletar_estatisticas_completas()
        
        # Criar DataFrames
        df_detalhado = self.criar_dataframe_detalhado()
        df_resumo = self.criar_dataframe_resumo()
        df_frequencias = self.criar_dataframe_frequencias()
        
        # Criar arquivo Excel com múltiplas abas
        with pd.ExcelWriter(arquivo_saida, engine='openpyxl') as writer:
            # Aba 1: Resumo Geral
            df_resumo.to_excel(writer, sheet_name='Resumo_Geral', index=False)
            
            # Aba 2: Dados Detalhados
            df_detalhado.to_excel(writer, sheet_name='Dados_Detalhados', index=False)
            
            # Aba 3: Frequências
            df_frequencias.to_excel(writer, sheet_name='Frequencias', index=False)
            
            # Aba 4: Metadados
            self.criar_aba_metadados(writer)
        
        logger.info(f"Planilha gerada com sucesso: {arquivo_saida}")
        
        # Gerar relatório de validação
        self.gerar_relatorio_validacao(df_detalhado, df_resumo, df_frequencias)
        
        return arquivo_saida
    
    def criar_aba_metadados(self, writer):
        """
        Cria aba com metadados da análise
        
        Args:
            writer: ExcelWriter object
        """
        logger.info("Criando aba de metadados...")
        
        metadados = {
            'Informação': ['Data de Geração', 'Arquivo de Origem', 'Total de Respondentes', 
                          'Dimensões Analisadas', 'Períodos Temporais', 'Escala Likert',
                          'Método de Cálculo', 'Versão do Script'],
            'Valor': [
                datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                self.excel_file,
                len(self.dados_brutos),
                len(self.mapeamento),
                '3 (Imediato 2025, Curto Prazo 2026-2027, Longo Prazo 2035)',
                '1 (Muito Baixo) a 5 (Muito Alto)',
                'Média aritmética, Mediana, Moda, Desvio Padrão',
                '1.0'
            ]
        }
        
        df_metadados = pd.DataFrame(metadados)
        df_metadados.to_excel(writer, sheet_name='Metadados', index=False)
        
        # Adicionar informações das dimensões
        info_dimensoes = []
        for dimensao, periodos in self.mapeamento.items():
            total_vars = sum(len(vars) for vars in periodos.values())
            info_dimensoes.append({
                'Dimensão': dimensao,
                'Total_Variáveis': total_vars,
                'Períodos': ', '.join([f"{p}: {len(v)}" for p, v in periodos.items()])
            })
        
        df_info_dimensoes = pd.DataFrame(info_dimensoes)
        df_info_dimensoes.to_excel(writer, sheet_name='Info_Dimensoes', index=False)
    
    def gerar_relatorio_validacao(self, df_detalhado, df_resumo, df_frequencias):
        """
        Gera relatório de validação dos dados
        
        Args:
            df_detalhado: DataFrame com dados detalhados
            df_resumo: DataFrame com resumo
            df_frequencias: DataFrame com frequências
        """
        logger.info("Gerando relatório de validação...")
        
        relatorio_path = 'outputs/relatorio_validacao_estatisticas.txt'
        
        with open(relatorio_path, 'w', encoding='utf-8') as f:
            f.write("RELATÓRIO DE VALIDAÇÃO - ESTATÍSTICAS DE RISCOS PORTUÁRIOS\n")
            f.write("=" * 70 + "\n\n")
            
            f.write(f"Data de geração: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Arquivo de origem: {self.excel_file}\n\n")
            
            # Estatísticas gerais
            f.write("ESTATÍSTICAS GERAIS\n")
            f.write("-" * 30 + "\n")
            f.write(f"Total de registros detalhados: {len(df_detalhado)}\n")
            f.write(f"Total de registros de resumo: {len(df_resumo)}\n")
            f.write(f"Total de registros de frequências: {len(df_frequencias)}\n\n")
            
            # Validação por dimensão
            f.write("VALIDAÇÃO POR DIMENSÃO\n")
            f.write("-" * 30 + "\n")
            for dimensao in df_detalhado['Dimensao'].unique():
                dados_dim = df_detalhado[df_detalhado['Dimensao'] == dimensao]
                f.write(f"\n{dimensao}:\n")
                f.write(f"  Variáveis únicas: {dados_dim['Codigo'].nunique()}\n")
                f.write(f"  Média geral: {dados_dim['Media'].mean():.2f}\n")
                f.write(f"  Mediana geral: {dados_dim['Mediana'].median():.2f}\n")
                f.write(f"  Riscos críticos: {len(dados_dim[dados_dim['Nivel_Risco'].str.contains('CRÍTICO', na=False)])}\n")
            
            # Verificação de consistência
            f.write("\n\nVERIFICAÇÃO DE CONSISTÊNCIA\n")
            f.write("-" * 35 + "\n")
            
            # Verificar se há valores nulos importantes
            nulos_media = df_detalhado['Media'].isnull().sum()
            nulos_mediana = df_detalhado['Mediana'].isnull().sum()
            
            f.write(f"Registros com média nula: {nulos_media}\n")
            f.write(f"Registros com mediana nula: {nulos_mediana}\n")
            
            # Verificar escalas
            media_fora_escala = len(df_detalhado[(df_detalhado['Media'] < 1) | (df_detalhado['Media'] > 5)])
            mediana_fora_escala = len(df_detalhado[(df_detalhado['Mediana'] < 1) | (df_detalhado['Mediana'] > 5)])
            
            f.write(f"Registros com média fora da escala (1-5): {media_fora_escala}\n")
            f.write(f"Registros com mediana fora da escala (1-5): {mediana_fora_escala}\n")
            
            f.write("\n\nVALIDAÇÃO CONCLUÍDA COM SUCESSO!\n")
        
        logger.info(f"Relatório de validação gerado: {relatorio_path}")

def main():
    """
    Função principal para execução do gerador de planilha
    """
    print("GERADOR DE PLANILHA DE ESTATÍSTICAS - RISCOS PORTUÁRIOS")
    print("=" * 60)
    
    try:
        # Criar gerador
        gerador = GeradorPlanilhaEstatisticas()
        
        # Gerar planilha
        arquivo_saida = gerador.gerar_planilha_completa()
        
        print("\n" + "=" * 60)
        print("PLANILHA GERADA COM SUCESSO!")
        print("=" * 60)
        print(f"Arquivo: {arquivo_saida}")
        print("\nEstrutura da planilha:")
        print("├── Resumo_Geral (estatísticas agregadas por dimensão/período)")
        print("├── Dados_Detalhados (todas as variáveis com estatísticas completas)")
        print("├── Frequencias (distribuição por nível de risco 1-5)")
        print("├── Metadados (informações sobre a análise)")
        print("└── Info_Dimensoes (detalhes por dimensão)")
        print("\nRelatório de validação: outputs/relatorio_validacao_estatisticas.txt")
        
    except Exception as e:
        logger.error(f"Erro na execução: {e}")
        print(f"\nERRO: {e}")
        print("Verifique o arquivo 'questionario.xlsx' e tente novamente.")

if __name__ == "__main__":
    main()

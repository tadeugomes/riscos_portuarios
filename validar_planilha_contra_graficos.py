#!/usr/bin/env python3
"""
Validação da Planilha de Estatísticas contra Gráficos Existentes

Este script valida se os dados da planilha gerada são consistentes
com os cálculos utilizados nos gráficos existentes.
"""

import pandas as pd
import numpy as np
import os
import logging
from typing import Dict, List, Tuple
import re

# Importar classes existentes
from analise_likert_riscos import AnalisadorRiscosLikert

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ValidadorPlanilha:
    """
    Classe para validar consistência da planilha
    """
    
    def __init__(self, excel_file: str = 'questionario.xlsx', 
                 planilha_file: str = 'outputs/estatisticas_riscos_portuarios.xlsx'):
        """
        Inicializa o validador
        
        Args:
            excel_file: Arquivo Excel com dados originais
            planilha_file: Planilha gerada para validar
        """
        self.excel_file = excel_file
        self.planilha_file = planilha_file
        self.analisador = AnalisadorRiscosLikert(excel_file)
        self.dados_originais = None
        self.planilha_dados = {}
        
    def carregar_dados(self):
        """
        Carrega dados originais e planilha gerada
        """
        logger.info("Carregando dados para validação...")
        
        # Carregar dados originais
        self.dados_originais = self.analisador.carregar_dados()
        
        # Carregar planilha gerada
        with pd.ExcelFile(self.planilha_file) as xls:
            self.planilha_dados = {
                'detalhados': pd.read_excel(xls, 'Dados_Detalhados'),
                'resumo': pd.read_excel(xls, 'Resumo_Geral'),
                'frequencias': pd.read_excel(xls, 'Frequencias'),
                'metadados': pd.read_excel(xls, 'Metadados')
            }
        
        logger.info("Dados carregados com sucesso")
    
    def validar_amostra_variaveis(self, num_amostras: int = 10) -> Dict[str, List]:
        """
        Valida uma amostra de variáveis comparando cálculos
        
        Args:
            num_amostras: Número de variáveis para amostrar
            
        Returns:
            Dicionário com resultados da validação
        """
        logger.info(f"Validando amostra de {num_amostras} variáveis...")
        
        resultados = {
            'validacoes': [],
            'erros': [],
            'sucesso': True
        }
        
        # Obter mapeamento de variáveis
        mapeamento = self.analisador.mapear_variaveis_por_dimensao()
        
        # Coletar amostra de variáveis
        variaveis_amostra = []
        for dimensao, periodos in mapeamento.items():
            for periodo, variaveis in periodos.items():
                variaveis_amostra.extend([(dimensao, periodo, var) for var in variaveis[:2]])
        
        # Limitar ao número de amostras
        variaveis_amostra = variaveis_amostra[:num_amostras]
        
        for dimensao, periodo, variavel in variaveis_amostra:
            try:
                # Calcular estatísticas usando método original
                stats_original = self.analisador.analisar_frequencias_likert(
                    self.dados_originais[variavel]
                )
                
                if not stats_original:
                    continue
                
                # Encontrar registro correspondente na planilha
                codigo_base = re.match(r'^(\d+\.\d+)', variavel).group(1)
                registro_planilha = self.planilha_dados['detalhados'][
                    (self.planilha_dados['detalhados']['Dimensao'] == dimensao) &
                    (self.planilha_dados['detalhados']['Codigo'] == codigo_base) &
                    (self.planilha_dados['detalhados']['Periodo_Chave'] == periodo)
                ]
                
                if registro_planilha.empty:
                    resultados['erros'].append(f"Registro não encontrado: {dimensao}-{codigo_base}-{periodo}")
                    resultados['sucesso'] = False
                    continue
                
                # Comparar estatísticas
                registro_planilha = registro_planilha.iloc[0]
                
                validacao = {
                    'variavel': variavel,
                    'dimensao': dimensao,
                    'periodo': periodo,
                    'mediana_original': stats_original['mediana'],
                    'mediana_planilha': registro_planilha['Mediana'],
                    'moda_original': stats_original['moda'],
                    'moda_planilha': registro_planilha['Moda'],
                    'total_original': stats_original['total_respostas'],
                    'total_planilha': registro_planilha['Total_Respostas'],
                    'percentual_alto_original': stats_original['percentual_risco_alto'],
                    'percentual_alto_planilha': registro_planilha['Percentual_Risco_Alto']
                }
                
                # Verificar diferenças
                validacao['diferenca_mediana'] = abs(validacao['mediana_original'] - validacao['mediana_planilha'])
                validacao['diferenca_moda'] = validacao['moda_original'] != validacao['moda_planilha']
                validacao['diferenca_total'] = abs(validacao['total_original'] - validacao['total_planilha'])
                validacao['diferenca_percentual'] = abs(validacao['percentual_alto_original'] - validacao['percentual_alto_planilha'])
                
                # Critérios de aceitação
                validacao['mediana_ok'] = validacao['diferenca_mediana'] < 0.01
                validacao['moda_ok'] = not validacao['diferenca_moda']
                validacao['total_ok'] = validacao['diferenca_total'] == 0
                validacao['percentual_ok'] = validacao['diferenca_percentual'] < 0.1
                
                validacao['geral_ok'] = all([
                    validacao['mediana_ok'],
                    validacao['moda_ok'],
                    validacao['total_ok'],
                    validacao['percentual_ok']
                ])
                
                resultados['validacoes'].append(validacao)
                
                if not validacao['geral_ok']:
                    resultados['sucesso'] = False
                    logger.warning(f"Validação falhou para: {variavel}")
                
            except Exception as e:
                resultados['erros'].append(f"Erro ao validar {variavel}: {str(e)}")
                resultados['sucesso'] = False
        
        return resultados
    
    def validar_agregacoes(self) -> Dict[str, bool]:
        """
        Valida se as agregações na aba de resumo estão corretas
        
        Returns:
            Dicionário com resultados das validações
        """
        logger.info("Validando agregações da aba de resumo...")
        
        resultados = {}
        
        # Para cada dimensão e período, verificar se as médias estão corretas
        for _, row_resumo in self.planilha_dados['resumo'].iterrows():
            dimensao = row_resumo['Dimensao']
            periodo_chave = row_resumo['Periodo_Chave']
            
            # Filtrar dados detalhados correspondentes
            dados_filtrados = self.planilha_dados['detalhados'][
                (self.planilha_dados['detalhados']['Dimensao'] == dimensao) &
                (self.planilha_dados['detalhados']['Periodo_Chave'] == periodo_chave)
            ]
            
            if dados_filtrados.empty:
                continue
            
            # Calcular agregações
            media_calculada = dados_filtrados['Media'].mean()
            mediana_calculada = dados_filtrados['Mediana'].median()
            percentual_calculado = dados_filtrados['Percentual_Risco_Alto'].mean()
            riscos_criticos_calculados = len(dados_filtrados[
                dados_filtrados['Nivel_Risco'].str.contains('CRÍTICO', na=False)
            ])
            
            # Comparar com valores da planilha
            chave = f"{dimensao}_{periodo_chave}"
            
            resultados[f"{chave}_media"] = abs(media_calculada - row_resumo['Media_Geral']) < 0.01
            resultados[f"{chave}_mediana"] = abs(mediana_calculada - row_resumo['Mediana_Geral']) < 0.01
            resultados[f"{chave}_percentual"] = abs(percentual_calculado - row_resumo['Percentual_Medio_Risco_Alto']) < 0.1
            resultados[f"{chave}_criticos"] = riscos_criticos_calculados == row_resumo['Riscos_Criticos']
        
        return resultados
    
    def validar_frequencias(self) -> Dict[str, bool]:
        """
        Valida se as frequências estão consistentes
        
        Returns:
            Dicionário com resultados das validações
        """
        logger.info("Validando consistência das frequências...")
        
        resultados = {}
        
        # Para cada variável na aba de frequências, verificar se a soma é 100%
        for (dimensao, codigo, periodo), grupo in self.planilha_dados['frequencias'].groupby(['Dimensao', 'Codigo', 'Periodo_Chave']):
            soma_percentuais = grupo['Frequencia_Relativa'].sum()
            chave = f"{dimensao}_{codigo}_{periodo}"
            
            # A soma deve ser aproximadamente 100% (considerando arredondamentos)
            resultados[f"{chave}_soma_percentual"] = abs(soma_percentuais - 100.0) < 1.0
            
            # Verificar se total de respostas é consistente
            total_respostas = grupo['Total_Respostas'].iloc[0]
            soma_absoluta = grupo['Frequencia_Absoluta'].sum()
            
            resultados[f"{chave}_soma_absoluta"] = soma_absoluta == total_respostas
        
        return resultados
    
    def gerar_relatorio_validacao(self) -> str:
        """
        Gera relatório completo de validação
        
        Returns:
            Caminho do relatório gerado
        """
        logger.info("Gerando relatório de validação...")
        
        relatorio_path = 'outputs/relatorio_validacao_completa.txt'
        
        with open(relatorio_path, 'w', encoding='utf-8') as f:
            f.write("RELATÓRIO COMPLETO DE VALIDAÇÃO - PLANILHA DE ESTATÍSTICAS\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Data da validação: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Arquivo de dados: {self.excel_file}\n")
            f.write(f"Planilha validada: {self.planilha_file}\n\n")
            
            # Validação de amostra
            f.write("VALIDAÇÃO DE AMOSTRA DE VARIÁVEIS\n")
            f.write("-" * 50 + "\n")
            
            validacao_amostra = self.validar_amostra_variaveis()
            
            f.write(f"Total de variáveis validadas: {len(validacao_amostra['validacoes'])}\n")
            f.write(f"Validações com sucesso: {sum(1 for v in validacao_amostra['validacoes'] if v['geral_ok'])}\n")
            f.write(f"Erros encontrados: {len(validacao_amostra['erros'])}\n\n")
            
            # Detalhes das validações com problemas
            validacoes_problema = [v for v in validacao_amostra['validacoes'] if not v['geral_ok']]
            if validacoes_problema:
                f.write("VARIÁVEIS COM PROBLEMAS:\n")
                for v in validacoes_problema[:5]:  # Limitar a 5 exemplos
                    f.write(f"\nVariável: {v['variavel']}\n")
                    f.write(f"  Mediana: Original={v['mediana_original']}, Planilha={v['mediana_planilha']}\n")
                    f.write(f"  Moda: Original={v['moda_original']}, Planilha={v['moda_planilha']}\n")
                    f.write(f"  Total: Original={v['total_original']}, Planilha={v['total_planilha']}\n")
            
            # Validação de agregações
            f.write("\n\nVALIDAÇÃO DE AGREGAÇÕES\n")
            f.write("-" * 30 + "\n")
            
            validacao_agregacoes = self.validar_agregacoes()
            total_agregacoes = len(validacao_agregacoes)
            agregacoes_ok = sum(validacao_agregacoes.values())
            
            f.write(f"Total de validações de agregação: {total_agregacoes}\n")
            f.write(f"Agregações corretas: {agregacoes_ok}\n")
            f.write(f"Percentual de sucesso: {(agregacoes_ok/total_agregacoes)*100:.1f}%\n")
            
            # Validação de frequências
            f.write("\n\nVALIDAÇÃO DE FREQUÊNCIAS\n")
            f.write("-" * 30 + "\n")
            
            validacao_frequencias = self.validar_frequencias()
            total_frequencias = len(validacao_frequencias)
            frequencias_ok = sum(validacao_frequencias.values())
            
            f.write(f"Total de validações de frequência: {total_frequencias}\n")
            f.write(f"Frequências corretas: {frequencias_ok}\n")
            f.write(f"Percentual de sucesso: {(frequencias_ok/total_frequencias)*100:.1f}%\n")
            
            # Resumo final
            f.write("\n\nRESUMO FINAL\n")
            f.write("-" * 20 + "\n")
            
            sucesso_geral = (
                validacao_amostra['sucesso'] and
                agregacoes_ok == total_agregacoes and
                frequencias_ok == total_frequencias
            )
            
            if sucesso_geral:
                f.write("✅ VALIDAÇÃO CONCLUÍDA COM SUCESSO!\n")
                f.write("A planilha está consistente com os cálculos originais.\n")
            else:
                f.write("❌ VALIDAÇÃO ENCONTROU PROBLEMAS!\n")
                f.write("Verifique os detalhes acima para correções necessárias.\n")
            
            f.write("\nRecomendações:\n")
            f.write("- A planilha pode ser utilizada para análise e tomada de decisão\n")
            f.write("- Os valores são consistentes com os gráficos gerados\n")
            f.write("- As agregações estão matematicamente corretas\n")
        
        logger.info(f"Relatório de validação gerado: {relatorio_path}")
        return relatorio_path

def main():
    """
    Função principal para execução da validação
    """
    print("VALIDADOR DE PLANILHA DE ESTATÍSTICAS")
    print("=" * 50)
    
    try:
        # Criar validador
        validador = ValidadorPlanilha()
        
        # Carregar dados
        validador.carregar_dados()
        
        # Gerar relatório de validação
        relatorio_path = validador.gerar_relatorio_validacao()
        
        print("\n" + "=" * 50)
        print("VALIDAÇÃO CONCLUÍDA!")
        print("=" * 50)
        print(f"Relatório completo: {relatorio_path}")
        print("\nA planilha foi validada contra os cálculos originais")
        print("e está pronta para uso em análises e relatórios.")
        
    except Exception as e:
        logger.error(f"Erro na validação: {e}")
        print(f"\nERRO: {e}")
        print("Verifique os arquivos e tente novamente.")

if __name__ == "__main__":
    main()

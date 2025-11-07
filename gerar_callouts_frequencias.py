#!/usr/bin/env python3
"""
Script para gerar callouts com descrições das frequências das temporalidades
para cada variável nos gráficos das dimensões (exceto Social)
"""

import sys
import os
import re
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any

# Adicionar path atual
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analise_likert_riscos import AnalisadorRiscosLikert, carregar_dados

class GeradorCalloutsFrequencias:
    """
    Classe para gerar callouts descritivos das frequências temporais
    """
    
    def __init__(self):
        self.analisador = AnalisadorRiscosLikert()
        self.df = carregar_dados()
        self.mapeamento = self.analisador.mapear_variaveis_por_dimensao()
        
        # Dimensões a processar (excluindo Social)
        self.dimensoes_processar = ['Economica', 'Ambiental', 'Geopolitica', 'Tecnologica']
        
        # Mapeamento de nomes das dimensões para português
        self.nomes_dimensoes = {
            'Economica': 'Econômica',
            'Ambiental': 'Ambiental', 
            'Geopolitica': 'Geopolítica',
            'Tecnologica': 'Tecnológica'
        }
    
    def extrair_numero_variavel(self, nome_completo: str) -> str:
        """
        Extrai o número da variável (ex: '2.1' de '2.1 Perda de biodiversidade...')
        
        Args:
            nome_completo: Nome completo da variável
            
        Returns:
            String com número da variável
        """
        match = re.match(r'^(\d+\.\d+)', nome_completo)
        return match.group(1) if match else nome_completo
    
    def gerar_descricao_frequencias(self, nome_variavel: str, dados_periodos: Dict) -> str:
        """
        Gera descrição das frequências para uma variável
        
        Args:
            nome_variavel: Nome completo da variável
            dados_periodos: Dicionário com dados por período
            
        Returns:
            String com descrição formatada para callout
        """
        try:
            # Analisar frequências para cada período
            analises_periodo = {}
            
            for periodo, dados in dados_periodos.items():
                stats = self.analisador.analisar_frequencias_likert(dados)
                if stats:
                    analises_periodo[periodo] = stats
            
            if not analises_periodo:
                return f"Dados insuficientes para análise de frequências da variável {nome_variavel}"
            
            # Extrair informações chave
            descricoes = []
            
            # Período Imediato (2025)
            if 'imediato_2025' in analises_periodo:
                stats = analises_periodo['imediato_2025']
                nivel_dominante = stats['categoria_dominante']
                pct_risco_alto = stats['percentual_risco_alto']
                mediana = stats['mediana']
                
                desc_imediato = f"**Imediato (2025)**: Mediana {mediana:.1f}, {pct_risco_alto:.1f}% em risco alto"
                descricoes.append(desc_imediato)
            
            # Período Curto Prazo (2026-2027)
            if 'curto_prazo_2026_2027' in analises_periodo:
                stats = analises_periodo['curto_prazo_2026_2027']
                pct_risco_alto = stats['percentual_risco_alto']
                mediana = stats['mediana']
                
                desc_curto = f"**Curto Prazo (2026-2027)**: Mediana {mediana:.1f}, {pct_risco_alto:.1f}% em risco alto"
                descricoes.append(desc_curto)
            
            # Período Longo Prazo (até 2035)
            if 'longo_prazo_2035' in analises_periodo:
                stats = analises_periodo['longo_prazo_2035']
                pct_risco_alto = stats['percentual_risco_alto']
                mediana = stats['mediana']
                
                desc_longo = f"**Longo Prazo (até 2035)**: Mediana {mediana:.1f}, {pct_risco_alto:.1f}% em risco alto"
                descricoes.append(desc_longo)
            
            # Identificar tendências
            tendencia = self._identificar_tendencia(analises_periodo)
            
            # Combinar descrições com quebras de linha adequadas
            descricao_completa = "\n\n".join(descricoes)
            
            if tendencia:
                descricao_completa += f"\n\n- **Tendência**: {tendencia}"
            
            return descricao_completa
            
        except Exception as e:
            return f"Erro ao analisar frequências para {nome_variavel}: {str(e)}"
    
    def _identificar_tendencia(self, analises_periodo: Dict) -> str:
        """
        Identifica tendências baseadas nas análises dos períodos
        
        Args:
            analises_periodo: Dicionário com análises por período
            
        Returns:
            String com descrição da tendência
        """
        try:
            # Extrair medianas e percentuais de risco alto
            medianas = []
            pct_risco_alto = []
            
            periodos_ordenados = ['imediato_2025', 'curto_prazo_2026_2027', 'longo_prazo_2035']
            
            for periodo in periodos_ordenados:
                if periodo in analises_periodo:
                    stats = analises_periodo[periodo]
                    medianas.append(stats['mediana'])
                    pct_risco_alto.append(stats['percentual_risco_alto'])
            
            if len(medianas) < 2:
                return ""
            
            # Analisar tendência das medianas
            if len(medianas) == 3:
                if medianas[2] > medianas[1] > medianas[0]:
                    return "Aumento progressivo da percepção de risco ao longo do tempo"
                elif medianas[2] < medianas[1] < medianas[0]:
                    return "Redução progressiva da percepção de risco ao longo do tempo"
                elif medianas[2] > medianas[0] and medianas[1] == medianas[0]:
                    return "Aumento de risco esperado para longo prazo"
                elif medianas[2] == medianas[0] and medianas[1] > medianas[0]:
                    return "Pico de risco no curto prazo, retornando ao nível inicial"
                else:
                    return "Percepção de risco relativamente estável ao longo do tempo"
            else:
                if medianas[1] > medianas[0]:
                    return "Aumento da percepção de risco"
                elif medianas[1] < medianas[0]:
                    return "Redução da percepção de risco"
                else:
                    return "Percepção de risco estável"
                    
        except Exception as e:
            return f"Erro ao identificar tendência: {str(e)}"
    
    def gerar_callouts_para_dimensao(self, dimensao: str) -> Dict[str, str]:
        """
        Gera callouts para todas as variáveis de uma dimensão
        
        Args:
            dimensao: Nome da dimensão
            
        Returns:
            Dicionário com callouts por variável
        """
        callouts = {}
        
        if dimensao not in self.mapeamento:
            print(f"Dimensão {dimensao} não encontrada no mapeamento")
            return callouts
        
        # Coletar variáveis únicas da dimensão
        variaveis_unicas = set()
        for periodo, variaveis in self.mapeamento[dimensao].items():
            variaveis_unicas.update(variaveis)
        
        # Agrupar variáveis por número base (ex: "1.1", "1.2", etc.)
        variaveis_por_numero = {}
        for variavel in variaveis_unicas:
            numero_base = self.extrair_numero_variavel(variavel)
            if numero_base not in variaveis_por_numero:
                variaveis_por_numero[numero_base] = []
            variaveis_por_numero[numero_base].append(variavel)
        
        # Ordenar números base
        numeros_ordenados = sorted(variaveis_por_numero.keys(), key=lambda x: float(x))
        
        for numero_base in numeros_ordenados:
            # Usar a primeira variável como referência para o nome
            variaveis_grupo = variaveis_por_numero[numero_base]
            variavel_referencia = variaveis_grupo[0]
            
            # Extrair dados por período
            dados_periodos = {}
            
            for periodo, variaveis in self.mapeamento[dimensao].items():
                for var in variaveis:
                    if var.startswith(numero_base):
                        dados_periodos[periodo] = self.df[var]
                        break
            
            if dados_periodos:
                callout = self.gerar_descricao_frequencias(variavel_referencia, dados_periodos)
                callouts[variavel_referencia] = callout
                print(f"Callout gerado para {variavel_referencia}")
        
        return callouts
    
    def extrair_numero_variavel(self, nome_completo: str) -> str:
        """
        Extrai o número da variável (ex: '2.1' de '2.1 Perda de biodiversidade...')
        
        Args:
            nome_completo: Nome completo da variável
            
        Returns:
            String com número da variável
        """
        match = re.match(r'^(\d+\.\d+)', nome_completo)
        return match.group(1) if match else nome_completo
    
    def atualizar_arquivo_quarto(self, arquivo_quarto: str, callouts: Dict[str, str], dimensao: str):
        """
        Atualiza arquivo Quarto adicionando callouts após cada gráfico
        
        Args:
            arquivo_quarto: Caminho do arquivo Quarto
            callouts: Dicionário com callouts por variável
            dimensao: Nome da dimensão para determinar o caminho dos assets
        """
        try:
            # Verificar se o arquivo existe
            if not os.path.exists(arquivo_quarto):
                print(f"Arquivo {arquivo_quarto} não encontrado. Criando novo arquivo...")
                return
            
            with open(arquivo_quarto, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            # Remover callouts existentes primeiro para evitar duplicatas
            linhas = conteudo.split('\n')
            linhas_limpo = []
            i = 0
            while i < len(linhas):
                linha = linhas[i]
                # Pular linhas que são callouts existentes
                if '::: {.callout-tip title="Análise de Frequências Temporais"}' in linha:
                    # Pular até o final do callout
                    i += 1
                    while i < len(linhas) and not linhas[i].startswith(':::'):
                        i += 1
                    i += 1  # Pular a linha de fechamento do callout
                else:
                    linhas_limpo.append(linha)
                    i += 1
            
            conteudo = '\n'.join(linhas_limpo)
            
            # Para cada variável, encontrar o gráfico e adicionar callout
            for variavel, callout in callouts.items():
                numero_var = self.extrair_numero_variavel(variavel)
                # Converter número da variável (ex: "1.1") para formato do arquivo (ex: "1_1")
                numero_arquivo = numero_var.replace('.', '_')
                
                # Formatar callout
                callout_formatado = f"""::: {{.callout-tip title="Destaques"}}
{callout}
:::"""
                
                # Encontrar a linha exata do gráfico e substituir
                linhas = conteudo.split('\n')
                for i, linha in enumerate(linhas):
                    if f"grafico_agrupado_{numero_arquivo}_temporal.png" in linha:
                        # Verificar se já não existe um callout após esta linha
                        if i + 1 < len(linhas) and 'callout-tip' in linhas[i + 1]:
                            break  # Já existe um callout, pular
                        
                        # Inserir callout após a linha do gráfico
                        linhas.insert(i + 1, "")
                        linhas.insert(i + 2, callout_formatado)
                        break
                
                conteudo = '\n'.join(linhas)
            
            # Salvar arquivo atualizado
            with open(arquivo_quarto, 'w', encoding='utf-8') as f:
                f.write(conteudo)
            
            print(f"Arquivo {arquivo_quarto} atualizado com {len(callouts)} callouts")
            
        except Exception as e:
            print(f"Erro ao atualizar arquivo {arquivo_quarto}: {str(e)}")
    
    def processar_todas_dimensoes(self):
        """
        Processa todas as dimensões e atualiza os arquivos Quarto
        """
        print("Iniciando geração de callouts de frequências temporais...")
        print(f"Dimensões a processar: {self.dimensoes_processar}")
        
        for dimensao in self.dimensoes_processar:
            print(f"\nProcessando dimensão: {dimensao}")
            
            # Gerar callouts
            callouts = self.gerar_callouts_para_dimensao(dimensao)
            
            if callouts:
                # Determinar caminho do arquivo Quarto com nomes corretos
                mapeamento_arquivos = {
                    'Economica': 'economic.qmd',
                    'Ambiental': 'ambiental.qmd',
                    'Geopolitica': 'geopolitico.qmd',
                    'Tecnologica': 'tecnologico.qmd'
                }
                arquivo_quarto = f"quarto/{mapeamento_arquivos.get(dimensao, dimensao.lower())}"
                
                # Atualizar arquivo
                self.atualizar_arquivo_quarto(arquivo_quarto, callouts, dimensao)
                
                print(f"✅ {len(callouts)} callouts adicionados ao arquivo {arquivo_quarto}")
            else:
                print(f"⚠️ Nenhum callout gerado para dimensão {dimensao}")
        
        print("\n✅ Processamento concluído!")

def main():
    """
    Função principal para execução do script
    """
    print("GERADOR DE CALLOUTS DE FREQUÊNCIAS TEMPORAIS")
    print("=" * 50)
    
    try:
        # Criar gerador
        gerador = GeradorCalloutsFrequencias()
        
        # Processar todas as dimensões
        gerador.processar_todas_dimensoes()
        
        print("\n" + "=" * 50)
        print("CALLOUTS GERADOS COM SUCESSO!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\nERRO: {e}")
        print("Verifique o arquivo 'questionario.xlsx' e tente novamente.")

if __name__ == "__main__":
    main()

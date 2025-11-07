"""
Análise Completa de Riscos Portuários - Escala Likert

Script para análise estatística e visualização de dados Likert de risco portuário
organizados por dimensões: Econômica, Ambiental, Geopolítica, Social e Tecnológica.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import re
from typing import Dict, List, Tuple, Any
import logging
from pathlib import Path

# Configuração
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuração de estilo dos gráficos
plt.style.use('default')
sns.set_palette("husl")

# Cores por nível de risco
CORES_RISCO = {
    1: '#90EE90',  # Verde claro - Muito baixa
    2: '#228B22',  # Verde - Baixa
    3: '#FFD700',  # Amarelo - Moderada
    4: '#FF8C00',  # Laranja - Alta
    5: '#DC143C'   # Vermelho - Muito Alta
}

NIVEIS_RISCO = {
    1: 'Muito baixa',
    2: 'Baixa', 
    3: 'Moderada',
    4: 'Alta',
    5: 'Muito Alta'
}

class AnalisadorRiscosLikert:
    """
    Classe principal para análise de riscos em escala Likert
    """
    
    def __init__(self, excel_file: str = 'questionario.xlsx'):
        """
        Inicializa o analisador
        
        Args:
            excel_file: Caminho do arquivo Excel com os dados
        """
        self.excel_file = excel_file
        self.dados_brutos = None
        self.apendice_variaveis = {}  # Armazenará informações completas das variáveis
        self.dimensoes = {
            'Economica': {'prefixo': '1.', 'pasta': 'graficos_economicos'},
            'Ambiental': {'prefixo': '2.', 'pasta': 'graficos_ambientais'},
            'Geopolitica': {'prefixo': '3.', 'pasta': 'graficos_geopoliticos'},
            'Social': {'prefixo': '4.', 'pasta': 'graficos_sociais'},
            'Tecnologica': {'prefixo': '5.', 'pasta': 'graficos_tecnologicos'}
        }
        self.periodos_temporais = {
            'imediato_2025': ['Imediato (2025)', '2025'],
            'curto_prazo_2026_2027': [
                'Curto prazo (2026 a 2027)',
                'Curto prazo (2026 a',
                '2026-2027'
            ],
            'longo_prazo_2035': [
                'Longo prazo (até 2035)',
                'Longo prazo (até 203',
                'Longo prazo (ate 203',
                '2035'
            ]
        }
    
    def gerar_label_sucinto(self, coluna_original: str, incluir_numero: bool = False) -> str:
        """
        Gera rótulo sucinto para eixos e labels
        
        Args:
            coluna_original: Nome original da coluna
            incluir_numero: Se deve incluir o número (ex: 1.1)
            
        Returns:
            String com rótulo sucinto
        """
        # Extrair número e descrição
        match = re.match(r'^(\d+\.\d+)\s*(.+?)\s*\[.*?\]\s*$', coluna_original)
        if match:
            numero = match.group(1)
            descricao_completa = match.group(2).strip()
            
            # Criar versão sucinta
            palavras = descricao_completa.split()
            if len(palavras) <= 5:
                sucinto = descricao_completa
            else:
                # Manter palavras-chave importantes
                palavras_chave = []
                for palavra in palavras:
                    if len(palavras_chave) < 4:
                        palavras_chave.append(palavra)
                    elif palavra.lower() in ['crise', 'risco', 'impacto', 'consequência', 'contaminação', 'disrupção']:
                        palavras_chave.append(palavra)
                    elif len(palavra) > 8:  # Palavras longas podem ser importantes
                        palavras_chave.append(palavra)
                    else:
                        continue
                
                sucinto = ' '.join(palavras_chave[:5])
                if len(palavras) > len(palavras_chave):
                    sucinto += '...'
            
            if incluir_numero:
                return f"{numero} - {sucinto}"
            else:
                return sucinto
        
        return coluna_original
    
    def gerar_titulo_grafico(self, tipo: str, variavel_info: str, periodo: str = None) -> str:
        """
        Gera títulos padronizados para diferentes tipos de gráficos
        
        Args:
            tipo: Tipo de gráfico ('frequencia', 'evolucao_temporal', 'comparativo', 'boxplot')
            variavel_info: Informações da variável
            periodo: Período temporal (opcional)
            
        Returns:
            String com título formatado
        """
        label_sucinto = self.gerar_label_sucinto(variavel_info)
        
        if tipo == 'frequencia':
            return label_sucinto
        elif tipo == 'evolucao_temporal':
            return f"Evolução Temporal: {label_sucinto}"
        elif tipo == 'comparativo':
            dimensao = self._extrair_dimensao_da_variavel(variavel_info)
            periodo_nome = self.periodos_temporais.get(periodo, [periodo])[1] if periodo else ""
            return f"Comparativo de Riscos - {dimensao} ({periodo_nome})"
        elif tipo == 'boxplot':
            dimensao = self._extrair_dimensao_da_variavel(variavel_info)
            periodo_nome = self.periodos_temporais.get(periodo, [periodo])[1] if periodo else ""
            return f"Distribuição de Riscos - {dimensao} ({periodo_nome})"
        
        return label_sucinto
    
    def _extrair_dimensao_da_variavel(self, variavel: str) -> str:
        """
        Extrai o nome da dimensão baseado no prefixo da variável
        
        Args:
            variavel: Nome da variável
            
        Returns:
            String com nome da dimensão
        """
        if variavel.startswith('1.'):
            return 'Econômica'
        elif variavel.startswith('2.'):
            return 'Ambiental'
        elif variavel.startswith('3.'):
            return 'Geopolítica'
        elif variavel.startswith('4.'):
            return 'Social'
        elif variavel.startswith('5.'):
            return 'Tecnológica'
        else:
            return 'Geral'
    
    def get_cor_risco(self, nivel_risco: str) -> str:
        """
        Retorna a cor correspondente ao nível de risco
        
        Args:
            nivel_risco: String com nível de risco
            
        Returns:
            String com código hexadecimal da cor
        """
        cores = {
            'RISCO CRÍTICO': '#DC143C',      # Vermelho
            'RISCO ALTO': '#FF8C00',         # Laranja  
            'RISCO MODERADO-ALTO': '#FFD700', # Amarelo
            'RISCO MODERADO': '#90EE90',     # Verde claro
            'RISCO BAIXO': '#228B22'         # Verde
        }
        return cores.get(nivel_risco, '#808080')
    
    def adicionar_informacoes_estatisticas_canto_direito(self, ax, stats: Dict):
        """
        Adiciona caixa de informações estatísticas no canto superior direito
        
        Args:
            ax: Eixo do matplotlib
            stats: Dicionário com estatísticas
        """
        # Extrair informações
        mediana = stats['mediana']
        moda = stats['moda']
        nivel_risco = self.classificar_nivel_risco(stats['mediana'], stats['percentual_risco_alto'])
        cor_risco = self.get_cor_risco(nivel_risco)
        
        # Formatar texto
        info_text = (
            f"Mediana: {mediana:.1f}\n"
            f"Moda: {moda}\n"
            f"Nível: "
        )
        
        # Caixa de informações
        props = dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9, 
                     edgecolor='lightgray', linewidth=1)
        
        # Primeira parte (Mediana e Moda)
        ax.text(0.98, 0.98, info_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', horizontalalignment='right', 
                bbox=props, fontweight='normal')
        
        # Segunda parte (Nível com cor)
        ax.text(0.98, 0.88, nivel_risco, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', horizontalalignment='right',
                color=cor_risco, fontweight='bold')
        
        # Linha separadora sutil
        ax.plot([0.85, 0.98], [0.91, 0.91], transform=ax.transAxes, 
                color='lightgray', linewidth=0.5, linestyle='-')
        
    def carregar_dados(self) -> pd.DataFrame:
        """
        Carrega os dados do arquivo Excel
        
        Returns:
            DataFrame com os dados carregados
        """
        try:
            logger.info(f"Carregando dados de {self.excel_file}")
            self.dados_brutos = pd.read_excel(self.excel_file)
            logger.info(f"Dados carregados: {self.dados_brutos.shape[0]} linhas, {self.dados_brutos.shape[1]} colunas")
            return self.dados_brutos
        except Exception as e:
            logger.error(f"Erro ao carregar dados: {e}")
            raise
    
    def mapear_variaveis_por_dimensao(self) -> Dict[str, Dict]:
        """
        Mapeia as variáveis por dimensão e período temporal
        
        Returns:
            Dicionário com variáveis organizadas por dimensão e período
        """
        if self.dados_brutos is None:
            self.carregar_dados()
            
        mapeamento = {}
        
        for dimensao, config in self.dimensoes.items():
            mapeamento[dimensao] = {}
            
            # Encontrar colunas da dimensão
            colunas_dimensao = [col for col in self.dados_brutos.columns 
                              if str(col).startswith(config['prefixo'])]
            
            # Agrupar por período temporal
            for periodo_key, periodo_values in self.periodos_temporais.items():
                mapeamento[dimensao][periodo_key] = []
                
                for col in colunas_dimensao:
                    # Verificar se a coluna contém o período temporal
                    if any(periodo in str(col) for periodo in periodo_values):
                        mapeamento[dimensao][periodo_key].append(col)
        
        # Log dos resultados
        for dimensao, periodos in mapeamento.items():
            total_vars = sum(len(vars) for vars in periodos.values())
            logger.info(f"{dimensao}: {total_vars} variáveis totais")
            for periodo, vars in periodos.items():
                logger.info(f"  {periodo}: {len(vars)} variáveis")
        
        return mapeamento
    
    def criar_estrutura_pastas(self):
        """
        Cria a estrutura de pastas para salvar os gráficos
        """
        logger.info("Criando estrutura de pastas...")
        
        base_path = Path('outputs')
        
        for dimensao, config in self.dimensoes.items():
            dimensao_path = base_path / config['pasta']
            
            for periodo in self.periodos_temporais.keys():
                # Criar subpastas
                (dimensao_path / periodo / 'frequencias').mkdir(parents=True, exist_ok=True)
                (dimensao_path / periodo / 'comparativos').mkdir(parents=True, exist_ok=True)
                (dimensao_path / periodo / 'boxplots').mkdir(parents=True, exist_ok=True)
        
        logger.info("Estrutura de pastas criada com sucesso!")
    
    def analisar_frequencias_likert(self, dados_coluna: pd.Series) -> Dict:
        """
        Analisa frequências para dados Likert
        
        Args:
            dados_coluna: Série pandas com os dados Likert
            
        Returns:
            Dicionário com estatísticas de frequência
        """
        # Remover valores nulos
        dados_limpos = dados_coluna.dropna()
        
        # Converter para numérico se necessário
        dados_numericos = pd.to_numeric(dados_limpos, errors='coerce').dropna()
        
        if len(dados_numericos) == 0:
            return {}
        
        # Frequências absolutas e relativas
        freq_abs = dados_numericos.value_counts().sort_index()
        freq_rel = dados_numericos.value_counts(normalize=True).sort_index()
        
        # Medidas ordinais
        mediana = dados_numericos.median()
        moda = dados_numericos.mode().iloc[0] if not dados_numericos.mode().empty else None
        percentis = dados_numericos.quantile([0.25, 0.5, 0.75])
        
        # Amplitude interquartil
        iqr = percentis[0.75] - percentis[0.25]
        
        # Análise de consenso
        total_respostas = len(dados_numericos)
        respostas_4_5 = sum(dados_numericos.isin([4, 5]))
        respostas_1_2 = sum(dados_numericos.isin([1, 2]))
        
        consenso_alto = max(freq_rel.values) > 0.7
        categoria_dominante = freq_abs.index[0] if not freq_abs.empty else None
        
        return {
            'total_respostas': total_respostas,
            'frequencias_absolutas': freq_abs.to_dict(),
            'frequencias_relativas': freq_rel.to_dict(),
            'mediana': mediana,
            'moda': moda,
            'percentis': percentis.to_dict(),
            'iqr': iqr,
            'consenso_alto': consenso_alto,
            'categoria_dominante': categoria_dominante,
            'percentual_risco_alto': (respostas_4_5 / total_respostas) * 100,
            'percentual_risco_baixo': (respostas_1_2 / total_respostas) * 100
        }
    
    def classificar_nivel_risco(self, mediana: float, percentual_risco_alto: float) -> str:
        """
        Classifica o nível de risco baseado na mediana e percentual de respostas altas
        
        Args:
            mediana: Mediana das respostas
            percentual_risco_alto: Percentual de respostas 4-5
            
        Returns:
            String com classificação do risco
        """
        if mediana >= 4.0 and percentual_risco_alto > 50:
            return "RISCO CRÍTICO"
        elif mediana >= 3.5 and percentual_risco_alto > 40:
            return "RISCO ALTO"
        elif mediana >= 3.0 and percentual_risco_alto > 30:
            return "RISCO MODERADO-ALTO"
        elif mediana >= 2.0:
            return "RISCO MODERADO"
        else:
            return "RISCO BAIXO"
    
    def gerar_grafico_frequencia(self, dados_coluna: pd.Series, titulo: str, 
                               caminho_salvar: str, nome_variavel: str = "") -> bool:
        """
        Gera gráfico de barras de frequência para dados Likert
        
        Args:
            dados_coluna: Série pandas com os dados
            titulo: Título do gráfico
            caminho_salvar: Caminho para salvar o gráfico
            nome_variavel: Nome da variável para legenda
            
        Returns:
            True se sucesso, False se erro
        """
        try:
            # Análise de frequências
            stats = self.analisar_frequencias_likert(dados_coluna)
            
            if not stats:
                logger.warning(f"Sem dados válidos para: {titulo}")
                return False
            
            # Preparar dados para o gráfico
            categorias = list(range(1, 6))
            frequencias = [stats['frequencias_absolutas'].get(cat, 0) for cat in categorias]
            rotulos = [NIVEIS_RISCO[cat] for cat in categorias]
            cores = [CORES_RISCO[cat] for cat in categorias]
            
            # Criar gráfico
            plt.figure(figsize=(12, 8))
            bars = plt.bar(rotulos, frequencias, color=cores, alpha=0.8, edgecolor='black', linewidth=1)
            
            # Adicionar valores nas barras
            for bar, freq in zip(bars, frequencias):
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{freq}\n({stats["frequencias_relativas"].get(categorias[frequencias.index(freq)], 0)*100:.1f}%)',
                        ha='center', va='bottom', fontweight='bold')
            
            # Configurações do gráfico com título sucinto
            titulo_sucinto = self.gerar_titulo_grafico('frequencia', nome_variavel)
            plt.title(titulo_sucinto, fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('Nível de Risco', fontsize=12, fontweight='bold')
            plt.ylabel('Frequência', fontsize=12, fontweight='bold')
            plt.xticks(rotation=45, ha='right')
            plt.grid(axis='y', alpha=0.3)
            
            # Adicionar informações estatísticas no canto direito
            ax = plt.gca()
            self.adicionar_informacoes_estatisticas_canto_direito(ax, stats)
            
            plt.tight_layout()
            
            # Salvar gráfico
            plt.savefig(caminho_salvar, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Gráfico salvo: {caminho_salvar}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao gerar gráfico {titulo}: {e}")
            return False
    
    def gerar_grafico_comparativo_dimensao(self, dados_dimensao: Dict, titulo: str, 
                                         caminho_salvar: str, periodo: str) -> bool:
        """
        Gera gráfico comparativo com todas as variáveis de uma dimensão
        
        Args:
            dados_dimensao: Dicionário com variáveis da dimensão
            titulo: Título do gráfico
            caminho_salvar: Caminho para salvar
            periodo: Período temporal
            
        Returns:
            True se sucesso, False se erro
        """
        try:
            # Preparar dados
            variaveis_stats = {}
            
            for nome_variavel, dados_coluna in dados_dimensao.items():
                stats = self.analisar_frequencias_likert(dados_coluna)
                if stats:
                    variaveis_stats[nome_variavel] = stats
            
            if not variaveis_stats:
                logger.warning(f"Sem dados válidos para dimensão: {titulo}")
                return False
            
            # Extrair medianas para ordenação
            medianas = {var: stats['mediana'] for var, stats in variaveis_stats.items()}
            variaveis_ordenadas = sorted(medianas.items(), key=lambda x: x[1], reverse=True)
            
            # Preparar dados para o gráfico com labels sucintos
            nomes_variaveis = [self.gerar_label_sucinto(var[0]) for var in variaveis_ordenadas]
            valores_medianas = [var[1] for var in variaveis_ordenadas]
            percentuais_alto = [variaveis_stats[var[0]]['percentual_risco_alto'] 
                              for var in variaveis_ordenadas]
            
            # Criar gráfico
            plt.figure(figsize=(15, 10))
            
            # Barras das medianas
            bars = plt.barh(range(len(nomes_variaveis)), valores_medianas, 
                           alpha=0.7, color='skyblue', edgecolor='navy', linewidth=1)
            
            # Colorir barras baseado no nível de risco
            for i, (bar, mediana, pct_alto) in enumerate(zip(bars, valores_medianas, percentuais_alto)):
                nivel_risco = self.classificar_nivel_risco(mediana, pct_alto)
                if 'CRÍTICO' in nivel_risco:
                    bar.set_color('#DC143C')
                elif 'ALTO' in nivel_risco:
                    bar.set_color('#FF8C00')
                elif 'MODERADO' in nivel_risco:
                    bar.set_color('#FFD700')
                else:
                    bar.set_color('#228B22')
            
            # Adicionar valores nas barras
            for i, (bar, pct_alto) in enumerate(zip(bars, percentuais_alto)):
                width = bar.get_width()
                plt.text(width + 0.05, bar.get_y() + bar.get_height()/2,
                        f'{valores_medianas[i]:.1f} ({pct_alto:.1f}%)',
                        ha='left', va='center', fontweight='bold')
            
            # Configurações com título sucinto
            titulo_sucinto = self.gerar_titulo_grafico('comparativo', list(dados_dimensao.keys())[0], periodo)
            plt.title(titulo_sucinto, fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('Mediana (Escala Likert)', fontsize=12, fontweight='bold')
            plt.ylabel('Variáveis de Risco', fontsize=12, fontweight='bold')
            plt.yticks(range(len(nomes_variaveis)), nomes_variaveis)
            plt.xlim(0, 5.5)
            plt.grid(axis='x', alpha=0.3)
            
            # Legenda de cores
            legend_elements = [
                plt.Rectangle((0,0),1,1, facecolor='#DC143C', label='Risco Crítico'),
                plt.Rectangle((0,0),1,1, facecolor='#FF8C00', label='Risco Alto'),
                plt.Rectangle((0,0),1,1, facecolor='#FFD700', label='Risco Moderado'),
                plt.Rectangle((0,0),1,1, facecolor='#228B22', label='Risco Baixo')
            ]
            plt.legend(handles=legend_elements, loc='lower right')
            
            plt.tight_layout()
            plt.savefig(caminho_salvar, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Gráfico comparativo salvo: {caminho_salvar}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao gerar gráfico comparativo {titulo}: {e}")
            return False
    
    def gerar_boxplot_dimensao(self, dados_dimensao: Dict, titulo: str, 
                              caminho_salvar: str) -> bool:
        """
        Gera boxplot para dimensão (mediana e quartis apenas)
        
        Args:
            dados_dimensao: Dicionário com variáveis da dimensão
            titulo: Título do gráfico
            caminho_salvar: Caminho para salvar
            
        Returns:
            True se sucesso, False se erro
        """
        try:
            # Preparar dados
            dados_boxplot = []
            nomes_variaveis = []
            
            for nome_variavel, dados_coluna in dados_dimensao.items():
                dados_numericos = pd.to_numeric(dados_coluna.dropna(), errors='coerce').dropna()
                if len(dados_numericos) > 0:
                    dados_boxplot.append(dados_numericos)
                    # Nome sucinto para o gráfico
                    nome_sucinto = self.gerar_label_sucinto(nome_variavel)
                    nomes_variaveis.append(nome_sucinto)
            
            if not dados_boxplot:
                logger.warning(f"Sem dados válidos para boxplot: {titulo}")
                return False
            
            # Criar boxplot
            plt.figure(figsize=(15, 10))
            box_plot = plt.boxplot(dados_boxplot, labels=nomes_variaveis, 
                                 patch_artist=True, vert=False)
            
            # Colorir boxplots
            colors = plt.cm.Set3(np.linspace(0, 1, len(dados_boxplot)))
            for patch, color in zip(box_plot['boxes'], colors):
                patch.set_facecolor(color)
                patch.set_alpha(0.7)
            
            # Configurações com título sucinto
            titulo_sucinto = self.gerar_titulo_grafico('boxplot', list(dados_dimensao.keys())[0])
            plt.title(titulo_sucinto, fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('Nível de Risco (Escala Likert)', fontsize=12, fontweight='bold')
            plt.ylabel('Variáveis de Risco', fontsize=12, fontweight='bold')
            plt.xlim(0.5, 5.5)
            plt.grid(axis='x', alpha=0.3)
            
            # Adicionar linhas de referência
            plt.axvline(x=3, color='orange', linestyle='--', alpha=0.5, label='Moderado')
            plt.axvline(x=4, color='red', linestyle='--', alpha=0.5, label='Alto')
            plt.legend()
            
            plt.tight_layout()
            plt.savefig(caminho_salvar, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Boxplot salvo: {caminho_salvar}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao gerar boxplot {titulo}: {e}")
            return False
    
    def gerar_grafico_evolucao_temporal(self, dados_periodos: Dict, nome_variavel: str, 
                                      caminho_salvar: str) -> bool:
        """
        Gera gráfico de evolução temporal para uma variável
        
        Args:
            dados_periodos: Dicionário com dados por período
            nome_variavel: Nome base da variável
            caminho_salvar: Caminho para salvar
            
        Returns:
            True se sucesso, False se erro
        """
        try:
            # Preparar dados
            periodos_ordenados = ['imediato_2025', 'curto_prazo_2026_2027', 'longo_prazo_2035']
            medianas = []
            percentuais_alto = []
            
            for periodo in periodos_ordenados:
                if periodo in dados_periodos:
                    stats = self.analisar_frequencias_likert(dados_periodos[periodo])
                    if stats:
                        medianas.append(stats['mediana'])
                        percentuais_alto.append(stats['percentual_risco_alto'])
                    else:
                        medianas.append(0)
                        percentuais_alto.append(0)
                else:
                    medianas.append(0)
                    percentuais_alto.append(0)
            
            # Criar gráfico
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            
            # Título sucinto
            titulo_sucinto = self.gerar_titulo_grafico('evolucao_temporal', nome_variavel)
            
            # Gráfico de medianas
            ax1.plot(periodos_ordenados, medianas, marker='o', linewidth=3, markersize=8, color='blue')
            ax1.set_title(titulo_sucinto, fontsize=14, fontweight='bold')
            ax1.set_ylabel('Mediana', fontsize=12)
            ax1.set_ylim(0.5, 5.5)
            ax1.grid(True, alpha=0.3)
            
            # Adicionar valores nos pontos
            for i, (x, y) in enumerate(zip(periodos_ordenados, medianas)):
                ax1.annotate(f'{y:.1f}', (x, y), textcoords="offset points", xytext=(0,10), ha='center')
            
            # Gráfico de percentuais de risco alto
            ax2.plot(periodos_ordenados, percentuais_alto, marker='s', linewidth=3, markersize=8, color='red')
            ax2.set_title(f'Evolução do Percentual de Risco Alto - {self.gerar_label_sucinto(nome_variavel)}', fontsize=14, fontweight='bold')
            ax2.set_ylabel('Percentual (%)', fontsize=12)
            ax2.set_xlabel('Período Temporal', fontsize=12)
            ax2.set_ylim(0, 100)
            ax2.grid(True, alpha=0.3)
            
            # Adicionar valores nos pontos
            for i, (x, y) in enumerate(zip(periodos_ordenados, percentuais_alto)):
                ax2.annotate(f'{y:.1f}%', (x, y), textcoords="offset points", xytext=(0,10), ha='center')
            
            plt.tight_layout()
            plt.savefig(caminho_salvar, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Gráfico de evolução salvo: {caminho_salvar}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao gerar gráfico de evolução {nome_variavel}: {e}")
            return False
    
    def gerar_apendice_variaveis(self, mapeamento: Dict):
        """
        Gera apêndice completo com identificação de todas as variáveis
        
        Args:
            mapeamento: Dicionário com mapeamento das variáveis
        """
        logger.info("Gerando apêndice completo das variáveis...")
        
        # Criar pasta para apêndice
        os.makedirs('outputs/apendice_variaveis', exist_ok=True)
        
        # Gerar apêndice em formato TXT
        self._gerar_apendice_txt(mapeamento)
        
        # Gerar apêndice em formato HTML
        self._gerar_apendice_html(mapeamento)
        
        logger.info("Apêndice gerado com sucesso!")
    
    def _gerar_apendice_txt(self, mapeamento: Dict):
        """
        Gera apêndice em formato TXT
        
        Args:
            mapeamento: Dicionário com mapeamento das variáveis
        """
        caminho_apendice = 'outputs/apendice_variaveis/apendice_completo.txt'
        
        with open(caminho_apendice, 'w', encoding='utf-8') as f:
            f.write("APÊNDICE - IDENTIFICAÇÃO COMPLETA DAS VARIÁVEIS DE RISCO\n")
            f.write("=" * 70 + "\n\n")
            f.write("Este apêndice contém a descrição completa de todas as variáveis\n")
            f.write("analisadas nos gráficos. Nos gráficos, são usados títulos sucintos\n")
            f.write("para melhor visualização. Consulte este apêndice para descrições\n")
            f.write("completas.\n\n")
            f.write("=" * 70 + "\n\n")
            
            for dimensao, periodos in mapeamento.items():
                f.write(f"DIMENSÃO: {dimensao.upper()}\n")
                f.write("-" * 50 + "\n\n")
                
                # Coletar todas as variáveis únicas da dimensão
                variaveis_unicas = set()
                for periodo, variaveis in periodos.items():
                    variaveis_unicas.update(variaveis)
                
                # Ordenar por número
                variaveis_ordenadas = sorted(variaveis_unicas, key=lambda x: float(x.split('.')[0] + '.' + x.split('.')[1].split()[0]))
                
                for variavel in variaveis_ordenadas:
                    # Extrair informações
                    match = re.match(r'^(\d+\.\d+)\s*(.+?)\s*\[.*?\]$', variavel)
                    if match:
                        numero = match.group(1)
                        descricao_completa = match.group(2).strip()
                        titulo_sucinto = self.gerar_label_sucinto(variavel)
                        
                        f.write(f"{numero} - {titulo_sucinto}\n")
                        f.write(f"    Descrição completa: {descricao_completa}\n")
                        f.write(f"    Código original: {variavel}\n\n")
                
                f.write("\n" + "=" * 70 + "\n\n")
        
        logger.info(f"Apêndice TXT gerado: {caminho_apendice}")
    
    def _gerar_apendice_html(self, mapeamento: Dict):
        """
        Gera apêndice em formato HTML
        
        Args:
            mapeamento: Dicionário com mapeamento das variáveis
        """
        caminho_apendice = 'outputs/apendice_variaveis/apendice_completo.html'
        
        html_content = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Apêndice - Variáveis de Risco Portuário</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
        .header { text-align: center; color: #333; border-bottom: 2px solid #333; padding-bottom: 10px; }
        .dimensao { margin: 30px 0; }
        .dimensao-titulo { color: #0066cc; font-size: 18px; font-weight: bold; border-bottom: 1px solid #ccc; padding-bottom: 5px; }
        .variavel { margin: 15px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; background-color: #f9f9f9; }
        .variavel-sucinto { font-weight: bold; color: #0066cc; font-size: 16px; }
        .variavel-completo { color: #666; font-style: italic; margin-top: 5px; }
        .variavel-codigo { color: #999; font-size: 12px; margin-top: 5px; }
        .intro { background-color: #e8f4f8; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>APÊNDICE - IDENTIFICAÇÃO COMPLETA DAS VARIÁVEIS</h1>
        <p>Análise de Riscos Portuários - Escala Likert</p>
    </div>
    
    <div class="intro">
        <p><strong>Nota:</strong> Este apêndice contém a descrição completa de todas as variáveis analisadas nos gráficos. 
        Nos gráficos, são usados títulos sucintos para melhor visualização. Consulte este apêndice para descrições completas.</p>
    </div>
"""
        
        for dimensao, periodos in mapeamento.items():
            html_content += f'\n    <div class="dimensao">\n        <div class="dimensao-titulo">DIMENSÃO: {dimensao.upper()}</div>\n'
            
            # Coletar todas as variáveis únicas da dimensão
            variaveis_unicas = set()
            for periodo, variaveis in periodos.items():
                variaveis_unicas.update(variaveis)
            
            # Ordenar por número
            variaveis_ordenadas = sorted(variaveis_unicas, key=lambda x: float(x.split('.')[0] + '.' + x.split('.')[1].split()[0]))
            
            for variavel in variaveis_ordenadas:
                # Extrair informações
                match = re.match(r'^(\d+\.\d+)\s*(.+?)\s*\[.*?\]$', variavel)
                if match:
                    numero = match.group(1)
                    descricao_completa = match.group(2).strip()
                    titulo_sucinto = self.gerar_label_sucinto(variavel)
                    
                    html_content += f'''
        <div class="variavel">
            <div class="variavel-sucinto">{numero} - {titulo_sucinto}</div>
            <div class="variavel-completo">{descricao_completa}</div>
            <div class="variavel-codigo">Código original: {variavel}</div>
        </div>'''
            
            html_content += '\n    </div>\n'
        
        html_content += '''
</body>
</html>'''
        
        with open(caminho_apendice, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Apêndice HTML gerado: {caminho_apendice}")
    
    def gerar_relatorio_dimensao(self, dimensao: str, dados_periodos: Dict) -> str:
        """
        Gera relatório analítico para uma dimensão
        
        Args:
            dimensao: Nome da dimensão
            dados_periodos: Dicionário com dados por período
            
        Returns:
            Caminho do relatório gerado
        """
        try:
            relatorio_path = f'outputs/{self.dimensoes[dimensao]["pasta"]}/relatorio_{dimensao.lower()}.txt'
            
            with open(relatorio_path, 'w', encoding='utf-8') as f:
                f.write(f"RELATÓRIO DE ANÁLISE - DIMENSÃO {dimensao.upper()}\n")
                f.write("=" * 60 + "\n\n")
                
                # Análise por período
                for periodo, dados in dados_periodos.items():
                    f.write(f"PERÍODO: {self.periodos_temporais[periodo][1]}\n")
                    f.write("-" * 40 + "\n")
                    
                    # Estatísticas gerais
                    todas_medianas = []
                    todos_percentuais_alto = []
                    riscos_criticos = []
                    
                    for nome_variavel, dados_coluna in dados.items():
                        stats = self.analisar_frequencias_likert(dados_coluna)
                        if stats:
                            todas_medianas.append(stats['mediana'])
                            todos_percentuais_alto.append(stats['percentual_risco_alto'])
                            
                            nivel_risco = self.classificar_nivel_risco(stats['mediana'], stats['percentual_risco_alto'])
                            if 'CRÍTICO' in nivel_risco:
                                riscos_criticos.append({
                                    'variavel': nome_variavel,
                                    'mediana': stats['mediana'],
                                    'percentual_alto': stats['percentual_risco_alto']
                                })
                    
                    if todas_medianas:
                        f.write(f"Total de variáveis analisadas: {len(todas_medianas)}\n")
                        f.write(f"Mediana geral da dimensão: {np.median(todas_medianas):.2f}\n")
                        f.write(f"Percentual médio de risco alto: {np.mean(todos_percentuais_alto):.1f}%\n")
                        f.write(f"Número de riscos críticos: {len(riscos_criticos)}\n\n")
                        
                        # Top 10 riscos críticos
                        if riscos_criticos:
                            f.write("RISCOS CRÍTICOS IDENTIFICADOS:\n")
                            riscos_criticos.sort(key=lambda x: x['percentual_alto'], reverse=True)
                            for i, risco in enumerate(riscos_criticos[:10], 1):
                                f.write(f"{i:2d}. {self.gerar_label_sucinto(risco['variavel'])}\n")
                                f.write(f"    Mediana: {risco['mediana']:.1f} | ")
                                f.write(f"Risco Alto: {risco['percentual_alto']:.1f}%\n")
                            f.write("\n")
                
                # Recomendações
                f.write("RECOMENDAÇÕES:\n")
                f.write("-" * 20 + "\n")
                f.write("1. Monitorar continuamente os riscos críticos identificados\n")
                f.write("2. Desenvolver planos de mitigação para riscos com mediana ≥ 4.0\n")
                f.write("3. Implementar sistemas de alerta precoce para tendências de aumento\n")
                f.write("4. Realizar análises comparativas entre períodos para identificar tendências\n")
                f.write("5. Priorizar recursos para as variáveis com maior percentual de risco alto\n")
                f.write("\nNOTA: Consulte o apêndice completo em outputs/apendice_variaveis/ para descrições detalhadas das variáveis.\n")
            
            logger.info(f"Relatório gerado: {relatorio_path}")
            return relatorio_path
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório para {dimensao}: {e}")
            return ""
    
    def executar_analise_completa(self):
        """
        Executa a análise completa para todas as dimensões
        """
        logger.info("Iniciando análise completa de riscos...")
        
        # Carregar dados
        self.carregar_dados()
        
        # Mapear variáveis
        mapeamento = self.mapear_variaveis_por_dimensao()
        
        # Criar estrutura de pastas
        self.criar_estrutura_pastas()
        
        # Gerar apêndice completo
        self.gerar_apendice_variaveis(mapeamento)
        
        # Analisar cada dimensão
        for dimensao, periodos in mapeamento.items():
            logger.info(f"\nAnalisando dimensão: {dimensao}")
            
            dados_periodos = {}
            resumo_dimensao = {}
            
            for periodo, variaveis in periodos.items():
                logger.info(f"  Período: {periodo} ({len(variaveis)} variáveis)")
                
                # Extrair dados para este período
                dados_periodo = {}
                for variavel in variaveis:
                    dados_periodo[variavel] = self.dados_brutos[variavel]
                
                dados_periodos[periodo] = dados_periodo
                
                # Gerar gráficos individuais de frequência
                for variavel, dados_coluna in dados_periodo.items():
                    # Nome limpo para o gráfico
                    nome_limpo = re.sub(r'[^\w\s]', '_', variavel)
                    nome_limpo = re.sub(r'_+', '_', nome_limpo).strip('_')
                    
                    caminho_grafico = (f'outputs/{self.dimensoes[dimensao]["pasta"]}/'
                                     f'{periodo}/frequencias/{nome_limpo}.png')
                    
                    self.gerar_grafico_frequencia(dados_coluna, "", caminho_grafico, variavel)
                
                # Gerar gráfico comparativo da dimensão
                caminho_comparativo = (f'outputs/{self.dimensoes[dimensao]["pasta"]}/'
                                     f'{periodo}/comparativos/{dimensao.lower()}_comparativo_{periodo}.png')
                
                self.gerar_grafico_comparativo_dimensao(dados_periodo, "", caminho_comparativo, periodo)
                
                # Gerar boxplot da dimensão
                caminho_boxplot = (f'outputs/{self.dimensoes[dimensao]["pasta"]}/'
                                 f'{periodo}/boxplots/{dimensao.lower()}_boxplot_{periodo}.png')
                
                self.gerar_boxplot_dimensao(dados_periodo, "", caminho_boxplot)
            
            # Gerar gráficos de evolução temporal
            logger.info(f"  Gerando gráficos de evolução temporal...")
            
            # Encontrar variáveis comuns aos três períodos
            variaveis_comuns = set()
            for periodo, variaveis in periodos.items():
                if not variaveis_comuns:
                    variaveis_comuns = set(variaveis)
                else:
                    variaveis_comuns &= set(variaveis)
            
            # Para cada variável comum, gerar evolução temporal
            for variavel in list(variaveis_comuns)[:10]:  # Limitar a 10 para não gerar muitos gráficos
                dados_evolucao = {}
                nome_base = re.sub(r'\s+\[.*?\]', '', variavel).strip()
                
                for periodo in periodos.keys():
                    if variavel in dados_periodos[periodo]:
                        dados_evolucao[periodo] = dados_periodos[periodo][variavel]
                
                if len(dados_evolucao) == 3:  # Tem dados nos 3 períodos
                    caminho_evolucao = (f'outputs/{self.dimensoes[dimensao]["pasta"]}/'
                                       f'evolucao_temporal/{nome_base[:50]}_evolucao.png')
                    
                    # Criar pasta se não existir
                    os.makedirs(os.path.dirname(caminho_evolucao), exist_ok=True)
                    
                    self.gerar_grafico_evolucao_temporal(dados_evolucao, variavel, caminho_evolucao)
            
            # Gerar relatório da dimensão
            self.gerar_relatorio_dimensao(dimensao, dados_periodos)
        
        logger.info("\nAnálise completa concluída com sucesso!")
        logger.info(f"Gráficos salvos em: outputs/")
        logger.info(f"Apêndice completo em: outputs/apendice_variaveis/")
        
        # Gerar relatório consolidado
        self.gerar_relatorio_consolidado(mapeamento)
    
    def gerar_grafico_barras_agrupado_temporal(self, dados_periodos: Dict, nome_variavel: str, 
                                             caminho_salvar: str) -> bool:
        """
        Gera gráfico de barras agrupado por período temporal para uma variável
        
        Args:
            dados_periodos: Dicionário com dados por período temporal
            nome_variavel: Nome base da variável
            caminho_salvar: Caminho para salvar o gráfico
            
        Returns:
            True se sucesso, False se erro
        """
        try:
            # Preparar dados para os três períodos
            periodos_ordenados = ['imediato_2025', 'curto_prazo_2026_2027', 'longo_prazo_2035']
            periodos_labels = ['Imediato 2025', 'Curto Prazo 2026-2027', 'Longo Prazo até 2035']
            cores_periodos = ['#2E86AB', '#A23B72', '#F18F01']  # Azul, Roxo, Laranja
            
            # Coletar dados de frequência para cada período
            dados_grafico = {}
            
            for i, periodo in enumerate(periodos_ordenados):
                if periodo in dados_periodos:
                    stats = self.analisar_frequencias_likert(dados_periodos[periodo])
                    if stats:
                        # Converter para percentuais
                        total = stats['total_respostas']
                        percentuais = {}
                        for nivel in range(1, 6):
                            freq_abs = stats['frequencias_absolutas'].get(nivel, 0)
                            percentuais[nivel] = (freq_abs / total) * 100 if total > 0 else 0
                        
                        dados_grafico[periodo] = {
                            'percentuais': percentuais,
                            'label': periodos_labels[i],
                            'cor': cores_periodos[i]
                        }
            
            if not dados_grafico:
                logger.warning(f"Sem dados válidos para gráfico agrupado: {nome_variavel}")
                return False
            
            # Criar gráfico
            plt.figure(figsize=(14, 8))
            
            # Configurar barras agrupadas
            largura_barra = 0.25
            posicoes = np.arange(1, 6)  # Posições para níveis 1-5
            
            # Plotar barras para cada período
            for i, (periodo, dados) in enumerate(dados_grafico.items()):
                offset = (i - 1) * largura_barra  # Centralizar grupos
                valores = [dados['percentuais'].get(nivel, 0) for nivel in range(1, 6)]
                
                bars = plt.bar(posicoes + offset, valores, largura_barra, 
                             label=dados['label'], color=dados['cor'], 
                             alpha=0.8, edgecolor='black', linewidth=1)
                
                # Adicionar valores percentuais nas barras
                for bar, valor in zip(bars, valores):
                    if valor > 0:  # Só mostrar se houver valor
                        height = bar.get_height()
                        plt.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                                f'{valor:.1f}%', ha='center', va='bottom', 
                                fontweight='bold', fontsize=9)
            
            
           # Configurações do gráfico
            # Extrai o título limpando o prefixo numérico e as informações de período
            titulo_grafico = nome_variavel
            # Remove o período do final, ex: [Imediato (2025)]
            titulo_grafico = re.sub(r'\s*\[.*?\]\s*$', '', titulo_grafico)
            # Remove o prefixo numérico do início, ex: "5.15 "
            titulo_grafico = re.sub(r'^\d+\.\d+\s*', '', titulo_grafico)
            
            plt.title(titulo_grafico.strip(), fontsize=16, fontweight='bold', pad=20)
            # Configurar eixos X
            plt.xticks(posicoes, [NIVEIS_RISCO[nivel] for nivel in range(1, 6)], 
                      rotation=45, ha='right')
            plt.xlim(0.5, 5.5)
            plt.ylim(0, max([max(dados['percentuais'].values()) for dados in dados_grafico.values()]) + 10)
            
            # Grid e legendas
            plt.grid(axis='y', alpha=0.3)
            plt.legend(loc='upper right', framealpha=0.9)
            
            # Adicionar informações estatísticas
            info_text = "Análise Temporal: Comparação da percepção de risco\n"
            info_text += "entre os três horizontes temporais"
            plt.figtext(0.02, 0.02, info_text, fontsize=9, 
                       style='italic', color='gray')
            
            plt.tight_layout()
            
            # Salvar gráfico
            plt.savefig(caminho_salvar, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Gráfico agrupado temporal salvo: {caminho_salvar}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao gerar gráfico agrupado temporal {nome_variavel}: {e}")
            return False

    def gerar_relatorio_consolidado(self, mapeamento: Dict):
        """
        Gera relatório consolidado com todas as dimensões
        
        Args:
            mapeamento: Dicionário com mapeamento completo das variáveis
        """
        try:
            relatorio_path = 'outputs/relatorio_consolidado.txt'
            
            with open(relatorio_path, 'w', encoding='utf-8') as f:
                f.write("RELATÓRIO CONSOLIDADO DE ANÁLISE DE RISCOS PORTUÁRIOS\n")
                f.write("=" * 70 + "\n\n")
                
                # Sumário geral
                f.write("SUMÁRIO EXECUTIVO\n")
                f.write("-" * 20 + "\n")
                f.write(f"Data da análise: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Total de respondentes: {len(self.dados_brutos)}\n")
                f.write(f"Dimensões analisadas: {len(mapeamento)}\n\n")
                
                # Comparação entre dimensões
                f.write("COMPARAÇÃO ENTRE DIMENSÕES\n")
                f.write("-" * 30 + "\n")
                
                for dimensao, periodos in mapeamento.items():
                    f.write(f"\n{dimensao}:\n")
                    
                    todas_medianas = []
                    todos_percentuais_alto = []
                    total_riscos_criticos = 0
                    
                    for periodo, variaveis in periodos.items():
                        for variavel in variaveis:
                            stats = self.analisar_frequencias_likert(self.dados_brutos[variavel])
                            if stats:
                                todas_medianas.append(stats['mediana'])
                                todos_percentuais_alto.append(stats['percentual_risco_alto'])
                                
                                nivel_risco = self.classificar_nivel_risco(stats['mediana'], stats['percentual_risco_alto'])
                                if 'CRÍTICO' in nivel_risco:
                                    total_riscos_criticos += 1
                    
                    if todas_medianas:
                        f.write(f"  Mediana geral: {np.median(todas_medianas):.2f}\n")
                        f.write(f"  Percentual médio risco alto: {np.mean(todos_percentuais_alto):.1f}%\n")
                        f.write(f"  Total de riscos críticos: {total_riscos_criticos}\n")
                
                # Recomendações gerais
                f.write("\n\nRECOMENDAÇÕES ESTRATÉGICAS\n")
                f.write("-" * 30 + "\n")
                f.write("1. Priorizar ações para dimensões com maior número de riscos críticos\n")
                f.write("2. Desenvolver planos de contingência para riscos de alta prioridade\n")
                f.write("3. Implementar monitoramento contínuo das tendências temporais\n")
                f.write("4. Fortalecer capacidade de resposta para riscos identificados como críticos\n")
                f.write("5. Realizar avaliações periódicas para atualização da análise de riscos\n")
                f.write("\nREFERÊNCIA COMPLETA DAS VARIÁVEIS\n")
                f.write("-" * 35 + "\n")
                f.write("Para descrições completas de todas as variáveis analisadas,\n")
                f.write("consulte o apêndice disponível em:\n")
                f.write("outputs/apendice_variaveis/apendice_completo.txt\n")
                f.write("outputs/apendice_variaveis/apendice_completo.html\n")
                
                f.write("\n\nPRÓXIMOS PASSOS\n")
                f.write("-" * 15 + "\n")
                f.write("1. Detalhar planos de mitigação para cada risco crítico\n")
                f.write("2. Alocar recursos baseados na priorização estabelecida\n")
                f.write("3. Estabelecer indicadores de monitoramento\n")
                f.write("4. Compartilhar resultados com stakeholders relevantes\n")
                f.write("5. Integrar análise ao planejamento estratégico portuário\n")
            
            logger.info(f"Relatório consolidado gerado: {relatorio_path}")
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório consolidado: {e}")

def criar_grafico_agrupado_temporal(df, variavel, output_dir='outputs', nome_arquivo=None):
    """
    Função simplificada para criar gráfico agrupado temporal (compatibilidade com script externo)
    
    Args:
        df: DataFrame com os dados
        variavel: Código da variável (ex: '4.1')
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
        
        # Procurar a variável em todos os períodos da dimensão social
        if 'Social' in mapeamento:
            for periodo, variaveis in mapeamento['Social'].items():
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

def carregar_dados(excel_file='questionario.xlsx'):
    """
    Função simplificada para carregar dados (compatibilidade com script externo)
    
    Args:
        excel_file: Caminho do arquivo Excel
        
    Returns:
        DataFrame com os dados ou None se erro
    """
    try:
        return pd.read_excel(excel_file)
    except Exception as e:
        logger.error(f"Erro ao carregar dados: {e}")
        return None

# Função principal
def main():
    """
    Função principal para execução da análise
    """
    print("INICIANDO ANÁLISE DE RISCOS PORTUÁRIOS - ESCALA LIKERT")
    print("=" * 60)
    
    try:
        # Criar analisador
        analisador = AnalisadorRiscosLikert()
        
        # Executar análise completa
        analisador.executar_analise_completa()
        
        print("\n" + "=" * 60)
        print("ANÁLISE CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print("Gráficos e relatórios gerados na pasta 'outputs/'")
        print("Apêndice completo em 'outputs/apendice_variaveis/'")
        print("\nEstrutura gerada:")
        print("├── outputs/")
        print("│   ├── graficos_economicos/")
        print("│   ├── graficos_ambientais/")
        print("│   ├── graficos_geopoliticos/")
        print("│   ├── graficos_sociais/")
        print("│   ├── graficos_tecnologicos/")
        print("│   ├── apendice_variaveis/")
        print("│   │   ├── apendice_completo.txt")
        print("│   │   └── apendice_completo.html")
        print("│   └── relatorio_consolidado.txt")
        
    except Exception as e:
        logger.error(f"Erro na execução da análise: {e}")
        print(f"\nERRO: {e}")
        print("Verifique o arquivo 'questionario.xlsx' e tente novamente.")

if __name__ == "__main__":
    main()

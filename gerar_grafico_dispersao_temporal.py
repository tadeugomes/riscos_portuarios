#!/usr/bin/env python3
"""
Gera grafico de dispersao com a relacao entre riscos de curto prazo (eixo x) 
e longo prazo (eixo y) utilizando filtros estatisticos robustos.
"""

from __future__ import annotations

import sys
import unicodedata
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from analise_likert_riscos import AnalisadorRiscosLikert

# Configuracao de cores por dimensao
CORES_DIMENSAO = {
    "Economica": "#2E86AB",      # Azul
    "Ambiental": "#228B22",      # Verde
    "Geopolitica": "#A23B72",   # Roxo
    "Social": "#F18F01",         # Laranja
    "Tecnologica": "#DC143C",    # Vermelho
}

# Configuracao de nomes amigaveis
NOMES_DIMENSAO = {
    "Economica": "Econômica",
    "Ambiental": "Ambiental", 
    "Geopolitica": "Geopolítica",
    "Social": "Social",
    "Tecnologica": "Tecnológica",
}

def ascii_safe(texto: str) -> str:
    """Remove acentuacao para evitar erros em consoles Windows."""
    return "".join(
        caractere
        for caractere in unicodedata.normalize("NFKD", texto)
        if not unicodedata.combining(caractere)
    )

def extrair_numero_variavel(nome_variavel: str) -> str:
    """Extrai o numero da variavel (ex: '1.1' de '1.1 Risco X')"""
    partes = nome_variavel.split('.')
    if len(partes) >= 2:
        return f"{partes[0]}.{partes[1].split()[0]}"
    return nome_variavel

def gerar_label_sucinto_dispersao(nome_variavel: str) -> str:
    """Gera rotulo sucinto para o grafico de dispersao."""
    # Extrair número e descrição
    import re
    match = re.match(r'^(\d+\.\d+)\s*(.+?)\s*\[.*?\]$', nome_variavel)
    if match:
        numero = match.group(1)
        descricao_completa = match.group(2).strip()
        
        # Criar versão sucinta (máximo 50 caracteres para dispersão)
        palavras = descricao_completa.split()
        if len(descricao_completa) <= 50:
            sucinto = descricao_completa
        else:
            # Manter palavras-chave importantes
            palavras_chave = []
            for palavra in palavras:
                if len(' '.join(palavras_chave + [palavra])) <= 45:
                    palavras_chave.append(palavra)
                elif palavra.lower() in ['crise', 'risco', 'impacto', 'disrupção', 'contaminação']:
                    palavras_chave.append(palavra)
                elif len(palavra) > 8:  # Palavras longas podem ser importantes
                    palavras_chave.append(palavra)
            
            sucinto = ' '.join(palavras_chave)
            if len(palavras) > len(palavras_chave):
                sucinto += '...'
        
        return f"{numero} - {sucinto}"
    
    return nome_variavel

def aplicar_filtros_estatisticos(dados_pares: List[Dict]) -> List[Dict]:
    """
    Prepara dados para análise sem filtros restritivos para maximizar visualização.
    
    Args:
        dados_pares: Lista com pares de dados (curto e longo prazo)
        
    Returns:
        Lista com todas as variáveis para análise completa
    """
    print(f"\nPreparando dados para análise completa...")
    print(f"Total de pares encontrados: {len(dados_pares)}")
    
    dados_preparados = []
    
    for par in dados_pares:
        stats_curto = par['stats_curto']
        stats_longo = par['stats_longo']
        
        # Calcular métricas para análise
        mediana_combinada = (stats_curto['mediana'] + stats_longo['mediana']) / 2
        delta_temporal = abs(stats_longo['mediana'] - stats_curto['mediana'])
        variabilidade_media = (stats_curto['iqr'] + stats_longo['iqr']) / 2
        
        # Adicionar informações adicionais para análise
        par['mediana_combinada'] = mediana_combinada
        par['delta_temporal'] = delta_temporal
        par['variabilidade_media'] = variabilidade_media
        
        dados_preparados.append(par)
    
    print(f"Todos os {len(dados_preparados)} pares incluídos na análise")
    
    return dados_preparados

def gerar_grafico_dispersao_temporal() -> Path:
    """
    Gera grafico de dispersao comparando curto prazo vs longo prazo.
    
    Returns:
        Path do arquivo gerado
    """
    print("Gerando gráfico de dispersão temporal...")
    
    # Inicializar analisador
    analisador = AnalisadorRiscosLikert()
    analisador.carregar_dados()
    mapeamento = analisador.mapear_variaveis_por_dimensao()
    
    # Coletar pares de variáveis (curto e longo prazo)
    pares_variaveis = []
    
    for dimensao, periodos in mapeamento.items():
        print(f"\nProcessando dimensão: {ascii_safe(dimensao)}")
        
        variaveis_curto = periodos.get("curto_prazo_2026_2027", [])
        variaveis_longo = periodos.get("longo_prazo_2035", [])
        
        # Encontrar correspondências
        for var_curto in variaveis_curto:
            # Extrair base da variável (sem o período)
            base_variavel = var_curto.split(' [')[0]
            
            # Procurar correspondente no longo prazo
            var_longo = None
            for vl in variaveis_longo:
                if vl.startswith(base_variavel):
                    var_longo = vl
                    break
            
            if var_longo and var_curto in analisador.dados_brutos and var_longo in analisador.dados_brutos:
                # Calcular estatísticas
                stats_curto = analisador.analisar_frequencias_likert(analisador.dados_brutos[var_curto])
                stats_longo = analisador.analisar_frequencias_likert(analisador.dados_brutos[var_longo])
                
                if stats_curto and stats_longo:
                    # Gerar label sucinto
                    label_completo = analisador.gerar_label_sucinto(var_curto, incluir_numero=True)
                    label_sucinto = ascii_safe(gerar_label_sucinto_dispersao(var_curto))
                    
                    pares_variaveis.append({
                        'variavel': var_curto,
                        'label': label_sucinto,
                        'dimensao': dimensao,
                        'stats_curto': stats_curto,
                        'stats_longo': stats_longo,
                        'cor': CORES_DIMENSAO[dimensao],
                        'nome_dimensao': NOMES_DIMENSAO[dimensao]
                    })
    
    if not pares_variaveis:
        print("Nenhum par de variáveis encontrado para análise.")
        return None
    
    print(f"Total de pares encontrados: {len(pares_variaveis)}")
    
    # Aplicar filtros estatísticos
    dados_filtrados = aplicar_filtros_estatisticos(pares_variaveis)
    
    if not dados_filtrados:
        print("Nenhuma variável passou pelos filtros estatísticos.")
        return None
    
    # Preparar dados para o gráfico
    x_vals = [par['stats_curto']['mediana'] for par in dados_filtrados]
    y_vals = [par['stats_longo']['mediana'] for par in dados_filtrados]
    cores = [par['cor'] for par in dados_filtrados]
    tamanhos = [par['variabilidade_media'] * 200 + 50 for par in dados_filtrados]  # Escalar para visualização
    labels = [par['label'] for par in dados_filtrados]
    
    # Criar gráfico
    plt.figure(figsize=(14, 10))
    
    # Configurar estilo
    sns.set_style("whitegrid")
    plt.style.use('default')
    
    # Criar scatter plot
    scatter = plt.scatter(x_vals, y_vals, c=cores, s=tamanhos, alpha=0.7, 
                       edgecolors='black', linewidth=1.5)
    
    # Adicionar linhas de referência
    # Linha diagonal (y=x) - riscos estáveis
    plt.plot([1, 5], [1, 5], 'k--', alpha=0.5, linewidth=2, label='Riscos Estáveis (y=x)')
    
    # Linhas verticais e horizontais em mediana=3.0 (limiar neutro)
    plt.axvline(x=3.0, color='orange', linestyle='--', alpha=0.5, linewidth=1.5, label='Limiar Neutro')
    plt.axhline(y=3.0, color='orange', linestyle='--', alpha=0.5, linewidth=1.5)
    
    # Configurar eixos
    plt.xlabel('Mediana Curto Prazo (2026-2027)', fontsize=14, fontweight='bold')
    plt.ylabel('Mediana Longo Prazo (até 2035)', fontsize=14, fontweight='bold')
    plt.title(
        'Análise de Dispersão Temporal de Riscos\n'
        'Relação entre Percepção de Curto e Longo Prazo',
        fontsize=16,
        fontweight='bold',
        pad=25
    )
    
    # Limites dos eixos
    plt.xlim(1.5, 5.5)
    plt.ylim(1.5, 5.5)
    plt.xticks(np.arange(2, 6))
    plt.yticks(np.arange(2, 6))
    
    # Adicionar grid
    plt.grid(True, alpha=0.3)
    
    # Adicionar labels para pontos principais (top 10 por variabilidade)
    pontos_ordenados = sorted(dados_filtrados, key=lambda x: x['variabilidade_media'], reverse=True)[:10]
    for par in pontos_ordenados:
        x_pos = par['stats_curto']['mediana']
        y_pos = par['stats_longo']['mediana']
        label = par['label']
        
        # Ajustar posição para evitar sobreposição
        offset_x = 0.1 if x_pos < 4 else -0.3
        offset_y = 0.1 if y_pos < 4 else -0.2
        
        plt.annotate(
            label,
            (x_pos, y_pos),
            xytext=(offset_x, offset_y),
            textcoords='offset points',
            fontsize=8,
            bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8, edgecolor='gray'),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', color='gray', alpha=0.5)
        )
    
    # Legenda de cores por dimensão
    legend_elements = []
    dimensoes_unicas = set(par['dimensao'] for par in dados_filtrados)
    for dimensao in dimensoes_unicas:
        legend_elements.append(
            plt.scatter([], [], c=CORES_DIMENSAO[dimensao], s=100, 
                      label=NOMES_DIMENSAO[dimensao], alpha=0.7, edgecolors='black')
        )
    
    # Legenda combinada
    legend1 = plt.legend(handles=legend_elements, loc='upper left', 
                     title='Dimensões', framealpha=0.95, fontsize=10)
    legend2 = plt.legend(loc='lower right', framealpha=0.95, fontsize=9)
    plt.gca().add_artist(legend1)
    
    # Adicionar texto explicativo dos quadrantes
    plt.figtext(0.02, 0.98, 'Q1: Riscos Crônicos\n(Alto-Alto)', 
                transform=plt.gca().transAxes, fontsize=9, fontweight='bold',
                verticalalignment='top', bbox=dict(boxstyle="round,pad=0.3", 
                facecolor='lightcoral', alpha=0.7))
    
    plt.figtext(0.02, 0.02, 'Q3: Riscos Controlados\n(Baixo-Baixo)', 
                transform=plt.gca().transAxes, fontsize=9, fontweight='bold',
                verticalalignment='bottom', bbox=dict(boxstyle="round,pad=0.3", 
                facecolor='lightgreen', alpha=0.7))
    
    plt.figtext(0.98, 0.98, 'Q2: Riscos Emergentes\n(Baixo-Alto)', 
                transform=plt.gca().transAxes, fontsize=9, fontweight='bold',
                verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='lightyellow', alpha=0.7))
    
    plt.figtext(0.98, 0.02, 'Q4: Riscos em Melhoria\n(Alto-Baixo)', 
                transform=plt.gca().transAxes, fontsize=9, fontweight='bold',
                verticalalignment='bottom', horizontalalignment='right',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.7))
    
    plt.tight_layout()
    
    # Salvar gráfico
    caminho_saida = Path("quarto/assets/graficos_agrupados/grafico_dispersao_temporal_riscos.png")
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    
    plt.savefig(caminho_saida, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"Gráfico salvo em: {caminho_saida}")
    
    # Gerar análise estatística detalhada
    gerar_analise_estatistica_dispersao(dados_filtrados)
    
    return caminho_saida

def gerar_analise_estatistica_dispersao(dados_filtrados: List[Dict]):
    """
    Gera análise estatística detalhada do gráfico de dispersão.
    
    Args:
        dados_filtrados: Lista com dados filtrados para análise
    """
    print("\n" + "="*70)
    print("ANÁLISE ESTATÍSTICA - GRÁFICO DE DISPERSÃO TEMPORAL")
    print("="*70)
    
    # Estatísticas gerais
    x_vals = [par['stats_curto']['mediana'] for par in dados_filtrados]
    y_vals = [par['stats_longo']['mediana'] for par in dados_filtrados]
    deltas = [par['delta_temporal'] for par in dados_filtrados]
    
    print(f"\nESTATÍSTICAS GERAIS:")
    print(f"Total de variáveis analisadas: {len(dados_filtrados)}")
    print(f"Mediana curto prazo - Média: {np.mean(x_vals):.2f} | Desvio: {np.std(x_vals):.2f}")
    print(f"Mediana longo prazo - Média: {np.mean(y_vals):.2f} | Desvio: {np.std(y_vals):.2f}")
    print(f"Delta temporal médio: {np.mean(deltas):.2f}")
    
    # Análise por dimensão
    analise_dimensoes = {}
    for par in dados_filtrados:
        dimensao = par['dimensao']
        if dimensao not in analise_dimensoes:
            analise_dimensoes[dimensao] = {
                'count': 0,
                'x_vals': [],
                'y_vals': [],
                'deltas': [],
                'riscos': []
            }
        
        analise_dimensoes[dimensao]['count'] += 1
        analise_dimensoes[dimensao]['x_vals'].append(par['stats_curto']['mediana'])
        analise_dimensoes[dimensao]['y_vals'].append(par['stats_longo']['mediana'])
        analise_dimensoes[dimensao]['deltas'].append(par['delta_temporal'])
        analise_dimensoes[dimensao]['riscos'].append(par)
    
    print(f"\nANÁLISE POR DIMENSÃO:")
    print("-" * 50)
    
    for dimensao, dados in analise_dimensoes.items():
        media_x = np.mean(dados['x_vals'])
        media_y = np.mean(dados['y_vals'])
        media_delta = np.mean(dados['deltas'])
        
        print(f"\n{NOMES_DIMENSAO[dimensao]}:")
        print(f"  Quantidade: {dados['count']} riscos")
        print(f"  Média curto prazo: {media_x:.2f}")
        print(f"  Média longo prazo: {media_y:.2f}")
        print(f"  Delta médio: {media_delta:.2f}")
        
        # Classificar tendência
        if media_delta > 0.5:
            tendencia = "Piora significativa"
        elif media_delta > 0.1:
            tendencia = "Piora moderada"
        elif media_delta > -0.1:
            tendencia = "Estável"
        else:
            tendencia = "Melhoria"
        
        print(f"  Tendência: {tendencia}")
        
        # Top 3 riscos da dimensão
        riscos_ordenados = sorted(dados['riscos'], key=lambda x: x['variabilidade_media'], reverse=True)
        print(f"  Top 3 por variabilidade:")
        for i, risco in enumerate(riscos_ordenados[:3], 1):
            print(f"    {i}. {risco['label']}: Δ={risco['delta_temporal']:.2f}")
    
    # Análise dos quadrantes
    print(f"\nANÁLISE DOS QUADRANTES:")
    print("-" * 40)
    
    q1 = []  # Alto-Alto (crônicos)
    q2 = []  # Baixo-Alto (emergentes)
    q3 = []  # Baixo-Baixo (controlados)
    q4 = []  # Alto-Baixo (melhoria)
    
    for par in dados_filtrados:
        x = par['stats_curto']['mediana']
        y = par['stats_longo']['mediana']
        
        if x >= 3.0 and y >= 3.0:
            q1.append(par)
        elif x < 3.0 and y >= 3.0:
            q2.append(par)
        elif x < 3.0 and y < 3.0:
            q3.append(par)
        else:  # x >= 3.0 and y < 3.0
            q4.append(par)
    
    print(f"Q1 - Riscos Crônicos (Alto-Alto): {len(q1)} variáveis")
    if q1:
        top_q1 = sorted(q1, key=lambda x: (x['stats_curto']['mediana'] + x['stats_longo']['mediana'])/2, reverse=True)[:3]
        for i, risco in enumerate(top_q1, 1):
            print(f"  {i}. {risco['label']} ({risco['nome_dimensao']})")
    
    print(f"\nQ2 - Riscos Emergentes (Baixo-Alto): {len(q2)} variáveis")
    if q2:
        top_q2 = sorted(q2, key=lambda x: x['delta_temporal'], reverse=True)[:3]
        for i, risco in enumerate(top_q2, 1):
            print(f"  {i}. {risco['label']} ({risco['nome_dimensao']}) - Δ={risco['delta_temporal']:.2f}")
    
    print(f"\nQ3 - Riscos Controlados (Baixo-Baixo): {len(q3)} variáveis")
    print(f"\nQ4 - Riscos em Melhoria (Alto-Baixo): {len(q4)} variáveis")
    if q4:
        top_q4 = sorted(q4, key=lambda x: -x['delta_temporal'], reverse=True)[:3]
        for i, risco in enumerate(top_q4, 1):
            print(f"  {i}. {risco['label']} ({risco['nome_dimensao']}) - Δ={risco['delta_temporal']:.2f}")
    
    # Correlação geral
    if len(x_vals) > 1 and len(y_vals) > 1:
        correlacao = np.corrcoef(x_vals, y_vals)[0, 1]
        print(f"\nCORRELAÇÃO TEMPORAL:")
        print(f"Coeficiente de correlação: {correlacao:.3f}")
        
        if correlacao > 0.7:
            interpretacao = "Forte correlação positiva (riscos estáveis)"
        elif correlacao > 0.3:
            interpretacao = "Correlação moderada positiva"
        elif correlacao > -0.3:
            interpretacao = "Correlação fraca"
        else:
            interpretacao = "Correlação negativa (mudança de padrão)"
        
        print(f"Interpretação: {interpretacao}")
    
    print("\n" + "="*70)

def main():
    """Função principal."""
    try:
        caminho_grafico = gerar_grafico_dispersao_temporal()
        if caminho_grafico:
            print(f"\n✅ Gráfico de dispersão temporal gerado com sucesso!")
            print(f"📁 Arquivo: {caminho_grafico}")
            print("\n📊 Pronto para integração com o capítulo interconexao-riscos.qmd")
        else:
            print("❌ Falha ao gerar gráfico de dispersão temporal")
            
    except Exception as e:
        print(f"❌ Erro ao executar análise: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

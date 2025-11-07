#!/usr/bin/env python3
"""
Gera grafico de barras invertido com os maiores riscos imediatos (niveis 4-5)
de todas as dimensoes para o capitulo de interconexao de riscos.
"""

from __future__ import annotations

import sys
import unicodedata
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

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

def gerar_label_sucinto_interconexao(nome_variavel: str) -> str:
    """Gera rotulo sucinto para o grafico de interconexao."""
    # Extrair número e descrição
    match = nome_variavel.match(r'^(\d+\.\d+)\s*(.+?)\s*\[.*?\]$', nome_variavel)
    if match:
        numero = match.group(1)
        descricao_completa = match.group(2).strip()
        
        # Criar versão sucinta (máximo 60 caracteres)
        palavras = descricao_completa.split()
        if len(descricao_completa) <= 60:
            sucinto = descricao_completa
        else:
            # Manter palavras-chave importantes
            palavras_chave = []
            for palavra in palavras:
                if len(' '.join(palavras_chave + [palavra])) <= 55:
                    palavras_chave.append(palavra)
                elif palavra.lower() in ['crise', 'risco', 'impacto', 'consequência', 'contaminação', 'disrupção']:
                    palavras_chave.append(palavra)
                elif len(palavra) > 8:  # Palavras longas podem ser importantes
                    palavras_chave.append(palavra)
            
            sucinto = ' '.join(palavras_chave)
            if len(palavras) > len(palavras_chave):
                sucinto += '...'
        
        return f"{numero} - {sucinto}"
    
    return nome_variavel

def gerar_grafico_interconexao_riscos() -> Path:
    """
    Gera grafico consolidado com os maiores riscos imediatos de todas as dimensoes.
    
    Returns:
        Path do arquivo gerado
    """
    print("Gerando gráfico de interconexão de riscos...")
    
    # Inicializar analisador
    analisador = AnalisadorRiscosLikert()
    analisador.carregar_dados()
    mapeamento = analisador.mapear_variaveis_por_dimensao()
    
    # Coletar todos os riscos do período imediato_2025
    todos_riscos = []
    
    for dimensao, periodos in mapeamento.items():
        print(f"Processando dimensão: {ascii_safe(dimensao)}")
        
        variaveis_periodo = periodos.get("imediato_2025", [])
        
        for variavel in variaveis_periodo:
            if variavel not in analisador.dados_brutos:
                continue
            
            serie = analisador.dados_brutos[variavel]
            estatisticas = analisador.analisar_frequencias_likert(serie)
            
            if not estatisticas:
                continue
            
            # Gerar label sucinto
            label_completo = analisador.gerar_label_sucinto(variavel, incluir_numero=False)
            label_sucinto = ascii_safe(label_completo)
            
            # Limitar tamanho do label para o gráfico
            if len(label_sucinto) > 80:
                label_sucinto = label_sucinto[:77] + "..."
            
            todos_riscos.append({
                'variavel': variavel,
                'label': label_sucinto,
                'dimensao': dimensao,
                'percentual_risco_alto': estatisticas['percentual_risco_alto'],
                'mediana': estatisticas['mediana'],
                'cor': CORES_DIMENSAO[dimensao],
                'nome_dimensao': NOMES_DIMENSAO[dimensao]
            })
    
    if not todos_riscos:
        print("Nenhum risco encontrado para análise.")
        return None
    
    # Ordenar por percentual de risco alto (maior primeiro)
    todos_riscos.sort(key=lambda x: x['percentual_risco_alto'], reverse=True)
    
    # Limitar ao top 20 para melhor visualização
    top_riscos = todos_riscos[:20]
    
    print(f"Total de riscos analisados: {len(todos_riscos)}")
    print(f"Top 20 riscos selecionados para visualização")
    
    # Preparar dados para o gráfico
    labels = [risco['label'] for risco in top_riscos][::-1]  # Inverter para barras horizontais
    valores = np.array([risco['percentual_risco_alto'] for risco in top_riscos][::-1])
    cores = [risco['cor'] for risco in top_riscos][::-1]
    medianas = [risco['mediana'] for risco in top_riscos][::-1]
    
    # Criar gráfico
    altura = max(8.0, 0.35 * len(labels))
    plt.figure(figsize=(16, altura))
    
    # Criar barras horizontais
    barras = plt.barh(range(len(labels)), valores, color=cores, alpha=0.8, edgecolor='black', linewidth=0.8)
    
    # Adicionar valores nas barras
    for i, (barra, valor, mediana) in enumerate(zip(barras, valores, medianas)):
        plt.text(
            barra.get_width() + 0.8,
            barra.get_y() + barra.get_height() / 2,
            f"{valor:.1f}% (M:{mediana:.1f})",
            ha='left',
            va='center',
            fontsize=9,
            fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8, edgecolor='gray')
        )
    
    # Configurações do gráfico
    plt.xlabel("Percentual de Respostas em Níveis Altos (4-5)", fontsize=14, fontweight='bold')
    plt.ylabel("Riscos por Dimensão", fontsize=14, fontweight='bold')
    plt.title(
        "Maiores Riscos Imediatos (Níveis 4-5) - Todas as Dimensões\n"
        "Período Imediato 2025 | Ordenado do Maior para Menor Risco",
        fontsize=16,
        fontweight='bold',
        pad=25
    )
    
    # Configurar eixos
    plt.yticks(range(len(labels)), labels, fontsize=10)
    plt.xlim(0, max(valores) * 1.15)
    plt.xticks(fontsize=11)
    plt.grid(axis='x', alpha=0.3, linestyle='--', linewidth=0.8)
    
    # Legenda de cores por dimensão
    legend_elements = []
    for dimensao, cor in CORES_DIMENSAO.items():
        if dimensao in [risco['dimensao'] for risco in top_riscos]:
            legend_elements.append(
                plt.Rectangle((0, 0), 1, 1, facecolor=cor, 
                           label=NOMES_DIMENSAO[dimensao], alpha=0.8)
            )
    
    if legend_elements:
        plt.legend(handles=legend_elements, loc='lower right', 
                 title='Dimensões', framealpha=0.95, 
                 bbox_to_anchor=(0.98, 0.02), fontsize=10)
    
    # Adicionar linha de referência para média geral
    media_geral = np.mean(valores)
    plt.axvline(x=media_geral, color='red', linestyle='--', alpha=0.7, linewidth=2)
    plt.text(media_geral + 0.5, len(labels) - 1, 
             f'Média: {media_geral:.1f}%', 
             fontsize=10, fontweight='bold', color='red',
             bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', alpha=0.7))
    
    plt.tight_layout()
    
    # Salvar gráfico
    caminho_saida = Path("quarto/assets/graficos_agrupados/grafico_interconexao_riscos_imediato_2025.png")
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    
    plt.savefig(caminho_saida, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"Gráfico salvo em: {caminho_saida}")
    
    # Gerar análise estatística
    gerar_analise_estatistica(top_riscos, media_geral)
    
    return caminho_saida

def gerar_analise_estatistica(top_riscos: List[Dict], media_geral: float):
    """
    Gera análise estatística dos top riscos para inclusão no relatório.
    
    Args:
        top_riscos: Lista com os top riscos analisados
        media_geral: Média geral de percentuais
    """
    print("\n" + "="*60)
    print("ANÁLISE ESTATÍSTICA - TOP RISCOS IMEDIATOS")
    print("="*60)
    
    # Análise por dimensão
    analise_dimensoes = {}
    for risco in top_riscos:
        dimensao = risco['dimensao']
        if dimensao not in analise_dimensoes:
            analise_dimensoes[dimensao] = {
                'count': 0,
                'soma': 0,
                'max': 0,
                'riscos': []
            }
        
        analise_dimensoes[dimensao]['count'] += 1
        analise_dimensoes[dimensao]['soma'] += risco['percentual_risco_alto']
        analise_dimensoes[dimensao]['riscos'].append(risco)
        
        if risco['percentual_risco_alto'] > analise_dimensoes[dimensao]['max']:
            analise_dimensoes[dimensao]['max'] = risco['percentual_risco_alto']
    
    print(f"Média geral de risco alto: {media_geral:.1f}%")
    print(f"Total de riscos analisados: {len(top_riscos)}")
    print(f"\nAnálise por Dimensão:")
    print("-" * 40)
    
    for dimensao, dados in analise_dimensoes.items():
        media_dimensao = dados['soma'] / dados['count']
        print(f"\n{NOMES_DIMENSAO[dimensao]}:")
        print(f"  Quantidade: {dados['count']} riscos")
        print(f"  Média: {media_dimensao:.1f}%")
        print(f"  Máximo: {dados['max']:.1f}%")
        print(f"  Top 3:")
        
        # Ordenar riscos da dimensão
        riscos_dimensao = sorted(dados['riscos'], key=lambda x: x['percentual_risco_alto'], reverse=True)
        for i, risco in enumerate(riscos_dimensao[:3], 1):
            print(f"    {i}. {risco['label']}: {risco['percentual_risco_alto']:.1f}%")
    
    # Riscos críticos (>40%)
    riscos_criticos = [r for r in top_riscos if r['percentual_risco_alto'] > 40]
    print(f"\nRISCOS CRÍTICOS (>40%): {len(riscos_criticos)}")
    for i, risco in enumerate(riscos_criticos, 1):
        print(f"  {i}. {risco['label']} ({risco['nome_dimensao']}): {risco['percentual_risco_alto']:.1f}%")
    
    print("\n" + "="*60)

def main():
    """Função principal."""
    try:
        caminho_grafico = gerar_grafico_interconexao_riscos()
        if caminho_grafico:
            print(f"\n✅ Gráfico de interconexão de riscos gerado com sucesso!")
            print(f"📁 Arquivo: {caminho_grafico}")
            print("\n📊 Pronto para integração com o capítulo interconexao-riscos.qmd")
        else:
            print("❌ Falha ao gerar gráfico de interconexão de riscos")
            
    except Exception as e:
        print(f"❌ Erro ao executar análise: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

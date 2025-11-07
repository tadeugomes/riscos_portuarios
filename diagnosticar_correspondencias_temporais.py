#!/usr/bin/env python3
"""
Diagnóstico de correspondências temporais para análise de dispersão
Identifica todas as variáveis disponíveis e possíveis correspondências entre períodos
"""

from __future__ import annotations

import sys
import unicodedata
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from difflib import SequenceMatcher

import pandas as pd

from analise_likert_riscos import AnalisadorRiscosLikert

def ascii_safe(texto: str) -> str:
    """Remove acentuação para evitar erros em consoles Windows."""
    return "".join(
        caractere
        for caractere in unicodedata.normalize("NFKD", texto)
        if not unicodedata.combining(caractere)
    )

def extrair_numero_base(nome_variavel: str) -> Optional[str]:
    """Extrai o número base da variável (ex: '1.1' de '1.2 Risco X [Curto Prazo]')"""
    match = re.match(r'^(\d+\.\d+)', nome_variavel)
    if match:
        return match.group(1)
    return None

def extrair_descricao_limpa(nome_variavel: str) -> str:
    """Extrai descrição limpa sem números e colchetes"""
    # Remover número inicial
    sem_numero = re.sub(r'^\d+\.\d+\s*', '', nome_variavel)
    # Remover conteúdo entre colchetes
    sem_colchetes = re.sub(r'\s*\[.*?\]\s*$', '', sem_numero)
    # Limpar espaços extras
    return sem_colchetes.strip()

def calcular_similaridade(texto1: str, texto2: str) -> float:
    """Calcula similaridade entre duas strings usando SequenceMatcher"""
    return SequenceMatcher(None, texto1.lower(), texto2.lower()).ratio()

def encontrar_correspondencias_por_numero(variaveis_curto: List[str], variaveis_longo: List[str]) -> List[Tuple[str, str, str]]:
    """
    Encontra correspondências usando número base como critério principal
    
    Returns:
        Lista de tuplas (var_curto, var_longo, metodo)
    """
    correspondencias = []
    
    # Criar mapa de variáveis de longo prazo por número base
    mapa_longo = {}
    for var_longo in variaveis_longo:
        num_base = extrair_numero_base(var_longo)
        if num_base:
            if num_base not in mapa_longo:
                mapa_longo[num_base] = []
            mapa_longo[num_base].append(var_longo)
    
    # Para cada variável de curto prazo, buscar correspondência
    for var_curto in variaveis_curto:
        num_base = extrair_numero_base(var_curto)
        if num_base and num_base in mapa_longo:
            # Se houver múltiplas opções, escolher a mais similar
            candidatos = mapa_longo[num_base]
            if len(candidatos) == 1:
                correspondencias.append((var_curto, candidatos[0], "numero_base_unico"))
            else:
                # Escolher o mais similar pela descrição
                desc_curto = extrair_descricao_limpa(var_curto)
                melhor_candidato = None
                melhor_similaridade = 0
                
                for candidato in candidatos:
                    desc_candidato = extrair_descricao_limpa(candidato)
                    similaridade = calcular_similaridade(desc_curto, desc_candidato)
                    if similaridade > melhor_similaridade:
                        melhor_similaridade = similaridade
                        melhor_candidato = candidato
                
                if melhor_candidato:
                    correspondencias.append((var_curto, melhor_candidato, f"numero_base_similaridade_{melhor_similaridade:.2f}"))
    
    return correspondencias

def encontrar_correspondencias_por_similaridade(variaveis_curto: List[str], variaveis_longo: List[str], 
                                             limiar: float = 0.7) -> List[Tuple[str, str, str]]:
    """
    Encontra correspondências usando similaridade de texto
    
    Returns:
        Lista de tuplas (var_curto, var_longo, metodo)
    """
    correspondencias = []
    usados_longo = set()
    
    for var_curto in variaveis_curto:
        desc_curto = extrair_descricao_limpa(var_curto)
        melhor_match = None
        melhor_similaridade = 0
        
        for var_longo in variaveis_longo:
            if var_longo in usados_longo:
                continue
                
            desc_longo = extrair_descricao_limpa(var_longo)
            similaridade = calcular_similaridade(desc_curto, desc_longo)
            
            if similaridade > melhor_similaridade and similaridade >= limiar:
                melhor_similaridade = similaridade
                melhor_match = var_longo
        
        if melhor_match:
            correspondencias.append((var_curto, melhor_match, f"similaridade_{melhor_similaridade:.2f}"))
            usados_longo.add(melhor_match)
    
    return correspondencias

def diagnosticar_correspondencias():
    """Função principal de diagnóstico"""
    print("DIAGNÓSTICO DE CORRESPONDÊNCIAS TEMPORAIS")
    print("=" * 60)
    
    # Inicializar analisador
    analisador = AnalisadorRiscosLikert()
    analisador.carregar_dados()
    mapeamento = analisador.mapear_variaveis_por_dimensao()
    
    # Estatísticas gerais
    print("\nESTATÍSTICAS GERAIS DE VARIÁVEIS:")
    print("-" * 40)
    
    total_curto = 0
    total_longo = 0
    total_potencial = 0
    
    for dimensao, periodos in mapeamento.items():
        vars_curto = len(periodos.get("curto_prazo_2026_2027", []))
        vars_longo = len(periodos.get("longo_prazo_2035", []))
        potencial = min(vars_curto, vars_longo)
        
        total_curto += vars_curto
        total_longo += vars_longo
        total_potencial += potencial
        
        print(f"{dimensao}:")
        print(f"  Curto prazo: {vars_curto} variáveis")
        print(f"  Longo prazo: {vars_longo} variáveis")
        print(f"  Potencial de pares: {potencial}")
    
    print(f"\nTOTAL GERAL:")
    print(f"  Curto prazo: {total_curto} variáveis")
    print(f"  Longo prazo: {total_longo} variáveis")
    print(f"  Potencial máximo de pares: {total_potencial}")
    
    # Análise detalhada por dimensão
    print("\n\nANÁLISE DETALHADA POR DIMENSÃO:")
    print("=" * 60)
    
    todas_correspondencias = {}
    
    for dimensao, periodos in mapeamento.items():
        print(f"\n{ascii_safe(dimensao.upper())}:")
        print("-" * 50)
        
        variaveis_curto = periodos.get("curto_prazo_2026_2027", [])
        variaveis_longo = periodos.get("longo_prazo_2035", [])
        
        print(f"Variáveis curto prazo ({len(variaveis_curto)}):")
        for i, var in enumerate(variaveis_curto, 1):
            num_base = extrair_numero_base(var)
            desc = extrair_descricao_limpa(var)
            print(f"  {i:2d}. {num_base or 'N/A'} - {desc[:60]}...")
        
        print(f"\nVariáveis longo prazo ({len(variaveis_longo)}):")
        for i, var in enumerate(variaveis_longo, 1):
            num_base = extrair_numero_base(var)
            desc = extrair_descricao_limpa(var)
            print(f"  {i:2d}. {num_base or 'N/A'} - {desc[:60]}...")
        
        # Encontrar correspondências por número base
        corr_numero = encontrar_correspondencias_por_numero(variaveis_curto, variaveis_longo)
        print(f"\nCorrespondências por número base: {len(corr_numero)}")
        
        # Encontrar correspondências por similaridade (para as não encontradas)
        usados_curto = {c[0] for c in corr_numero}
        restantes_curto = [v for v in variaveis_curto if v not in usados_curto]
        usados_longo = {c[1] for c in corr_numero}
        restantes_longo = [v for v in variaveis_longo if v not in usados_longo]
        
        corr_similaridade = encontrar_correspondencias_por_similaridade(restantes_curto, restantes_longo, 0.6)
        print(f"Correspondências por similaridade: {len(corr_similaridade)}")
        
        # Combinar correspondências
        todas_corr = corr_numero + corr_similaridade
        todas_correspondencias[dimensao] = todas_corr
        
        print(f"\nTotal de correspondências encontradas: {len(todas_corr)} de {min(len(variaveis_curto), len(variaveis_longo))} possíveis")
        
        # Mostrar detalhes das correspondências
        if todas_corr:
            print("\nDetalhes das correspondências:")
            for i, (curto, longo, metodo) in enumerate(todas_corr[:10], 1):  # Limitar a 10 para não sobrecarregar
                num_curto = extrair_numero_base(curto)
                num_longo = extrair_numero_base(longo)
                desc_curto = extrair_descricao_limpa(curto)[:40]
                desc_longo = extrair_descricao_limpa(longo)[:40]
                
                print(f"  {i:2d}. {num_curto}→{num_longo} | {metodo}")
                print(f"      C: {desc_curto}...")
                print(f"      L: {desc_longo}...")
                print()
    
    # Resumo final
    print("\n\nRESUMO FINAL:")
    print("=" * 40)
    
    total_encontrado = sum(len(corr) for corr in todas_correspondencias.values())
    print(f"Total de correspondências encontradas: {total_encontrado}")
    print(f"Potencial máximo: {total_potencial}")
    print(f"Cobertura: {total_encontrado/total_potencial*100:.1f}%")
    
    print("\nPor dimensão:")
    for dimensao, corr in todas_correspondencias.items():
        potencial_dim = min(len(mapeamento[dimensao].get("curto_prazo_2026_2027", [])),
                          len(mapeamento[dimensao].get("longo_prazo_2035", [])))
        cobertura = len(corr) / potencial_dim * 100 if potencial_dim > 0 else 0
        print(f"  {dimensao}: {len(corr)}/{potencial_dim} ({cobertura:.1f}%)")
    
    # Salvar relatório detalhado
    salvar_relatorio_diagnostico(todas_correspondencias, mapeamento)
    
    return todas_correspondencias

def salvar_relatorio_diagnostico(correspondencias: Dict, mapeamento: Dict):
    """Salva relatório detalhado do diagnóstico em arquivo"""
    caminho_relatorio = Path("outputs/diagnostico_correspondencias_temporais.txt")
    caminho_relatorio.parent.mkdir(exist_ok=True)
    
    with open(caminho_relatorio, 'w', encoding='utf-8') as f:
        f.write("RELATÓRIO DE DIAGNÓSTICO DE CORRESPONDÊNCIAS TEMPORAIS\n")
        f.write("=" * 70 + "\n\n")
        
        f.write("Data do diagnóstico: {}\n\n".format(pd.Timestamp.now().strftime('%d/%m/%Y %H:%M:%S')))
        
        for dimensao, corr_list in correspondencias.items():
            f.write(f"DIMENSÃO: {dimensao.upper()}\n")
            f.write("-" * 50 + "\n\n")
            
            variaveis_curto = mapeamento[dimensao].get("curto_prazo_2026_2027", [])
            variaveis_longo = mapeamento[dimensao].get("longo_prazo_2035", [])
            
            f.write(f"Variáveis curto prazo: {len(variaveis_curto)}\n")
            f.write(f"Variáveis longo prazo: {len(variaveis_longo)}\n")
            f.write(f"Correspondências encontradas: {len(corr_list)}\n\n")
            
            f.write("DETALHES DAS CORRESPONDÊNCIAS:\n")
            f.write("-" * 30 + "\n")
            
            for i, (curto, longo, metodo) in enumerate(corr_list, 1):
                f.write(f"{i:3d}. Método: {metodo}\n")
                f.write(f"     Curto: {curto}\n")
                f.write(f"     Longo: {longo}\n\n")
            
            f.write("\n" + "=" * 70 + "\n\n")
    
    print(f"\nRelatório detalhado salvo em: {caminho_relatorio}")

def main():
    """Função principal"""
    try:
        correspondencias = diagnosticar_correspondencias()
        print("\n✅ Diagnóstico concluído com sucesso!")
        print("📁 Relatório detalhado salvo em outputs/diagnostico_correspondencias_temporais.txt")
        
    except Exception as e:
        print(f"❌ Erro durante diagnóstico: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

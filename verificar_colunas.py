#!/usr/bin/env python3
"""
Script para verificar os nomes exatos das colunas no arquivo Excel
"""

import pandas as pd

def verificar_colunas():
    """Verifica os nomes das colunas no arquivo Excel"""
    
    try:
        # Carregar dados
        df = pd.read_excel('questionario.xlsx')
        
        print("Colunas encontradas no arquivo Excel:")
        print("=" * 80)
        
        # Filtrar apenas colunas que começam com "4."
        colunas_sociais = [col for col in df.columns if str(col).startswith('4.')]
        
        for i, col in enumerate(colunas_sociais, 1):
            print(f"{i:2d}. {col}")
        
        print(f"\nTotal de colunas sociais: {len(colunas_sociais)}")
        
        # Verificar se há colunas com períodos temporais
        print("\nVerificando períodos temporais:")
        print("-" * 40)
        
        periodos = ['2025', '2026', '2027', '2035', 'Imediato', 'Curto', 'Longo']
        
        for periodo in periodos:
            colunas_periodo = [col for col in colunas_sociais if periodo in str(col)]
            if colunas_periodo:
                print(f"{periodo}: {len(colunas_periodo)} colunas")
                for col in colunas_periodo[:3]:  # Mostrar apenas as 3 primeiras
                    print(f"  - {col}")
                if len(colunas_periodo) > 3:
                    print(f"  ... e mais {len(colunas_periodo) - 3}")
                print()
        
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    verificar_colunas()

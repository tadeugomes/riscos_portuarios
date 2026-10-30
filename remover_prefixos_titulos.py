#!/usr/bin/env python3
"""
Script para remover prefixos numéricos dos títulos das seções nos arquivos .qmd
Remove padrões como "### 4.1 Título" para "### Título"
"""

import os
import re
from pathlib import Path

def remover_prefixos_titulos(arquivo_path):
    """
    Remove prefixos numéricos dos títulos em um arquivo .qmd
    """
    try:
        # Ler o arquivo
        with open(arquivo_path, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Backup do conteúdo original
        conteudo_original = conteudo
        
        # Padrão regex para encontrar títulos com prefixos numéricos
        # Captura títulos como ### 4.1 Título, ## 1.2 Título, etc.
        padrao = r'^(#{1,6})\s+\d+\.\d+\s+(.+)$'
        
        # Substituir os títulos removendo os prefixos numéricos
        def substituir_titulo(match):
            nivel = match.group(1)  # ###, ##, etc.
            titulo = match.group(2)  # Título sem o prefixo
            return f"{nivel} {titulo}"
        
        # Aplicar a substituição em todo o conteúdo
        conteudo_modificado = re.sub(padrao, substituir_titulo, conteudo, flags=re.MULTILINE)
        
        # Verificar se houve alterações
        if conteudo_modificado != conteudo_original:
            # Salvar o arquivo modificado
            with open(arquivo_path, 'w', encoding='utf-8') as f:
                f.write(conteudo_modificado)
            
            # Contar quantas alterações foram feitas
            alteracoes = len(re.findall(padrao, conteudo_original, flags=re.MULTILINE))
            print(f"✅ {arquivo_path}: {alteracoes} títulos corrigidos")
            return alteracoes
        else:
            print(f"⏭️  {arquivo_path}: Nenhuma alteração necessária")
            return 0
            
    except Exception as e:
        print(f"❌ Erro ao processar {arquivo_path}: {str(e)}")
        return 0

def main():
    """
    Função principal para processar todos os arquivos .qmd
    """
    print("🔧 Iniciando remoção de prefixos numéricos dos títulos...")
    print("=" * 60)
    
    # Diretório dos arquivos Quarto
    quarto_dir = Path("quarto")
    
    # Encontrar todos os arquivos .qmd
    arquivos_qmd = list(quarto_dir.glob("*.qmd"))
    
    # Excluir o arquivo _book se existir
    arquivos_qmd = [f for f in arquivos_qmd if not f.name.startswith("_")]
    
    total_alteracoes = 0
    
    # Processar cada arquivo
    for arquivo in sorted(arquivos_qmd):
        alteracoes = remover_prefixos_titulos(arquivo)
        total_alteracoes += alteracoes
    
    print("=" * 60)
    print(f"📊 Resumo: {total_alteracoes} títulos corrigidos em {len(arquivos_qmd)} arquivos")
    
    if total_alteracoes > 0:
        print("\n🎯 Próximos passos:")
        print("1. Verifique as alterações nos arquivos .qmd")
        print("2. Compile o documento Quarto para ver o resultado")
        print("3. Se necessário, reverta com git para desfazer alterações")
    else:
        print("\n✅ Nenhuma alteração foi necessária")

if __name__ == "__main__":
    main()

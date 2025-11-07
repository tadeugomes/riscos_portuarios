from gerar_graficos_agrupados_tecnologicos import criar_grafico_agrupado_temporal_tecnologico, carregar_dados
import os
import shutil

variaveis = ["5.3", "5.5", "5.9", "5.11", "5.12", "5.13", "5.14", "5.16"]
base_dir = "outputs/tecnica_temp"
os.makedirs(base_dir, exist_ok=True)

df = carregar_dados()
if df is None:
    raise SystemExit("Falha ao carregar dados do questionário.")

for var in variaveis:
    nome_arquivo = f"grafico_agrupado_{var.replace('.', '_')}_temporal.png"
    print(f"Gerando {nome_arquivo}...")
    sucesso = criar_grafico_agrupado_temporal_tecnologico(df, var, output_dir=base_dir, nome_arquivo=nome_arquivo)
    if not sucesso:
        print(f"  -> falha ao gerar {var}")
        continue
    origem = os.path.join(base_dir, nome_arquivo)
    destinos = [
        os.path.join('quarto', 'assets', 'graficos_agrupados', nome_arquivo),
        os.path.join('quarto', 'assets', 'tecnologicos', nome_arquivo),
    ]
    for destino in destinos:
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        shutil.copy2(origem, destino)
        print(f"  -> atualizado {destino}")

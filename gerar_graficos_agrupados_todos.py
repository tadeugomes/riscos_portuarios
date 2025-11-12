#!/usr/bin/env python3
"""
Gera automaticamente os gráficos agrupados temporais para todas as variáveis
identificadas no questionário, verificando se já existem nos diretórios-alvo.
"""

import os
import re
import shutil
from collections import defaultdict

from analise_likert_riscos import AnalisadorRiscosLikert

DIMENSION_ASSET_DIR = {
    'Economica': 'economicos',
    'Ambiental': 'ambientais',
    'Geopolitica': 'geopoliticos',
    'Social': 'social',
    'Tecnologica': 'tecnologicos',
}

PERIOD_ORDER = ['imediato_2025', 'curto_prazo_2026_2027', 'longo_prazo_2035']


def montar_mapa_variaveis_por_dimensao(mapeamento):
    """Retorna dict[dimensao][codigo_base] -> dict[periodo] = nome_coluna."""
    resultado = {}
    for dimensao, periodos in mapeamento.items():
        base_map = defaultdict(dict)
        for periodo, variaveis in periodos.items():
            for coluna in variaveis:
                match = re.match(r'^(\d+\.\d+)', str(coluna))
                if not match:
                    continue
                codigo = match.group(1)
                base_map[codigo][periodo] = coluna
        resultado[dimensao] = base_map
    return resultado


def garantir_grafico(analisador, df, dimensao, codigo, periodos_colunas):
    """Cria o gráfico da variável informada se ele ainda não existir."""
    nome_base = codigo.replace('.', '_')
    filename = f'grafico_agrupado_{nome_base}_temporal.png'
    destino_comum = os.path.join('quarto', 'assets', 'graficos_agrupados', filename)
    destino_dim = os.path.join('quarto', 'assets', DIMENSION_ASSET_DIR[dimensao], filename)

    if os.path.exists(destino_comum) and os.path.exists(destino_dim):
        return False, filename  # nada a fazer

    dados_periodos = {
        periodo: df[coluna]
        for periodo, coluna in periodos_colunas.items()
        if coluna in df
    }

    if not dados_periodos:
        return None, filename

    nome_variavel = None
    for periodo in PERIOD_ORDER:
        if periodo in periodos_colunas:
            nome_variavel = periodos_colunas[periodo]
            break
    if not nome_variavel:
        nome_variavel = next(iter(periodos_colunas.values()))

    temp_dir = os.path.join('outputs', 'graficos_temp')
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, filename)

    sucesso = analisador.gerar_grafico_barras_agrupado_temporal(
        dados_periodos,
        nome_variavel,
        temp_path,
    )

    if not sucesso or not os.path.exists(temp_path):
        return None, filename

    for destino in (destino_comum, destino_dim):
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        shutil.copy2(temp_path, destino)

    return True, filename


def main():
    analisador = AnalisadorRiscosLikert()
    df = analisador.carregar_dados()
    mapeamento = analisador.mapear_variaveis_por_dimensao()
    variaveis_dim = montar_mapa_variaveis_por_dimensao(mapeamento)

    gerados = []
    ja_existiam = []
    erros = []

    for dimensao, variaveis in variaveis_dim.items():
        asset_dir = DIMENSION_ASSET_DIR.get(dimensao)
        if not asset_dir:
            continue

        for codigo, periodos_colunas in sorted(variaveis.items()):
            status, filename = garantir_grafico(
                analisador,
                df,
                dimensao,
                codigo,
                periodos_colunas,
            )
            registro = (dimensao, codigo, filename)
            if status is True:
                gerados.append(registro)
            elif status is False:
                ja_existiam.append(registro)
            else:
                erros.append(registro)

    print(f"Total de variáveis analisadas: {len(gerados) + len(ja_existiam) + len(erros)}")
    print(f" - Gráficos já existentes: {len(ja_existiam)}")
    print(f" - Gráficos gerados agora: {len(gerados)}")
    print(f" - Falhas: {len(erros)}")

    if gerados:
        print("\nGráficos gerados:")
        for dimensao, codigo, filename in gerados:
            print(f"  [{dimensao}] {codigo} -> {filename}")

    if erros:
        print("\nErros encontrados:")
        for dimensao, codigo, filename in erros:
            print(f"  [{dimensao}] {codigo} -> {filename}")


if __name__ == "__main__":
    main()

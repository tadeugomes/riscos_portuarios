@echo off
echo Atualizando grafico de dispersao temporal de riscos...
echo.

REM Verificar se o ambiente virtual existe
if not exist "venv\Scripts\activate.bat" (
    echo Erro: Ambiente virtual nao encontrado. Execute setup_venv.bat primeiro.
    pause
    exit /b 1
)

REM Ativar ambiente virtual
call venv\Scripts\activate.bat

REM Executar script de geracao do grafico
python gerar_grafico_dispersao_temporal.py

REM Verificar se o grafico foi gerado
if exist "quarto\assets\graficos_agrupados\grafico_dispersao_temporal_riscos.png" (
    echo.
    echo ✅ Grafico de dispersao temporal atualizado com sucesso!
    echo 📁 Arquivo: quarto\assets\graficos_agrupados\grafico_dispersao_temporal_riscos.png
    echo.
    echo 📊 Pronto para compilacao do relatorio Quarto
) else (
    echo.
    echo ❌ Falha na geracao do grafico
)

echo.
pause

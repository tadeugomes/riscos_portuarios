@echo off
echo Executando Análise de Riscos Portuários - Escala Likert
echo ========================================================

echo Verificando ambiente virtual...
if exist "venv\Scripts\python.exe" (
    echo Ambiente virtual encontrado.
    set PYTHON_CMD=venv\Scripts\python.exe
) else (
    echo Ambiente virtual não encontrado. Usando Python global.
    set PYTHON_CMD=python
)

echo.
echo Verificando dependências...
%PYTHON_CMD% -c "import matplotlib, seaborn, pandas, numpy" 2>nul
if %errorlevel% neq 0 (
    echo Instalando dependências necessárias...
    %PYTHON_CMD% -m pip install matplotlib seaborn pandas numpy openpyxl
    if %errorlevel% neq 0 (
        echo Erro ao instalar dependências.
        pause
        exit /b 1
    )
)

echo.
echo Executando análise completa...
%PYTHON_CMD% analise_likert_riscos.py

if %errorlevel% equ 0 (
    echo.
    echo ========================================================
    echo ANÁLISE CONCLUÍDA COM SUCESSO!
    echo ========================================================
    echo.
    echo Verifique os resultados na pasta 'outputs\'
    echo.
    echo Estrutura gerada:
    echo ├─ outputs\
    echo │  ├─ graficos_economicos\
    echo │  ├─ graficos_ambientais\
    echo │  ├─ graficos_geopoliticos\
    echo │  ├─ graficos_sociais\
    echo │  ├─ graficos_tecnologicos\
    echo │  └─ relatorio_consolidado.txt
    echo.
    echo Para visualizar os gráficos, abra a pasta outputs\
    echo.
) else (
    echo.
    echo Ocorreu um erro durante a análise.
    echo Verifique se o arquivo 'questionario.xlsx' existe no diretório.
    echo.
)

pause

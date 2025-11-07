@echo off
echo Atualizando gráfico de interconexão de riscos...
echo.

REM Ativar ambiente virtual
call venv\Scripts\activate

REM Executar script Python
python gerar_grafico_interconexao_riscos.py

REM Renderizar projeto Quarto
cd quarto
quarto render

echo.
echo ✅ Gráfico de interconexão atualizado com sucesso!
echo 📁 Arquivo: quarto\assets\graficos_agrupados\grafico_interconexao_riscos_imediato_2025.png
echo 🌐 HTML atualizado: quarto\_book\interconexao-riscos.html
echo.
pause

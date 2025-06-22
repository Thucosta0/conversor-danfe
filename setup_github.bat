@echo off
echo =================================================================
echo                 🚀 SETUP GITHUB - renamerPRO©
echo          Hospital Israelita Albert Einstein
echo =================================================================
echo.
echo Este script conectará seu projeto local ao GitHub
echo.
echo ANTES DE EXECUTAR:
echo 1. Crie um repositório no GitHub chamado "renamerPRO"
echo 2. Copie a URL do repositório (ex: https://github.com/usuario/renamerPRO.git)
echo.
set /p REPO_URL="Digite a URL do seu repositório GitHub: "

if "%REPO_URL%"=="" (
    echo ❌ URL não fornecida. Operação cancelada.
    pause
    exit /b 1
)

echo.
echo 🔗 Conectando ao repositório: %REPO_URL%
git remote add origin %REPO_URL%

echo.
echo 📤 Enviando arquivos para o GitHub...
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ SUCESSO! Projeto enviado para o GitHub com sucesso!
    echo.
    echo 🔗 Acesse seu repositório em: %REPO_URL%
    echo.
    echo 📋 Arquivos enviados:
    echo   • danfe_app.py       - Aplicação principal
    echo   • gerador_danfe.php  - Engine de processamento
    echo   • live_preview.py    - Sistema de monitoramento  
    echo   • README.md          - Documentação completa
    echo   • requirements.txt   - Dependências Python
    echo   • composer.json      - Dependências PHP
    echo   • .gitignore         - Configuração Git
    echo.
) else (
    echo.
    echo ❌ ERRO ao enviar para o GitHub!
    echo.
    echo Possíveis soluções:
    echo 1. Verifique se a URL está correta
    echo 2. Verifique suas credenciais do GitHub
    echo 3. Tente executar manualmente:
    echo    git remote add origin SUA_URL_AQUI
    echo    git push -u origin main
    echo.
)

echo =================================================================
pause 
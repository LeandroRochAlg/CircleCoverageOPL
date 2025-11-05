@echo off
REM Script principal para gerenciar o benchmark automatizado

:menu
cls
echo ================================================================================
echo SISTEMA DE BENCHMARK AUTOMATIZADO - COBERTURA DE CIRCULOS
echo ================================================================================
echo.
echo Escolha uma opcao:
echo.
echo 1. Setup inicial (instalar dependencias)
echo 2. Iniciar benchmark (execucao continua)
echo 3. Monitorar progresso (em tempo real)
echo 4. Analisar resultados
echo 5. Ver ultimos resultados
echo 6. Abrir pasta de resultados
echo 7. Sair
echo.
echo ================================================================================
set /p choice="Digite sua escolha (1-7): "

if "%choice%"=="1" goto setup
if "%choice%"=="2" goto benchmark
if "%choice%"=="3" goto monitor
if "%choice%"=="4" goto analyze
if "%choice%"=="5" goto latest
if "%choice%"=="6" goto open_results
if "%choice%"=="7" goto end

echo.
echo Opcao invalida! Tente novamente.
timeout /t 2 >nul
goto menu

:setup
cls
echo ================================================================================
echo EXECUTANDO SETUP...
echo ================================================================================
python "%~dp0setup_benchmark.py"
echo.
pause
goto menu

:benchmark
cls
echo ================================================================================
echo INICIANDO BENCHMARK AUTOMATIZADO
echo ================================================================================
echo.
echo O benchmark rodara indefinidamente ate voce pressionar Ctrl+C
echo.
echo Pressione qualquer tecla para iniciar...
pause >nul
python "%~dp0automated_benchmark.py"
echo.
pause
goto menu

:monitor
cls
echo ================================================================================
echo MONITOR DE PROGRESSO
echo ================================================================================
echo.
echo O monitor atualizara a cada 10 segundos
echo Pressione Ctrl+C para parar
echo.
echo Pressione qualquer tecla para iniciar...
pause >nul
python "%~dp0monitor_benchmark.py"
echo.
pause
goto menu

:analyze
cls
echo ================================================================================
echo ANALISE DE RESULTADOS
echo ================================================================================
python "%~dp0analyze_results.py"
echo.
pause
goto menu

:latest
cls
echo ================================================================================
echo ULTIMOS RESULTADOS
echo ================================================================================
set /p n="Quantos resultados exibir? (padrao=5): "
if "%n%"=="" set n=5
python "%~dp0monitor_benchmark.py" --latest %n%
echo.
pause
goto menu

:open_results
cls
echo ================================================================================
echo ABRINDO PASTA DE RESULTADOS
echo ================================================================================
start "" "%~dp0..\tests\automated_results"
echo.
echo Pasta aberta!
timeout /t 2 >nul
goto menu

:end
cls
echo.
echo Encerrando...
echo.
exit

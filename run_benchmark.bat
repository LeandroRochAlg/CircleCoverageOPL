@echo off
REM Atalho para o Sistema de Benchmark
REM Este script redireciona para a subpasta automated_benchmark/

echo.
echo ================================================================================
echo        SISTEMA DE BENCHMARK AUTOMATIZADO
echo ================================================================================
echo.
echo O sistema foi organizado em: automated_benchmark\
echo.
echo Abrindo menu...
echo.

cd /d "%~dp0automated_benchmark"
call benchmark_menu.bat

cd /d "%~dp0"

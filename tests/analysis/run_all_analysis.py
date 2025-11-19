"""
Master Script - Executa todas as análises
Execute este script para gerar todos os gráficos, tabelas e relatórios
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent

print("=" * 80)
print("ANÁLISE COMPLETA DE BENCHMARK - CIRCLE COVERAGE")
print("=" * 80)
print(f"Início: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print()

scripts = [
    ("benchmark_analyzer.py", "Análise Principal de Benchmark"),
    ("statistical_analysis.py", "Análise Estatística Avançada"),
    ("instance_analysis.py", "Análise de Instâncias"),
    ("generate_latex_report.py", "Geração de Relatório LaTeX")
]

for script_name, description in scripts:
    script_path = SCRIPT_DIR / script_name
    
    print(f"\n{'=' * 80}")
    print(f"Executando: {description}")
    print(f"Script: {script_name}")
    print('=' * 80)
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(SCRIPT_DIR),
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print(f"\n✓ {description} - CONCLUÍDO")
        else:
            print(f"\n✗ {description} - ERRO (código {result.returncode})")
    except Exception as e:
        print(f"\n✗ Erro ao executar {script_name}: {e}")

print("\n" + "=" * 80)
print("ANÁLISE COMPLETA FINALIZADA")
print("=" * 80)
print(f"Término: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print()
print("Todos os arquivos foram salvos em: tests/analysis/results/")
print()
print("Arquivos gerados:")
print("  • 16 gráficos PNG (300 DPI)")
print("  • 15+ tabelas CSV com dados")
print("  • 1 relatório LaTeX completo")
print()
print("Para compilar o relatório LaTeX:")
print("  cd tests/analysis/results")
print("  pdflatex relatorio_benchmark.tex")
print("=" * 80)

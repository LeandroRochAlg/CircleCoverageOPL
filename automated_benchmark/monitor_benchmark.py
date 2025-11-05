"""
Monitor de Progresso do Benchmark
Exibe estatísticas em tempo real dos testes em execução
"""

import csv
import time
from pathlib import Path
from datetime import datetime, timedelta

# Ajuste de diretórios para subpasta
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
RESULTS_DIR = PROJECT_DIR / "tests" / "automated_results"
CSV_FILE = RESULTS_DIR / "results_table.csv"

def load_results():
    """Carrega resultados do CSV"""
    if not CSV_FILE.exists():
        return None
    
    results = []
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(row)
    
    return results

def calculate_statistics(results):
    """Calcula estatísticas dos resultados"""
    if not results:
        return None
    
    total_tests = len(results)
    
    # Estatísticas por configuração
    configs = ['Teste1', 'Teste2', 'Teste3', 'Teste4', 'Teste5', 'Teste6']
    config_stats = {}
    
    for config in configs:
        num_key = f'{config}_numCirculos'
        tempo_key = f'{config}_tempo'
        
        successes = 0
        timeouts = 0
        total_time = 0
        total_circles = 0
        
        for result in results:
            if result.get(num_key) and result[num_key] != 'Sem resultado':
                successes += 1
                try:
                    total_circles += int(float(result[num_key]))
                except:
                    pass
            else:
                timeouts += 1
            
            if result.get(tempo_key) and result[tempo_key] != 'Sem resultado':
                try:
                    total_time += float(result[tempo_key])
                except:
                    pass
        
        config_stats[config] = {
            'successes': successes,
            'timeouts': timeouts,
            'success_rate': (successes / total_tests * 100) if total_tests > 0 else 0,
            'avg_time': (total_time / successes) if successes > 0 else 0,
            'avg_circles': (total_circles / successes) if successes > 0 else 0
        }
    
    # Estatísticas gerais
    general_stats = {
        'total_tests': total_tests,
        'total_executions': total_tests * len(configs),
        'config_stats': config_stats
    }
    
    return general_stats

def display_statistics(stats):
    """Exibe estatísticas formatadas"""
    print("\n" + "=" * 100)
    print("ESTATÍSTICAS DO BENCHMARK")
    print("=" * 100)
    print(f"Atualizado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total de testes executados: {stats['total_tests']}")
    print(f"Total de execuções: {stats['total_executions']}")
    print("=" * 100)
    
    print("\n{:<15} {:<12} {:<12} {:<15} {:<15} {:<15}".format(
        "Config", "Sucessos", "Timeouts", "Taxa Sucesso", "Tempo Médio", "Círc. Médio"
    ))
    print("-" * 100)
    
    for config, data in stats['config_stats'].items():
        print("{:<15} {:<12} {:<12} {:<15.1f}% {:<15.2f}s {:<15.1f}".format(
            config,
            data['successes'],
            data['timeouts'],
            data['success_rate'],
            data['avg_time'],
            data['avg_circles']
        ))
    
    print("=" * 100)

def monitor_loop(refresh_seconds=10):
    """Loop de monitoramento"""
    print("=" * 100)
    print("MONITOR DE PROGRESSO DO BENCHMARK")
    print("=" * 100)
    print(f"Arquivo monitorado: {CSV_FILE}")
    print(f"Atualização a cada {refresh_seconds} segundos")
    print("Pressione Ctrl+C para parar")
    print("=" * 100)
    
    try:
        while True:
            # Limpar tela (Windows)
            import os
            os.system('cls' if os.name == 'nt' else 'clear')
            
            # Carregar e exibir resultados
            results = load_results()
            
            if results:
                stats = calculate_statistics(results)
                display_statistics(stats)
            else:
                print("\nAguardando resultados...")
                print(f"Arquivo esperado: {CSV_FILE}")
            
            # Aguardar próxima atualização
            print(f"\nPróxima atualização em {refresh_seconds} segundos... (Ctrl+C para parar)")
            time.sleep(refresh_seconds)
            
    except KeyboardInterrupt:
        print("\n\nMonitor encerrado.")

def show_latest_results(n=5):
    """Exibe os últimos N resultados"""
    results = load_results()
    
    if not results:
        print("Nenhum resultado encontrado.")
        return
    
    print("\n" + "=" * 100)
    print(f"ÚLTIMOS {min(n, len(results))} RESULTADOS")
    print("=" * 100)
    
    for result in results[-n:]:
        print(f"\nTest ID: {result['TestID']}")
        print(f"  Clientes: {result['nClientes']}, Raio: {result['raio']}, "
              f"Cobertura: {result['minCoverage']}, DistMin: {result['minDistCirculos']}")
        
        configs = ['Teste1', 'Teste2', 'Teste3', 'Teste4', 'Teste5', 'Teste6']
        for config in configs:
            num_key = f'{config}_numCirculos'
            tempo_key = f'{config}_tempo'
            
            num = result.get(num_key, '')
            tempo = result.get(tempo_key, '')
            
            if num and num != 'Sem resultado':
                print(f"    {config}: {num} círculos em {tempo}s")
            else:
                print(f"    {config}: Timeout/Erro")
    
    print("=" * 100)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--latest':
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        show_latest_results(n)
    else:
        monitor_loop()

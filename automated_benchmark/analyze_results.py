"""
Analisador de Resultados do Benchmark
Gera relatórios detalhados e gráficos de comparação
"""

import csv
import json
from pathlib import Path
from collections import defaultdict
import statistics

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent  # Diretório raiz do projeto
RESULTS_DIR = PROJECT_DIR / "tests" / "automated_results"
CSV_FILE = RESULTS_DIR / "results_table.csv"

def load_results():
    """Carrega todos os resultados"""
    if not CSV_FILE.exists():
        print(f"Arquivo não encontrado: {CSV_FILE}")
        return None
    
    results = []
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(row)
    
    return results

def analyze_by_config(results):
    """Análise detalhada por configuração"""
    configs = ['Teste1', 'Teste2', 'Teste3', 'Teste4', 'Teste5', 'Teste6']
    
    analysis = {}
    
    for config in configs:
        num_key = f'{config}_numCirculos'
        tempo_key = f'{config}_tempo'
        
        times = []
        circles = []
        successes = 0
        failures = 0
        
        for result in results:
            num = result.get(num_key, '')
            tempo = result.get(tempo_key, '')
            
            if num and num != 'Sem resultado':
                try:
                    circles.append(int(float(num)))
                    successes += 1
                except:
                    failures += 1
            else:
                failures += 1
            
            if tempo and tempo != 'Sem resultado':
                try:
                    times.append(float(tempo))
                except:
                    pass
        
        analysis[config] = {
            'total': len(results),
            'successes': successes,
            'failures': failures,
            'success_rate': (successes / len(results) * 100) if results else 0,
            'times': {
                'min': min(times) if times else 0,
                'max': max(times) if times else 0,
                'mean': statistics.mean(times) if times else 0,
                'median': statistics.median(times) if times else 0,
                'stdev': statistics.stdev(times) if len(times) > 1 else 0
            },
            'circles': {
                'min': min(circles) if circles else 0,
                'max': max(circles) if circles else 0,
                'mean': statistics.mean(circles) if circles else 0,
                'median': statistics.median(circles) if circles else 0,
                'stdev': statistics.stdev(circles) if len(circles) > 1 else 0
            }
        }
    
    return analysis

def analyze_by_instance_size(results):
    """Análise por tamanho de instância"""
    # Categorizar por número de clientes
    categories = {
        'tiny': (0, 20),
        'small': (21, 50),
        'medium': (51, 100),
        'large': (101, 200)
    }
    
    analysis = {cat: defaultdict(list) for cat in categories}
    
    configs = ['Teste1', 'Teste2', 'Teste3', 'Teste4', 'Teste5', 'Teste6']
    
    for result in results:
        try:
            n = int(float(result['nClientes']))
        except:
            continue
        
        # Determinar categoria
        cat = None
        for cat_name, (min_n, max_n) in categories.items():
            if min_n <= n <= max_n:
                cat = cat_name
                break
        
        if not cat:
            continue
        
        # Coletar dados de cada configuração
        for config in configs:
            tempo_key = f'{config}_tempo'
            tempo = result.get(tempo_key, '')
            
            if tempo and tempo != 'Sem resultado':
                try:
                    analysis[cat][config].append(float(tempo))
                except:
                    pass
    
    # Calcular estatísticas
    stats = {}
    for cat, config_data in analysis.items():
        stats[cat] = {}
        for config, times in config_data.items():
            if times:
                stats[cat][config] = {
                    'count': len(times),
                    'mean': statistics.mean(times),
                    'median': statistics.median(times),
                    'min': min(times),
                    'max': max(times)
                }
    
    return stats

def compare_configs(results):
    """Compara configurações lado a lado"""
    configs = ['Teste1', 'Teste2', 'Teste3', 'Teste4', 'Teste5', 'Teste6']
    
    # Para cada teste, comparar configurações
    comparisons = []
    
    for result in results:
        test_id = result['TestID']
        n = result.get('nClientes', '')
        
        comparison = {
            'test_id': test_id,
            'n': n,
            'configs': {}
        }
        
        for config in configs:
            num_key = f'{config}_numCirculos'
            tempo_key = f'{config}_tempo'
            
            num = result.get(num_key, '')
            tempo = result.get(tempo_key, '')
            
            if num and num != 'Sem resultado' and tempo and tempo != 'Sem resultado':
                try:
                    comparison['configs'][config] = {
                        'circles': int(float(num)),
                        'time': float(tempo),
                        'success': True
                    }
                except:
                    comparison['configs'][config] = {'success': False}
            else:
                comparison['configs'][config] = {'success': False}
        
        comparisons.append(comparison)
    
    return comparisons

def generate_report(results):
    """Gera relatório completo"""
    print("\n" + "=" * 100)
    print("RELATÓRIO DETALHADO DE ANÁLISE")
    print("=" * 100)
    
    print(f"\nTotal de testes analisados: {len(results)}")
    
    # Análise por configuração
    print("\n" + "-" * 100)
    print("ANÁLISE POR CONFIGURAÇÃO")
    print("-" * 100)
    
    config_analysis = analyze_by_config(results)
    
    for config, data in config_analysis.items():
        print(f"\n{config}:")
        print(f"  Sucessos: {data['successes']}/{data['total']} ({data['success_rate']:.1f}%)")
        print(f"  Falhas: {data['failures']}")
        
        if data['times']['mean'] > 0:
            print(f"  Tempo (s):")
            print(f"    Mínimo: {data['times']['min']:.2f}")
            print(f"    Máximo: {data['times']['max']:.2f}")
            print(f"    Média: {data['times']['mean']:.2f}")
            print(f"    Mediana: {data['times']['median']:.2f}")
            print(f"    Desvio: {data['times']['stdev']:.2f}")
        
        if data['circles']['mean'] > 0:
            print(f"  Círculos:")
            print(f"    Mínimo: {data['circles']['min']}")
            print(f"    Máximo: {data['circles']['max']}")
            print(f"    Média: {data['circles']['mean']:.1f}")
            print(f"    Mediana: {data['circles']['median']}")
            print(f"    Desvio: {data['circles']['stdev']:.2f}")
    
    # Análise por tamanho de instância
    print("\n" + "-" * 100)
    print("ANÁLISE POR TAMANHO DE INSTÂNCIA")
    print("-" * 100)
    
    size_analysis = analyze_by_instance_size(results)
    
    for category, configs in size_analysis.items():
        print(f"\n{category.upper()}:")
        
        if not configs:
            print("  (sem dados)")
            continue
        
        for config, stats in configs.items():
            print(f"  {config}:")
            print(f"    Testes: {stats['count']}")
            print(f"    Tempo médio: {stats['mean']:.2f}s")
            print(f"    Tempo mediano: {stats['median']:.2f}s")
            print(f"    Range: {stats['min']:.2f}s - {stats['max']:.2f}s")
    
    # Ranking de configurações
    print("\n" + "-" * 100)
    print("RANKING DE CONFIGURAÇÕES (por taxa de sucesso)")
    print("-" * 100)
    
    ranking = sorted(config_analysis.items(), 
                    key=lambda x: x[1]['success_rate'], 
                    reverse=True)
    
    for i, (config, data) in enumerate(ranking, 1):
        print(f"{i}. {config}: {data['success_rate']:.1f}% "
              f"(tempo médio: {data['times']['mean']:.2f}s, "
              f"círculos médios: {data['circles']['mean']:.1f})")
    
    print("\n" + "=" * 100)

def export_summary(results):
    """Exporta resumo em JSON"""
    summary_file = RESULTS_DIR / "analysis_summary.json"
    
    config_analysis = analyze_by_config(results)
    size_analysis = analyze_by_instance_size(results)
    
    summary = {
        'total_tests': len(results),
        'by_config': config_analysis,
        'by_size': size_analysis,
        'timestamp': str(Path(CSV_FILE).stat().st_mtime)
    }
    
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nResumo exportado para: {summary_file}")

def find_best_and_worst(results):
    """Encontra melhores e piores casos"""
    configs = ['Teste1', 'Teste2', 'Teste3', 'Teste4', 'Teste5', 'Teste6']
    
    print("\n" + "=" * 100)
    print("MELHORES E PIORES CASOS")
    print("=" * 100)
    
    for config in configs:
        tempo_key = f'{config}_tempo'
        num_key = f'{config}_numCirculos'
        
        best_time = None
        worst_time = None
        best_circles = None
        worst_circles = None
        
        for result in results:
            tempo = result.get(tempo_key, '')
            num = result.get(num_key, '')
            
            if tempo and tempo != 'Sem resultado':
                try:
                    t = float(tempo)
                    if best_time is None or t < best_time[1]:
                        best_time = (result, t)
                    if worst_time is None or t > worst_time[1]:
                        worst_time = (result, t)
                except:
                    pass
            
            if num and num != 'Sem resultado':
                try:
                    n = int(float(num))
                    if best_circles is None or n < best_circles[1]:
                        best_circles = (result, n)
                    if worst_circles is None or n > worst_circles[1]:
                        worst_circles = (result, n)
                except:
                    pass
        
        print(f"\n{config}:")
        
        if best_time:
            print(f"  Tempo mais rápido: {best_time[1]:.2f}s "
                  f"(Test {best_time[0]['TestID']}, n={best_time[0]['nClientes']})")
        
        if worst_time:
            print(f"  Tempo mais lento: {worst_time[1]:.2f}s "
                  f"(Test {worst_time[0]['TestID']}, n={worst_time[0]['nClientes']})")
        
        if best_circles:
            print(f"  Menos círculos: {best_circles[1]} "
                  f"(Test {best_circles[0]['TestID']}, n={best_circles[0]['nClientes']})")
        
        if worst_circles:
            print(f"  Mais círculos: {worst_circles[1]} "
                  f"(Test {worst_circles[0]['TestID']}, n={worst_circles[0]['nClientes']})")

def main():
    """Função principal"""
    print("=" * 100)
    print("ANALISADOR DE RESULTADOS DO BENCHMARK")
    print("=" * 100)
    
    results = load_results()
    
    if not results:
        print("\nNenhum resultado encontrado para analisar.")
        print(f"Arquivo esperado: {CSV_FILE}")
        return
    
    print(f"\n✓ Carregados {len(results)} testes")
    
    # Gerar relatório completo
    generate_report(results)
    
    # Encontrar melhores e piores casos
    find_best_and_worst(results)
    
    # Exportar resumo
    export_summary(results)
    
    print("\n" + "=" * 100)
    print("ANÁLISE CONCLUÍDA")
    print("=" * 100)

if __name__ == "__main__":
    main()

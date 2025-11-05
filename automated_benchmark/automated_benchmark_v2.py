"""
Script de Benchmark Automatizado - Versão 2
Replica o comportamento do circle_visualizer.py e gera resultados estruturados
"""

import subprocess
import time
import random
import numpy as np
import csv
import os
import json
import signal
import matplotlib
matplotlib.use('Agg')  # Backend sem interface gráfica
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from datetime import datetime
from pathlib import Path

# ==================== CONFIGURAÇÕES ====================

MAX_EXECUTION_TIME = 3600  # 1 hora
TIMEOUT_KILL = 4200  # 1h10min
MAX_N = 200
MIN_COVERAGE_RANGE = (1, 5)

TEST_CONFIGS = ["Teste1", "Teste2", "Teste3", "Teste4", "Teste5", "Teste6"]
REPEATS_PER_INSTANCE = 5  # Executar 5x cada configuração por instância

# Diretórios
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
DAT_FILE = PROJECT_DIR / "circle_coverage.dat"
SOLUTIONS_DIR = PROJECT_DIR / "tests" / "solutions"
TABLES_DIR = PROJECT_DIR / "tests" / "tables"
OPLRUN_PATH = r"C:\Program Files\IBM\ILOG\CPLEX_Studio2211\opl\bin\x64_win64\oplrun.exe"

SOLUTIONS_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)

# ==================== CONFIGURAÇÃO DE CPU ====================

try:
    import psutil
    p = psutil.Process()
    cpu_count = psutil.cpu_count(logical=True)
    if cpu_count and cpu_count > 1:
        available_cpus = list(range(cpu_count - 1))
        p.cpu_affinity(available_cpus)
        print(f"✓ Afinidade de CPU configurada: usando {len(available_cpus)} de {cpu_count} CPUs")
except:
    print("⚠ psutil não disponível, usando todas as CPUs")

# ==================== GERAÇÃO DE DADOS ====================

def generate_clustered_points(n, center_x=0, center_y=0, cluster_radius=150):
    """Gera pontos com distribuição normal"""
    std_dev = cluster_radius / 2.5
    points_x = []
    points_y = []
    
    for i in range(n):
        x = np.random.normal(center_x, std_dev)
        y = np.random.normal(center_y, std_dev)
        x = max(-300, min(300, x))
        y = max(-300, min(300, y))
        points_x.append(round(x, 2))
        points_y.append(round(y, 2))
    
    return points_x, points_y

def calculate_reasonable_parameters(n, points_x, points_y):
    """Calcula parâmetros baseados na distribuição dos pontos"""
    min_x, max_x = min(points_x), max(points_x)
    min_y, max_y = min(points_y), max(points_y)
    
    area_width = max_x - min_x
    area_height = max_y - min_y
    area_diagonal = np.sqrt(area_width**2 + area_height**2)
    
    base_radius = max(10, min(75, area_diagonal / (n ** 0.5) * 1.5))
    r = round(base_radius, 1)
    
    min_coverage = random.randint(*MIN_COVERAGE_RANGE)
    min_dist_circles = round(random.uniform(1.0, min(3.0, r * 0.1)), 2)
    
    return r, min_coverage, min_dist_circles, min_x, max_x, min_y, max_y

def generate_test_data():
    """Gera dados de teste e retorna dict com parâmetros"""
    n = random.randint(10, MAX_N)
    points_x, points_y = generate_clustered_points(n)
    r, min_coverage, min_dist_circles, min_x, max_x, min_y, max_y = calculate_reasonable_parameters(n, points_x, points_y)
    
    return {
        'n': n,
        'radius': r,
        'min_coverage': min_coverage,
        'min_dist_circles': min_dist_circles,
        'points_x': points_x,
        'points_y': points_y,
        'min_x': min_x,
        'max_x': max_x,
        'min_y': min_y,
        'max_y': max_y
    }

def write_dat_file(data):
    """Escreve o arquivo .dat"""
    with open(DAT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"n = {data['n']};\n")
        f.write(f"r = {data['radius']};\n")
        f.write(f"minCoverage = {data['min_coverage']};\n")
        f.write(f"minDistCirculos = {data['min_dist_circles']};\n")
        f.write(f"x = [{', '.join(map(str, data['points_x']))}];\n")
        f.write(f"y = [{', '.join(map(str, data['points_y']))}];\n")

# ==================== EXECUÇÃO E PARSING ====================

def run_test_with_timeout(config_name, timeout=TIMEOUT_KILL):
    """Executa um teste com timeout"""
    oplproject_file = PROJECT_DIR / ".oplproject"
    
    cmd = [
        OPLRUN_PATH,
        ".oplproject",
        "-config", config_name
    ]
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=timeout,
            encoding='utf-8',
            errors='ignore',
            cwd=str(PROJECT_DIR)
        )
        
        execution_time = time.time() - start_time
        
        # DEBUG: Salvar output
        debug_file = PROJECT_DIR / f"debug_output_{config_name}.txt"
        with open(debug_file, 'w', encoding='utf-8', errors='ignore') as f:
            f.write(result.stdout)
        
        # Parse do output
        solution_data = parse_cplex_output(result.stdout)
        
        if solution_data:
            solution_data['execution_time'] = execution_time
            solution_data['status'] = 'SUCCESS'
            solution_data['config'] = config_name
            return solution_data
        else:
            return {
                'status': 'NO_SOLUTION',
                'execution_time': execution_time,
                'config': config_name,
                'num_circles': None
            }
            
    except subprocess.TimeoutExpired:
        execution_time = time.time() - start_time
        return {
            'status': 'TIMEOUT',
            'execution_time': execution_time,
            'config': config_name,
            'num_circles': None
        }
    except Exception as e:
        execution_time = time.time() - start_time
        return {
            'status': 'ERROR',
            'execution_time': execution_time,
            'config': config_name,
            'num_circles': None,
            'error': str(e)
        }

def parse_cplex_output(output):
    """Parse do output do CPLEX"""
    try:
        # Procurar por SOLUTION_DATA
        if "SOLUTION_DATA = {" not in output:
            return None
        
        start_idx = output.find("SOLUTION_DATA = {")
        dict_part = output[start_idx + len("SOLUTION_DATA = "):]
        
        # Encontrar o final do dicionário
        brace_count = 0
        end_idx = 0
        for i, char in enumerate(dict_part):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_idx = i + 1
                    break
        
        dict_str = dict_part[:end_idx]
        solution_data = eval(dict_str)
        
        return solution_data
        
    except Exception as e:
        print(f"  ⚠ Erro ao fazer parse: {e}")
        return None

# ==================== VISUALIZAÇÃO ====================

def create_visualization(solution_data, instance_data, output_dir, timestamp):
    """Cria visualização PNG igual ao circle_visualizer.py"""
    try:
        points = solution_data['points']
        circles = solution_data['circles']
        radius = solution_data['radius']
        
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Desenhar círculos
        for circle in circles:
            circle_patch = Circle(
                (circle[0], circle[1]),
                radius,
                color='lightblue',
                alpha=0.3,
                zorder=1
            )
            ax.add_patch(circle_patch)
            ax.plot(circle[0], circle[1], 'ro', markersize=8, zorder=3)
        
        # Desenhar pontos
        points_x = [p[0] for p in points]
        points_y = [p[1] for p in points]
        ax.scatter(points_x, points_y, c='blue', s=50, zorder=2, alpha=0.7)
        
        # Configurar limites e grid
        all_x = points_x + [c[0] for c in circles]
        all_y = points_y + [c[1] for c in circles]
        
        margin = radius * 1.2
        ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
        ax.set_ylim(min(all_y) - margin, max(all_y) + margin)
        
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_axisbelow(True)
        
        # Título e informações
        ax.set_title(
            f'Cobertura de Círculos - {solution_data["num_circles"]} círculos para {solution_data["num_points"]} pontos',
            fontsize=14,
            fontweight='bold'
        )
        
        info_text = '\n'.join([
            f'Pontos: {solution_data["num_points"]}',
            f'Círculos: {solution_data["num_circles"]}',
            f'Raio: {solution_data["radius"]}',
            f'Cobertura mín.: {solution_data["min_coverage"]}',
            f'Dist. mín. círculos: {solution_data["min_dist_circles"]}',
            f'Tempo exec.: {solution_data["execution_time"]:.2f}s',
            f'Config: {solution_data["config"]}'
        ])
        
        ax.text(
            0.02, 0.98, info_text,
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        )
        
        filename = f"{output_dir}/visualization_{timestamp}.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filename
        
    except Exception as e:
        print(f"  ⚠ Erro ao criar visualização: {e}")
        return None

def save_solution_files(solution_data, instance_data, output_dir, timestamp):
    """Salva arquivos de solução (txt e json)"""
    
    # Arquivo TXT
    txt_file = f"{output_dir}/solution_data_{timestamp}.txt"
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write("=== RESULTADOS DA SOLUÇÃO ===\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Configuração: {solution_data['config']}\n")
        f.write(f"Número de pontos: {solution_data['num_points']}\n")
        f.write(f"Número de círculos: {solution_data['num_circles']}\n")
        f.write(f"Raio dos círculos: {solution_data['radius']}\n")
        f.write(f"Cobertura mínima: {solution_data['min_coverage']}\n")
        f.write(f"Distância mínima entre círculos: {solution_data['min_dist_circles']}\n")
        f.write(f"Tempo de execução: {solution_data['execution_time']:.2f} segundos\n")
        f.write("\n=== PONTOS ===\n")
        for i, point in enumerate(solution_data['points']):
            coverage = solution_data['coverage_per_point'][i]
            f.write(f"Ponto {i+1}: ({point[0]}, {point[1]}) - Cobertura: {coverage}\n")
        f.write("\n=== CÍRCULOS ===\n")
        for i, circle in enumerate(solution_data['circles']):
            f.write(f"Círculo {i+1}: Centro ({circle[0]}, {circle[1]})\n")
    
    # Arquivo JSON
    json_file = f"{output_dir}/solution_data_{timestamp}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(solution_data, f, indent=2)
    
    return txt_file, json_file

# ==================== TABELAS CSV ====================

def update_instances_table(instance_id, instance_data):
    """Atualiza tabela de instâncias"""
    instances_csv = TABLES_DIR / "instances_table.csv"
    
    # Criar ou ler tabela existente
    if instances_csv.exists():
        with open(instances_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    else:
        rows = []
    
    # Adicionar nova instância
    new_row = {
        'instance_id': instance_id,
        'nClientes': instance_data['n'],
        'raio': instance_data['radius'],
        'minDistCirculos': instance_data['min_dist_circles'],
        'minCoverage': instance_data['min_coverage'],
        'minX': instance_data['min_x'],
        'minY': instance_data['min_y'],
        'maxX': instance_data['max_x'],
        'maxY': instance_data['max_y']
    }
    
    rows.append(new_row)
    
    # Escrever tabela
    with open(instances_csv, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['instance_id', 'nClientes', 'raio', 'minDistCirculos', 'minCoverage', 
                     'minX', 'minY', 'maxX', 'maxY']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def update_results_table(instance_id, config_name, result, repeat_num):
    """Atualiza tabela de resultados (formato igual Testes - Página1.csv)"""
    results_csv = TABLES_DIR / "results_table.csv"
    
    # Criar ou ler tabela existente
    if results_csv.exists():
        with open(results_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    else:
        rows = []
    
    # Determinar status e valores
    if result['status'] == 'SUCCESS':
        num_circulos = result['num_circles']
        tempo = f"{result['execution_time']:.2f}"
        visualization = result.get('visualization_file', 'N/A')
    elif result['status'] == 'TIMEOUT':
        num_circulos = 'TIMEOUT'
        tempo = f"{result['execution_time']:.2f}"
        visualization = 'N/A'
    else:
        num_circulos = 'Sem resultado'
        tempo = 'Sem resultado'
        visualization = 'Sem resultado'
    
    # Adicionar resultado
    new_row = {
        'instance_id': instance_id,
        'config': config_name,
        'repeat': repeat_num,
        'numCirculos': num_circulos,
        'tempo': tempo,
        'visualization': visualization,
        'status': result['status']
    }
    
    rows.append(new_row)
    
    # Escrever tabela
    with open(results_csv, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['instance_id', 'config', 'repeat', 'numCirculos', 'tempo', 'visualization', 'status']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

# ==================== LOOP PRINCIPAL ====================

def run_benchmark():
    """Loop principal do benchmark"""
    
    print("=" * 80)
    print("BENCHMARK AUTOMATIZADO - VERSÃO 2")
    print("=" * 80)
    print(f"Diretório do projeto: {PROJECT_DIR}")
    print(f"Diretório de soluções: {SOLUTIONS_DIR}")
    print(f"Diretório de tabelas: {TABLES_DIR}")
    print(f"Timeout por teste: {TIMEOUT_KILL}s")
    print(f"Configurações: {', '.join(TEST_CONFIGS)}")
    print(f"Repetições por instância: {REPEATS_PER_INSTANCE}x cada configuração")
    print("=" * 80)
    print()
    
    instance_counter = 1
    
    try:
        while True:
            timestamp_instance = datetime.now().strftime("%Y%m%d_%H%M%S")
            instance_id = f"Instance_{timestamp_instance}"
            
            print("=" * 80)
            print(f"INSTÂNCIA {instance_counter}: {instance_id}")
            print("=" * 80)
            
            # Gerar dados
            print("\n[1/3] Gerando dados de teste...")
            instance_data = generate_test_data()
            print(f"  - Pontos: {instance_data['n']}")
            print(f"  - Raio: {instance_data['radius']}")
            print(f"  - Cobertura mínima: {instance_data['min_coverage']}")
            print(f"  - Dist. mín. círculos: {instance_data['min_dist_circles']}")
            
            # Escrever .dat
            print("\n[2/3] Escrevendo arquivo .dat...")
            write_dat_file(instance_data)
            print("  ✓ Arquivo atualizado")
            
            # Atualizar tabela de instâncias
            update_instances_table(instance_id, instance_data)
            
            # Executar testes: 5 repetições de cada configuração
            print(f"\n[3/3] Executando testes ({REPEATS_PER_INSTANCE} repetições x {len(TEST_CONFIGS)} configs = {REPEATS_PER_INSTANCE * len(TEST_CONFIGS)} testes)...")
            
            test_num = 0
            for repeat_num in range(1, REPEATS_PER_INSTANCE + 1):
                for config_name in TEST_CONFIGS:
                    test_num += 1
                    print(f"\n  [{test_num}/{REPEATS_PER_INSTANCE * len(TEST_CONFIGS)}] {config_name} (repetição {repeat_num})...")
                    
                    start_time = time.time()
                    result = run_test_with_timeout(config_name)
                    
                    # Se sucesso, salvar arquivos
                    if result['status'] == 'SUCCESS':
                        timestamp_result = datetime.now().strftime("%Y%m%d_%H%M%S")
                        output_dir = SOLUTIONS_DIR / timestamp_result
                        output_dir.mkdir(exist_ok=True)
                        
                        # Adicionar dados da instância ao resultado
                        result['num_points'] = instance_data['n']
                        result['radius'] = instance_data['radius']
                        result['min_coverage'] = instance_data['min_coverage']
                        result['min_dist_circles'] = instance_data['min_dist_circles']
                        
                        # Salvar arquivos
                        txt_file, json_file = save_solution_files(result, instance_data, output_dir, timestamp_result)
                        viz_file = create_visualization(result, instance_data, output_dir, timestamp_result)
                        
                        result['visualization_file'] = viz_file if viz_file else 'ERROR'
                        
                        print(f"      ✓ {result['num_circles']} círculos em {result['execution_time']:.2f}s")
                        print(f"      ✓ Salvos em: {output_dir.name}/")
                    
                    elif result['status'] == 'TIMEOUT':
                        print(f"      ⏱ TIMEOUT após {result['execution_time']:.2f}s")
                    else:
                        print(f"      ✗ {result['status']}: {result.get('error', 'N/A')}")
                    
                    # Atualizar tabela de resultados
                    update_results_table(instance_id, config_name, result, repeat_num)
            
            print(f"\n✓ Instância {instance_counter} concluída!")
            print(f"  Resultados salvos em:")
            print(f"  - {TABLES_DIR / 'instances_table.csv'}")
            print(f"  - {TABLES_DIR / 'results_table.csv'}")
            
            instance_counter += 1
            
            # Aguardar antes da próxima instância
            wait_time = 10
            print(f"\nAguardando {wait_time}s antes da próxima instância...")
            time.sleep(wait_time)
            
    except KeyboardInterrupt:
        print("\n\n" + "=" * 80)
        print("BENCHMARK INTERROMPIDO PELO USUÁRIO")
        print("=" * 80)
        print(f"Total de instâncias testadas: {instance_counter - 1}")
        print("Resultados salvos nas tabelas CSV")

if __name__ == "__main__":
    run_benchmark()

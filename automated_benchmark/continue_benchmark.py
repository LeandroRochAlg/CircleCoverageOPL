"""
Continua o Benchmark de onde parou
Executa apenas as configurações pendentes
"""

import subprocess
import time
import random
import numpy as np
import csv
import os
import json
from datetime import datetime
from pathlib import Path

# ==================== CONFIGURAÇÕES ====================

TIMEOUT_KILL = 3660  # 1h1min
OPTIMAL_TIME_LIMIT = 3600  # 1h - limite para considerar ótimo

# Configurações fixas
FIXED_RADIUS = 40
FIXED_MIN_DIST = 1.5

REPEATS_PER_INSTANCE = 1

TEST_CONFIGS = ["Teste1", "Teste2", "Teste3", "Teste4", "Teste5", "Teste6"]

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
DAT_FILE = PROJECT_DIR / "circle_coverage.dat"
SOLUTIONS_DIR = PROJECT_DIR / "tests" / "solutions"
TABLES_DIR = PROJECT_DIR / "tests" / "tables_v2"
OPLRUN_PATH = r"oplrun"

SOLUTIONS_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)

# CPU Affinity
try:
    import psutil
    p = psutil.Process()
    cpu_count = psutil.cpu_count(logical=True)
    if cpu_count and cpu_count > 1:
        available_cpus = list(range(cpu_count - 1))
        p.cpu_affinity(available_cpus)
        print(f"✓ Afinidade de CPU: {len(available_cpus)} de {cpu_count} CPUs")
except:
    pass

# ==================== CARREGAR DADOS EXISTENTES ====================

def load_existing_results():
    """Carrega resultados já executados"""
    results_csv = TABLES_DIR / "results_table.csv"
    executed = set()
    
    if results_csv.exists():
        with open(results_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                executed.add((row['instance_id'], row['config']))
    
    return executed

def load_existing_instances():
    """Carrega instâncias já criadas"""
    instances_csv = TABLES_DIR / "instances_table.csv"
    instances = {}
    
    if instances_csv.exists():
        with open(instances_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                instances[row['instance_id']] = {
                    'n': int(row['nClientes']),
                    'r': int(row['raio']),
                    'min_coverage': int(row['minCoverage']),
                    'min_dist_circles': float(row['minDistCirculos']),
                    'min_x': int(row['minX']),
                    'max_x': int(row['maxX']),
                    'min_y': int(row['minY']),
                    'max_y': int(row['maxY'])
                }
    
    return instances

def load_points_from_dat(dat_file_path):
    """Extrai os pontos x e y do arquivo .dat"""
    try:
        with open(dat_file_path, 'r') as f:
            content = f.read()
        
        # Extrair x
        x_match = content.split('x = [')[1].split('];')[0]
        x_values = [float(v.strip()) for v in x_match.split(',')]
        
        # Extrair y
        y_match = content.split('y = [')[1].split('];')[0]
        y_values = [float(v.strip()) for v in y_match.split(',')]
        
        return x_values, y_values
    except Exception as e:
        print(f"  ⚠ Erro ao ler pontos do .dat: {e}")
        return None, None

# ==================== GERAÇÃO ====================

BASE_POINTS_X = []
BASE_POINTS_Y = []

def generate_base_points(max_n, cluster_radius=150):
    """Gera todos os pontos necessários de uma vez (até max_n)"""
    global BASE_POINTS_X, BASE_POINTS_Y
    
    std_dev = cluster_radius / 2.5
    BASE_POINTS_X = []
    BASE_POINTS_Y = []
    
    for i in range(max_n):
        x = np.random.normal(0, std_dev)
        y = np.random.normal(0, std_dev)
        x = max(-300, min(300, x))
        y = max(-300, min(300, y))
        BASE_POINTS_X.append(round(x, 2))
        BASE_POINTS_Y.append(round(y, 2))
    
    print(f"  ✓ Gerados {max_n} pontos base")

def get_instance_points(n):
    """Retorna os primeiros n pontos dos pontos base"""
    return BASE_POINTS_X[:n], BASE_POINTS_Y[:n]

def calculate_bounds(points_x, points_y):
    """Calcula os limites da área"""
    min_x = int(min(points_x))
    max_x = int(max(points_x))
    min_y = int(min(points_y))
    max_y = int(max(points_y))
    return min_x, max_x, min_y, max_y

def create_instance(n, k):
    """Cria uma instância com n clientes e cobertura mínima k"""
    points_x, points_y = get_instance_points(n)
    min_x, max_x, min_y, max_y = calculate_bounds(points_x, points_y)
    
    return {
        'n': n,
        'r': FIXED_RADIUS,
        'points_x': points_x,
        'points_y': points_y,
        'min_coverage': k,
        'min_dist_circles': FIXED_MIN_DIST,
        'min_x': min_x,
        'max_x': max_x,
        'min_y': min_y,
        'max_y': max_y
    }

def write_dat(data):
    timestamp = datetime.now().strftime("%d de %b de %Y at %H:%M:%S")
    content = f"""/*********************************************
 * OPL 22.1.1.0 Data
 * Author: Automated Benchmark
 * Creation Date: {timestamp}
 *********************************************/
r = {data['r']};
n = {data['n']};
x = [{', '.join(map(str, data['points_x']))}];
y = [{', '.join(map(str, data['points_y']))}];
minCoverage = {data['min_coverage']};
minDistCirculos = {data['min_dist_circles']};
minX = {data['min_x']};
minY = {data['min_y']};
maxX = {data['max_x']};
maxY = {data['max_y']};
"""
    with open(DAT_FILE, 'w') as f:
        f.write(content)

# ==================== EXECUÇÃO ====================

def run_oplrun(config_name):
    cmd = [OPLRUN_PATH, "-p", str(PROJECT_DIR), config_name]
    start = time.time()
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=TIMEOUT_KILL,
            encoding='utf-8',
            errors='ignore',
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )
        exec_time = time.time() - start
        
        if exec_time > OPTIMAL_TIME_LIMIT:
            return result.stdout, exec_time, 'NOT_OPTIMAL'
        
        return result.stdout, exec_time, 'SUCCESS'
    except subprocess.TimeoutExpired:
        exec_time = time.time() - start
        return '', exec_time, 'TIMEOUT'
    except Exception as e:
        exec_time = time.time() - start
        return f'ERROR: {e}', exec_time, 'ERROR'

def parse_solution(output):
    """Parse do SOLUTION_DATA"""
    try:
        if "SOLUTION_DATA = {" not in output:
            return None
        
        start_idx = output.find("SOLUTION_DATA = {")
        dict_part = output[start_idx + len("SOLUTION_DATA = "):]
        
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
        return eval(dict_str)
    except:
        return None

# ==================== SALVAR RESULTADOS ====================

def save_solution(solution_data, instance_data, timestamp):
    """Salva solução"""
    output_dir = SOLUTIONS_DIR / timestamp
    output_dir.mkdir(exist_ok=True)
    
    # TXT
    txt_file = output_dir / f"solution_data_{timestamp}.txt"
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write("=== RESULTADOS DA SOLUÇÃO ===\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Número de pontos: {solution_data['num_points']}\n")
        f.write(f"Número de círculos: {solution_data['num_circles']}\n")
        f.write(f"Raio dos círculos: {solution_data['radius']}\n")
        f.write(f"Cobertura mínima: {solution_data['min_coverage']}\n")
        f.write(f"Distância mínima entre círculos: {solution_data['min_dist_circles']}\n")
        f.write(f"Tempo de execução: {solution_data['execution_time']:.2f} segundos\n")
    
    # JSON
    json_file = output_dir / f"solution_data_{timestamp}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(solution_data, f, indent=2)
    
    # PNG
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        
        fig, ax = plt.subplots(1, 1, figsize=(12, 10))
        
        points = solution_data['points']
        circles = solution_data['circles']
        radius = solution_data['radius']
        
        points_x = [p[0] for p in points]
        points_y = [p[1] for p in points]
        ax.scatter(points_x, points_y, c='red', s=50, zorder=5, label='Pontos', alpha=0.8)
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(circles)))
        for i, (cx, cy) in enumerate(circles):
            circle_fill = patches.Circle((cx, cy), radius, alpha=0.2, 
                                       facecolor=colors[i], edgecolor='none')
            ax.add_patch(circle_fill)
            
            circle_edge = patches.Circle((cx, cy), radius, fill=False, 
                                       edgecolor=colors[i], linewidth=2)
            ax.add_patch(circle_edge)
            
            ax.scatter([cx], [cy], c='blue', s=100, marker='x', 
                      zorder=6, linewidth=3)
        
        all_x = points_x + [c[0] for c in circles]
        all_y = points_y + [c[1] for c in circles]
        
        margin = max(radius * 1.5, (max(all_x) - min(all_x)) * 0.1)
        ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
        ax.set_ylim(min(all_y) - margin, max(all_y) + margin)
        
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        
        ax.set_title(f'Cobertura de Círculos - {solution_data["num_circles"]} círculos para {solution_data["num_points"]} pontos', 
                    fontsize=14, fontweight='bold')
        
        png_file = output_dir / f"visualization_{timestamp}.png"
        plt.savefig(png_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(png_file.name)
    except Exception as e:
        print(f"  ⚠ Erro ao criar PNG: {e}")
        return None

def update_tables(instance_id, instance_data, config_name, result, repeat_num, visualization):
    """Atualiza tabelas CSV"""
    
    # Tabela de instâncias
    instances_csv = TABLES_DIR / "instances_table.csv"
    if not instances_csv.exists():
        with open(instances_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['instance_id', 'nClientes', 'raio', 'minDistCirculos', 'minCoverage',
                           'minX', 'minY', 'maxX', 'maxY'])
    
    with open(instances_csv, 'r', encoding='utf-8') as f:
        existing = [row[0] for row in csv.reader(f)]
    
    if instance_id not in existing:
        with open(instances_csv, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([instance_id, instance_data['n'], instance_data['r'],
                           instance_data['min_dist_circles'], instance_data['min_coverage'],
                           instance_data['min_x'], instance_data['min_y'],
                           instance_data['max_x'], instance_data['max_y']])
    
    # Tabela de resultados
    results_csv = TABLES_DIR / "results_table.csv"
    if not results_csv.exists():
        with open(results_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['instance_id', 'config', 'repeat', 'numCirculos', 'tempo', 'visualization', 'status'])
    
    with open(results_csv, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        if result['status'] in ['SUCCESS', 'NOT_OPTIMAL'] and result.get('num_circles'):
            writer.writerow([instance_id, config_name, repeat_num,
                           result['num_circles'], f"{result['execution_time']:.2f}",
                           visualization or 'N/A', result['status']])
        elif result['status'] == 'TIMEOUT':
            writer.writerow([instance_id, config_name, repeat_num,
                           'TIMEOUT', f"{result['execution_time']:.2f}", 'N/A', 'TIMEOUT'])
        else:
            writer.writerow([instance_id, config_name, repeat_num,
                           'Sem resultado', 'Sem resultado', 'Sem resultado', result['status']])

# ==================== LOOP PRINCIPAL ====================

def main():
    print("=" * 80)
    print("CONTINUAÇÃO DO BENCHMARK")
    print("=" * 80)
    
    # Carregar estado
    print("\n[CARREGANDO] Estado anterior...")
    existing_results = load_existing_results()
    existing_instances = load_existing_instances()
    print(f"  ✓ {len(existing_results)} execuções já completadas")
    print(f"  ✓ {len(existing_instances)} instâncias já criadas")
    
    # Definir o que falta executar
    pending_tasks = [
        # n128_k3: Teste4, Teste5, Teste6
        ("n128_k3_20251121_010205", 128, 3, ["Teste5", "Teste6"]),
        # n256: todas as configurações
        ("n256_k1", 256, 1, TEST_CONFIGS),
        ("n256_k2", 256, 2, TEST_CONFIGS),
        ("n256_k3", 256, 3, TEST_CONFIGS),
    ]
    
    # Carregar pontos existentes do .dat
    global BASE_POINTS_X, BASE_POINTS_Y
    
    print("\n[SETUP] Carregando pontos do .dat existente...")
    existing_x, existing_y = load_points_from_dat(DAT_FILE)
    
    if existing_x and existing_y:
        BASE_POINTS_X = existing_x
        BASE_POINTS_Y = existing_y
        print(f"  ✓ Carregados {len(BASE_POINTS_X)} pontos existentes")
        
        # Se precisar expandir para 256, gerar os pontos adicionais
        if len(BASE_POINTS_X) < 256:
            print(f"  → Expandindo de {len(BASE_POINTS_X)} para 256 pontos...")
            current_count = len(BASE_POINTS_X)
            for i in range(current_count, 256):
                x = np.random.normal(0, 60)
                y = np.random.normal(0, 60)
                x = max(-300, min(300, x))
                y = max(-300, min(300, y))
                BASE_POINTS_X.append(round(x, 2))
                BASE_POINTS_Y.append(round(y, 2))
            print(f"  ✓ Total de pontos disponíveis: {len(BASE_POINTS_X)}")
    else:
        print("  ⚠ Não foi possível carregar pontos, gerando novos...")
        generate_base_points(256)
    print()
    
    task_counter = 1
    total_tasks = sum(len(configs) for _, _, _, configs in pending_tasks)
    
    try:
        for instance_id, n, k, configs in pending_tasks:
            print("=" * 80)
            print(f"INSTÂNCIA: {instance_id} (n={n}, k={k})")
            print("=" * 80)
            
            # Criar ou recuperar instância
            if instance_id in existing_instances:
                print(f"\n[RECUPERANDO] Instância existente: {instance_id}")
                # Usar os pontos já carregados
                instance_data = create_instance(n, k)
                # Não reescrever o .dat, usar o que já existe
                print(f"  ✓ Usando .dat existente com {n} pontos")
            else:
                print(f"\n[CRIANDO] Nova instância: {instance_id}")
                instance_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                instance_id = f"n{n}_k{k}_{instance_timestamp}"
                instance_data = create_instance(n, k)
                write_dat(instance_data)
                print(f"  ✓ .dat criado com {n} pontos")
            
            # Executar configs pendentes
            for config_name in configs:
                if (instance_id, config_name) in existing_results:
                    print(f"  ⏩ Pulando {config_name} (já executado)")
                    continue
                
                print(f"\n[{task_counter}/{total_tasks}] Executando {config_name}...")
                task_counter += 1
                
                output, exec_time, status = run_oplrun(config_name)
                
                result = {
                    'status': status,
                    'execution_time': exec_time
                }
                
                if status == 'SUCCESS' or status == 'NOT_OPTIMAL':
                    solution_data = parse_solution(output)
                    
                    if solution_data:
                        result['num_circles'] = solution_data['num_circles']
                        # Adicionar tempo de execução ao solution_data
                        solution_data['execution_time'] = exec_time
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        visualization = save_solution(solution_data, instance_data, timestamp)
                        print(f"  ✓ Círculos: {solution_data['num_circles']}")
                        print(f"  ✓ Tempo: {exec_time:.2f}s")
                        print(f"  ✓ Status: {status}")
                    else:
                        visualization = None
                        print(f"  ⚠ Sem solução parseada")
                else:
                    visualization = None
                    print(f"  ⚠ Status: {status} (Tempo: {exec_time:.2f}s)")
                
                update_tables(instance_id, instance_data, config_name, result, 1, visualization)
        
        print("\n" + "=" * 80)
        print("✓ BENCHMARK CONTINUADO COMPLETO!")
        print("=" * 80)
            
    except KeyboardInterrupt:
        print("\n\n" + "=" * 80)
        print("INTERROMPIDO PELO USUÁRIO")
        print("=" * 80)

if __name__ == "__main__":
    main()

"""
Benchmark Automatizado - Corrigido
Executa 5x cada configuração (Teste1-6) para cada instância gerada
Salva no formato igual aos tests/solutions/
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
N_VALUES = [8, 16, 32, 64, 128, 256]  # Número de clientes
K_VALUES = [1, 2, 3]  # Valores de minCoverage
FIXED_RADIUS = 30
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

# ==================== GERAÇÃO ====================

# Armazena os pontos base que serão reutilizados
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
        
        # Verificar se terminou mas não é ótimo (tempo > 3600s)
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
    """Parse do SOLUTION_DATA igual ao circle_visualizer.py"""
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
    """Salva igual aos tests/solutions/TIMESTAMP/"""
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
        f.write("\n=== PONTOS ===\n")
        for i, point in enumerate(solution_data['points']):
            coverage = solution_data['coverage_per_point'][i]
            f.write(f"Ponto {i+1}: ({point[0]}, {point[1]}) - Cobertura: {coverage}\n")
        f.write("\n=== CÍRCULOS ===\n")
        for i, circle in enumerate(solution_data['circles']):
            f.write(f"Círculo {i+1}: Centro ({circle[0]}, {circle[1]})\n")
    
    # JSON
    json_file = output_dir / f"solution_data_{timestamp}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(solution_data, f, indent=2)
    
    # PNG - EXATAMENTE igual ao circle_visualizer.py
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        
        # Configurar figura
        fig, ax = plt.subplots(1, 1, figsize=(12, 10))
        
        # Extrair dados
        points = solution_data['points']
        circles = solution_data['circles']
        radius = solution_data['radius']
        
        # Plotar pontos
        points_x = [p[0] for p in points]
        points_y = [p[1] for p in points]
        ax.scatter(points_x, points_y, c='red', s=50, zorder=5, label='Pontos', alpha=0.8)
        
        # Numerar pontos
        for i, (x, y) in enumerate(points):
            ax.annotate(str(i+1), (x, y), xytext=(5, 5), textcoords='offset points', 
                       fontsize=8, alpha=0.7)
        
        # Plotar círculos
        colors = plt.cm.Set3(np.linspace(0, 1, len(circles)))
        for i, (cx, cy) in enumerate(circles):
            # Círculo preenchido (transparente)
            circle_fill = patches.Circle((cx, cy), radius, alpha=0.2, 
                                       facecolor=colors[i], edgecolor='none')
            ax.add_patch(circle_fill)
            
            # Borda do círculo
            circle_edge = patches.Circle((cx, cy), radius, fill=False, 
                                       edgecolor=colors[i], linewidth=2)
            ax.add_patch(circle_edge)
            
            # Centro do círculo
            ax.scatter([cx], [cy], c='blue', s=100, marker='x', 
                      zorder=6, linewidth=3)
            
            # Numerar círculo
            ax.annotate(f'C{i+1}', (cx, cy), xytext=(10, -10), 
                       textcoords='offset points', fontsize=10, 
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
        
        # Configurar eixos
        all_x = points_x + [c[0] for c in circles]
        all_y = points_y + [c[1] for c in circles]
        
        margin = max(radius * 1.5, (max(all_x) - min(all_x)) * 0.1)
        ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
        ax.set_ylim(min(all_y) - margin, max(all_y) + margin)
        
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        
        # Título
        ax.set_title(f'Cobertura de Círculos - {solution_data["num_circles"]} círculos para {solution_data["num_points"]} pontos', 
                    fontsize=14, fontweight='bold')
        
        # Legenda com informações
        legend_text = [
            f'Pontos: {solution_data["num_points"]}',
            f'Círculos: {solution_data["num_circles"]}',
            f'Raio: {solution_data["radius"]}',
            f'Cobertura mín.: {solution_data["min_coverage"]}',
            f'Dist. mín. círculos: {solution_data["min_dist_circles"]}',
            f'Tempo exec.: {solution_data["execution_time"]:.2f}s'
        ]
        
        # Adicionar legenda como texto no canto
        legend_str = '\n'.join(legend_text)
        ax.text(0.02, 0.98, legend_str, transform=ax.transAxes, 
                verticalalignment='top', fontsize=10,
                bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgray', alpha=0.8))
        
        # Salvar figura
        png_file = output_dir / f"visualization_{timestamp}.png"
        plt.savefig(png_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(png_file.name)
    except Exception as e:
        print(f"  ⚠ Erro ao criar PNG: {e}")
        import traceback
        traceback.print_exc()
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
    
    # Adicionar instância se não existir
    with open(instances_csv, 'r', encoding='utf-8') as f:
        existing = [row[0] for row in csv.reader(f)]
    
    if instance_id not in existing:
        with open(instances_csv, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([instance_id, instance_data['n'], instance_data['r'],
                           instance_data['min_dist_circles'], instance_data['min_coverage'],
                           instance_data['min_x'], instance_data['min_y'],
                           instance_data['max_x'], instance_data['max_y']])
    
    # Tabela de resultados (formato igual à sua)
    results_csv = TABLES_DIR / "results_table.csv"
    if not results_csv.exists():
        with open(results_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['instance_id', 'config', 'repeat', 'numCirculos', 'tempo', 'visualization', 'status'])
    
    with open(results_csv, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        if result['status'] in ['SUCCESS', 'NOT_OPTIMUM'] and result.get('num_circles'):
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
    print("BENCHMARK AUTOMATIZADO - VERSÃO ESTRUTURADA")
    print("=" * 80)
    print(f"Projeto: {PROJECT_DIR}")
    print(f"Solutions: {SOLUTIONS_DIR}")
    print(f"Tabelas: {TABLES_DIR}")
    print(f"Timeout: {TIMEOUT_KILL}s")
    print(f"Limite ótimo: {OPTIMAL_TIME_LIMIT}s")
    print(f"Repetições: {REPEATS_PER_INSTANCE}x cada config")
    print(f"Clientes: {N_VALUES}")
    print(f"Coberturas (k): {K_VALUES}")
    print(f"Raio fixo: {FIXED_RADIUS}")
    print(f"Distância mínima fixa: {FIXED_MIN_DIST}")
    print("=" * 80)
    print()
    
    # Gerar pontos base uma única vez
    print("[SETUP] Gerando pontos base...")
    generate_base_points(max(N_VALUES))
    print()
    
    instance_counter = 1
    total_instances = len(N_VALUES) * len(K_VALUES)
    
    try:
        for n in N_VALUES:
            for k in K_VALUES:
                instance_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                instance_id = f"n{n}_k{k}_{instance_timestamp}"
                
                print("=" * 80)
                print(f"INSTÂNCIA {instance_counter}/{total_instances}: {instance_id}")
                print("=" * 80)
                
                # Criar instância
                print("\n[1/3] Criando instância...")
                instance_data = create_instance(n, k)
                print(f"  - Clientes (n): {instance_data['n']}")
                print(f"  - Cobertura (k): {instance_data['min_coverage']}")
                print(f"  - Raio: {instance_data['r']}")
                print(f"  - MinDist: {instance_data['min_dist_circles']}")
                
                # Escrever .dat
                print("\n[2/3] Escrevendo .dat...")
                write_dat(instance_data)
                print("  ✓ Arquivo atualizado")
                
                # Executar testes
                total_tests = REPEATS_PER_INSTANCE * len(TEST_CONFIGS)
                print(f"\n[3/3] Executando {REPEATS_PER_INSTANCE} x {len(TEST_CONFIGS)} = {total_tests} testes...")
                
                test_num = 0
                for repeat_num in range(1, REPEATS_PER_INSTANCE + 1):
                    for config_name in TEST_CONFIGS:
                        test_num += 1
                        print(f"\n  [{test_num}/{total_tests}] {config_name} (rep {repeat_num})...", end=' ')
                        
                        output, exec_time, status = run_oplrun(config_name)
                        
                        result = {'execution_time': exec_time, 'status': status}
                        visualization = None
                        
                        if status in ['SUCCESS', 'NOT_OPTIMUM']:
                            solution_data = parse_solution(output)
                            
                            if solution_data:
                                # Adicionar dados da instância
                                solution_data['num_points'] = instance_data['n']
                                solution_data['radius'] = instance_data['r']
                                solution_data['min_coverage'] = instance_data['min_coverage']
                                solution_data['min_dist_circles'] = instance_data['min_dist_circles']
                                solution_data['execution_time'] = exec_time
                                
                                # Salvar
                                result_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                visualization = save_solution(solution_data, instance_data, result_timestamp)
                                
                                result['num_circles'] = solution_data['num_circles']
                                
                                if status == 'NOT_OPTIMUM':
                                    print(f"⚠ {solution_data['num_circles']} círculos em {exec_time:.2f}s (NOT_OPTIMUM)")
                                else:
                                    print(f"✓ {solution_data['num_circles']} círculos em {exec_time:.2f}s")
                            else:
                                result['status'] = 'NO_SOLUTION'
                                print(f"✗ NO_SOLUTION em {exec_time:.2f}s")
                        elif status == 'TIMEOUT':
                            print(f"⏱ TIMEOUT após {exec_time:.2f}s")
                        else:
                            print(f"✗ {status}")
                        
                        # Atualizar tabelas
                        update_tables(instance_id, instance_data, config_name, result, repeat_num, visualization)
                
                print(f"\n✓ Instância {instance_counter}/{total_instances} concluída!")
                print(f"  Tabelas: {TABLES_DIR}")
                print(f"  Solutions: {SOLUTIONS_DIR}")
                
                instance_counter += 1
                
                # Pausa entre instâncias (exceto a última)
                if instance_counter <= total_instances:
                    print(f"\nAguardando 5s...")
                    time.sleep(5)
        
        print("\n" + "=" * 80)
        print("✓ BENCHMARK COMPLETO!")
        print("=" * 80)
        print(f"Total de instâncias: {total_instances}")
        print(f"Total de execuções: {total_instances * total_tests}")
        print(f"Tabelas salvas em: {TABLES_DIR}")
        print(f"Soluções salvas em: {SOLUTIONS_DIR}")
            
    except KeyboardInterrupt:
        print("\n\n" + "=" * 80)
        print("INTERROMPIDO PELO USUÁRIO")
        print("=" * 80)
        print(f"Instâncias completadas: {instance_counter - 1}/{total_instances}")

if __name__ == "__main__":
    main()

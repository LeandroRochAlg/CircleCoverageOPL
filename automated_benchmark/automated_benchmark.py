"""
Script de Benchmark Automatizado para Modelos de Cobertura de Círculos
Autor: Sistema Automatizado
Data: 04 de Nov de 2025

Este script executa testes automatizados em loop infinito sem intervenção humana.
"""

import subprocess
import time
import random
import numpy as np
import csv
import os
import signal
import threading
from datetime import datetime
from pathlib import Path

# ==================== CONFIGURAÇÕES ====================

# Configurações de execução
MAX_EXECUTION_TIME = 3600  # 1 hora em segundos
TIMEOUT_KILL = 4200  # 1h10min em segundos (tempo máximo antes de forçar parada)
MAX_N = 200  # Número máximo de pontos
MIN_COVERAGE_RANGE = (1, 5)  # Range para minCoverage
REPEATS_PER_INSTANCE = 5  # Executar 5x cada configuração

# Configurações de teste (Teste1 a Teste6)
TEST_CONFIGS = [
    "Teste1",
    "Teste2", 
    "Teste3",
    "Teste4",
    "Teste5",
    "Teste6"
]

# Diretórios (ajustado para subpasta)
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent  # Diretório raiz do projeto
DAT_FILE = PROJECT_DIR / "circle_coverage.dat"
SOLUTIONS_DIR = PROJECT_DIR / "tests" / "solutions"
TABLES_DIR = PROJECT_DIR / "tests" / "tables"
OPLRUN_PATH = r"C:\Program Files\IBM\ILOG\CPLEX_Studio2211\opl\bin\x64_win64\oplrun.exe"

# Criar diretórios se não existirem
SOLUTIONS_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)

# ==================== GERAÇÃO DE DADOS ====================

def generate_clustered_points(n, center_x=0, center_y=0, cluster_radius=100):
    """
    Gera pontos concentrados em torno de um centro usando distribuição normal
    """
    points_x = []
    points_y = []
    
    # Ajustar o desvio padrão baseado no cluster_radius
    std_dev = cluster_radius / 3  # 99.7% dos pontos ficam dentro de 3*std_dev
    
    for i in range(n):
        x = np.random.normal(center_x, std_dev)
        y = np.random.normal(center_y, std_dev)
        
        # Limitar entre -1000 e +1000
        x = max(-1000, min(1000, x))
        y = max(-1000, min(1000, y))
        
        points_x.append(round(x, 2))
        points_y.append(round(y, 2))
    
    return points_x, points_y

def calculate_reasonable_parameters(n, points_x, points_y):
    """
    Calcula parâmetros razoáveis baseados na distribuição dos pontos
    """
    # Calcular área ocupada pelos pontos
    min_x, max_x = min(points_x), max(points_x)
    min_y, max_y = min(points_y), max(points_y)
    
    area_width = max_x - min_x
    area_height = max_y - min_y
    area_diagonal = np.sqrt(area_width**2 + area_height**2)
    
    # Raio baseado na área e número de pontos
    base_radius = max(3, min(75, area_diagonal / (n * 0.1)))
    r = round(base_radius, 1)
    
    # Cobertura mínima: range definido
    min_coverage = random.randint(*MIN_COVERAGE_RANGE)
    
    # Distância mínima entre círculos: proporcional ao raio
    min_dist_circles = round(random.uniform(0.5, min(3.0, r * 0.3)), 2)
    
    return r, min_coverage, min_dist_circles

def generate_test_data():
    """
    Gera novos dados de teste
    Retorna: dict com os parâmetros gerados
    """
    # Número de pontos
    n = random.randint(5, MAX_N)
    
    # Determinar raio do cluster baseado no número de pontos
    if n <= 20:
        cluster_radius = random.randint(50, 150)
    elif n <= 75:
        cluster_radius = random.randint(75, 200)
    else:
        cluster_radius = random.randint(150, 300)
    
    # Gerar pontos concentrados
    points_x, points_y = generate_clustered_points(n, cluster_radius=cluster_radius)
    
    # Calcular parâmetros razoáveis
    r, min_coverage, min_dist_circles = calculate_reasonable_parameters(n, points_x, points_y)
    
    return {
        'n': n,
        'r': r,
        'points_x': points_x,
        'points_y': points_y,
        'min_coverage': min_coverage,
        'min_dist_circles': min_dist_circles,
        'min_x': int(min(points_x)),
        'min_y': int(min(points_y)),
        'max_x': int(max(points_x)),
        'max_y': int(max(points_y))
    }

def write_dat_file(data):
    """
    Escreve os dados no arquivo .dat
    """
    timestamp = datetime.now().strftime("%d de %b de %Y at %H:%M:%S")
    
    dat_content = f"""/*********************************************
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
        f.write(dat_content)

# ==================== EXECUÇÃO DE TESTES ====================

class TimeoutException(Exception):
    """Exceção lançada quando o tempo limite é excedido"""
    pass

def run_test_with_timeout(config_name, timeout_seconds):
    """
    Executa um teste com limite de tempo
    Retorna: (success, num_circles, execution_time, output)
    """
    cmd = [
        OPLRUN_PATH,
        "-p", str(PROJECT_DIR),
        config_name
    ]
    
    start_time = time.time()
    process = None
    killed = False
    
    try:
        # Iniciar processo com encoding UTF-8 e ignorar erros
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8',
            errors='ignore',
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )
        
        # Aguardar com timeout
        try:
            stdout, stderr = process.communicate(timeout=timeout_seconds)
            execution_time = time.time() - start_time
            
            # Analisar saída para extrair número de círculos
            num_circles = extract_num_circles(stdout)
            
            return True, num_circles, execution_time, stdout
            
        except subprocess.TimeoutExpired:
            # Timeout atingido - matar processo
            killed = True
            try:
                process.kill()
                process.wait(timeout=10)
            except:
                # Se kill() falhar, tentar terminar via taskkill
                try:
                    subprocess.run(['taskkill', '/F', '/T', '/PID', str(process.pid)], 
                                 timeout=10, capture_output=True)
                except:
                    pass
            
            execution_time = time.time() - start_time
            return False, None, execution_time, "TIMEOUT"
            
    except Exception as e:
        execution_time = time.time() - start_time
        return False, None, execution_time, f"ERROR: {str(e)}"
    
    finally:
        # Garantir que o processo foi terminado
        if process and process.poll() is None:
            try:
                process.kill()
            except:
                pass

def extract_num_circles(output):
    """
    Extrai o número de círculos da saída do CPLEX
    """
    try:
        # Procurar por padrões comuns na saída
        lines = output.split('\n')
        
        for line in lines:
            # Padrão: "OBJECTIVE: X"
            if 'OBJECTIVE' in line.upper():
                parts = line.split(':')
                if len(parts) >= 2:
                    try:
                        return int(float(parts[1].strip()))
                    except:
                        pass
            
            # Padrão: "Total de círculos usados: X"
            if 'círculos usados' in line.lower() or 'circulos usados' in line.lower():
                parts = line.split(':')
                if len(parts) >= 2:
                    try:
                        return int(float(parts[1].strip()))
                    except:
                        pass
        
        return None
    except:
        return None

# ==================== GERENCIAMENTO DE RESULTADOS ====================

def save_generation_data(test_id, data_params):
    """
    Salva generation_data.txt como no circle_data_generator.py
    """
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    gen_file = RESULTS_DIR / f"generation_data_{test_id}.txt"
    
    with open(gen_file, 'w', encoding='utf-8') as f:
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Raio: {data_params['r']}\n")
        f.write(f"Número de pontos: {data_params['n']}\n")
        f.write(f"Cobertura mínima: {data_params['min_coverage']}\n")
        f.write(f"Distância mínima entre círculos: {data_params['min_dist_circles']}\n")
        f.write(f"Pontos X: {data_params['points_x']}\n")
        f.write(f"Pontos Y: {data_params['points_y']}\n")

def save_test_result(test_id, config_name, data_params, num_circles, execution_time, success, output):
    """
    Salva resultado de um teste individual
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = RESULTS_DIR / f"result_{test_id}_{config_name}_{timestamp}.txt"
    
    with open(result_file, 'w', encoding='utf-8') as f:
        f.write("=== RESULTADO DO TESTE ===\n")
        f.write(f"Test ID: {test_id}\n")
        f.write(f"Config: {config_name}\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Success: {success}\n")
        f.write(f"Num Circles: {num_circles}\n")
        f.write(f"Execution Time: {execution_time:.2f}s\n")
        f.write("\n=== PARÂMETROS DA INSTÂNCIA ===\n")
        f.write(f"n: {data_params['n']}\n")
        f.write(f"r: {data_params['r']}\n")
        f.write(f"minCoverage: {data_params['min_coverage']}\n")
        f.write(f"minDistCirculos: {data_params['min_dist_circles']}\n")
        f.write("\n=== OUTPUT DO CPLEX ===\n")
        f.write(output if output else "Sem output")

def update_results_table(test_id, config_results, data_params):
    """
    Atualiza a tabela de resultados CSV no formato original do usuário
    """
    csv_file = RESULTS_DIR / "results_table.csv"
    
    # Verificar se arquivo existe
    file_exists = csv_file.exists()
    
    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Escrever cabeçalho se arquivo novo
        if not file_exists:
            header = ['TestID', 'nClientes', 'raio', 'minDistCirculos', 'minCoverage']
            for config in TEST_CONFIGS:
                header.extend([f'{config}_numCirculos', f'{config}_tempo', f'{config}_resultado'])
            writer.writerow(header)
        
        # Preparar linha de dados (formato: TestID,n,r,minDist,minCov,num,tempo,ok,num,tempo,ok,...)
        row = [
            test_id,
            data_params['n'],
            data_params['r'],
            data_params['min_dist_circles'],
            data_params['min_coverage']
        ]
        
        # Adicionar resultados de cada configuração
        for config in TEST_CONFIGS:
            if config in config_results:
                result = config_results[config]
                row.extend([
                    result['num_circles'] if result['num_circles'] is not None else '',
                    f"{result['execution_time']:.2f}",
                    'OK' if result['success'] else 'TIMEOUT'
                ])
            else:
                row.extend(['', '', ''])
        
        writer.writerow(row)

# ==================== LOOP PRINCIPAL ====================

def main_loop():
    """
    Loop principal de execução dos testes
    """
    print("=" * 80)
    print("BENCHMARK AUTOMATIZADO DE COBERTURA DE CÍRCULOS")
    print("=" * 80)
    print(f"Diretório do projeto: {PROJECT_DIR}")
    print(f"Arquivo de dados: {DAT_FILE}")
    print(f"Diretório de resultados: {RESULTS_DIR}")
    print(f"Tempo limite por teste: {MAX_EXECUTION_TIME}s ({MAX_EXECUTION_TIME/60:.1f} min)")
    print(f"Timeout de kill: {TIMEOUT_KILL}s ({TIMEOUT_KILL/60:.1f} min)")
    print(f"Configurações de teste: {', '.join(TEST_CONFIGS)}")
    print("=" * 80)
    print("\nIniciando testes em 5 segundos...")
    print("Pressione Ctrl+C para parar\n")
    time.sleep(5)
    
    test_counter = 0
    
    try:
        while True:
            test_counter += 1
            test_id = f"Test_{test_counter:04d}"
            
            print("\n" + "=" * 80)
            print(f"INICIANDO {test_id}")
            print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 80)
            
            # Gerar novos dados
            print("\n[1/3] Gerando dados de teste...")
            data_params = generate_test_data()
            print(f"  - Pontos: {data_params['n']}")
            print(f"  - Raio: {data_params['r']}")
            print(f"  - Cobertura mínima: {data_params['min_coverage']}")
            print(f"  - Dist. mín. círculos: {data_params['min_dist_circles']}")
            
            # Escrever no arquivo .dat
            print("\n[2/3] Escrevendo arquivo .dat...")
            write_dat_file(data_params)
            print("  ✓ Arquivo atualizado")
            
            # Salvar generation_data
            save_generation_data(test_id, data_params)
            
            # Executar testes: 5 rodadas x 6 configurações = 30 testes por instância
            print("\n[3/3] Executando testes (5 rodadas x 6 configurações)...")
            
            # Estrutura: {config_name: [resultado1, resultado2, ...]}
            all_runs = {config: [] for config in TEST_CONFIGS}
            total_tests = 5 * len(TEST_CONFIGS)
            test_num = 0
            
            for rodada in range(1, 6):  # 5 rodadas
                print(f"\n  === RODADA {rodada}/5 ===")
                
                for i, config_name in enumerate(TEST_CONFIGS, 1):
                    test_num += 1
                    print(f"\n  [{test_num}/{total_tests}] Testando {config_name} (rodada {rodada})...")
                    print(f"      Iniciando em: {datetime.now().strftime('%H:%M:%S')}")
                    
                    success, num_circles, exec_time, output = run_test_with_timeout(
                        config_name, 
                        TIMEOUT_KILL
                    )
                    
                    run_result = {
                        'success': success,
                        'num_circles': num_circles,
                        'execution_time': exec_time,
                        'output': output
                    }
                    
                    all_runs[config_name].append(run_result)
                    
                    # Exibir resultado
                    if success:
                        print(f"      ✓ Concluído: {num_circles} círculos em {exec_time:.2f}s")
                    else:
                        print(f"      ✗ Falhou: {exec_time:.2f}s (TIMEOUT/ERROR)")
                    
                    # Salvar resultado individual
                    result_id = f"{test_id}_R{rodada}"
                    save_test_result(result_id, config_name, data_params, num_circles, exec_time, success, output)
                    
                    # Pequena pausa entre testes
                    time.sleep(2)
            
            # Calcular estatísticas e salvar cada rodada na tabela
            print("\n  Atualizando tabela de resultados...")
            
            for rodada in range(1, 6):
                rodada_id = f"{test_id}_R{rodada}"
                
                # Pegar resultados desta rodada
                config_results = {}
                for config in TEST_CONFIGS:
                    if rodada - 1 < len(all_runs[config]):
                        config_results[config] = all_runs[config][rodada - 1]
                
                update_results_table(rodada_id, config_results, data_params)
            
            print("  ✓ Tabela atualizada (5 rodadas)")
            
            # Resumo do teste
            print(f"\n{'=' * 80}")
            print(f"RESUMO DO {test_id}")
            print(f"{'=' * 80}")
            
            total_success = sum(sum(1 for r in runs if r['success']) for runs in all_runs.values())
            total_time = sum(sum(r['execution_time'] for r in runs) for runs in all_runs.values())
            
            print(f"Testes bem-sucedidos: {total_success}/{total_tests}")
            print(f"Tempo total: {total_time:.2f}s ({total_time/60:.1f} min)")
            
            # Estatísticas por configuração
            print("\nEstatísticas por configuração:")
            for config in TEST_CONFIGS:
                runs = all_runs[config]
                success_count = sum(1 for r in runs if r['success'])
                avg_time = sum(r['execution_time'] for r in runs) / len(runs)
                circles = [r['num_circles'] for r in runs if r['num_circles'] is not None]
                avg_circles = sum(circles) / len(circles) if circles else 0
                
                print(f"  {config}: {success_count}/5 OK, "
                      f"avg {avg_circles:.1f} círculos, "
                      f"avg {avg_time:.1f}s")
            
            print(f"{'=' * 80}")
            
            # Pequena pausa antes do próximo teste
            print("\nAguardando 10 segundos antes do próximo teste...")
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n\n" + "=" * 80)
        print("ENCERRANDO BENCHMARK")
        print("=" * 80)
        print(f"Total de testes executados: {test_counter}")
        print(f"Resultados salvos em: {RESULTS_DIR}")
        print("=" * 80)

# ==================== EXECUÇÃO ====================

if __name__ == "__main__":
    # Configurar afinidade de CPU (deixar 1 núcleo livre)
    try:
        import psutil
        process = psutil.Process()
        cpu_count = psutil.cpu_count()
        
        if cpu_count > 1:
            # Usar todos os CPUs exceto 1
            available_cpus = list(range(cpu_count - 1))
            process.cpu_affinity(available_cpus)
            print(f"✓ Afinidade de CPU configurada: usando {len(available_cpus)} de {cpu_count} CPUs")
        else:
            print("⚠ Apenas 1 CPU disponível - não é possível reservar")
    except ImportError:
        print("⚠ psutil não instalado - não foi possível configurar afinidade de CPU")
        print("  Instale com: pip install psutil")
    except Exception as e:
        print(f"⚠ Erro ao configurar afinidade de CPU: {e}")
    
    # Iniciar loop principal
    main_loop()

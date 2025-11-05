import random
import math
import numpy as np
from datetime import datetime
import os

def generate_clustered_points(n, center_x=0, center_y=0, cluster_radius=100):
    """
    Gera pontos concentrados em torno de um centro usando distribuição normal
    """
    points_x = []
    points_y = []
    
    for i in range(n):
        # Usar distribuição normal para concentrar pontos no centro
        # Ajustar o desvio padrão baseado no cluster_radius
        std_dev = cluster_radius / 3  # 99.7% dos pontos ficam dentro de 3*std_dev
        
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
    area_diagonal = math.sqrt(area_width**2 + area_height**2)
    
    # Raio baseado na área e número de pontos
    # Raio maior para áreas maiores, menor para mais pontos
    base_radius = max(3, min(75, area_diagonal / (n * 0.1)))
    r = round(base_radius, 1)
    
    # Cobertura mínima: mais alta para poucos pontos, mais baixa para muitos
    if n <= 10:
        min_coverage = random.randint(3, 8)
    elif n <= 50:
        min_coverage = random.randint(2, 5)
    elif n <= 200:
        min_coverage = random.randint(1, 3)
    else:
        min_coverage = random.randint(1, 2)
    
    # Distância mínima entre círculos: proporcional ao raio
    min_dist_circles = round(random.uniform(0.5, min(3.0, r * 0.3)), 2)
    
    return r, min_coverage, min_dist_circles

def generate_circle_coverage_data():
    """
    Gera dados para o problema de cobertura de círculos
    """
    print("=== GERADOR DE DADOS PARA COBERTURA DE CÍRCULOS ===")
    
    # Número de pontos
    n = random.randint(5, 500)
    print(f"Número de pontos: {n}")
    
    # Determinar raio do cluster baseado no número de pontos
    # Mais pontos = cluster mais disperso
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
    
    # Criar timestamp único
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Formatação dos dados
    dat_content = f"""/*********************************************
 * OPL 22.1.1.0 Data
 * Author: Python Generator
 * Creation Date: {datetime.now().strftime("%d de %b de %Y at %H:%M:%S")}
 * Instance ID: {timestamp}
 *********************************************/
r = {r};
n = {n};
x = [{', '.join(map(str, points_x))}];
y = [{', '.join(map(str, points_y))}];
minCoverage = {min_coverage};
minDistCirculos = {min_dist_circles};
minX = {int(min(points_x))};
minY = {int(min(points_y))};
maxX = {int(max(points_x))};
maxY = {int(max(points_y))};
"""
    
    print("\n=== DADOS GERADOS ===")
    print(f"Raio dos círculos: {r}")
    print(f"Número de pontos: {n}")
    print(f"Cobertura mínima: {min_coverage}")
    print(f"Distância mínima entre círculos: {min_dist_circles}")
    print(f"Área aproximada dos pontos: {max(points_x) - min(points_x):.1f} x {max(points_y) - min(points_y):.1f}")
    
    print("\n=== DADOS PARA COPIAR NO circle_coverage.dat ===")
    print("=" * 60)
    print(dat_content)
    print("=" * 60)
    
    # Salvar dados de geração para uso posterior
    generation_data = {
        'timestamp': timestamp,
        'r': r,
        'n': n,
        'x': points_x,
        'y': points_y,
        'minCoverage': min_coverage,
        'minDistCirculos': min_dist_circles
    }
    
    # Criar diretório para esta instância
    instance_dir = f"instances/{timestamp}"
    os.makedirs(instance_dir, exist_ok=True)
    
    # Salvar dados de geração
    with open(f"{instance_dir}/generation_data.txt", "w") as f:
        f.write("=== DADOS DE GERAÇÃO ===\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Raio: {r}\n")
        f.write(f"Número de pontos: {n}\n")
        f.write(f"Cobertura mínima: {min_coverage}\n")
        f.write(f"Distância mínima entre círculos: {min_dist_circles}\n")
        f.write(f"Pontos X: {points_x}\n")
        f.write(f"Pontos Y: {points_y}\n")
    
    # Salvar arquivo .dat
    with open(f"{instance_dir}/circle_coverage.dat", "w") as f:
        f.write(dat_content)
    
    print(f"\nArquivos salvos em: {instance_dir}/")
    print("- generation_data.txt: dados de geração")
    print("- circle_coverage.dat: arquivo para usar no CPLEX")
    
    return generation_data

if __name__ == "__main__":
    generate_circle_coverage_data()
    
    print("\n=== PRÓXIMOS PASSOS ===")
    print("1. Copie os dados acima e cole no arquivo circle_coverage.dat")
    print("2. Execute o modelo circle_k_coverage.mod no CPLEX")
    print("3. Copie os resultados e use no visualizador")
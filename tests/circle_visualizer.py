import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from datetime import datetime
import os
import json

def load_generation_data(instance_dir):
    """
    Carrega os dados de geração de uma instância específica
    """
    try:
        with open(f"{instance_dir}/generation_data.txt", "r") as f:
            lines = f.readlines()
            
        data = {}
        for line in lines:
            if "Timestamp:" in line:
                data['timestamp'] = line.split(": ")[1].strip()
            elif "Raio:" in line:
                data['radius'] = float(line.split(": ")[1].strip())
            elif "Número de pontos:" in line:
                data['num_points'] = int(line.split(": ")[1].strip())
            elif "Cobertura mínima:" in line:
                data['min_coverage'] = int(line.split(": ")[1].strip())
            elif "Distância mínima entre círculos:" in line:
                data['min_dist_circles'] = float(line.split(": ")[1].strip())
            elif "Pontos X:" in line:
                x_str = line.split(": ")[1].strip()
                data['points_x'] = eval(x_str)  # Cuidado: usar apenas com dados confiáveis
            elif "Pontos Y:" in line:
                y_str = line.split(": ")[1].strip()
                data['points_y'] = eval(y_str)  # Cuidado: usar apenas com dados confiáveis
                
        return data
    except Exception as e:
        print(f"Erro ao carregar dados de geração: {e}")
        return None

def parse_cplex_results():
    """
    Interface para entrada manual dos dados do CPLEX
    """
    print("=== ENTRADA DE DADOS DO CPLEX ===")
    print("Cole os dados da seção 'DADOS PARA PYTHON' do resultado do CPLEX:")
    print("(Cole tudo entre '======= DADOS PARA PYTHON - INÍCIO =======' e '======= DADOS PARA PYTHON - FIM =======')")
    print()
    
    # Ler entrada do usuário
    lines = []
    print("Cole os dados aqui (termine com uma linha vazia):")
    while True:
        line = input()
        if line.strip() == "":
            break
        lines.append(line)
    
    # Processar entrada
    full_text = "\n".join(lines)
    
    # Extrair o dicionário SOLUTION_DATA
    try:
        # Encontrar início do dicionário
        start_idx = full_text.find("SOLUTION_DATA = {")
        if start_idx == -1:
            print("Erro: Não foi possível encontrar 'SOLUTION_DATA = {'")
            return None
            
        # Extrair só a parte do dicionário
        dict_part = full_text[start_idx + len("SOLUTION_DATA = "):]
        
        # Usar eval para converter (cuidado: usar apenas com dados confiáveis)
        solution_data = eval(dict_part)
        
        # Adicionar tempo de execução (será solicitado separadamente)
        print("\nDigite o tempo de execução (em segundos, ex: 12.5):")
        execution_time = float(input().strip())
        solution_data['execution_time'] = execution_time
        
        return solution_data
        
    except Exception as e:
        print(f"Erro ao processar dados: {e}")
        print("Verifique se você copiou todos os dados corretamente.")
        return None

def create_visualization(solution_data, output_dir):
    """
    Cria visualização dos resultados
    """
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
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/visualization_{timestamp}.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.show()
    
    return filename

def save_complete_results(solution_data, output_dir):
    """
    Salva todos os resultados em arquivos
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Salvar dados da solução
    with open(f"{output_dir}/solution_data_{timestamp}.txt", "w") as f:
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
    
    # Salvar dados em formato JSON para facilitar importação futura
    with open(f"{output_dir}/solution_data_{timestamp}.json", "w") as f:
        json.dump(solution_data, f, indent=2)
    
    print(f"Resultados salvos em {output_dir}/")
    print(f"- solution_data_{timestamp}.txt: dados legíveis")
    print(f"- solution_data_{timestamp}.json: dados em formato JSON")

def main():
    """
    Função principal do visualizador
    """
    print("=== VISUALIZADOR DE RESULTADOS DE COBERTURA DE CÍRCULOS ===")
    print()
    
    # Opções do usuário
    print("Escolha uma opção:")
    print("1. Visualizar resultado novo (inserir dados do CPLEX)")
    print("2. Carregar e visualizar instância existente")
    
    choice = input("Digite sua escolha (1 ou 2): ").strip()
    
    if choice == "1":
        # Novo resultado
        solution_data = parse_cplex_results()
        if solution_data is None:
            print("Erro ao processar dados. Encerrando.")
            return
        
        # Criar diretório para esta solução
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"solutions/{timestamp}"
        os.makedirs(output_dir, exist_ok=True)
        
        # Criar visualização
        print("\nCriando visualização...")
        image_file = create_visualization(solution_data, output_dir)
        print(f"Visualização salva: {image_file}")
        
        # Salvar dados completos
        save_complete_results(solution_data, output_dir)
        
    elif choice == "2":
        # Carregar instância existente
        print("Diretórios disponíveis:")
        dirs = [d for d in os.listdir(".") if os.path.isdir(d) and 
                (d.startswith("instances/") or d.startswith("solutions/"))]
        
        if not dirs:
            print("Nenhum diretório de instância encontrado.")
            return
        
        for i, dir_name in enumerate(dirs, 1):
            print(f"{i}. {dir_name}")
        
        try:
            dir_idx = int(input("Digite o número do diretório: ")) - 1
            selected_dir = dirs[dir_idx]
            
            if selected_dir.startswith("instance_"):
                # Carregar dados de geração, precisa de dados da solução
                print("Esta é uma instância gerada. Você precisa executar o CPLEX primeiro.")
                print("Digite os dados da solução:")
                solution_data = parse_cplex_results()
                if solution_data is None:
                    return
            else:
                # Carregar dados da solução
                json_files = [f for f in os.listdir(selected_dir) if f.endswith('.json')]
                if not json_files:
                    print("Arquivo JSON não encontrado no diretório.")
                    return
                
                with open(f"{selected_dir}/{json_files[0]}", "r") as f:
                    solution_data = json.load(f)
            
            # Criar nova visualização
            print("\nCriando visualização...")
            image_file = create_visualization(solution_data, selected_dir)
            print(f"Nova visualização salva: {image_file}")
            
        except (ValueError, IndexError):
            print("Seleção inválida.")
            return
    
    else:
        print("Opção inválida.")
        return
    
    print("\n=== CONCLUÍDO ===")
    print("Visualização criada com sucesso!")

def analyze_instance_directory():
    """
    Função auxiliar para analisar diretórios de instâncias
    """
    print("\n=== ANÁLISE DE DIRETÓRIOS ===")
    dirs = [d for d in os.listdir(".") if os.path.isdir(d) and 
            (d.startswith("instance_") or d.startswith("solution_"))]
    
    if not dirs:
        print("Nenhum diretório encontrado.")
        return
    
    for dir_name in dirs:
        print(f"\nDiretório: {dir_name}")
        files = os.listdir(dir_name)
        for file in files:
            size = os.path.getsize(f"{dir_name}/{file}")
            print(f"  - {file} ({size} bytes)")

if __name__ == "__main__":
    main()
    
    # Opção para analisar diretórios
    if input("\nDeseja analisar os diretórios existentes? (s/n): ").lower() == 's':
        analyze_instance_directory()
"""
Análise Completa dos Resultados - Circle Coverage Problem
Gera tabelas comparativas e gráficos individuais para análise de desempenho
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

# Configuração de estilo
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9

# Diretórios
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / 'analysis_output'
OUTPUT_DIR.mkdir(exist_ok=True)

# Mapeamento dos métodos
METHOD_NAMES = {
    'Teste1': 'CP Puro',
    'Teste2': 'Heurística 3 + CP',
    'Teste3': 'Heurística 4 + CP',
    'Teste4': 'Âncora + Quebra Entre',
    'Teste5': 'Âncora + Quebra Intra',
    'Teste6': 'Âncora + Quebra Entre+Intra'
}

METHOD_COLORS = {
    'CP Puro': '#e74c3c',
    'Heurística 3 + CP': '#3498db',
    'Heurística 4 + CP': '#2ecc71',
    'Âncora + Quebra Entre': '#f39c12',
    'Âncora + Quebra Intra': '#9b59b6',
    'Âncora + Quebra Entre+Intra': '#1abc9c'
}

def load_data():
    """Carrega e prepara os dados"""
    results = pd.read_csv(BASE_DIR / 'results_table.csv')
    instances = pd.read_csv(BASE_DIR / 'instances_table.csv')
    
    # Mapear nomes dos métodos
    results['method'] = results['config'].map(METHOD_NAMES)
    
    # Converter tempo para numérico (tratar "Sem resultado")
    results['tempo_num'] = pd.to_numeric(results['tempo'], errors='coerce')
    results['numCirculos_num'] = pd.to_numeric(results['numCirculos'], errors='coerce')
    
    # Extrair informações da instância
    results['n'] = results['instance_id'].str.extract(r'n(\d+)_')[0].astype(int)
    results['k'] = results['instance_id'].str.extract(r'_k(\d+)_')[0].astype(int)
    
    # Merge com dados das instâncias
    data = results.merge(instances, on='instance_id', how='left')
    
    return data, instances

def create_comparison_table(data):
    """Cria tabela comparativa completa (18 instâncias x 6 métodos)"""
    
    # Pivot para círculos
    circulos_pivot = data.pivot_table(
        values='numCirculos_num',
        index='instance_id',
        columns='method',
        aggfunc='first'
    )
    
    # Pivot para tempo
    tempo_pivot = data.pivot_table(
        values='tempo_num',
        index='instance_id',
        columns='method',
        aggfunc='first'
    )
    
    # Criar tabela combinada
    table_data = []
    instances = sorted(data['instance_id'].unique())
    
    for inst in instances:
        # Extrair n e k
        n = data[data['instance_id'] == inst]['n'].iloc[0]
        k = data[data['instance_id'] == inst]['k'].iloc[0]
        
        row = {'Instância': f'n={n}, k={k}'}
        
        for method in METHOD_NAMES.values():
            if method in circulos_pivot.columns:
                circ = circulos_pivot.loc[inst, method]
                tempo = tempo_pivot.loc[inst, method]
                
                if pd.notna(circ) and pd.notna(tempo):
                    row[method] = f'{int(circ)} ({tempo:.2f}s)'
                else:
                    row[method] = 'N/A'
            else:
                row[method] = 'N/A'
        
        table_data.append(row)
    
    df_table = pd.DataFrame(table_data)
    
    # Salvar como CSV
    df_table.to_csv(OUTPUT_DIR / 'comparison_table.csv', index=False)
    
    # Criar versão formatada para markdown
    with open(OUTPUT_DIR / 'comparison_table.md', 'w', encoding='utf-8') as f:
        f.write("# Tabela Comparativa de Resultados\n\n")
        f.write(df_table.to_markdown(index=False))
    
    print(f"✓ Tabela comparativa salva em {OUTPUT_DIR / 'comparison_table.csv'}")
    print(f"✓ Tabela Markdown salva em {OUTPUT_DIR / 'comparison_table.md'}")
    
    return df_table

def plot_circles_by_instance(data):
    """Gráfico 1: Número de círculos por instância"""
    
    # Filtrar dados válidos
    valid_data = data[data['numCirculos_num'].notna()].copy()
    
    # Criar label de instância
    valid_data['instance_label'] = valid_data.apply(
        lambda x: f"n={x['n']}\nk={x['k']}", axis=1
    )
    
    # Ordenar por n, depois k
    valid_data = valid_data.sort_values(['n', 'k'])
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Obter instâncias únicas ordenadas
    instances_order = valid_data[['instance_label', 'n', 'k']].drop_duplicates().sort_values(['n', 'k'])
    x_positions = np.arange(len(instances_order))
    
    # Plot para cada método
    width = 0.13
    for i, method in enumerate(METHOD_NAMES.values()):
        method_data = valid_data[valid_data['method'] == method]
        
        # Alinhar com order
        y_values = []
        for _, inst in instances_order.iterrows():
            match = method_data[method_data['instance_label'] == inst['instance_label']]
            if len(match) > 0:
                y_values.append(match['numCirculos_num'].iloc[0])
            else:
                y_values.append(0)
        
        offset = (i - 2.5) * width
        ax.bar(x_positions + offset, y_values, width, 
               label=method, color=METHOD_COLORS[method], alpha=0.8)
    
    ax.set_xlabel('Instância (n=pontos, k=cobertura mínima)', fontweight='bold')
    ax.set_ylabel('Número de Círculos', fontweight='bold')
    ax.set_title('Comparação do Número de Círculos por Instância e Método', 
                 fontweight='bold', pad=20)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(instances_order['instance_label'], rotation=45, ha='right')
    ax.legend(title='Método', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'graph_01_circles_by_instance.png', bbox_inches='tight')
    plt.close()
    
    print(f"✓ Gráfico 1: Círculos por instância salvo")

def plot_time_by_instance(data):
    """Gráfico 2: Tempo de execução por instância"""
    
    valid_data = data[data['tempo_num'].notna()].copy()
    valid_data['instance_label'] = valid_data.apply(
        lambda x: f"n={x['n']}\nk={x['k']}", axis=1
    )
    valid_data = valid_data.sort_values(['n', 'k'])
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    instances_order = valid_data[['instance_label', 'n', 'k']].drop_duplicates().sort_values(['n', 'k'])
    x_positions = np.arange(len(instances_order))
    
    width = 0.13
    for i, method in enumerate(METHOD_NAMES.values()):
        method_data = valid_data[valid_data['method'] == method]
        
        y_values = []
        for _, inst in instances_order.iterrows():
            match = method_data[method_data['instance_label'] == inst['instance_label']]
            if len(match) > 0:
                y_values.append(match['tempo_num'].iloc[0])
            else:
                y_values.append(0)
        
        offset = (i - 2.5) * width
        ax.bar(x_positions + offset, y_values, width, 
               label=method, color=METHOD_COLORS[method], alpha=0.8)
    
    ax.set_xlabel('Instância (n=pontos, k=cobertura mínima)', fontweight='bold')
    ax.set_ylabel('Tempo de Execução (segundos)', fontweight='bold')
    ax.set_title('Comparação do Tempo de Execução por Instância e Método', 
                 fontweight='bold', pad=20)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(instances_order['instance_label'], rotation=45, ha='right')
    ax.set_yscale('log')  # Escala logarítmica para melhor visualização
    ax.legend(title='Método', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(axis='y', alpha=0.3, which='both')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'graph_02_time_by_instance.png', bbox_inches='tight')
    plt.close()
    
    print(f"✓ Gráfico 2: Tempo por instância salvo")

def plot_time_vs_size(data):
    """Gráfico 3: Escalabilidade - Tempo por Instância"""
    
    # Preparar dados: considerar falhas como 3600s
    plot_data = data.copy()
    plot_data['tempo_plot'] = plot_data['tempo_num'].fillna(3600)
    
    # Criar label de instância
    plot_data['instance_label'] = plot_data.apply(
        lambda x: f"n={x['n']}, k={x['k']}", axis=1
    )
    
    # Ordenar por n, depois k
    plot_data = plot_data.sort_values(['n', 'k'])
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Obter instâncias únicas ordenadas
    instances_order = plot_data[['instance_label', 'n', 'k']].drop_duplicates().sort_values(['n', 'k'])
    x_positions = np.arange(len(instances_order))
    
    # Plot para cada método
    for method in METHOD_NAMES.values():
        method_data = plot_data[plot_data['method'] == method]
        
        # Alinhar com ordem das instâncias
        y_values = []
        for _, inst in instances_order.iterrows():
            match = method_data[method_data['instance_label'] == inst['instance_label']]
            if len(match) > 0:
                y_values.append(match['tempo_plot'].iloc[0])
            else:
                y_values.append(np.nan)
        
        ax.plot(x_positions, y_values, 
                marker='o', label=method, color=METHOD_COLORS[method],
                linewidth=2.5, markersize=8, alpha=0.8)
    
    ax.set_xlabel('Instância', fontweight='bold', fontsize=12)
    ax.set_ylabel('Tempo de Execução (segundos)', fontweight='bold', fontsize=12)
    ax.set_title('Tempo de Execução por Instância\n(Falhas consideradas como 3600s)', 
                 fontweight='bold', pad=20, fontsize=13)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(instances_order['instance_label'], rotation=45, ha='right', fontsize=9)
    ax.set_yscale('log')
    ax.legend(title='Método', fontsize=9, loc='upper left')
    ax.grid(True, alpha=0.3, which='both')
    
    # Adicionar linha de referência para timeout
    ax.axhline(y=3600, color='red', linestyle='--', linewidth=1.5, 
               alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'graph_03_scalability_time.png', bbox_inches='tight')
    plt.close()
    
    print(f"✓ Gráfico 3: Escalabilidade salvo")

def plot_circles_vs_coverage(data):
    """Gráfico 4: Círculos vs Nível de Cobertura (k)"""
    
    valid_data = data[data['numCirculos_num'].notna()].copy()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for method in METHOD_NAMES.values():
        method_data = valid_data[valid_data['method'] == method]
        
        # Agrupar por k e calcular média
        grouped = method_data.groupby('k')['numCirculos_num'].mean().reset_index()
        
        ax.plot(grouped['k'], grouped['numCirculos_num'], 
                marker='s', label=method, color=METHOD_COLORS[method],
                linewidth=2, markersize=10, alpha=0.8)
    
    ax.set_xlabel('Nível de Cobertura Mínima (k)', fontweight='bold')
    ax.set_ylabel('Número Médio de Círculos', fontweight='bold')
    ax.set_title('Impacto do Nível de Cobertura no Número de Círculos', 
                 fontweight='bold', pad=20)
    ax.set_xticks([1, 2, 3])
    ax.legend(title='Método')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'graph_04_circles_vs_coverage.png', bbox_inches='tight')
    plt.close()
    
    print(f"✓ Gráfico 4: Círculos vs Cobertura salvo")

def plot_success_rate(data):
    """Gráfico 5: Taxa de Sucesso por Método"""
    
    # Calcular taxa de sucesso
    success_data = []
    
    for method in METHOD_NAMES.values():
        method_data = data[data['method'] == method]
        total = len(method_data)
        success = len(method_data[method_data['status'] == 'SUCCESS'])
        rate = (success / total * 100) if total > 0 else 0
        
        success_data.append({
            'Método': method,
            'Taxa de Sucesso (%)': rate,
            'Sucesso': success,
            'Total': total
        })
    
    df_success = pd.DataFrame(success_data)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bars = ax.bar(df_success['Método'], df_success['Taxa de Sucesso (%)'],
                  color=[METHOD_COLORS[m] for m in df_success['Método']],
                  alpha=0.8, edgecolor='black', linewidth=1.5)
    
    # Adicionar valores nas barras
    for bar, row in zip(bars, df_success.itertuples()):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%\n({row.Sucesso}/{row.Total})',
                ha='center', va='bottom', fontweight='bold')
    
    ax.set_xlabel('Método', fontweight='bold')
    ax.set_ylabel('Taxa de Sucesso (%)', fontweight='bold')
    ax.set_title('Taxa de Sucesso por Método (Soluções Ótimas Encontradas)', 
                 fontweight='bold', pad=20)
    ax.set_ylim(0, 110)
    ax.grid(axis='y', alpha=0.3)
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'graph_05_success_rate.png', bbox_inches='tight')
    plt.close()
    
    print(f"✓ Gráfico 5: Taxa de sucesso salvo")

def plot_speedup_comparison(data):
    """Gráfico 6: Speedup em relação ao Modelo Base"""
    
    valid_data = data[data['tempo_num'].notna()].copy()
    
    # Calcular tempo médio por método
    avg_times = valid_data.groupby('method')['tempo_num'].mean().reset_index()
    avg_times.columns = ['Método', 'Tempo Médio']
    
    # Calcular speedup relativo ao CP Puro
    base_time = avg_times[avg_times['Método'] == 'CP Puro']['Tempo Médio'].iloc[0]
    avg_times['Speedup'] = base_time / avg_times['Tempo Médio']
    
    # Remover CP Puro (speedup = 1)
    speedup_data = avg_times[avg_times['Método'] != 'CP Puro']
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bars = ax.bar(speedup_data['Método'], speedup_data['Speedup'],
                  color=[METHOD_COLORS[m] for m in speedup_data['Método']],
                  alpha=0.8, edgecolor='black', linewidth=1.5)
    
    # Linha de referência em speedup = 1
    ax.axhline(y=1, color='red', linestyle='--', linewidth=2, 
               label='CP Puro (referência)', alpha=0.7)
    
    # Adicionar valores nas barras
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}x',
                ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    ax.set_xlabel('Método', fontweight='bold')
    ax.set_ylabel('Speedup (vezes mais rápido)', fontweight='bold')
    ax.set_title('Speedup Médio em Relação ao CP Puro', 
                 fontweight='bold', pad=20)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'graph_06_speedup.png', bbox_inches='tight')
    plt.close()
    
    print(f"✓ Gráfico 6: Speedup salvo")

def plot_quality_vs_time(data):
    """Gráfico 7: Trade-off Qualidade vs Tempo"""
    
    valid_data = data[(data['tempo_num'].notna()) & (data['numCirculos_num'].notna())].copy()
    
    # Calcular médias por método
    summary = valid_data.groupby('method').agg({
        'numCirculos_num': 'mean',
        'tempo_num': 'mean'
    }).reset_index()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    for _, row in summary.iterrows():
        method = row['method']
        ax.scatter(row['tempo_num'], row['numCirculos_num'], 
                  s=300, color=METHOD_COLORS[method], alpha=0.7,
                  edgecolors='black', linewidth=2, label=method)
        
        # Adicionar label
        ax.annotate(method, 
                   (row['tempo_num'], row['numCirculos_num']),
                   xytext=(10, 10), textcoords='offset points',
                   fontsize=9, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.7))
    
    ax.set_xlabel('Tempo Médio de Execução (segundos)', fontweight='bold')
    ax.set_ylabel('Número Médio de Círculos', fontweight='bold')
    ax.set_title('Trade-off: Qualidade da Solução vs Tempo de Execução', 
                 fontweight='bold', pad=20)
    ax.set_xscale('log')
    ax.grid(True, alpha=0.3, which='both')
    ax.legend(title='Método', loc='best')
    
    # Adicionar anotação explicativa
    ax.text(0.02, 0.98, 'Ideal: Canto inferior esquerdo\n(menos círculos, menos tempo)',
            transform=ax.transAxes, fontsize=9, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'graph_07_quality_vs_time.png', bbox_inches='tight')
    plt.close()
    
    print(f"✓ Gráfico 7: Trade-off qualidade vs tempo salvo")

def plot_boxplot_circles(data):
    """Gráfico 8: Distribuição do número de círculos (boxplot)"""
    
    valid_data = data[data['numCirculos_num'].notna()].copy()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Preparar dados para boxplot
    box_data = [valid_data[valid_data['method'] == method]['numCirculos_num'].values 
                for method in METHOD_NAMES.values()]
    
    bp = ax.boxplot(box_data, labels=METHOD_NAMES.values(), patch_artist=True,
                    showmeans=True, meanline=True)
    
    # Colorir boxes
    for patch, method in zip(bp['boxes'], METHOD_NAMES.values()):
        patch.set_facecolor(METHOD_COLORS[method])
        patch.set_alpha(0.7)
    
    ax.set_xlabel('Método', fontweight='bold')
    ax.set_ylabel('Número de Círculos', fontweight='bold')
    ax.set_title('Distribuição do Número de Círculos por Método', 
                 fontweight='bold', pad=20)
    ax.grid(axis='y', alpha=0.3)
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'graph_08_boxplot_circles.png', bbox_inches='tight')
    plt.close()
    
    print(f"✓ Gráfico 8: Boxplot círculos salvo")

def plot_boxplot_time(data):
    """Gráfico 9: Distribuição do tempo de execução (boxplot)"""
    
    valid_data = data[data['tempo_num'].notna()].copy()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Preparar dados para boxplot
    box_data = [valid_data[valid_data['method'] == method]['tempo_num'].values 
                for method in METHOD_NAMES.values()]
    
    bp = ax.boxplot(box_data, labels=METHOD_NAMES.values(), patch_artist=True,
                    showmeans=True, meanline=True)
    
    # Colorir boxes
    for patch, method in zip(bp['boxes'], METHOD_NAMES.values()):
        patch.set_facecolor(METHOD_COLORS[method])
        patch.set_alpha(0.7)
    
    ax.set_xlabel('Método', fontweight='bold')
    ax.set_ylabel('Tempo de Execução (segundos)', fontweight='bold')
    ax.set_title('Distribuição do Tempo de Execução por Método', 
                 fontweight='bold', pad=20)
    ax.set_yscale('log')
    ax.grid(axis='y', alpha=0.3, which='both')
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'graph_09_boxplot_time.png', bbox_inches='tight')
    plt.close()
    
    print(f"✓ Gráfico 9: Boxplot tempo salvo")

def plot_heatmap_performance(data):
    """Gráfico 10: Heatmap de desempenho (n x k)"""
    
    valid_data = data[data['numCirculos_num'].notna()].copy()
    
    # Criar um heatmap para cada método
    for method in METHOD_NAMES.values():
        method_data = valid_data[valid_data['method'] == method]
        
        # Pivot para criar matriz n x k
        pivot = method_data.pivot_table(
            values='numCirculos_num',
            index='n',
            columns='k',
            aggfunc='mean'
        )
        
        fig, ax = plt.subplots(figsize=(8, 6))
        
        sns.heatmap(pivot, annot=True, fmt='.1f', cmap='YlOrRd', 
                    cbar_kws={'label': 'Número de Círculos'},
                    linewidths=0.5, ax=ax)
        
        ax.set_xlabel('Nível de Cobertura (k)', fontweight='bold')
        ax.set_ylabel('Número de Pontos (n)', fontweight='bold')
        ax.set_title(f'Heatmap de Desempenho - {method}', 
                     fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        # Nome do arquivo sanitizado
        filename = f"graph_10_heatmap_{method.replace(' ', '_').lower()}.png"
        plt.savefig(OUTPUT_DIR / filename, bbox_inches='tight')
        plt.close()
    
    print(f"✓ Gráfico 10: Heatmaps salvos (um por método)")

def plot_gap_from_best(data):
    """Gráfico 11: Gap do melhor resultado por instância"""
    
    # Separar dados válidos e inválidos
    valid_data = data[data['numCirculos_num'].notna()].copy()
    all_data = data.copy()
    
    # Criar label de instância
    all_data['instance_label'] = all_data.apply(
        lambda x: f"n={x['n']}, k={x['k']}", axis=1
    )
    valid_data['instance_label'] = valid_data.apply(
        lambda x: f"n={x['n']}, k={x['k']}", axis=1
    )
    
    # Encontrar o melhor (menor) número de círculos para cada instância
    best_per_instance = valid_data.groupby('instance_label')['numCirculos_num'].min().reset_index()
    best_per_instance.columns = ['instance_label', 'best_circles']
    
    # Merge para adicionar o melhor resultado
    plot_data = valid_data.merge(best_per_instance, on='instance_label')
    
    # Calcular gap: diferença absoluta do melhor
    plot_data['gap'] = plot_data['numCirculos_num'] - plot_data['best_circles']
    
    # Ordenar por n, k
    plot_data = plot_data.sort_values(['n', 'k'])
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Obter instâncias únicas ordenadas
    instances_order = plot_data[['instance_label', 'n', 'k']].drop_duplicates().sort_values(['n', 'k'])
    x_positions = np.arange(len(instances_order))
    
    # Configurar largura das barras
    width = 0.13
    
    # Encontrar o gap máximo para definir altura das barras de "sem solução"
    max_gap = plot_data['gap'].max() if len(plot_data) > 0 else 10
    no_solution_height = max_gap * 1.3  # 30% acima do máximo
    
    # Plot barras agrupadas para cada método
    legend_handles = []
    legend_labels = []
    
    for i, method in enumerate(METHOD_NAMES.values()):
        method_data = plot_data[plot_data['method'] == method]
        
        # Alinhar com ordem das instâncias
        y_values = []
        colors = []
        hatches = []
        
        for _, inst in instances_order.iterrows():
            # Verificar se existe resultado válido
            match_all = all_data[(all_data['instance_label'] == inst['instance_label']) & 
                                 (all_data['method'] == method)]
            match_valid = method_data[method_data['instance_label'] == inst['instance_label']]
            
            if len(match_valid) > 0:
                # Solução encontrada
                y_values.append(match_valid['gap'].iloc[0])
                colors.append(METHOD_COLORS[method])
                hatches.append('')
            elif len(match_all) > 0:
                # Sem solução (numCirculos é NaN)
                y_values.append(no_solution_height)
                colors.append(METHOD_COLORS[method])  # Mesma cor do método
                hatches.append('///')  # Hachura para indicar sem solução
            else:
                # Nenhum dado
                y_values.append(0)
                colors.append(METHOD_COLORS[method])
                hatches.append('')
        
        offset = (i - 2.5) * width
        bars = ax.bar(x_positions + offset, y_values, width,
                      color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)
        
        # Aplicar hachuras
        for bar, hatch in zip(bars, hatches):
            bar.set_hatch(hatch)
        
        # Criar handle personalizado para legenda com cor correta
        from matplotlib.patches import Patch
        legend_handles.append(Patch(facecolor=METHOD_COLORS[method], edgecolor='black', 
                                   linewidth=0.5, alpha=0.8))
        legend_labels.append(method)
    
    # Adicionar legenda para "sem solução" com hachura
    legend_handles.append(Patch(facecolor='gray', edgecolor='black', hatch='///', 
                               linewidth=0.5, alpha=0.8))
    legend_labels.append('Sem solução encontrada')
    
    # Criar legenda com handles personalizados
    ax.legend(legend_handles, legend_labels, title='Método', fontsize=9, loc='upper left')
    
    ax.set_xlabel('Instância', fontweight='bold', fontsize=12)
    ax.set_ylabel('Distância do Melhor Resultado (círculos)', fontweight='bold', fontsize=12)
    ax.set_title('Gap de Qualidade: Distância do Melhor Número de Círculos por Instância\n(Barras hachuradas indicam que nenhuma solução foi encontrada)', 
                 fontweight='bold', pad=20, fontsize=12)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(instances_order['instance_label'], rotation=45, ha='right', fontsize=9)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'graph_11_gap_from_best.png', bbox_inches='tight')
    plt.close()
    
    print(f"✓ Gráfico 11: Gap do melhor resultado salvo")

def generate_summary_statistics(data):
    """Gera estatísticas resumidas"""
    
    valid_circles = data[data['numCirculos_num'].notna()].copy()
    
    # Para tempo, considerar 3600s para execuções sem resultado
    data_with_time = data.copy()
    data_with_time['tempo_total'] = data_with_time['tempo_num'].fillna(3600)
    
    summary = []
    
    for method in METHOD_NAMES.values():
        method_circles = valid_circles[valid_circles['method'] == method]
        method_time = data_with_time[data_with_time['method'] == method]
        
        stats = {
            'Método': method,
            'Círculos Médio': method_circles['numCirculos_num'].mean(),
            'Círculos Mediano': method_circles['numCirculos_num'].median(),
            'Círculos Std': method_circles['numCirculos_num'].std(),
            'Tempo Médio (s)': method_time['tempo_total'].mean(),
            'Tempo Mediano (s)': method_time['tempo_total'].median(),
            'Tempo Std (s)': method_time['tempo_total'].std(),
            'Taxa Sucesso (%)': (len(data[(data['method'] == method) & (data['status'] == 'SUCCESS')]) / 
                                 len(data[data['method'] == method]) * 100)
        }
        
        summary.append(stats)
    
    df_summary = pd.DataFrame(summary)
    df_summary.to_csv(OUTPUT_DIR / 'summary_statistics.csv', index=False)
    
    print(f"✓ Estatísticas resumidas salvas")
    print("\n" + "="*80)
    print("RESUMO ESTATÍSTICO")
    print("="*80)
    print(df_summary.to_string(index=False))
    print("="*80)

def main():
    """Execução principal"""
    print("\n" + "="*80)
    print("ANÁLISE COMPLETA DOS RESULTADOS - CIRCLE COVERAGE PROBLEM")
    print("="*80 + "\n")
    
    # Carregar dados
    print("Carregando dados...")
    data, instances = load_data()
    print(f"✓ {len(data)} resultados carregados de {len(instances)} instâncias\n")
    
    # Criar tabela comparativa
    print("Gerando tabela comparativa...")
    comparison_table = create_comparison_table(data)
    print()
    
    # Gerar todos os gráficos
    print("Gerando gráficos individuais...")
    plot_circles_by_instance(data)
    plot_time_by_instance(data)
    plot_time_vs_size(data)
    plot_circles_vs_coverage(data)
    plot_success_rate(data)
    plot_speedup_comparison(data)
    plot_quality_vs_time(data)
    plot_boxplot_circles(data)
    plot_boxplot_time(data)
    plot_heatmap_performance(data)
    plot_gap_from_best(data)
    print()
    
    # Gerar estatísticas
    print("Gerando estatísticas resumidas...")
    generate_summary_statistics(data)
    print()
    
    print("="*80)
    print(f"ANÁLISE COMPLETA! Todos os arquivos salvos em: {OUTPUT_DIR}")
    print("="*80)
    print("\nArquivos gerados:")
    print("  - comparison_table.csv (tabela 18x6)")
    print("  - comparison_table.md (versão Markdown)")
    print("  - summary_statistics.csv")
    print("  - graph_01_circles_by_instance.png")
    print("  - graph_02_time_by_instance.png")
    print("  - graph_03_scalability_time.png")
    print("  - graph_04_circles_vs_coverage.png")
    print("  - graph_05_success_rate.png")
    print("  - graph_06_speedup.png")
    print("  - graph_07_quality_vs_time.png")
    print("  - graph_08_boxplot_circles.png")
    print("  - graph_09_boxplot_time.png")
    print("  - graph_10_heatmap_*.png (um por método)")
    print("  - graph_11_gap_from_best.png")
    print()

if __name__ == '__main__':
    main()

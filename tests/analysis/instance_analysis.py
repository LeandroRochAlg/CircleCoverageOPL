"""
Análise de Instâncias - Circle Coverage
Analisa características das instâncias e sua relação com dificuldade
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Configurações
SCRIPT_DIR = Path(__file__).parent
TABLES_DIR = SCRIPT_DIR.parent / "tables"
OUTPUT_DIR = SCRIPT_DIR / "results"
OUTPUT_DIR.mkdir(exist_ok=True)

COLORS = {
    'Teste1': '#8DD3C7',
    'Teste2': '#FFFFB3',
    'Teste3': '#BEBADA',
    'Teste4': '#FB8072',
    'Teste5': '#80B1D3',
    'Teste6': '#FDB462',
}

# Carregar dados (com tratamento de erros)
try:
    results_df = pd.read_csv(TABLES_DIR / "results_table.csv", on_bad_lines='skip', encoding='utf-8')
    instances_df = pd.read_csv(TABLES_DIR / "instances_table.csv", on_bad_lines='skip', encoding='utf-8')
except:
    results_df = pd.read_csv(TABLES_DIR / "results_table.csv", engine='python', on_bad_lines='skip')
    instances_df = pd.read_csv(TABLES_DIR / "instances_table.csv", engine='python', on_bad_lines='skip')

# Calcular características adicionais das instâncias
instances_df['area'] = (instances_df['maxX'] - instances_df['minX']) * (instances_df['maxY'] - instances_df['minY'])
instances_df['densidade'] = instances_df['nClientes'] / instances_df['area']
instances_df['raio_normalizado'] = instances_df['raio'] / np.sqrt(instances_df['area'])
instances_df['razao_aspecto'] = (instances_df['maxX'] - instances_df['minX']) / (instances_df['maxY'] - instances_df['minY'])

# Merge com resultados
data = results_df.merge(instances_df, on='instance_id', how='left')
data['tempo_num'] = pd.to_numeric(data['tempo'], errors='coerce')
success_data = data[data['status'] == 'SUCCESS'].copy()

print("=" * 80)
print("ANÁLISE DE INSTÂNCIAS")
print("=" * 80)

# ==================== 1. DISTRIBUIÇÃO DAS CARACTERÍSTICAS ====================
print("\n[1/4] Analisando distribuição das características...")

caracteristicas = ['nClientes', 'raio', 'minDistCirculos', 'minCoverage', 'area', 'densidade']

fig, axes = plt.subplots(2, 3, figsize=(16, 10))
axes = axes.flatten()

for idx, carac in enumerate(caracteristicas):
    ax = axes[idx]
    
    data_plot = instances_df[carac].dropna()
    
    # Histograma
    n, bins, patches = ax.hist(data_plot, bins=20, edgecolor='black', 
                               linewidth=1.5, alpha=0.7, color='skyblue')
    
    # Estatísticas
    media = data_plot.mean()
    mediana = data_plot.median()
    
    ax.axvline(media, color='red', linestyle='--', linewidth=2, label=f'Média: {media:.2f}')
    ax.axvline(mediana, color='green', linestyle='--', linewidth=2, label=f'Mediana: {mediana:.2f}')
    
    ax.set_xlabel(carac, fontsize=11, fontweight='bold')
    ax.set_ylabel('Frequência', fontsize=11, fontweight='bold')
    ax.set_title(f'Distribuição: {carac}', fontsize=12, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(axis='y', alpha=0.3, linestyle='--')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "13_distribuicao_caracteristicas.png", dpi=300, bbox_inches='tight')
plt.close()

# Estatísticas descritivas
desc_stats = instances_df[caracteristicas].describe().T
desc_stats = desc_stats.round(2)
desc_stats.to_csv(OUTPUT_DIR / "13_distribuicao_caracteristicas.csv")
print(f"  ✓ Salvo: 13_distribuicao_caracteristicas.png e .csv")

# ==================== 2. INSTÂNCIAS MAIS DIFÍCEIS ====================
print("\n[2/4] Identificando instâncias mais difíceis...")

# Calcular tempo médio e taxa de falha por instância
dificuldade = data.groupby('instance_id').agg({
    'tempo_num': 'mean',
    'status': lambda x: (x == 'SUCCESS').sum() / len(x) * 100  # Taxa de sucesso
}).reset_index()
dificuldade.columns = ['instance_id', 'tempo_medio', 'taxa_sucesso']

# Merge com características
dificuldade = dificuldade.merge(instances_df, on='instance_id', how='left')

# Top 10 mais difíceis (maior tempo)
top10_tempo = dificuldade.nlargest(10, 'tempo_medio')[
    ['instance_id', 'nClientes', 'raio', 'minCoverage', 'tempo_medio', 'taxa_sucesso']
]
top10_tempo['tempo_medio'] = top10_tempo['tempo_medio'].round(2)
top10_tempo['taxa_sucesso'] = top10_tempo['taxa_sucesso'].round(1)

# Top 10 menor taxa de sucesso
top10_falhas = dificuldade.nsmallest(10, 'taxa_sucesso')[
    ['instance_id', 'nClientes', 'raio', 'minCoverage', 'tempo_medio', 'taxa_sucesso']
]
top10_falhas['tempo_medio'] = top10_falhas['tempo_medio'].round(2)
top10_falhas['taxa_sucesso'] = top10_falhas['taxa_sucesso'].round(1)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

# Gráfico 1: Instâncias com maior tempo
y_pos = np.arange(len(top10_tempo))
bars1 = ax1.barh(y_pos, top10_tempo['tempo_medio'], color='coral', 
                 edgecolor='black', linewidth=1.5, alpha=0.8)

for i, (bar, taxa) in enumerate(zip(bars1, top10_tempo['taxa_sucesso'])):
    width = bar.get_width()
    ax1.text(width, bar.get_y() + bar.get_height()/2, 
            f' {width:.1f}s ({taxa:.0f}%)', 
            ha='left', va='center', fontsize=9, fontweight='bold')

ax1.set_yticks(y_pos)
ax1.set_yticklabels(top10_tempo['instance_id'], fontsize=8)
ax1.set_xlabel('Tempo Médio (segundos)', fontsize=12, fontweight='bold')
ax1.set_title('Top 10 Instâncias com Maior Tempo', fontsize=14, fontweight='bold')
ax1.grid(axis='x', alpha=0.3, linestyle='--')

# Gráfico 2: Instâncias com menor sucesso
y_pos = np.arange(len(top10_falhas))
colors = ['red' if x < 50 else 'orange' if x < 80 else 'lightgreen' 
          for x in top10_falhas['taxa_sucesso']]
bars2 = ax2.barh(y_pos, top10_falhas['taxa_sucesso'], color=colors,
                 edgecolor='black', linewidth=1.5, alpha=0.8)

for bar in bars2:
    width = bar.get_width()
    ax2.text(width, bar.get_y() + bar.get_height()/2, 
            f' {width:.1f}%', 
            ha='left', va='center', fontsize=9, fontweight='bold')

ax2.set_yticks(y_pos)
ax2.set_yticklabels(top10_falhas['instance_id'], fontsize=8)
ax2.set_xlabel('Taxa de Sucesso (%)', fontsize=12, fontweight='bold')
ax2.set_title('Top 10 Instâncias com Menor Taxa de Sucesso', fontsize=14, fontweight='bold')
ax2.axvline(x=50, color='red', linestyle='--', linewidth=2, alpha=0.5)
ax2.grid(axis='x', alpha=0.3, linestyle='--')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "14_instancias_dificeis.png", dpi=300, bbox_inches='tight')
plt.close()

top10_tempo.to_csv(OUTPUT_DIR / "14_instancias_maior_tempo.csv", index=False)
top10_falhas.to_csv(OUTPUT_DIR / "14_instancias_menor_sucesso.csv", index=False)
print(f"  ✓ Salvo: 14_instancias_dificeis.png e .csv")

# ==================== 3. SCATTER: CARACTERÍSTICAS vs TEMPO ====================
print("\n[3/4] Analisando relação características vs tempo...")

# Usar apenas média de tempo por instância (para Teste4 - mais rápido)
tempo_por_inst = success_data[success_data['config'] == 'Teste4'].groupby('instance_id').agg({
    'tempo_num': 'mean',
    'numCirculos_num': 'mean'
}).reset_index()
tempo_por_inst = tempo_por_inst.merge(instances_df, on='instance_id', how='left')

fig, axes = plt.subplots(2, 2, figsize=(14, 12))

# 1. nClientes vs Tempo
ax = axes[0, 0]
scatter = ax.scatter(tempo_por_inst['nClientes'], tempo_por_inst['tempo_num'],
                    c=tempo_por_inst['tempo_num'], cmap='YlOrRd', 
                    s=100, alpha=0.7, edgecolors='black', linewidth=1)
ax.set_xlabel('Número de Clientes (n)', fontsize=11, fontweight='bold')
ax.set_ylabel('Tempo (segundos)', fontsize=11, fontweight='bold')
ax.set_title('Tempo × Número de Clientes', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3, linestyle='--')
ax.set_yscale('log')
plt.colorbar(scatter, ax=ax, label='Tempo (s)')

# 2. Raio vs Tempo
ax = axes[0, 1]
scatter = ax.scatter(tempo_por_inst['raio'], tempo_por_inst['tempo_num'],
                    c=tempo_por_inst['nClientes'], cmap='viridis', 
                    s=100, alpha=0.7, edgecolors='black', linewidth=1)
ax.set_xlabel('Raio', fontsize=11, fontweight='bold')
ax.set_ylabel('Tempo (segundos)', fontsize=11, fontweight='bold')
ax.set_title('Tempo × Raio (cor = n)', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3, linestyle='--')
ax.set_yscale('log')
plt.colorbar(scatter, ax=ax, label='n clientes')

# 3. Densidade vs Tempo
ax = axes[1, 0]
scatter = ax.scatter(tempo_por_inst['densidade'], tempo_por_inst['tempo_num'],
                    c=tempo_por_inst['tempo_num'], cmap='YlOrRd', 
                    s=100, alpha=0.7, edgecolors='black', linewidth=1)
ax.set_xlabel('Densidade (pontos/área)', fontsize=11, fontweight='bold')
ax.set_ylabel('Tempo (segundos)', fontsize=11, fontweight='bold')
ax.set_title('Tempo × Densidade', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3, linestyle='--')
ax.set_yscale('log')
plt.colorbar(scatter, ax=ax, label='Tempo (s)')

# 4. minCoverage vs Tempo
ax = axes[1, 1]
for cov in sorted(tempo_por_inst['minCoverage'].unique()):
    subset = tempo_por_inst[tempo_por_inst['minCoverage'] == cov]
    ax.scatter(subset['nClientes'], subset['tempo_num'],
              label=f'k={int(cov)}', s=100, alpha=0.7, edgecolors='black', linewidth=1)
ax.set_xlabel('Número de Clientes (n)', fontsize=11, fontweight='bold')
ax.set_ylabel('Tempo (segundos)', fontsize=11, fontweight='bold')
ax.set_title('Tempo × n (por minCoverage)', fontsize=12, fontweight='bold')
ax.legend(title='minCoverage', fontsize=9)
ax.grid(True, alpha=0.3, linestyle='--')
ax.set_yscale('log')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "15_caracteristicas_vs_tempo.png", dpi=300, bbox_inches='tight')
plt.close()

print(f"  ✓ Salvo: 15_caracteristicas_vs_tempo.png")

# ==================== 4. PERFIL DE COMPLEXIDADE ====================
print("\n[4/4] Criando perfil de complexidade...")

# Definir classes de dificuldade baseado em tempo médio
dificuldade['classe_dificuldade'] = pd.cut(dificuldade['tempo_medio'], 
                                            bins=[0, 1, 10, 100, float('inf')],
                                            labels=['Fácil', 'Média', 'Difícil', 'Muito Difícil'])

# Contar por classe
perfil = dificuldade.groupby('classe_dificuldade').size().reset_index(name='quantidade')

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Pizza
colors_pizza = ['lightgreen', 'yellow', 'orange', 'red']
wedges, texts, autotexts = ax1.pie(perfil['quantidade'], labels=perfil['classe_dificuldade'],
                                     autopct='%1.1f%%', colors=colors_pizza,
                                     startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'},
                                     wedgeprops={'edgecolor': 'black', 'linewidth': 2})
ax1.set_title('Distribuição de Dificuldade das Instâncias', fontsize=14, fontweight='bold')

# Barras com características médias por classe
carac_por_classe = dificuldade.groupby('classe_dificuldade').agg({
    'nClientes': 'mean',
    'raio': 'mean',
    'densidade': 'mean',
    'minCoverage': 'mean'
}).reset_index()

x = np.arange(len(carac_por_classe))
width = 0.2

bars1 = ax2.bar(x - 1.5*width, carac_por_classe['nClientes']/10, width, 
               label='n/10', color='skyblue', edgecolor='black', linewidth=1.5)
bars2 = ax2.bar(x - 0.5*width, carac_por_classe['raio'], width, 
               label='raio', color='lightcoral', edgecolor='black', linewidth=1.5)
bars3 = ax2.bar(x + 0.5*width, carac_por_classe['densidade']*1000, width, 
               label='densidade×1000', color='lightgreen', edgecolor='black', linewidth=1.5)
bars4 = ax2.bar(x + 1.5*width, carac_por_classe['minCoverage'], width, 
               label='minCoverage', color='gold', edgecolor='black', linewidth=1.5)

ax2.set_ylabel('Valor (normalizado)', fontsize=11, fontweight='bold')
ax2.set_xlabel('Classe de Dificuldade', fontsize=11, fontweight='bold')
ax2.set_title('Características Médias por Classe', fontsize=14, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(carac_por_classe['classe_dificuldade'], fontsize=10)
ax2.legend(fontsize=9)
ax2.grid(axis='y', alpha=0.3, linestyle='--')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "16_perfil_complexidade.png", dpi=300, bbox_inches='tight')
plt.close()

perfil.to_csv(OUTPUT_DIR / "16_perfil_complexidade.csv", index=False)
carac_por_classe.to_csv(OUTPUT_DIR / "16_caracteristicas_por_classe.csv", index=False)
print(f"  ✓ Salvo: 16_perfil_complexidade.png e .csv")

# ==================== RELATÓRIO FINAL ====================
print("\n" + "=" * 80)
print("ANÁLISE DE INSTÂNCIAS COMPLETA")
print("=" * 80)
print(f"\nArquivos salvos em: {OUTPUT_DIR}")
print("\nArquivos gerados:")
print("  13. 13_distribuicao_caracteristicas.png / .csv")
print("  14. 14_instancias_dificeis.png / .csv (maior_tempo e menor_sucesso)")
print("  15. 15_caracteristicas_vs_tempo.png")
print("  16. 16_perfil_complexidade.png / .csv")
print("\n" + "=" * 80)
print("✓ Análise de instâncias concluída!")
print("=" * 80)

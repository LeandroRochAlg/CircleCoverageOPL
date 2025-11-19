"""
Análise Aprimorada - Circle Coverage Benchmark
Foco nas CARACTERÍSTICAS das instâncias, não nos nomes
Médias das repetições para cada configuração
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Configurações
SCRIPT_DIR = Path(__file__).parent
TABLES_DIR = SCRIPT_DIR.parent / "tables"
OUTPUT_DIR = SCRIPT_DIR / "results_v2"
OUTPUT_DIR.mkdir(exist_ok=True)

COLORS = {
    'Teste1': '#8DD3C7', 'Teste2': '#FFFFB3', 'Teste3': '#BEBADA',
    'Teste4': '#FB8072', 'Teste5': '#80B1D3', 'Teste6': '#FDB462',
}

CONFIG_NAMES = {
    'Teste1': 'CP Puro',
    'Teste2': 'Heurística 2.3 + CP',
    'Teste3': 'Heurística 3 + CP',
    'Teste4': 'Heurística K-Coverage',
    'Teste5': 'Modelo Fix Circ v3',
    'Teste6': 'Modelo Fix Circ v4',
}

# Carregar e limpar dados
try:
    results_df = pd.read_csv(TABLES_DIR / "results_table.csv", on_bad_lines='skip', encoding='utf-8')
    instances_df = pd.read_csv(TABLES_DIR / "instances_table.csv", on_bad_lines='skip', encoding='utf-8')
except:
    results_df = pd.read_csv(TABLES_DIR / "results_table.csv", engine='python', on_bad_lines='skip')
    instances_df = pd.read_csv(TABLES_DIR / "instances_table.csv", engine='python', on_bad_lines='skip')

# Renomear colunas para nomes legíveis
instances_df = instances_df.rename(columns={
    'nClientes': 'Número de Clientes',
    'raio': 'Raio',
    'minDistCirculos': 'Distância Mínima entre Círculos',
    'minCoverage': 'Cobertura Mínima (k)',
    'minX': 'X Mínimo', 'maxX': 'X Máximo',
    'minY': 'Y Mínimo', 'maxY': 'Y Máximo'
})

# Calcular características adicionais
instances_df['Área da Região'] = (instances_df['X Máximo'] - instances_df['X Mínimo']) * \
                                  (instances_df['Y Máximo'] - instances_df['Y Mínimo'])
instances_df['Densidade'] = instances_df['Número de Clientes'] / instances_df['Área da Região']
instances_df['Largura'] = instances_df['X Máximo'] - instances_df['X Mínimo']
instances_df['Altura'] = instances_df['Y Máximo'] - instances_df['Y Mínimo']

# Merge
data = results_df.merge(instances_df, on='instance_id', how='left')
data['tempo_num'] = pd.to_numeric(data['tempo'], errors='coerce')
data['numCirculos_num'] = pd.to_numeric(data['numCirculos'], errors='coerce')

# MÉDIA DAS REPETIÇÕES por instância e configuração
data_agregado = data.groupby(['instance_id', 'config']).agg({
    'tempo_num': 'mean',
    'numCirculos_num': 'mean',
    'status': lambda x: 'SUCESSO' if (x == 'SUCCESS').all() else 'FALHA',
    'Número de Clientes': 'first',
    'Raio': 'first',
    'Distância Mínima entre Círculos': 'first',
    'Cobertura Mínima (k)': 'first',
    'Área da Região': 'first',
    'Densidade': 'first',
    'Largura': 'first',
    'Altura': 'first'
}).reset_index()

# Filtrar sucessos
success_data = data_agregado[data_agregado['status'] == 'SUCESSO'].copy()

print("=" * 80)
print("ANÁLISE APRIMORADA - FOCO NAS CARACTERÍSTICAS DAS INSTÂNCIAS")
print("=" * 80)
print(f"Instâncias únicas: {len(instances_df)}")
print(f"Dados agregados (média das repetições): {len(data_agregado)}")
print(f"Sucessos: {len(success_data)}")
print()

# ==================== 1. TABELA MESTRE DAS INSTÂNCIAS ====================
print("\n[1/8] Gerando tabela mestre das instâncias...")

# Calcular estatísticas por instância (média entre todas configs)
tabela_instancias = success_data.groupby('instance_id').agg({
    'Número de Clientes': 'first',
    'Raio': 'first',
    'Distância Mínima entre Círculos': 'first',
    'Cobertura Mínima (k)': 'first',
    'Densidade': 'first',
    'Área da Região': 'first',
    'tempo_num': 'mean',  # Média entre todas configs
    'numCirculos_num': 'mean'
}).reset_index()

tabela_instancias = tabela_instancias.sort_values('Número de Clientes')
tabela_instancias['Tempo Médio (s)'] = tabela_instancias['tempo_num'].round(2)
tabela_instancias['Círculos Médios'] = tabela_instancias['numCirculos_num'].round(1)

# Classificar dificuldade
tabela_instancias['Classe de Dificuldade'] = pd.cut(
    tabela_instancias['tempo_num'],
    bins=[0, 1, 10, 100, float('inf')],
    labels=['Fácil', 'Média', 'Difícil', 'Muito Difícil']
)

# Salvar tabela completa
tabela_export = tabela_instancias[[
    'Número de Clientes', 'Raio', 'Distância Mínima entre Círculos',
    'Cobertura Mínima (k)', 'Densidade', 'Área da Região',
    'Tempo Médio (s)', 'Círculos Médios', 'Classe de Dificuldade'
]].round(3)

tabela_export.to_csv(OUTPUT_DIR / "TABELA_MESTRE_INSTANCIAS.csv", index=False)
print(f"  ✓ Tabela mestre salva: {len(tabela_export)} instâncias")
print(tabela_export.head(10).to_string(index=False))

# ==================== 2. PERFIL DAS INSTÂNCIAS POR TAMANHO ====================
print("\n\n[2/8] Gerando perfil por tamanho...")

# Criar faixas de tamanho
tabela_instancias['Faixa de Tamanho'] = pd.cut(
    tabela_instancias['Número de Clientes'],
    bins=[0, 25, 50, 100, 200, 500],
    labels=['Pequena (≤25)', 'Média (26-50)', 'Grande (51-100)', 'Muito Grande (101-200)', 'Extra Grande (>200)']
)

perfil_por_tamanho = tabela_instancias.groupby('Faixa de Tamanho').agg({
    'Número de Clientes': ['count', 'mean', 'min', 'max'],
    'Raio': 'mean',
    'Distância Mínima entre Círculos': 'mean',
    'Cobertura Mínima (k)': 'mean',
    'Densidade': 'mean',
    'Tempo Médio (s)': ['mean', 'median', 'min', 'max'],
    'Círculos Médios': 'mean'
}).round(2)

perfil_por_tamanho.columns = ['_'.join(col).strip() for col in perfil_por_tamanho.columns.values]
perfil_por_tamanho = perfil_por_tamanho.reset_index()

# Visualização
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# 1. Quantidade por faixa
ax = axes[0, 0]
bars = ax.bar(range(len(perfil_por_tamanho)), perfil_por_tamanho['Número de Clientes_count'],
              color='skyblue', edgecolor='black', linewidth=2, alpha=0.8)
for i, (bar, val) in enumerate(zip(bars, perfil_por_tamanho['Número de Clientes_count'])):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), 
            f'{int(val)}\ninstâncias', ha='center', va='bottom', fontweight='bold', fontsize=11)
ax.set_xticks(range(len(perfil_por_tamanho)))
ax.set_xticklabels(perfil_por_tamanho['Faixa de Tamanho'], rotation=15, ha='right')
ax.set_ylabel('Quantidade de Instâncias', fontsize=12, fontweight='bold')
ax.set_title('Distribuição de Instâncias por Tamanho', fontsize=14, fontweight='bold', pad=15)
ax.grid(axis='y', alpha=0.3)

# 2. Características médias por faixa
ax = axes[0, 1]
x = np.arange(len(perfil_por_tamanho))
width = 0.2
ax.bar(x - width, perfil_por_tamanho['Raio_mean'], width, label='Raio', 
       color='lightcoral', edgecolor='black', linewidth=1.5)
ax.bar(x, perfil_por_tamanho['Distância Mínima entre Círculos_mean'], width, 
       label='Distância Mín.', color='lightgreen', edgecolor='black', linewidth=1.5)
ax.bar(x + width, perfil_por_tamanho['Cobertura Mínima (k)_mean'], width, 
       label='Cobertura k', color='gold', edgecolor='black', linewidth=1.5)
ax.set_xticks(x)
ax.set_xticklabels(perfil_por_tamanho['Faixa de Tamanho'], rotation=15, ha='right')
ax.set_ylabel('Valor Médio', fontsize=12, fontweight='bold')
ax.set_title('Características Médias por Faixa de Tamanho', fontsize=14, fontweight='bold', pad=15)
ax.legend(fontsize=10)
ax.grid(axis='y', alpha=0.3)

# 3. Tempo por faixa
ax = axes[1, 0]
ax.bar(range(len(perfil_por_tamanho)), perfil_por_tamanho['Tempo Médio (s)_mean'],
       color='orange', edgecolor='black', linewidth=2, alpha=0.8)
for i, val in enumerate(perfil_por_tamanho['Tempo Médio (s)_mean']):
    ax.text(i, val, f'{val:.1f}s', ha='center', va='bottom', fontweight='bold', fontsize=10)
ax.set_xticks(range(len(perfil_por_tamanho)))
ax.set_xticklabels(perfil_por_tamanho['Faixa de Tamanho'], rotation=15, ha='right')
ax.set_ylabel('Tempo Médio (segundos)', fontsize=12, fontweight='bold')
ax.set_title('Tempo de Execução por Faixa de Tamanho', fontsize=14, fontweight='bold', pad=15)
ax.set_yscale('log')
ax.grid(axis='y', alpha=0.3)

# 4. Densidade vs tempo
ax = axes[1, 1]
scatter = ax.scatter(tabela_instancias['Densidade'], tabela_instancias['Tempo Médio (s)'],
                    c=tabela_instancias['Número de Clientes'], s=100, 
                    cmap='viridis', alpha=0.7, edgecolors='black', linewidth=1)
ax.set_xlabel('Densidade (clientes/área)', fontsize=12, fontweight='bold')
ax.set_ylabel('Tempo Médio (segundos)', fontsize=12, fontweight='bold')
ax.set_title('Densidade × Tempo (cor = nº clientes)', fontsize=14, fontweight='bold', pad=15)
ax.set_yscale('log')
ax.grid(True, alpha=0.3)
plt.colorbar(scatter, ax=ax, label='Nº Clientes')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "01_PERFIL_POR_TAMANHO.png", dpi=300, bbox_inches='tight')
plt.close()

perfil_por_tamanho.to_csv(OUTPUT_DIR / "01_PERFIL_POR_TAMANHO.csv", index=False)
print(f"  ✓ Salvo: 01_PERFIL_POR_TAMANHO.png e .csv")

# ==================== 3. DESEMPENHO POR CARACTERÍSTICAS ====================
print("\n[3/8] Analisando desempenho por características...")

fig, axes = plt.subplots(2, 3, figsize=(18, 12))

caracteristicas = [
    ('Número de Clientes', 'Número de Clientes'),
    ('Raio', 'Raio dos Círculos'),
    ('Distância Mínima entre Círculos', 'Distância Mínima entre Círculos'),
    ('Cobertura Mínima (k)', 'Cobertura Mínima (k)'),
    ('Densidade', 'Densidade (clientes/área)'),
    ('Área da Região', 'Área da Região')
]

for idx, (col, titulo) in enumerate(caracteristicas):
    ax = axes[idx // 3, idx % 3]
    
    # Agrupar por config
    for cfg in sorted(success_data['config'].unique()):
        cfg_data = success_data[success_data['config'] == cfg]
        ax.scatter(cfg_data[col], cfg_data['tempo_num'], 
                  label=CONFIG_NAMES.get(cfg, cfg), alpha=0.6, s=60,
                  color=COLORS[cfg], edgecolors='black', linewidth=0.5)
    
    ax.set_xlabel(titulo, fontsize=11, fontweight='bold')
    ax.set_ylabel('Tempo (s)', fontsize=11, fontweight='bold')
    ax.set_title(f'Tempo × {titulo}', fontsize=12, fontweight='bold')
    ax.set_yscale('log')
    ax.grid(True, alpha=0.3)
    if idx == 0:
        ax.legend(fontsize=8, loc='upper left')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "02_DESEMPENHO_POR_CARACTERISTICAS.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"  ✓ Salvo: 02_DESEMPENHO_POR_CARACTERISTICAS.png")

# ==================== 4. COMPARAÇÃO DE CONFIGURAÇÕES POR CARACTERÍSTICA ====================
print("\n[4/8] Comparando configurações por características...")

# Para cada faixa de tamanho, mostrar desempenho das configs
success_data['Faixa de Tamanho'] = pd.cut(
    success_data['Número de Clientes'],
    bins=[0, 25, 50, 100, 200, 500],
    labels=['≤25', '26-50', '51-100', '101-200', '>200']
)

comp_por_faixa = success_data.groupby(['Faixa de Tamanho', 'config']).agg({
    'tempo_num': 'mean',
    'numCirculos_num': 'mean'
}).reset_index()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Tempo por faixa e config
faixas = sorted([f for f in comp_por_faixa['Faixa de Tamanho'].unique() if pd.notna(f)])
x = np.arange(len(faixas))
width = 0.13

for i, cfg in enumerate(sorted(comp_por_faixa['config'].unique())):
    cfg_data = comp_por_faixa[comp_por_faixa['config'] == cfg]
    valores = [cfg_data[cfg_data['Faixa de Tamanho'] == f]['tempo_num'].values[0] 
               if len(cfg_data[cfg_data['Faixa de Tamanho'] == f]) > 0 else 0 
               for f in faixas]
    ax1.bar(x + i*width, valores, width, label=CONFIG_NAMES.get(cfg, cfg),
           color=COLORS[cfg], edgecolor='black', linewidth=1.5, alpha=0.8)

ax1.set_xlabel('Faixa de Número de Clientes', fontsize=12, fontweight='bold')
ax1.set_ylabel('Tempo Médio (segundos)', fontsize=12, fontweight='bold')
ax1.set_title('Tempo por Faixa de Tamanho e Configuração', fontsize=14, fontweight='bold', pad=15)
ax1.set_xticks(x + width * 2.5)
ax1.set_xticklabels(faixas)
ax1.legend(fontsize=9, loc='upper left')
ax1.set_yscale('log')
ax1.grid(axis='y', alpha=0.3)

# Círculos por faixa e config
for i, cfg in enumerate(sorted(comp_por_faixa['config'].unique())):
    cfg_data = comp_por_faixa[comp_por_faixa['config'] == cfg]
    valores = [cfg_data[cfg_data['Faixa de Tamanho'] == f]['numCirculos_num'].values[0] 
               if len(cfg_data[cfg_data['Faixa de Tamanho'] == f]) > 0 else 0 
               for f in faixas]
    ax2.bar(x + i*width, valores, width, label=CONFIG_NAMES.get(cfg, cfg),
           color=COLORS[cfg], edgecolor='black', linewidth=1.5, alpha=0.8)

ax2.set_xlabel('Faixa de Número de Clientes', fontsize=12, fontweight='bold')
ax2.set_ylabel('Número Médio de Círculos', fontsize=12, fontweight='bold')
ax2.set_title('Qualidade por Faixa de Tamanho e Configuração', fontsize=14, fontweight='bold', pad=15)
ax2.set_xticks(x + width * 2.5)
ax2.set_xticklabels(faixas)
ax2.legend(fontsize=9, loc='upper left')
ax2.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "03_COMPARACAO_POR_FAIXA.png", dpi=300, bbox_inches='tight')
plt.close()

comp_por_faixa.to_csv(OUTPUT_DIR / "03_COMPARACAO_POR_FAIXA.csv", index=False)
print(f"  ✓ Salvo: 03_COMPARACAO_POR_FAIXA.png e .csv")

# ==================== 5. TOP INSTÂNCIAS DESAFIADORAS (COM CARACTERÍSTICAS) ====================
print("\n[5/8] Identificando instâncias mais desafiadoras...")

# Top 15 por tempo
top_dificeis = tabela_instancias.nlargest(15, 'Tempo Médio (s)')[[
    'Número de Clientes', 'Raio', 'Distância Mínima entre Círculos',
    'Cobertura Mínima (k)', 'Densidade', 'Tempo Médio (s)', 'Círculos Médios'
]].round(2)

fig, ax = plt.subplots(figsize=(14, 8))

# Criar descrição legível para cada instância
labels = []
for _, row in top_dificeis.iterrows():
    label = f"n={int(row['Número de Clientes'])}, r={row['Raio']:.1f}, k={int(row['Cobertura Mínima (k)'])}"
    labels.append(label)

y_pos = np.arange(len(labels))
colors_bars = plt.cm.Reds(np.linspace(0.4, 0.9, len(labels)))

bars = ax.barh(y_pos, top_dificeis['Tempo Médio (s)'], color=colors_bars, 
               edgecolor='black', linewidth=1.5, alpha=0.8)

for i, (bar, row) in enumerate(zip(bars, top_dificeis.iterrows())):
    width = bar.get_width()
    _, data = row
    ax.text(width + width*0.05, bar.get_y() + bar.get_height()/2,
            f"{width:.1f}s | {data['Círculos Médios']:.0f} círc. | dens={data['Densidade']:.4f}",
            ha='left', va='center', fontsize=9, fontweight='bold')

ax.set_yticks(y_pos)
ax.set_yticklabels(labels, fontsize=10)
ax.set_xlabel('Tempo Médio (segundos)', fontsize=12, fontweight='bold')
ax.set_title('Top 15 Instâncias Mais Desafiadoras (por características)', 
             fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "04_TOP_INSTANCIAS_DIFICEIS.png", dpi=300, bbox_inches='tight')
plt.close()

top_dificeis.to_csv(OUTPUT_DIR / "04_TOP_INSTANCIAS_DIFICEIS.csv", index=False)
print(f"  ✓ Salvo: 04_TOP_INSTANCIAS_DIFICEIS.png e .csv")

# ==================== 6. IMPACTO DE k (COBERTURA MÍNIMA) ====================
print("\n[6/8] Analisando impacto da cobertura mínima (k)...")

por_k = success_data.groupby(['Cobertura Mínima (k)', 'config']).agg({
    'tempo_num': 'mean',
    'numCirculos_num': 'mean',
    'Número de Clientes': 'mean'
}).reset_index()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Tempo por k
for cfg in sorted(por_k['config'].unique()):
    cfg_data = por_k[por_k['config'] == cfg]
    ax1.plot(cfg_data['Cobertura Mínima (k)'], cfg_data['tempo_num'],
            marker='o', linewidth=2.5, markersize=10, label=CONFIG_NAMES.get(cfg, cfg),
            color=COLORS[cfg])

ax1.set_xlabel('Cobertura Mínima (k)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Tempo Médio (segundos)', fontsize=12, fontweight='bold')
ax1.set_title('Impacto da Cobertura Mínima (k) no Tempo', fontsize=14, fontweight='bold', pad=15)
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)
ax1.set_yscale('log')

# Círculos por k
for cfg in sorted(por_k['config'].unique()):
    cfg_data = por_k[por_k['config'] == cfg]
    ax2.plot(cfg_data['Cobertura Mínima (k)'], cfg_data['numCirculos_num'],
            marker='s', linewidth=2.5, markersize=10, label=CONFIG_NAMES.get(cfg, cfg),
            color=COLORS[cfg])

ax2.set_xlabel('Cobertura Mínima (k)', fontsize=12, fontweight='bold')
ax2.set_ylabel('Número Médio de Círculos', fontsize=12, fontweight='bold')
ax2.set_title('Impacto da Cobertura Mínima (k) na Solução', fontsize=14, fontweight='bold', pad=15)
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "05_IMPACTO_COBERTURA_K.png", dpi=300, bbox_inches='tight')
plt.close()

por_k.to_csv(OUTPUT_DIR / "05_IMPACTO_COBERTURA_K.csv", index=False)
print(f"  ✓ Salvo: 05_IMPACTO_COBERTURA_K.png e .csv")

# ==================== 7. RESUMO EXECUTIVO POR CONFIG ====================
print("\n[7/8] Gerando resumo executivo por configuração...")

resumo_configs = []
for cfg in sorted(success_data['config'].unique()):
    cfg_data = success_data[success_data['config'] == cfg]
    
    resumo_configs.append({
        'Configuração': CONFIG_NAMES.get(cfg, cfg),
        'Instâncias Resolvidas': len(cfg_data),
        'Tempo Médio (s)': cfg_data['tempo_num'].mean(),
        'Tempo Mediana (s)': cfg_data['tempo_num'].median(),
        'Tempo Mín (s)': cfg_data['tempo_num'].min(),
        'Tempo Máx (s)': cfg_data['tempo_num'].max(),
        'Círculos Médio': cfg_data['numCirculos_num'].mean(),
        'Círculos Mín': cfg_data['numCirculos_num'].min(),
        'Círculos Máx': cfg_data['numCirculos_num'].max(),
        'Clientes Médio': cfg_data['Número de Clientes'].mean(),
    })

resumo_df = pd.DataFrame(resumo_configs).round(2)
resumo_df.to_csv(OUTPUT_DIR / "06_RESUMO_CONFIGURACOES.csv", index=False)

# Visualização da tabela
fig, ax = plt.subplots(figsize=(16, 6))
ax.axis('tight')
ax.axis('off')

# Preparar dados para tabela visual
table_data = resumo_df[['Configuração', 'Instâncias Resolvidas', 'Tempo Médio (s)', 
                         'Tempo Mediana (s)', 'Círculos Médio', 'Clientes Médio']].values

table = ax.table(cellText=table_data, 
                colLabels=['Configuração', 'Instâncias', 'Tempo Méd.', 'Tempo Med.', 'Círculos', 'n Médio'],
                cellLoc='center', loc='center', 
                colColours=['lightgray']*6)

table.auto_set_font_size(False)
table.set_fontsize(11)
table.scale(1, 2.5)

# Colorir primeira coluna
for i in range(len(resumo_df)):
    cfg_original = sorted(success_data['config'].unique())[i]
    table[(i+1, 0)].set_facecolor(COLORS.get(cfg_original, 'white'))

ax.set_title('Resumo Executivo das Configurações', fontsize=16, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "06_RESUMO_CONFIGURACOES.png", dpi=300, bbox_inches='tight')
plt.close()

print(f"  ✓ Salvo: 06_RESUMO_CONFIGURACOES.png e .csv")
print("\nResumo:")
print(resumo_df.to_string(index=False))

# ==================== 8. HEATMAP: CARACTERÍSTICAS × TEMPO ====================
print("\n\n[8/8] Gerando heatmap de correlação...")

# Matriz de correlação com nomes legíveis
corr_cols = ['Número de Clientes', 'Raio', 'Distância Mínima entre Círculos',
             'Cobertura Mínima (k)', 'Densidade', 'Área da Região', 'tempo_num', 'numCirculos_num']

corr_data = success_data[corr_cols].copy()
corr_data = corr_data.rename(columns={
    'tempo_num': 'Tempo de Execução',
    'numCirculos_num': 'Nº Círculos'
})

correlation_matrix = corr_data.corr()

fig, ax = plt.subplots(figsize=(12, 10))
sns.heatmap(correlation_matrix, annot=True, fmt='.3f', cmap='RdYlGn',
            center=0, square=True, linewidths=2, cbar_kws={"shrink": 0.8},
            vmin=-1, vmax=1, ax=ax, annot_kws={'size': 10, 'weight': 'bold'})

ax.set_title('Correlação entre Características e Desempenho', 
             fontsize=16, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "07_CORRELACAO_CARACTERISTICAS.png", dpi=300, bbox_inches='tight')
plt.close()

correlation_matrix.to_csv(OUTPUT_DIR / "07_CORRELACAO_CARACTERISTICAS.csv")
print(f"  ✓ Salvo: 07_CORRELACAO_CARACTERISTICAS.png e .csv")

# ==================== RELATÓRIO FINAL ====================
print("\n" + "=" * 80)
print("ANÁLISE APRIMORADA CONCLUÍDA!")
print("=" * 80)
print(f"\nArquivos salvos em: {OUTPUT_DIR}\n")
print("Arquivos gerados:")
print("  • TABELA_MESTRE_INSTANCIAS.csv - Todas características")
print("  • 01_PERFIL_POR_TAMANHO.png/csv - Distribuição por faixas")
print("  • 02_DESEMPENHO_POR_CARACTERISTICAS.png - 6 scatter plots")
print("  • 03_COMPARACAO_POR_FAIXA.png/csv - Configs por tamanho")
print("  • 04_TOP_INSTANCIAS_DIFICEIS.png/csv - Top 15 com características")
print("  • 05_IMPACTO_COBERTURA_K.png/csv - Análise do parâmetro k")
print("  • 06_RESUMO_CONFIGURACOES.png/csv - Tabela executiva")
print("  • 07_CORRELACAO_CARACTERISTICAS.png/csv - Heatmap")
print("\n" + "=" * 80)
print("✓ Todas as análises focam nas CARACTERÍSTICAS, não nos nomes!")
print("✓ Dados agregados (média das repetições)")
print("=" * 80)

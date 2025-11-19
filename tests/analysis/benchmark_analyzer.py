"""
Análise de Resultados do Benchmark - Circle Coverage
Gera gráficos e tabelas estatísticas para análise no TCC
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import seaborn as sns
from matplotlib.patches import Rectangle

# Configurações visuais (mesma identidade das imagens de círculos)
plt.style.use('default')
COLORS = {
    'Teste1': '#8DD3C7',  # Cyan claro
    'Teste2': '#FFFFB3',  # Amarelo claro
    'Teste3': '#BEBADA',  # Roxo claro
    'Teste4': '#FB8072',  # Vermelho claro
    'Teste5': '#80B1D3',  # Azul claro
    'Teste6': '#FDB462',  # Laranja claro
}

# Caminhos
SCRIPT_DIR = Path(__file__).parent
TABLES_DIR = SCRIPT_DIR.parent / "tables"
OUTPUT_DIR = SCRIPT_DIR / "results"
OUTPUT_DIR.mkdir(exist_ok=True)

# Carregar dados (com tratamento de erros)
try:
    results_df = pd.read_csv(TABLES_DIR / "results_table.csv", on_bad_lines='skip', encoding='utf-8')
    instances_df = pd.read_csv(TABLES_DIR / "instances_table.csv", on_bad_lines='skip', encoding='utf-8')
except Exception as e:
    print(f"Erro ao ler CSVs: {e}")
    print("Tentando com engine python...")
    results_df = pd.read_csv(TABLES_DIR / "results_table.csv", engine='python', on_bad_lines='skip')
    instances_df = pd.read_csv(TABLES_DIR / "instances_table.csv", engine='python', on_bad_lines='skip')

# Merge dos dados
data = results_df.merge(instances_df, on='instance_id', how='left')

# Converter tempo para numérico (tratar "Sem resultado" como NaN)
data['tempo_num'] = pd.to_numeric(data['tempo'], errors='coerce')
data['numCirculos_num'] = pd.to_numeric(data['numCirculos'], errors='coerce')

print("=" * 80)
print("ANÁLISE DE BENCHMARK - CIRCLE COVERAGE")
print("=" * 80)
print(f"Total de instâncias: {len(instances_df)}")
print(f"Total de execuções: {len(results_df)}")
print(f"Configurações testadas: {data['config'].nunique()}")
print()

# ==================== 1. TAXA DE SUCESSO ====================
print("\n[1/7] Gerando análise de taxa de sucesso...")

success_rate = data.groupby('config').apply(
    lambda x: (x['status'] == 'SUCCESS').sum() / len(x) * 100
).reset_index(name='taxa_sucesso')

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(success_rate['config'], success_rate['taxa_sucesso'], 
              color=[COLORS[c] for c in success_rate['config']], 
              edgecolor='black', linewidth=1.5, alpha=0.8)

# Adicionar valores nas barras
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=11)

ax.set_ylabel('Taxa de Sucesso (%)', fontsize=12, fontweight='bold')
ax.set_xlabel('Configuração', fontsize=12, fontweight='bold')
ax.set_title('Taxa de Sucesso por Configuração', fontsize=14, fontweight='bold', pad=20)
ax.set_ylim(0, 110)
ax.grid(axis='y', alpha=0.3, linestyle='--')
ax.axhline(y=100, color='green', linestyle='--', linewidth=2, alpha=0.5, label='100%')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "1_taxa_sucesso.png", dpi=300, bbox_inches='tight')
plt.close()

# Salvar tabela
success_rate.to_csv(OUTPUT_DIR / "1_taxa_sucesso.csv", index=False)
print(f"  ✓ Salvo: 1_taxa_sucesso.png e .csv")

# ==================== 2. TEMPO MÉDIO DE EXECUÇÃO ====================
print("[2/7] Gerando análise de tempo de execução...")

success_data = data[data['status'] == 'SUCCESS'].copy()
tempo_stats = success_data.groupby('config').agg({
    'tempo_num': ['mean', 'median', 'std', 'min', 'max', 'count']
}).round(2)
tempo_stats.columns = ['_'.join(col).strip() for col in tempo_stats.columns.values]
tempo_stats = tempo_stats.reset_index()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Gráfico de barras (média)
bars = ax1.bar(tempo_stats['config'], tempo_stats['tempo_num_mean'], 
               color=[COLORS[c] for c in tempo_stats['config']],
               edgecolor='black', linewidth=1.5, alpha=0.8)

for bar in bars:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.1f}s', ha='center', va='bottom', fontweight='bold')

ax1.set_ylabel('Tempo Médio (segundos)', fontsize=12, fontweight='bold')
ax1.set_xlabel('Configuração', fontsize=12, fontweight='bold')
ax1.set_title('Tempo Médio de Execução', fontsize=14, fontweight='bold')
ax1.grid(axis='y', alpha=0.3, linestyle='--')

# Boxplot
boxplot_data = [success_data[success_data['config'] == cfg]['tempo_num'].values 
                for cfg in tempo_stats['config']]
bp = ax2.boxplot(boxplot_data, labels=tempo_stats['config'], patch_artist=True,
                 medianprops=dict(color='red', linewidth=2),
                 boxprops=dict(facecolor='lightblue', alpha=0.7, edgecolor='black', linewidth=1.5),
                 whiskerprops=dict(linewidth=1.5),
                 capprops=dict(linewidth=1.5))

for patch, cfg in zip(bp['boxes'], tempo_stats['config']):
    patch.set_facecolor(COLORS[cfg])

ax2.set_ylabel('Tempo (segundos)', fontsize=12, fontweight='bold')
ax2.set_xlabel('Configuração', fontsize=12, fontweight='bold')
ax2.set_title('Distribuição de Tempo de Execução', fontsize=14, fontweight='bold')
ax2.grid(axis='y', alpha=0.3, linestyle='--')
ax2.set_yscale('log')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "2_tempo_execucao.png", dpi=300, bbox_inches='tight')
plt.close()

tempo_stats.to_csv(OUTPUT_DIR / "2_tempo_execucao_stats.csv", index=False)
print(f"  ✓ Salvo: 2_tempo_execucao.png e .csv")

# ==================== 3. QUALIDADE DA SOLUÇÃO (Número de Círculos) ====================
print("[3/7] Gerando análise de qualidade da solução...")

circulos_stats = success_data.groupby('config').agg({
    'numCirculos_num': ['mean', 'median', 'std', 'min', 'max']
}).round(2)
circulos_stats.columns = ['_'.join(col).strip() for col in circulos_stats.columns.values]
circulos_stats = circulos_stats.reset_index()

fig, ax = plt.subplots(figsize=(12, 6))

x = np.arange(len(circulos_stats))
width = 0.35

bars1 = ax.bar(x - width/2, circulos_stats['numCirculos_num_mean'], width,
               label='Média', color='skyblue', edgecolor='black', linewidth=1.5, alpha=0.8)
bars2 = ax.bar(x + width/2, circulos_stats['numCirculos_num_median'], width,
               label='Mediana', color='lightcoral', edgecolor='black', linewidth=1.5, alpha=0.8)

for bar in bars1:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

for bar in bars2:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

ax.set_ylabel('Número de Círculos', fontsize=12, fontweight='bold')
ax.set_xlabel('Configuração', fontsize=12, fontweight='bold')
ax.set_title('Qualidade da Solução (Número de Círculos)', fontsize=14, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(circulos_stats['config'])
ax.legend(fontsize=11, loc='upper left')
ax.grid(axis='y', alpha=0.3, linestyle='--')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "3_qualidade_solucao.png", dpi=300, bbox_inches='tight')
plt.close()

circulos_stats.to_csv(OUTPUT_DIR / "3_qualidade_solucao_stats.csv", index=False)
print(f"  ✓ Salvo: 3_qualidade_solucao.png e .csv")

# ==================== 4. IMPACTO DO TAMANHO DA INSTÂNCIA ====================
print("[4/7] Gerando análise de escalabilidade...")

# Agrupar por faixas de tamanho
success_data['faixa_tamanho'] = pd.cut(success_data['nClientes'], 
                                        bins=[0, 25, 50, 100, 200, 400],
                                        labels=['≤25', '26-50', '51-100', '101-200', '>200'])

escalabilidade = success_data.groupby(['config', 'faixa_tamanho']).agg({
    'tempo_num': 'mean',
    'numCirculos_num': 'mean'
}).reset_index()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Tempo vs Tamanho
for cfg in escalabilidade['config'].unique():
    cfg_data = escalabilidade[escalabilidade['config'] == cfg]
    ax1.plot(cfg_data['faixa_tamanho'], cfg_data['tempo_num'], 
            marker='o', linewidth=2.5, markersize=8, 
            label=cfg, color=COLORS[cfg])

ax1.set_ylabel('Tempo Médio (segundos)', fontsize=12, fontweight='bold')
ax1.set_xlabel('Tamanho da Instância (n)', fontsize=12, fontweight='bold')
ax1.set_title('Escalabilidade: Tempo × Tamanho da Instância', fontsize=14, fontweight='bold')
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3, linestyle='--')
ax1.set_yscale('log')

# Círculos vs Tamanho
for cfg in escalabilidade['config'].unique():
    cfg_data = escalabilidade[escalabilidade['config'] == cfg]
    ax2.plot(cfg_data['faixa_tamanho'], cfg_data['numCirculos_num'], 
            marker='s', linewidth=2.5, markersize=8, 
            label=cfg, color=COLORS[cfg])

ax2.set_ylabel('Número Médio de Círculos', fontsize=12, fontweight='bold')
ax2.set_xlabel('Tamanho da Instância (n)', fontsize=12, fontweight='bold')
ax2.set_title('Escalabilidade: Círculos × Tamanho da Instância', fontsize=14, fontweight='bold')
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3, linestyle='--')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "4_escalabilidade.png", dpi=300, bbox_inches='tight')
plt.close()

escalabilidade.to_csv(OUTPUT_DIR / "4_escalabilidade.csv", index=False)
print(f"  ✓ Salvo: 4_escalabilidade.png e .csv")

# ==================== 5. COMPARAÇÃO DIRETA ENTRE CONFIGURAÇÕES ====================
print("[5/7] Gerando comparação head-to-head...")

# Comparar apenas instâncias onde TODAS as configs tiveram sucesso
pivot_tempo = success_data.pivot_table(index='instance_id', columns='config', 
                                        values='tempo_num', aggfunc='mean')
pivot_circulos = success_data.pivot_table(index='instance_id', columns='config', 
                                           values='numCirculos_num', aggfunc='mean')

# Remover instâncias com valores faltantes
pivot_tempo_completo = pivot_tempo.dropna()
pivot_circulos_completo = pivot_circulos.dropna()

# Speedup relativo ao Teste1 (baseline)
if 'Teste1' in pivot_tempo_completo.columns:
    speedup = pivot_tempo_completo.div(pivot_tempo_completo['Teste1'], axis=0)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    speedup_mean = speedup.mean().drop('Teste1')
    bars = ax.bar(speedup_mean.index, speedup_mean.values,
                  color=[COLORS[c] for c in speedup_mean.index],
                  edgecolor='black', linewidth=1.5, alpha=0.8)
    
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}x', ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    ax.axhline(y=1, color='red', linestyle='--', linewidth=2, label='Baseline (Teste1)')
    ax.set_ylabel('Speedup Relativo', fontsize=12, fontweight='bold')
    ax.set_xlabel('Configuração', fontsize=12, fontweight='bold')
    ax.set_title('Speedup em Relação ao Teste1 (Baseline)', fontsize=14, fontweight='bold', pad=20)
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "5_speedup_relativo.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    speedup_mean.to_csv(OUTPUT_DIR / "5_speedup_relativo.csv", header=['speedup'])
    print(f"  ✓ Salvo: 5_speedup_relativo.png e .csv")

# ==================== 6. HEATMAP DE DESEMPENHO ====================
print("[6/7] Gerando heatmap de desempenho...")

# Normalizar tempos por instância (0-1 scale)
tempo_normalized = pivot_tempo_completo.div(pivot_tempo_completo.max(axis=1), axis=0)

fig, ax = plt.subplots(figsize=(10, 12))
sns.heatmap(tempo_normalized.head(30), cmap='RdYlGn_r', annot=False, 
            cbar_kws={'label': 'Tempo Normalizado (0=melhor, 1=pior)'}, ax=ax,
            linewidths=0.5, linecolor='gray')

ax.set_title('Heatmap de Desempenho (primeiras 30 instâncias)', 
             fontsize=14, fontweight='bold', pad=20)
ax.set_xlabel('Configuração', fontsize=12, fontweight='bold')
ax.set_ylabel('ID da Instância', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "6_heatmap_desempenho.png", dpi=300, bbox_inches='tight')
plt.close()

print(f"  ✓ Salvo: 6_heatmap_desempenho.png")

# ==================== 7. TABELA RESUMO GERAL ====================
print("[7/7] Gerando tabela resumo geral...")

resumo = []
for cfg in data['config'].unique():
    cfg_data = data[data['config'] == cfg]
    success_cfg = cfg_data[cfg_data['status'] == 'SUCCESS']
    
    resumo.append({
        'Configuração': cfg,
        'Total Execuções': len(cfg_data),
        'Sucessos': len(success_cfg),
        'Taxa Sucesso (%)': f"{len(success_cfg)/len(cfg_data)*100:.1f}",
        'Tempo Médio (s)': f"{success_cfg['tempo_num'].mean():.2f}" if len(success_cfg) > 0 else 'N/A',
        'Tempo Mediana (s)': f"{success_cfg['tempo_num'].median():.2f}" if len(success_cfg) > 0 else 'N/A',
        'Tempo Desvio (s)': f"{success_cfg['tempo_num'].std():.2f}" if len(success_cfg) > 0 else 'N/A',
        'Círculos Médio': f"{success_cfg['numCirculos_num'].mean():.1f}" if len(success_cfg) > 0 else 'N/A',
        'Círculos Min': int(success_cfg['numCirculos_num'].min()) if len(success_cfg) > 0 else 'N/A',
        'Círculos Max': int(success_cfg['numCirculos_num'].max()) if len(success_cfg) > 0 else 'N/A',
    })

resumo_df = pd.DataFrame(resumo)
resumo_df.to_csv(OUTPUT_DIR / "7_resumo_geral.csv", index=False)

# Criar figura de tabela visual
fig, ax = plt.subplots(figsize=(14, 6))
ax.axis('tight')
ax.axis('off')

table = ax.table(cellText=resumo_df.values, colLabels=resumo_df.columns,
                cellLoc='center', loc='center', 
                colColours=['lightgray']*len(resumo_df.columns))

table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1, 2)

# Colorir células por configuração
for i in range(len(resumo_df)):
    cfg = resumo_df.iloc[i]['Configuração']
    table[(i+1, 0)].set_facecolor(COLORS.get(cfg, 'white'))

ax.set_title('Resumo Geral de Desempenho das Configurações', 
             fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "7_resumo_geral.png", dpi=300, bbox_inches='tight')
plt.close()

print(f"  ✓ Salvo: 7_resumo_geral.png e .csv")

# ==================== RELATÓRIO FINAL ====================
print("\n" + "=" * 80)
print("ANÁLISE COMPLETA")
print("=" * 80)
print(f"\nArquivos salvos em: {OUTPUT_DIR}")
print("\nArquivos gerados:")
print("  1. 1_taxa_sucesso.png / .csv")
print("  2. 2_tempo_execucao.png / .csv")
print("  3. 3_qualidade_solucao.png / .csv")
print("  4. 4_escalabilidade.png / .csv")
print("  5. 5_speedup_relativo.png / .csv")
print("  6. 6_heatmap_desempenho.png")
print("  7. 7_resumo_geral.png / .csv")
print("\n" + "=" * 80)
print("✓ Análise concluída com sucesso!")
print("=" * 80)

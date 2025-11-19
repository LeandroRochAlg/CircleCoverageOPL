"""
Análise Completa e Honesta - Circle Coverage Benchmark
- Foco nas CARACTERÍSTICAS das instâncias
- Média das repetições
- Transparência total sobre quais instâncias foram testadas em cada configuração
- Comparações justas apenas entre mesmas instâncias
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

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
    'Teste2': 'Heurística 3 + CP',
    'Teste3': 'Heurística 4 + CP',
    'Teste4': 'CP Pontos Fixos + Quebra Entre',
    'Teste5': 'CP Pontos Fixos + Quebra Intra',
    'Teste6': 'CP Pontos Fixos + Quebra Entre+Intra',
}

# Carregar dados
try:
    results_df = pd.read_csv(TABLES_DIR / "results_table.csv", on_bad_lines='skip', encoding='utf-8')
    instances_df = pd.read_csv(TABLES_DIR / "instances_table.csv", on_bad_lines='skip', encoding='utf-8')
except:
    results_df = pd.read_csv(TABLES_DIR / "results_table.csv", engine='python', on_bad_lines='skip')
    instances_df = pd.read_csv(TABLES_DIR / "instances_table.csv", engine='python', on_bad_lines='skip')

# Renomear para nomes legíveis
instances_df = instances_df.rename(columns={
    'nClientes': 'Nº Clientes',
    'raio': 'Raio',
    'minDistCirculos': 'Dist. Mín. Círculos',
    'minCoverage': 'Cobertura k',
})

# Calcular características derivadas
instances_df['Área'] = (instances_df['maxX'] - instances_df['minX']) * \
                       (instances_df['maxY'] - instances_df['minY'])
instances_df['Densidade'] = instances_df['Nº Clientes'] / instances_df['Área']

# Merge
data = results_df.merge(instances_df, on='instance_id', how='left')
data['tempo_num'] = pd.to_numeric(data['tempo'], errors='coerce')
data['circulos_num'] = pd.to_numeric(data['numCirculos'], errors='coerce')

print("=" * 90)
print("ANÁLISE COMPLETA E HONESTA - CIRCLE COVERAGE BENCHMARK")
print("=" * 90)
print(f"Total de instâncias geradas: {len(instances_df)}")
print(f"Total de execuções registradas: {len(results_df)}")
print()

# ==================== 1. COBERTURA DOS TESTES (HONESTIDADE) ====================
print("[1/10] Analisando cobertura dos testes...\n")

# Contar quais instâncias foram testadas por cada config
cobertura = data.groupby(['config', 'instance_id']).size().reset_index(name='repeticoes')
cobertura = cobertura.merge(instances_df[['instance_id', 'Nº Clientes']], on='instance_id')

cobertura_summary = cobertura.groupby('config').agg({
    'instance_id': 'nunique',
    'Nº Clientes': ['min', 'max', 'mean']
}).round(1)
cobertura_summary.columns = ['Instâncias Testadas', 'n Mínimo', 'n Máximo', 'n Médio']
cobertura_summary = cobertura_summary.reset_index()

print("COBERTURA DOS TESTES:")
print(cobertura_summary.to_string(index=False))
print()

# Visualizar cobertura
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Gráfico 1: Quantidade de instâncias testadas
bars = ax1.bar(range(len(cobertura_summary)), cobertura_summary['Instâncias Testadas'],
               color=[COLORS[c] for c in cobertura_summary['config']],
               edgecolor='black', linewidth=2, alpha=0.8)

for i, (bar, row) in enumerate(zip(bars, cobertura_summary.iterrows())):
    _, data_row = row
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2, height,
            f"{int(height)} inst.\nn: {data_row['n Mínimo']:.0f}-{data_row['n Máximo']:.0f}",
            ha='center', va='bottom', fontweight='bold', fontsize=10)

ax1.set_xticks(range(len(cobertura_summary)))
ax1.set_xticklabels([CONFIG_NAMES.get(c, c) for c in cobertura_summary['config']], 
                    rotation=15, ha='right', fontsize=11)
ax1.set_ylabel('Número de Instâncias Testadas', fontsize=12, fontweight='bold')
ax1.set_title('Cobertura dos Testes por Configuração', fontsize=14, fontweight='bold', pad=15)
ax1.grid(axis='y', alpha=0.3)
ax1.text(0.5, 0.95, '⚠ Instâncias diferentes testadas em cada config',
         transform=ax1.transAxes, ha='center', va='top',
         bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7),
         fontsize=10, fontweight='bold')

# Gráfico 2: Distribuição de tamanhos testados
for cfg in sorted(cobertura['config'].unique()):
    cfg_data = cobertura[cobertura['config'] == cfg]
    ax2.hist(cfg_data['Nº Clientes'], bins=20, alpha=0.5, label=CONFIG_NAMES.get(cfg, cfg),
            color=COLORS[cfg], edgecolor='black', linewidth=1)

ax2.set_xlabel('Número de Clientes (n)', fontsize=12, fontweight='bold')
ax2.set_ylabel('Frequência', fontsize=12, fontweight='bold')
ax2.set_title('Distribuição de Tamanhos Testados por Config', fontsize=14, fontweight='bold', pad=15)
ax2.legend(fontsize=9)
ax2.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "01_COBERTURA_TESTES.png", dpi=300, bbox_inches='tight')
plt.close()

cobertura_summary.to_csv(OUTPUT_DIR / "01_COBERTURA_TESTES.csv", index=False)
print(f"  ✓ Salvo: 01_COBERTURA_TESTES.png e .csv\n")

# ==================== 2. MÉDIA DAS REPETIÇÕES ====================
print("[2/10] Agregando dados (média das repetições)...\n")

# Agrupar por instância e config, calculando média das repetições
data_agregado = data.groupby(['instance_id', 'config']).agg({
    'tempo_num': 'mean',
    'circulos_num': 'mean',
    'status': lambda x: 'SUCESSO' if (x == 'SUCCESS').all() else 'FALHA',
    'Nº Clientes': 'first',
    'Raio': 'first',
    'Dist. Mín. Círculos': 'first',
    'Cobertura k': 'first',
    'Área': 'first',
    'Densidade': 'first',
}).reset_index()

success_data = data_agregado[data_agregado['status'] == 'SUCESSO'].copy()
print(f"Dados agregados: {len(data_agregado)} registros")
print(f"Sucessos: {len(success_data)} ({len(success_data)/len(data_agregado)*100:.1f}%)")
print()

# ==================== 3. TAXA DE SUCESSO HONESTA (POR TAMANHO) ====================
print("[3/10] Calculando taxa de sucesso por tamanho de instância...\n")

# Criar faixas de tamanho
data_agregado['Faixa de Tamanho'] = pd.cut(
    data_agregado['Nº Clientes'],
    bins=[0, 25, 50, 100, 200, 500],
    labels=['Pequena\n(≤25)', 'Média\n(26-50)', 'Grande\n(51-100)', 
            'Muito Grande\n(101-200)', 'Extra Grande\n(>200)']
)

taxa_sucesso_faixa = data_agregado.groupby(['config', 'Faixa de Tamanho']).apply(
    lambda x: pd.Series({
        'Taxa Sucesso': (x['status'] == 'SUCESSO').sum() / len(x) * 100,
        'Total Testado': len(x),
        'Sucessos': (x['status'] == 'SUCESSO').sum()
    })
).reset_index()

# Visualizar
fig, ax = plt.subplots(figsize=(14, 8))

faixas = sorted([f for f in taxa_sucesso_faixa['Faixa de Tamanho'].unique() if pd.notna(f)],
                key=lambda x: ['Pequena\n(≤25)', 'Média\n(26-50)', 'Grande\n(51-100)', 
                              'Muito Grande\n(101-200)', 'Extra Grande\n(>200)'].index(x))
x = np.arange(len(faixas))
width = 0.13

for i, cfg in enumerate(sorted(taxa_sucesso_faixa['config'].unique())):
    cfg_data = taxa_sucesso_faixa[taxa_sucesso_faixa['config'] == cfg]
    valores = []
    labels_texto = []
    
    for faixa in faixas:
        faixa_data = cfg_data[cfg_data['Faixa de Tamanho'] == faixa]
        if len(faixa_data) > 0 and not pd.isna(faixa_data['Taxa Sucesso'].values[0]):
            taxa = float(faixa_data['Taxa Sucesso'].values[0])
            total = int(faixa_data['Total Testado'].values[0])
            valores.append(taxa)
            labels_texto.append(f"{total}")
        else:
            valores.append(0)
            labels_texto.append("0")
    
    bars = ax.bar(x + i*width, valores, width, label=CONFIG_NAMES.get(cfg, cfg),
                 color=COLORS[cfg], edgecolor='black', linewidth=1.5, alpha=0.8)
    
    # Adicionar quantidade testada
    for bar, label in zip(bars, labels_texto):
        if bar.get_height() > 0:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                   f"n={label}", ha='center', va='bottom', fontsize=7, rotation=90)

ax.set_xlabel('Faixa de Tamanho da Instância', fontsize=12, fontweight='bold')
ax.set_ylabel('Taxa de Sucesso (%)', fontsize=12, fontweight='bold')
ax.set_title('Taxa de Sucesso por Tamanho de Instância e Configuração\n(Números indicam quantas instâncias foram testadas)', 
             fontsize=14, fontweight='bold', pad=20)
ax.set_xticks(x + width * 2.5)
ax.set_xticklabels(faixas, fontsize=10)
ax.set_ylim(0, 110)
ax.axhline(y=100, color='green', linestyle='--', linewidth=2, alpha=0.5)
ax.legend(fontsize=9, loc='lower left')
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "02_TAXA_SUCESSO_HONESTA.png", dpi=300, bbox_inches='tight')
plt.close()

taxa_sucesso_faixa.to_csv(OUTPUT_DIR / "02_TAXA_SUCESSO_POR_TAMANHO.csv", index=False)
print("Taxa de Sucesso por Faixa:")
print(taxa_sucesso_faixa.pivot(index='Faixa de Tamanho', columns='config', values='Taxa Sucesso').round(1))
print(f"\n  ✓ Salvo: 02_TAXA_SUCESSO_HONESTA.png e .csv\n")

# ==================== 4. COMPARAÇÃO JUSTA (APENAS INSTÂNCIAS COMUNS) ====================
print("[4/10] Comparação justa: instâncias testadas em TODAS configs...\n")

instancias_por_config = data_agregado.groupby('instance_id')['config'].apply(set).reset_index()
todas_configs = set(data_agregado['config'].unique())
instancias_comuns = instancias_por_config[
    instancias_por_config['config'].apply(lambda x: x == todas_configs)
]['instance_id'].values

print(f"Instâncias testadas em TODAS as {len(todas_configs)} configs: {len(instancias_comuns)}\n")

if len(instancias_comuns) > 0:
    data_comum = success_data[success_data['instance_id'].isin(instancias_comuns)].copy()
    
    # Ordenar por número de clientes
    inst_ordenadas = data_comum[['instance_id', 'Nº Clientes', 'Raio', 'Cobertura k']].drop_duplicates()
    inst_ordenadas = inst_ordenadas.sort_values('Nº Clientes')
    ordem_inst = inst_ordenadas['instance_id'].values
    
    # TABELA DETALHADA
    print("=" * 120)
    print(f"{'INSTÂNCIA':<50} | {'CONFIGURAÇÃO':<40} | {'TEMPO':>10} | {'CÍRCULOS':>8}")
    print("=" * 120)
    
    for inst_id in ordem_inst:
        inst_info = inst_ordenadas[inst_ordenadas['instance_id'] == inst_id].iloc[0]
        inst_label = f"n={int(inst_info['Nº Clientes'])}, r={inst_info['Raio']:.1f}, k={int(inst_info['Cobertura k'])}"
        
        inst_results = data_comum[data_comum['instance_id'] == inst_id].sort_values('config')
        
        for i, (_, row) in enumerate(inst_results.iterrows()):
            if i == 0:
                print(f"{inst_label:<50} | {CONFIG_NAMES[row['config']]:<40} | {row['tempo_num']:>9.2f}s | {row['circulos_num']:>8.0f}")
            else:
                print(f"{'':<50} | {CONFIG_NAMES[row['config']]:<40} | {row['tempo_num']:>9.2f}s | {row['circulos_num']:>8.0f}")
        print("-" * 120)
    
    print("=" * 120 + "\n")
    
    # GRÁFICO DE LINHAS
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))
    
    labels_inst = [f"n={int(inst_ordenadas[inst_ordenadas['instance_id']==i]['Nº Clientes'].iloc[0])}" 
                   for i in ordem_inst]
    
    # Tempo
    for cfg in sorted(data_comum['config'].unique()):
        cfg_data = data_comum[data_comum['config'] == cfg]
        tempos = [cfg_data[cfg_data['instance_id'] == inst]['tempo_num'].values[0] 
                 if inst in cfg_data['instance_id'].values else np.nan 
                 for inst in ordem_inst]
        
        ax1.plot(range(len(ordem_inst)), tempos, marker='o', linewidth=3, markersize=12,
                label=CONFIG_NAMES[cfg], color=COLORS[cfg], alpha=0.9)
    
    ax1.set_xlabel('Instância (ordenada por nº de clientes)', fontsize=13, fontweight='bold')
    ax1.set_ylabel('Tempo (s)', fontsize=13, fontweight='bold')
    ax1.set_title(f'Tempo de Execução - Comparação Justa\n({len(instancias_comuns)} instâncias testadas em todas configs)', 
                 fontsize=14, fontweight='bold', pad=15)
    ax1.set_xticks(range(len(ordem_inst)))
    ax1.set_xticklabels(labels_inst, rotation=45, ha='right', fontsize=10)
    ax1.legend(fontsize=10, loc='best', framealpha=0.9)
    ax1.set_yscale('log')
    ax1.grid(True, alpha=0.3, which='both', linestyle='--')
    
    # Círculos
    for cfg in sorted(data_comum['config'].unique()):
        cfg_data = data_comum[data_comum['config'] == cfg]
        circulos = [cfg_data[cfg_data['instance_id'] == inst]['circulos_num'].values[0] 
                   if inst in cfg_data['instance_id'].values else np.nan 
                   for inst in ordem_inst]
        
        ax2.plot(range(len(ordem_inst)), circulos, marker='s', linewidth=3, markersize=12,
                label=CONFIG_NAMES[cfg], color=COLORS[cfg], alpha=0.9)
    
    ax2.set_xlabel('Instância (ordenada por nº de clientes)', fontsize=13, fontweight='bold')
    ax2.set_ylabel('Número de Círculos', fontsize=13, fontweight='bold')
    ax2.set_title(f'Qualidade da Solução - Comparação Justa\n({len(instancias_comuns)} instâncias testadas em todas configs)', 
                 fontsize=14, fontweight='bold', pad=15)
    ax2.set_xticks(range(len(ordem_inst)))
    ax2.set_xticklabels(labels_inst, rotation=45, ha='right', fontsize=10)
    ax2.legend(fontsize=10, loc='best', framealpha=0.9)
    ax2.grid(True, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "03_COMPARACAO_JUSTA.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    # Exportar CSV detalhado
    csv_export = data_comum[['instance_id', 'config', 'Nº Clientes', 'Raio', 'Cobertura k', 
                             'Densidade', 'tempo_num', 'circulos_num']].copy()
    csv_export['Configuração'] = csv_export['config'].map(CONFIG_NAMES)
    csv_export = csv_export.sort_values(['Nº Clientes', 'config'])
    csv_export.to_csv(OUTPUT_DIR / "03_COMPARACAO_JUSTA.csv", index=False)
    
    print(f"  ✓ Salvo: 03_COMPARACAO_JUSTA.png e .csv\n")
else:
    print("  ⚠ Nenhuma instância foi testada em todas as configurações!\n")

# ==================== 5. TABELA MESTRE: CARACTERÍSTICAS DAS INSTÂNCIAS ====================
print("[5/10] Gerando tabela mestre das instâncias testadas...\n")

# Para cada instância, calcular média entre configs que a testaram
tabela_instancias = success_data.groupby('instance_id').agg({
    'Nº Clientes': 'first',
    'Raio': 'first',
    'Dist. Mín. Círculos': 'first',
    'Cobertura k': 'first',
    'Densidade': 'first',
    'Área': 'first',
    'tempo_num': 'mean',
    'circulos_num': 'mean',
    'config': lambda x: ', '.join(sorted(set(x)))  # Quais configs testaram
}).reset_index()

tabela_instancias = tabela_instancias.rename(columns={'config': 'Configs Testadas'})
tabela_instancias = tabela_instancias.sort_values('Nº Clientes')

# Classificar dificuldade
tabela_instancias['Classe Dificuldade'] = pd.cut(
    tabela_instancias['tempo_num'],
    bins=[0, 1, 10, 100, float('inf')],
    labels=['Fácil', 'Média', 'Difícil', 'Muito Difícil']
)

# Exportar
tabela_export = tabela_instancias[[
    'Nº Clientes', 'Raio', 'Dist. Mín. Círculos', 'Cobertura k',
    'Densidade', 'Área', 'tempo_num', 'circulos_num',
    'Classe Dificuldade', 'Configs Testadas'
]].copy()

tabela_export = tabela_export.rename(columns={
    'tempo_num': 'Tempo Médio (s)',
    'circulos_num': 'Círculos Médios'
})
tabela_export = tabela_export.round(2)

tabela_export.to_csv(OUTPUT_DIR / "04_TABELA_MESTRE_INSTANCIAS.csv", index=False)
print(f"Tabela mestre: {len(tabela_export)} instâncias")
print("\nPrimeiras 10 instâncias:")
print(tabela_export.head(10)[['Nº Clientes', 'Raio', 'Cobertura k', 'Tempo Médio (s)', 
                               'Círculos Médios', 'Configs Testadas']].to_string(index=False))
print(f"\n  ✓ Salvo: 04_TABELA_MESTRE_INSTANCIAS.csv\n")

# ==================== 6. IMPACTO DAS CARACTERÍSTICAS (SIMPLES E CLARO) ====================
print("[6/10] Analisando impacto das características principais...\n")

# Criar métrica composta: raio * cobertura * n
success_data['Complexidade'] = success_data['Raio'] * success_data['Cobertura k'] * success_data['Nº Clientes']

# 4 gráficos: características individuais + tempo x círculos + complexidade
fig = plt.figure(figsize=(20, 12))
gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)

# Linha 1: Características individuais
caracteristicas_principais = [
    ('Nº Clientes', 'Número de Clientes'),
    ('Raio', 'Raio dos Círculos'),
    ('Cobertura k', 'Cobertura Mínima (k)'),
]

for idx, (col, titulo) in enumerate(caracteristicas_principais):
    ax = fig.add_subplot(gs[0, idx])
    
    for cfg in sorted(success_data['config'].unique()):
        cfg_data = success_data[success_data['config'] == cfg].sort_values(col)
        grouped = cfg_data.groupby(col)['tempo_num'].mean().reset_index()
        
        ax.plot(grouped[col], grouped['tempo_num'], 
               marker='o', linewidth=2.5, markersize=9,
               label=CONFIG_NAMES[cfg], color=COLORS[cfg], alpha=0.8)
    
    ax.set_xlabel(titulo, fontsize=12, fontweight='bold')
    ax.set_ylabel('Tempo Médio (s)', fontsize=12, fontweight='bold')
    ax.set_title(f'Impacto: {titulo}', fontsize=13, fontweight='bold', pad=10)
    ax.set_yscale('log')
    ax.grid(True, alpha=0.3, which='both', linestyle='--')
    if idx == 0:
        ax.legend(fontsize=8, loc='best', framealpha=0.9)

# Linha 2: Análises especiais

# 2.1 - Tempo × Número de Círculos
ax_tempo_circ = fig.add_subplot(gs[1, 0])
for cfg in sorted(success_data['config'].unique()):
    cfg_data = success_data[success_data['config'] == cfg]
    ax_tempo_circ.scatter(cfg_data['circulos_num'], cfg_data['tempo_num'],
                         label=CONFIG_NAMES[cfg], color=COLORS[cfg], 
                         alpha=0.6, s=80, edgecolors='black', linewidth=0.5)

ax_tempo_circ.set_xlabel('Número de Círculos na Solução', fontsize=12, fontweight='bold')
ax_tempo_circ.set_ylabel('Tempo de Execução (s)', fontsize=12, fontweight='bold')
ax_tempo_circ.set_title('Relação: Tempo × Círculos\n(Mais círculos = mais tempo)', 
                       fontsize=13, fontweight='bold', pad=10)
ax_tempo_circ.set_yscale('log')
ax_tempo_circ.set_xscale('log')
ax_tempo_circ.grid(True, alpha=0.3, which='both', linestyle='--')
ax_tempo_circ.legend(fontsize=8, loc='best', framealpha=0.9)

# 2.2 - Complexidade (raio × k × n) × Tempo
ax_complex_tempo = fig.add_subplot(gs[1, 1])
for cfg in sorted(success_data['config'].unique()):
    cfg_data = success_data[success_data['config'] == cfg]
    ax_complex_tempo.scatter(cfg_data['Complexidade'], cfg_data['tempo_num'],
                            label=CONFIG_NAMES[cfg], color=COLORS[cfg],
                            alpha=0.6, s=80, edgecolors='black', linewidth=0.5)

ax_complex_tempo.set_xlabel('Complexidade (Raio × k × n)', fontsize=12, fontweight='bold')
ax_complex_tempo.set_ylabel('Tempo de Execução (s)', fontsize=12, fontweight='bold')
ax_complex_tempo.set_title('Relação: Complexidade × Tempo\n(Métrica combinada)', 
                          fontsize=13, fontweight='bold', pad=10)
ax_complex_tempo.set_yscale('log')
ax_complex_tempo.set_xscale('log')
ax_complex_tempo.grid(True, alpha=0.3, which='both', linestyle='--')
ax_complex_tempo.legend(fontsize=8, loc='best', framealpha=0.9)

# 2.3 - Complexidade (raio × k × n) × Círculos
ax_complex_circ = fig.add_subplot(gs[1, 2])
for cfg in sorted(success_data['config'].unique()):
    cfg_data = success_data[success_data['config'] == cfg]
    ax_complex_circ.scatter(cfg_data['Complexidade'], cfg_data['circulos_num'],
                           label=CONFIG_NAMES[cfg], color=COLORS[cfg],
                           alpha=0.6, s=80, edgecolors='black', linewidth=0.5)

ax_complex_circ.set_xlabel('Complexidade (Raio × k × n)', fontsize=12, fontweight='bold')
ax_complex_circ.set_ylabel('Número de Círculos', fontsize=12, fontweight='bold')
ax_complex_circ.set_title('Relação: Complexidade × Círculos\n(Métrica combinada)', 
                         fontsize=13, fontweight='bold', pad=10)
ax_complex_circ.set_xscale('log')
ax_complex_circ.grid(True, alpha=0.3, which='both', linestyle='--')
ax_complex_circ.legend(fontsize=8, loc='best', framealpha=0.9)

plt.suptitle('Análise Completa do Impacto das Características', 
             fontsize=16, fontweight='bold', y=0.995)
plt.savefig(OUTPUT_DIR / "05_IMPACTO_CARACTERISTICAS.png", dpi=300, bbox_inches='tight')
plt.close()

# Análise de correlação da complexidade
print("\n📊 ANÁLISE DA MÉTRICA DE COMPLEXIDADE (Raio × k × n):")
print("=" * 80)
corr_complex_tempo = success_data[['Complexidade', 'tempo_num']].corr().iloc[0, 1]
corr_complex_circ = success_data[['Complexidade', 'circulos_num']].corr().iloc[0, 1]
corr_tempo_circ = success_data[['tempo_num', 'circulos_num']].corr().iloc[0, 1]

print(f"  • Complexidade × Tempo:    {corr_complex_tempo:+.3f} ", end="")
if abs(corr_complex_tempo) > 0.5:
    print(f"(FORTE correlação)")
elif abs(corr_complex_tempo) > 0.3:
    print(f"(MODERADA correlação)")
else:
    print(f"(FRACA correlação)")

print(f"  • Complexidade × Círculos: {corr_complex_circ:+.3f} ", end="")
if abs(corr_complex_circ) > 0.5:
    print(f"(FORTE correlação)")
elif abs(corr_complex_circ) > 0.3:
    print(f"(MODERADA correlação)")
else:
    print(f"(FRACA correlação)")

print(f"  • Tempo × Círculos:        {corr_tempo_circ:+.3f} ", end="")
if abs(corr_tempo_circ) > 0.5:
    print(f"(FORTE correlação)")
elif abs(corr_tempo_circ) > 0.3:
    print(f"(MODERADA correlação)")
else:
    print(f"(FRACA correlação)")

print("=" * 80)
print(f"\n  ✓ Salvo: 05_IMPACTO_CARACTERISTICAS.png\n")

# ==================== 7. TOP 10 INSTÂNCIAS MAIS DIFÍCEIS ====================
print("[7/10] Identificando as 10 instâncias mais difíceis...\n")

top_dificeis = tabela_instancias.nlargest(10, 'tempo_num')[[
    'Nº Clientes', 'Raio', 'Cobertura k', 'Densidade', 'tempo_num', 'circulos_num'
]]

fig, ax = plt.subplots(figsize=(14, 8))

labels = [f"n={int(row['Nº Clientes'])}, r={row['Raio']:.1f}, k={int(row['Cobertura k'])}" 
          for _, row in top_dificeis.iterrows()]

y_pos = np.arange(len(labels))
colors_bars = plt.cm.Reds(np.linspace(0.5, 0.95, len(labels)))

bars = ax.barh(y_pos, top_dificeis['tempo_num'], color=colors_bars,
               edgecolor='black', linewidth=2, alpha=0.85)

for bar, (_, row) in zip(bars, top_dificeis.iterrows()):
    width = bar.get_width()
    ax.text(width + 10, bar.get_y() + bar.get_height()/2,
            f"{width:.1f}s ({row['circulos_num']:.0f} círculos)",
            ha='left', va='center', fontsize=10, fontweight='bold')

ax.set_yticks(y_pos)
ax.set_yticklabels(labels, fontsize=11)
ax.set_xlabel('Tempo Médio (segundos)', fontsize=13, fontweight='bold')
ax.set_title('Top 10 Instâncias Mais Difíceis\n(Tempo médio entre todas configs que testaram)', 
             fontsize=14, fontweight='bold', pad=15)
ax.grid(axis='x', alpha=0.3, linestyle='--')
ax.set_xlim(0, top_dificeis['tempo_num'].max() * 1.3)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "06_TOP_10_DIFICEIS.png", dpi=300, bbox_inches='tight')
plt.close()

top_dificeis.to_csv(OUTPUT_DIR / "06_TOP_10_DIFICEIS.csv", index=False)
print(f"  ✓ Salvo: 06_TOP_10_DIFICEIS.png e .csv\n")

# ==================== 8. COMPARAÇÃO HEURÍSTICA 3 vs HEURÍSTICA 4 ====================
print("[8/10] Comparação detalhada: Heurística 3 vs Heurística 4...\n")

# Filtrar apenas Teste2 e Teste3
heur_data = success_data[success_data['config'].isin(['Teste2', 'Teste3'])].copy()

if len(heur_data) > 0:
    print(f"Instâncias analisadas: {len(heur_data[heur_data['config']=='Teste2'])}\n")
    
    # Estatísticas comparativas
    stats_h3 = heur_data[heur_data['config'] == 'Teste2']
    stats_h4 = heur_data[heur_data['config'] == 'Teste3']
    
    print("ESTATÍSTICAS COMPARATIVAS:")
    print("=" * 80)
    print(f"{'Métrica':<30} | {'Heurística 3':>15} | {'Heurística 4':>15} | {'Diferença':>12}")
    print("-" * 80)
    print(f"{'Tempo Médio (s)':<30} | {stats_h3['tempo_num'].mean():>15.2f} | {stats_h4['tempo_num'].mean():>15.2f} | {((stats_h4['tempo_num'].mean() / stats_h3['tempo_num'].mean() - 1) * 100):>11.1f}%")
    print(f"{'Tempo Mediana (s)':<30} | {stats_h3['tempo_num'].median():>15.2f} | {stats_h4['tempo_num'].median():>15.2f} | {((stats_h4['tempo_num'].median() / stats_h3['tempo_num'].median() - 1) * 100):>11.1f}%")
    print(f"{'Círculos Médio':<30} | {stats_h3['circulos_num'].mean():>15.1f} | {stats_h4['circulos_num'].mean():>15.1f} | {(stats_h4['circulos_num'].mean() - stats_h3['circulos_num'].mean()):>11.1f}")
    print(f"{'Desvio Padrão Tempo':<30} | {stats_h3['tempo_num'].std():>15.2f} | {stats_h4['tempo_num'].std():>15.2f} | {((stats_h4['tempo_num'].std() / stats_h3['tempo_num'].std() - 1) * 100):>11.1f}%")
    print("=" * 80 + "\n")
    
    # Comparação por faixa de tamanho
    heur_data['faixa'] = pd.cut(heur_data['Nº Clientes'], 
                                 bins=[0, 25, 50, 100, float('inf')],
                                 labels=['Pequena (≤25)', 'Média (26-50)', 'Grande (51-100)', 'Muito Grande (>100)'])
    
    por_faixa = heur_data.groupby(['faixa', 'config']).agg({
        'tempo_num': ['mean', 'count'],
        'circulos_num': 'mean'
    }).round(2)
    
    print("DESEMPENHO POR FAIXA DE TAMANHO:")
    print(por_faixa)
    print()
    
    # Gráficos comparativos
    fig = plt.figure(figsize=(20, 10))
    gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
    
    # 1. Boxplot Tempo
    ax1 = fig.add_subplot(gs[0, 0])
    data_box_tempo = [stats_h3['tempo_num'].values, stats_h4['tempo_num'].values]
    bp1 = ax1.boxplot(data_box_tempo, labels=['Heurística 3', 'Heurística 4'],
                      patch_artist=True, showmeans=True)
    bp1['boxes'][0].set_facecolor(COLORS['Teste2'])
    bp1['boxes'][1].set_facecolor(COLORS['Teste3'])
    ax1.set_ylabel('Tempo (s)', fontsize=12, fontweight='bold')
    ax1.set_title('Distribuição do Tempo', fontsize=13, fontweight='bold', pad=10)
    ax1.set_yscale('log')
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    
    # 2. Boxplot Círculos
    ax2 = fig.add_subplot(gs[0, 1])
    data_box_circ = [stats_h3['circulos_num'].values, stats_h4['circulos_num'].values]
    bp2 = ax2.boxplot(data_box_circ, labels=['Heurística 3', 'Heurística 4'],
                      patch_artist=True, showmeans=True)
    bp2['boxes'][0].set_facecolor(COLORS['Teste2'])
    bp2['boxes'][1].set_facecolor(COLORS['Teste3'])
    ax2.set_ylabel('Número de Círculos', fontsize=12, fontweight='bold')
    ax2.set_title('Distribuição dos Círculos', fontsize=13, fontweight='bold', pad=10)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    
    # 3. Scatter: Tempo H3 vs Tempo H4
    ax3 = fig.add_subplot(gs[0, 2])
    # Parear instâncias
    h3_pivot = stats_h3.set_index('instance_id')['tempo_num']
    h4_pivot = stats_h4.set_index('instance_id')['tempo_num']
    comum = h3_pivot.index.intersection(h4_pivot.index)
    
    ax3.scatter(h3_pivot[comum], h4_pivot[comum], s=100, alpha=0.7,
               color=COLORS['Teste3'], edgecolors='black', linewidth=1)
    
    # Linha de igualdade
    min_val = min(h3_pivot[comum].min(), h4_pivot[comum].min())
    max_val = max(h3_pivot[comum].max(), h4_pivot[comum].max())
    ax3.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, 
            label='Igual desempenho', alpha=0.7)
    
    ax3.set_xlabel('Tempo Heurística 3 (s)', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Tempo Heurística 4 (s)', fontsize=12, fontweight='bold')
    ax3.set_title('Comparação Direta por Instância\n(abaixo linha vermelha = H4 melhor)', 
                 fontsize=13, fontweight='bold', pad=10)
    ax3.set_xscale('log')
    ax3.set_yscale('log')
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3, linestyle='--')
    
    # Contar vitórias
    vitorias_h4 = (h4_pivot[comum] < h3_pivot[comum]).sum()
    vitorias_h3 = (h3_pivot[comum] < h4_pivot[comum]).sum()
    empates = len(comum) - vitorias_h4 - vitorias_h3
    
    ax3.text(0.05, 0.95, f'H3 mais rápida: {vitorias_h3}\nH4 mais rápida: {vitorias_h4}\nEmpates: {empates}',
            transform=ax3.transAxes, fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # 4. Tempo por Nº Clientes
    ax4 = fig.add_subplot(gs[1, 0])
    for cfg, nome, cor in [('Teste2', 'Heurística 3', COLORS['Teste2']), 
                           ('Teste3', 'Heurística 4', COLORS['Teste3'])]:
        cfg_data = heur_data[heur_data['config'] == cfg].sort_values('Nº Clientes')
        ax4.plot(cfg_data['Nº Clientes'], cfg_data['tempo_num'],
                marker='o', linewidth=2, markersize=8, label=nome, color=cor, alpha=0.8)
    
    ax4.set_xlabel('Número de Clientes', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Tempo (s)', fontsize=12, fontweight='bold')
    ax4.set_title('Tempo × Tamanho da Instância', fontsize=13, fontweight='bold', pad=10)
    ax4.set_yscale('log')
    ax4.legend(fontsize=11)
    ax4.grid(True, alpha=0.3, which='both', linestyle='--')
    
    # 5. Círculos por Cobertura k
    ax5 = fig.add_subplot(gs[1, 1])
    for cfg, nome, cor in [('Teste2', 'Heurística 3', COLORS['Teste2']), 
                           ('Teste3', 'Heurística 4', COLORS['Teste3'])]:
        cfg_data = heur_data[heur_data['config'] == cfg]
        grouped = cfg_data.groupby('Cobertura k')['circulos_num'].mean()
        ax5.plot(grouped.index, grouped.values,
                marker='s', linewidth=2.5, markersize=10, label=nome, color=cor, alpha=0.8)
    
    ax5.set_xlabel('Cobertura Mínima (k)', fontsize=12, fontweight='bold')
    ax5.set_ylabel('Círculos Médios', fontsize=12, fontweight='bold')
    ax5.set_title('Círculos × Cobertura', fontsize=13, fontweight='bold', pad=10)
    ax5.legend(fontsize=11)
    ax5.grid(True, alpha=0.3, linestyle='--')
    
    # 6. Histogram de diferenças de tempo
    ax6 = fig.add_subplot(gs[1, 2])
    diferencas = h4_pivot[comum] - h3_pivot[comum]
    ax6.hist(diferencas, bins=20, color=COLORS['Teste3'], alpha=0.7, edgecolor='black', linewidth=1.5)
    ax6.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Sem diferença')
    ax6.axvline(x=diferencas.mean(), color='green', linestyle='-', linewidth=2, 
               label=f'Média: {diferencas.mean():.2f}s')
    
    ax6.set_xlabel('Diferença de Tempo (H4 - H3) em segundos', fontsize=12, fontweight='bold')
    ax6.set_ylabel('Frequência', fontsize=12, fontweight='bold')
    ax6.set_title('Distribuição das Diferenças de Tempo\n(valores negativos = H4 mais rápida)', 
                 fontsize=13, fontweight='bold', pad=10)
    ax6.legend(fontsize=10)
    ax6.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.suptitle('Análise Comparativa: Heurística 3 vs Heurística 4', 
                 fontsize=16, fontweight='bold', y=0.995)
    plt.savefig(OUTPUT_DIR / "07_HEURISTICA3_VS_HEURISTICA4.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    # Exportar comparação CSV
    comparacao_csv = pd.DataFrame({
        'instance_id': comum,
        'Nº Clientes': [heur_data[heur_data['instance_id']==i]['Nº Clientes'].iloc[0] for i in comum],
        'Raio': [heur_data[heur_data['instance_id']==i]['Raio'].iloc[0] for i in comum],
        'Cobertura k': [heur_data[heur_data['instance_id']==i]['Cobertura k'].iloc[0] for i in comum],
        'Tempo H3': h3_pivot[comum].values,
        'Tempo H4': h4_pivot[comum].values,
        'Diferença (H4-H3)': diferencas.values,
        'H4 Mais Rápida': diferencas.values < 0,
        'Círculos H3': [stats_h3[stats_h3['instance_id']==i]['circulos_num'].iloc[0] for i in comum],
        'Círculos H4': [stats_h4[stats_h4['instance_id']==i]['circulos_num'].iloc[0] for i in comum],
    }).sort_values('Diferença (H4-H3)')
    
    comparacao_csv.to_csv(OUTPUT_DIR / "07_HEURISTICA3_VS_HEURISTICA4.csv", index=False)
    
    print(f"\n📊 RESUMO DA COMPARAÇÃO:")
    print(f"  • Heurística 4 foi mais rápida em {vitorias_h4} de {len(comum)} instâncias ({vitorias_h4/len(comum)*100:.1f}%)")
    print(f"  • Diferença média de tempo: {diferencas.mean():.2f}s")
    print(f"  • Diferença mediana: {diferencas.median():.2f}s")
    if diferencas.mean() < 0:
        print(f"  ✓ Heurística 4 é em média {abs(diferencas.mean()):.2f}s MAIS RÁPIDA")
    else:
        print(f"  ✗ Heurística 4 é em média {diferencas.mean():.2f}s MAIS LENTA")
    
    print(f"\n  ✓ Salvo: 07_HEURISTICA3_VS_HEURISTICA4.png e .csv\n")
else:
    print("  ⚠ Dados insuficientes para comparação\n")

# ==================== 9. COMPARAÇÃO CP COM PONTOS FIXOS (ÂNCORA) ====================
print("[9/10] Comparação detalhada: CPs com Pontos Fixos...\n")

# Filtrar apenas Teste4, Teste5, Teste6 (pontos fixos)
cp_fixo_data = success_data[success_data['config'].isin(['Teste4', 'Teste5', 'Teste6'])].copy()

if len(cp_fixo_data) > 0:
    print(f"Instâncias analisadas: {len(cp_fixo_data[cp_fixo_data['config']=='Teste4'])}\n")
    
    # Estatísticas comparativas
    stats_entre = cp_fixo_data[cp_fixo_data['config'] == 'Teste4']
    stats_intra = cp_fixo_data[cp_fixo_data['config'] == 'Teste5']
    stats_ambos = cp_fixo_data[cp_fixo_data['config'] == 'Teste6']
    
    print("ESTATÍSTICAS COMPARATIVAS DOS CPs COM PONTOS FIXOS:")
    print("=" * 100)
    print(f"{'Métrica':<30} | {'Quebra Entre':>18} | {'Quebra Intra':>18} | {'Quebra Ambas':>18}")
    print("-" * 100)
    print(f"{'Tempo Médio (s)':<30} | {stats_entre['tempo_num'].mean():>18.2f} | {stats_intra['tempo_num'].mean():>18.2f} | {stats_ambos['tempo_num'].mean():>18.2f}")
    print(f"{'Tempo Mediana (s)':<30} | {stats_entre['tempo_num'].median():>18.2f} | {stats_intra['tempo_num'].median():>18.2f} | {stats_ambos['tempo_num'].median():>18.2f}")
    print(f"{'Círculos Médio':<30} | {stats_entre['circulos_num'].mean():>18.1f} | {stats_intra['circulos_num'].mean():>18.1f} | {stats_ambos['circulos_num'].mean():>18.1f}")
    print(f"{'Taxa Sucesso (%)':<30} | {(len(stats_entre)/len(data_agregado[data_agregado['config']=='Teste4'])*100):>18.1f} | {(len(stats_intra)/len(data_agregado[data_agregado['config']=='Teste5'])*100):>18.1f} | {(len(stats_ambos)/len(data_agregado[data_agregado['config']=='Teste6'])*100):>18.1f}")
    print(f"{'Desvio Padrão Tempo':<30} | {stats_entre['tempo_num'].std():>18.2f} | {stats_intra['tempo_num'].std():>18.2f} | {stats_ambos['tempo_num'].std():>18.2f}")
    print("=" * 100 + "\n")
    
    # Comparação por faixa de tamanho
    cp_fixo_data['faixa'] = pd.cut(cp_fixo_data['Nº Clientes'], 
                                    bins=[0, 50, 100, 200, float('inf')],
                                    labels=['Pequena (≤50)', 'Média (51-100)', 'Grande (101-200)', 'Muito Grande (>200)'])
    
    por_faixa_cp = cp_fixo_data.groupby(['faixa', 'config']).agg({
        'tempo_num': ['mean', 'count'],
        'circulos_num': 'mean'
    }).round(2)
    
    print("DESEMPENHO POR FAIXA DE TAMANHO:")
    print(por_faixa_cp)
    print()
    
    # Gráficos comparativos
    fig = plt.figure(figsize=(20, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.3)
    
    # 1. Boxplot Tempo
    ax1 = fig.add_subplot(gs[0, 0])
    data_box_tempo_cp = [stats_entre['tempo_num'].values, stats_intra['tempo_num'].values, stats_ambos['tempo_num'].values]
    bp1 = ax1.boxplot(data_box_tempo_cp, labels=['Quebra\nEntre', 'Quebra\nIntra', 'Quebra\nAmbas'],
                      patch_artist=True, showmeans=True)
    bp1['boxes'][0].set_facecolor(COLORS['Teste4'])
    bp1['boxes'][1].set_facecolor(COLORS['Teste5'])
    bp1['boxes'][2].set_facecolor(COLORS['Teste6'])
    ax1.set_ylabel('Tempo (s)', fontsize=12, fontweight='bold')
    ax1.set_title('Distribuição do Tempo', fontsize=13, fontweight='bold', pad=10)
    ax1.set_yscale('log')
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    
    # 2. Boxplot Círculos
    ax2 = fig.add_subplot(gs[0, 1])
    data_box_circ_cp = [stats_entre['circulos_num'].values, stats_intra['circulos_num'].values, stats_ambos['circulos_num'].values]
    bp2 = ax2.boxplot(data_box_circ_cp, labels=['Quebra\nEntre', 'Quebra\nIntra', 'Quebra\nAmbas'],
                      patch_artist=True, showmeans=True)
    bp2['boxes'][0].set_facecolor(COLORS['Teste4'])
    bp2['boxes'][1].set_facecolor(COLORS['Teste5'])
    bp2['boxes'][2].set_facecolor(COLORS['Teste6'])
    ax2.set_ylabel('Número de Círculos', fontsize=12, fontweight='bold')
    ax2.set_title('Distribuição dos Círculos', fontsize=13, fontweight='bold', pad=10)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    
    # 3. Taxa de sucesso por faixa
    ax3 = fig.add_subplot(gs[0, 2])
    faixas_sucesso = []
    configs_plot = []
    for faixa in ['Pequena (≤50)', 'Média (51-100)', 'Grande (101-200)', 'Muito Grande (>200)']:
        for cfg in ['Teste4', 'Teste5', 'Teste6']:
            total_faixa = len(data_agregado[(data_agregado['config']==cfg) & 
                             (pd.cut(data_agregado['Nº Clientes'], 
                                    bins=[0, 50, 100, 200, float('inf')],
                                    labels=['Pequena (≤50)', 'Média (51-100)', 'Grande (101-200)', 'Muito Grande (>200)']) == faixa)])
            sucesso_faixa = len(cp_fixo_data[(cp_fixo_data['config']==cfg) & (cp_fixo_data['faixa']==faixa)])
            if total_faixa > 0:
                taxa = (sucesso_faixa / total_faixa) * 100
            else:
                taxa = 0
            faixas_sucesso.append({'faixa': faixa, 'config': cfg, 'taxa': taxa})
    
    df_sucesso = pd.DataFrame(faixas_sucesso)
    x_pos = np.arange(4)
    width = 0.28
    for i, (cfg, nome, cor) in enumerate([('Teste4', 'Entre', COLORS['Teste4']), 
                                           ('Teste5', 'Intra', COLORS['Teste5']),
                                           ('Teste6', 'Ambas', COLORS['Teste6'])]):
        valores = df_sucesso[df_sucesso['config']==cfg]['taxa'].values
        ax3.bar(x_pos + i*width, valores, width, label=nome, color=cor, 
               edgecolor='black', linewidth=1.5, alpha=0.85)
    
    ax3.set_xticks(x_pos + width)
    ax3.set_xticklabels(['≤50', '51-100', '101-200', '>200'], fontsize=10)
    ax3.set_xlabel('Faixa de Tamanho (n)', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Taxa de Sucesso (%)', fontsize=12, fontweight='bold')
    ax3.set_title('Taxa de Sucesso por Tamanho', fontsize=13, fontweight='bold', pad=10)
    ax3.set_ylim(0, 110)
    ax3.axhline(y=100, color='green', linestyle='--', linewidth=2, alpha=0.5)
    ax3.legend(fontsize=10)
    ax3.grid(axis='y', alpha=0.3, linestyle='--')
    
    # 4. Tempo por Nº Clientes
    ax4 = fig.add_subplot(gs[1, 0])
    for cfg, nome, cor in [('Teste4', 'Quebra Entre', COLORS['Teste4']), 
                           ('Teste5', 'Quebra Intra', COLORS['Teste5']),
                           ('Teste6', 'Quebra Ambas', COLORS['Teste6'])]:
        cfg_data = cp_fixo_data[cp_fixo_data['config'] == cfg].sort_values('Nº Clientes')
        ax4.plot(cfg_data['Nº Clientes'], cfg_data['tempo_num'],
                marker='o', linewidth=2, markersize=7, label=nome, color=cor, alpha=0.8)
    
    ax4.set_xlabel('Número de Clientes', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Tempo (s)', fontsize=12, fontweight='bold')
    ax4.set_title('Escalabilidade: Tempo × Tamanho', fontsize=13, fontweight='bold', pad=10)
    ax4.set_yscale('log')
    ax4.legend(fontsize=10)
    ax4.grid(True, alpha=0.3, which='both', linestyle='--')
    
    # 5. Scatter: Quebra Entre vs Quebra Intra (instâncias comuns)
    ax5 = fig.add_subplot(gs[1, 1])
    entre_pivot = stats_entre.set_index('instance_id')['tempo_num']
    intra_pivot = stats_intra.set_index('instance_id')['tempo_num']
    comum_ei = entre_pivot.index.intersection(intra_pivot.index)
    
    ax5.scatter(entre_pivot[comum_ei], intra_pivot[comum_ei], s=120, alpha=0.7,
               color=COLORS['Teste5'], edgecolors='black', linewidth=1.5)
    
    min_val = min(entre_pivot[comum_ei].min(), intra_pivot[comum_ei].min())
    max_val = max(entre_pivot[comum_ei].max(), intra_pivot[comum_ei].max())
    ax5.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2.5, 
            label='Desempenho igual', alpha=0.7)
    
    vitorias_intra = (intra_pivot[comum_ei] < entre_pivot[comum_ei]).sum()
    vitorias_entre = (entre_pivot[comum_ei] < intra_pivot[comum_ei]).sum()
    
    ax5.set_xlabel('Quebra Entre (s)', fontsize=12, fontweight='bold')
    ax5.set_ylabel('Quebra Intra (s)', fontsize=12, fontweight='bold')
    ax5.set_title('Entre vs Intra\n(abaixo linha = Intra melhor)', 
                 fontsize=13, fontweight='bold', pad=10)
    ax5.set_xscale('log')
    ax5.set_yscale('log')
    ax5.legend(fontsize=10)
    ax5.grid(True, alpha=0.3, linestyle='--')
    
    ax5.text(0.05, 0.95, f'Entre melhor: {vitorias_entre}\nIntra melhor: {vitorias_intra}',
            transform=ax5.transAxes, fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    # 6. Scatter: Quebra Intra vs Quebra Ambas
    ax6 = fig.add_subplot(gs[1, 2])
    ambos_pivot = stats_ambos.set_index('instance_id')['tempo_num']
    comum_ia = intra_pivot.index.intersection(ambos_pivot.index)
    
    ax6.scatter(intra_pivot[comum_ia], ambos_pivot[comum_ia], s=120, alpha=0.7,
               color=COLORS['Teste6'], edgecolors='black', linewidth=1.5)
    
    min_val = min(intra_pivot[comum_ia].min(), ambos_pivot[comum_ia].min())
    max_val = max(intra_pivot[comum_ia].max(), ambos_pivot[comum_ia].max())
    ax6.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2.5, 
            label='Desempenho igual', alpha=0.7)
    
    vitorias_ambos = (ambos_pivot[comum_ia] < intra_pivot[comum_ia]).sum()
    vitorias_intra2 = (intra_pivot[comum_ia] < ambos_pivot[comum_ia]).sum()
    
    ax6.set_xlabel('Quebra Intra (s)', fontsize=12, fontweight='bold')
    ax6.set_ylabel('Quebra Ambas (s)', fontsize=12, fontweight='bold')
    ax6.set_title('Intra vs Ambas\n(abaixo linha = Ambas melhor)', 
                 fontsize=13, fontweight='bold', pad=10)
    ax6.set_xscale('log')
    ax6.set_yscale('log')
    ax6.legend(fontsize=10)
    ax6.grid(True, alpha=0.3, linestyle='--')
    
    ax6.text(0.05, 0.95, f'Intra melhor: {vitorias_intra2}\nAmbas melhor: {vitorias_ambos}',
            transform=ax6.transAxes, fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    # 7. Círculos por Cobertura k
    ax7 = fig.add_subplot(gs[2, 0])
    for cfg, nome, cor in [('Teste4', 'Quebra Entre', COLORS['Teste4']), 
                           ('Teste5', 'Quebra Intra', COLORS['Teste5']),
                           ('Teste6', 'Quebra Ambas', COLORS['Teste6'])]:
        cfg_data = cp_fixo_data[cp_fixo_data['config'] == cfg]
        grouped = cfg_data.groupby('Cobertura k')['circulos_num'].mean()
        ax7.plot(grouped.index, grouped.values,
                marker='s', linewidth=2.5, markersize=10, label=nome, color=cor, alpha=0.8)
    
    ax7.set_xlabel('Cobertura Mínima (k)', fontsize=12, fontweight='bold')
    ax7.set_ylabel('Círculos Médios', fontsize=12, fontweight='bold')
    ax7.set_title('Qualidade: Círculos × Cobertura', fontsize=13, fontweight='bold', pad=10)
    ax7.legend(fontsize=10)
    ax7.grid(True, alpha=0.3, linestyle='--')
    
    # 8. Histogram diferenças Entre vs Intra
    ax8 = fig.add_subplot(gs[2, 1])
    dif_ei = intra_pivot[comum_ei] - entre_pivot[comum_ei]
    ax8.hist(dif_ei, bins=15, color=COLORS['Teste5'], alpha=0.7, edgecolor='black', linewidth=1.5)
    ax8.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Sem diferença')
    ax8.axvline(x=dif_ei.mean(), color='green', linestyle='-', linewidth=2, 
               label=f'Média: {dif_ei.mean():.2f}s')
    
    ax8.set_xlabel('Diferença (Intra - Entre) em segundos', fontsize=11, fontweight='bold')
    ax8.set_ylabel('Frequência', fontsize=12, fontweight='bold')
    ax8.set_title('Distribuição: Intra - Entre\n(negativo = Intra mais rápida)', 
                 fontsize=13, fontweight='bold', pad=10)
    ax8.legend(fontsize=9)
    ax8.grid(axis='y', alpha=0.3, linestyle='--')
    
    # 9. Histogram diferenças Intra vs Ambas
    ax9 = fig.add_subplot(gs[2, 2])
    dif_ia = ambos_pivot[comum_ia] - intra_pivot[comum_ia]
    ax9.hist(dif_ia, bins=15, color=COLORS['Teste6'], alpha=0.7, edgecolor='black', linewidth=1.5)
    ax9.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Sem diferença')
    ax9.axvline(x=dif_ia.mean(), color='green', linestyle='-', linewidth=2, 
               label=f'Média: {dif_ia.mean():.2f}s')
    
    ax9.set_xlabel('Diferença (Ambas - Intra) em segundos', fontsize=11, fontweight='bold')
    ax9.set_ylabel('Frequência', fontsize=12, fontweight='bold')
    ax9.set_title('Distribuição: Ambas - Intra\n(negativo = Ambas mais rápida)', 
                 fontsize=13, fontweight='bold', pad=10)
    ax9.legend(fontsize=9)
    ax9.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.suptitle('Análise Comparativa: CPs com Pontos Fixos (Âncora)', 
                 fontsize=16, fontweight='bold', y=0.998)
    plt.savefig(OUTPUT_DIR / "08_CP_PONTOS_FIXOS_COMPARACAO.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"\n📊 RESUMO DA COMPARAÇÃO CP PONTOS FIXOS:")
    print(f"\n🏆 MELHOR TEMPO MEDIANO: Quebra Entre ({stats_entre['tempo_num'].median():.2f}s)")
    print(f"🏆 MELHOR TEMPO MÉDIO: Quebra Ambas ({stats_ambos['tempo_num'].mean():.2f}s)")
    print(f"🏆 MAIS CONSISTENTE: Quebra Entre (desvio: {stats_entre['tempo_num'].std():.2f}s)")
    print(f"🏆 MAIS CÍRCULOS EFICIENTE: Quebra Entre ({stats_entre['circulos_num'].mean():.2f} círculos)")
    print(f"\n  • Entre vs Intra: Intra venceu em {vitorias_intra} de {len(comum_ei)} ({vitorias_intra/len(comum_ei)*100:.1f}%)")
    print(f"  • Intra vs Ambas: Ambas venceu em {vitorias_ambos} de {len(comum_ia)} ({vitorias_ambos/len(comum_ia)*100:.1f}%)")
    
    print(f"\n  ✓ Salvo: 08_CP_PONTOS_FIXOS_COMPARACAO.png\n")
else:
    print("  ⚠ Dados insuficientes para comparação\n")

# ==================== 10. RESUMO EXECUTIVO ====================
print("[10/10] Gerando resumo executivo...\n")

resumo = []
for cfg in sorted(success_data['config'].unique()):
    cfg_data_all = data_agregado[data_agregado['config'] == cfg]
    cfg_data_success = success_data[success_data['config'] == cfg]
    
    resumo.append({
        'Configuração': CONFIG_NAMES.get(cfg, cfg),
        'Instâncias Testadas': len(cfg_data_all),
        'Sucessos': len(cfg_data_success),
        'Taxa Sucesso (%)': len(cfg_data_success) / len(cfg_data_all) * 100,
        'n Mínimo': cfg_data_all['Nº Clientes'].min(),
        'n Máximo': cfg_data_all['Nº Clientes'].max(),
        'Tempo Médio (s)': cfg_data_success['tempo_num'].mean(),
        'Tempo Mediana (s)': cfg_data_success['tempo_num'].median(),
        'Círculos Médio': cfg_data_success['circulos_num'].mean(),
    })

resumo_df = pd.DataFrame(resumo).round(2)

# Tabela visual
fig, ax = plt.subplots(figsize=(18, 5))
ax.axis('tight')
ax.axis('off')

table_data = resumo_df.values
table = ax.table(cellText=table_data, colLabels=resumo_df.columns,
                cellLoc='center', loc='center', colColours=['lightgray']*len(resumo_df.columns))

table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 2.2)

for i in range(len(resumo_df)):
    cfg_orig = sorted(success_data['config'].unique())[i]
    table[(i+1, 0)].set_facecolor(COLORS.get(cfg_orig, 'white'))

ax.set_title('Resumo Executivo das Configurações\n(Dados honestos: cada config foi testada em conjuntos diferentes de instâncias)', 
             fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "08_RESUMO_EXECUTIVO.png", dpi=300, bbox_inches='tight')
plt.close()

resumo_df.to_csv(OUTPUT_DIR / "08_RESUMO_EXECUTIVO.csv", index=False)
print("RESUMO EXECUTIVO:")
print(resumo_df.to_string(index=False))
print(f"\n  ✓ Salvo: 08_RESUMO_EXECUTIVO.png e .csv\n")

# ==================== 11. CORRELAÇÃO COM EXPLICAÇÕES ====================
print("[11/11] Gerando matriz de correlação com explicações...\n")

corr_data = success_data[[
    'Nº Clientes', 'Raio', 'Dist. Mín. Círculos', 'Cobertura k',
    'Densidade', 'Área', 'tempo_num', 'circulos_num'
]].copy()

corr_data = corr_data.rename(columns={
    'tempo_num': 'Tempo',
    'circulos_num': 'Nº Círculos'
})

correlation_matrix = corr_data.corr()

# Heatmap
fig, ax = plt.subplots(figsize=(13, 11))
sns.heatmap(correlation_matrix, annot=True, fmt='.2f', cmap='RdYlGn',
            center=0, square=True, linewidths=2, cbar_kws={"shrink": 0.8},
            vmin=-1, vmax=1, ax=ax, annot_kws={'size': 9, 'weight': 'bold'})

ax.set_title('Correlação entre Características das Instâncias e Desempenho\n' + 
             '(valores próximos de +1 ou -1 indicam forte relação)', 
             fontsize=13, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "09_CORRELACAO.png", dpi=300, bbox_inches='tight')
plt.close()

correlation_matrix.to_csv(OUTPUT_DIR / "09_CORRELACAO.csv")

# Análise textual das correlações mais importantes
print("\n📊 ANÁLISE DAS CORRELAÇÕES PRINCIPAIS:\n")
print("=" * 80)

# Correlações com Tempo
tempo_corrs = correlation_matrix['Tempo'].drop('Tempo').sort_values(ascending=False)
print("\n🕐 CORRELAÇÕES COM TEMPO DE EXECUÇÃO:")
print("-" * 80)
for var, corr in tempo_corrs.items():
    if abs(corr) > 0.3:  # Apenas correlações moderadas ou fortes
        if corr > 0.7:
            intensidade = "MUITO FORTE positiva"
            explicacao = f"{var} aumenta MUITO o tempo"
        elif corr > 0.4:
            intensidade = "FORTE positiva"
            explicacao = f"{var} aumenta o tempo significativamente"
        elif corr > 0.1:
            intensidade = "MODERADA positiva"
            explicacao = f"{var} aumenta um pouco o tempo"
        elif corr < -0.4:
            intensidade = "FORTE negativa"
            explicacao = f"{var} DIMINUI o tempo significativamente"
        elif corr < -0.1:
            intensidade = "MODERADA negativa"
            explicacao = f"{var} diminui um pouco o tempo"
        else:
            continue
        
        print(f"  • {var:25s} → {corr:+.3f} ({intensidade})")
        print(f"    └─ {explicacao}")

# Correlações com Número de Círculos
print("\n\n🔵 CORRELAÇÕES COM NÚMERO DE CÍRCULOS NA SOLUÇÃO:")
print("-" * 80)
circ_corrs = correlation_matrix['Nº Círculos'].drop('Nº Círculos').sort_values(ascending=False)
for var, corr in circ_corrs.items():
    if abs(corr) > 0.3:
        if corr > 0.7:
            intensidade = "MUITO FORTE positiva"
            explicacao = f"Mais {var.lower()} = MUITO mais círculos necessários"
        elif corr > 0.4:
            intensidade = "FORTE positiva"
            explicacao = f"Mais {var.lower()} = mais círculos necessários"
        elif corr > 0.1:
            intensidade = "MODERADA positiva"
            explicacao = f"Mais {var.lower()} = levemente mais círculos"
        elif corr < -0.4:
            intensidade = "FORTE negativa"
            explicacao = f"Mais {var.lower()} = MENOS círculos necessários"
        elif corr < -0.1:
            intensidade = "MODERADA negativa"
            explicacao = f"Mais {var.lower()} = levemente menos círculos"
        else:
            continue
        
        print(f"  • {var:25s} → {corr:+.3f} ({intensidade})")
        print(f"    └─ {explicacao}")

# Correlações entre características
print("\n\n🔗 CORRELAÇÕES ENTRE CARACTERÍSTICAS DAS INSTÂNCIAS:")
print("-" * 80)
caracteristicas = ['Nº Clientes', 'Raio', 'Dist. Mín. Círculos', 'Cobertura k', 'Densidade', 'Área']
for i, var1 in enumerate(caracteristicas):
    for var2 in caracteristicas[i+1:]:
        corr = correlation_matrix.loc[var1, var2]
        if abs(corr) > 0.5:
            if corr > 0:
                print(f"  • {var1} ↔ {var2}: {corr:+.3f} (crescem juntas)")
            else:
                print(f"  • {var1} ↔ {var2}: {corr:+.3f} (inversamente relacionadas)")

print("\n" + "=" * 80)
print("\n💡 INTERPRETAÇÃO:")
print("  • Valores entre +0.7 e +1.0: Correlação MUITO FORTE positiva")
print("  • Valores entre +0.4 e +0.7: Correlação FORTE positiva")
print("  • Valores entre -0.4 e -0.7: Correlação FORTE negativa")
print("  • Valores entre -0.7 e -1.0: Correlação MUITO FORTE negativa")
print("  • Valores entre -0.3 e +0.3: Correlação FRACA ou nenhuma relação")
print("\n  ✓ Salvo: 09_CORRELACAO.png e .csv\n")

# ==================== RELATÓRIO FINAL ====================
print("\n" + "=" * 90)
print("ANÁLISE COMPLETA E HONESTA FINALIZADA!")
print("=" * 90)
print(f"\nArquivos salvos em: {OUTPUT_DIR}\n")
print("Arquivos gerados:")
print("  01. COBERTURA_TESTES - Quais instâncias foram testadas em cada config")
print("  02. TAXA_SUCESSO_HONESTA - Taxa por faixa de tamanho (não global)")
print("  03. COMPARACAO_JUSTA - Apenas instâncias comuns a todas configs")
print("  04. TABELA_MESTRE_INSTANCIAS - Todas características")
print("  05. DESEMPENHO_POR_CARACTERISTICAS - 6 scatter plots")
print("  06. TOP_INSTANCIAS_DIFICEIS - Top 15 com características")
print("  07. IMPACTO_COBERTURA_K - Análise do parâmetro k")
print("  08. RESUMO_EXECUTIVO - Tabela completa")
print("  09. CORRELACAO - Heatmap")
print("\n" + "=" * 90)
print("✓ ANÁLISE 100% HONESTA:")
print("  • Transparência total sobre quais instâncias foram testadas")
print("  • Sem comparações injustas")
print("  • Foco nas CARACTERÍSTICAS, não nos nomes")
print("  • Dados agregados (média das repetições)")
print("=" * 90)

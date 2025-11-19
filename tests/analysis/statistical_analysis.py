"""
Análise Estatística Avançada - Circle Coverage
Testes estatísticos e análises adicionais para o TCC
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy import stats
from scipy.stats import mannwhitneyu, friedmanchisquare, wilcoxon

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
data = results_df.merge(instances_df, on='instance_id', how='left')

data['tempo_num'] = pd.to_numeric(data['tempo'], errors='coerce')
data['numCirculos_num'] = pd.to_numeric(data['numCirculos'], errors='coerce')
success_data = data[data['status'] == 'SUCCESS'].copy()

print("=" * 80)
print("ANÁLISE ESTATÍSTICA AVANÇADA")
print("=" * 80)

# ==================== 1. TESTE DE NORMALIDADE ====================
print("\n[1/5] Teste de Normalidade (Shapiro-Wilk)...")

normalidade = []
for cfg in success_data['config'].unique():
    tempos = success_data[success_data['config'] == cfg]['tempo_num'].dropna()
    if len(tempos) >= 3:
        stat, p_value = stats.shapiro(tempos)
        normalidade.append({
            'Configuração': cfg,
            'Estatística': f"{stat:.4f}",
            'p-valor': f"{p_value:.4f}",
            'Normal?': 'Sim' if p_value > 0.05 else 'Não',
            'N amostras': len(tempos)
        })

normalidade_df = pd.DataFrame(normalidade)
normalidade_df.to_csv(OUTPUT_DIR / "8_teste_normalidade.csv", index=False)
print(normalidade_df.to_string(index=False))
print(f"  ✓ Salvo: 8_teste_normalidade.csv")

# ==================== 2. TESTE DE FRIEDMAN (Configurações relacionadas) ====================
print("\n[2/5] Teste de Friedman (comparação múltipla)...")

# Apenas instâncias com todas configs bem-sucedidas
pivot = success_data.pivot_table(index='instance_id', columns='config', 
                                  values='tempo_num', aggfunc='mean')
pivot_completo = pivot.dropna()

if len(pivot_completo) >= 3:
    configs_disponiveis = [c for c in pivot_completo.columns]
    dados_friedman = [pivot_completo[cfg].values for cfg in configs_disponiveis]
    
    stat, p_value = friedmanchisquare(*dados_friedman)
    
    friedman_result = {
        'Teste': 'Friedman',
        'Estatística': f"{stat:.4f}",
        'p-valor': f"{p_value:.6f}",
        'Significativo?': 'Sim (há diferenças)' if p_value < 0.05 else 'Não',
        'N instâncias': len(pivot_completo),
        'Configs comparadas': ', '.join(configs_disponiveis)
    }
    
    pd.DataFrame([friedman_result]).to_csv(OUTPUT_DIR / "9_teste_friedman.csv", index=False)
    print(f"  Estatística: {stat:.4f}, p-valor: {p_value:.6f}")
    print(f"  Resultado: {'Diferenças significativas' if p_value < 0.05 else 'Sem diferenças significativas'}")
    print(f"  ✓ Salvo: 9_teste_friedman.csv")
else:
    print("  ⚠ Dados insuficientes para teste de Friedman")

# ==================== 3. COMPARAÇÕES PAREADAS (Mann-Whitney U) ====================
print("\n[3/5] Testes de Mann-Whitney U (comparações pareadas)...")

comparacoes = []
configs = success_data['config'].unique()

for i, cfg1 in enumerate(configs):
    for cfg2 in configs[i+1:]:
        tempo1 = success_data[success_data['config'] == cfg1]['tempo_num'].dropna()
        tempo2 = success_data[success_data['config'] == cfg2]['tempo_num'].dropna()
        
        if len(tempo1) >= 3 and len(tempo2) >= 3:
            stat, p_value = mannwhitneyu(tempo1, tempo2, alternative='two-sided')
            
            comparacoes.append({
                'Comparação': f"{cfg1} vs {cfg2}",
                'Mediana 1': f"{tempo1.median():.2f}s",
                'Mediana 2': f"{tempo2.median():.2f}s",
                'Estatística U': f"{stat:.2f}",
                'p-valor': f"{p_value:.6f}",
                'Significativo?': 'Sim' if p_value < 0.05 else 'Não',
                'N1': len(tempo1),
                'N2': len(tempo2)
            })

comparacoes_df = pd.DataFrame(comparacoes)
comparacoes_df = comparacoes_df.sort_values('p-valor')
comparacoes_df.to_csv(OUTPUT_DIR / "10_comparacoes_pareadas.csv", index=False)
print(f"  {len(comparacoes)} comparações realizadas")
print(f"  ✓ Salvo: 10_comparacoes_pareadas.csv")

# Visualização das comparações
if len(comparacoes) > 0:
    fig, ax = plt.subplots(figsize=(12, max(6, len(comparacoes) * 0.4)))
    
    y_pos = np.arange(len(comparacoes_df))
    colors = ['red' if comp == 'Sim' else 'green' for comp in comparacoes_df['Significativo?']]
    p_values = comparacoes_df['p-valor'].astype(float)
    
    bars = ax.barh(y_pos, -np.log10(p_values), color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(comparacoes_df['Comparação'], fontsize=10)
    ax.set_xlabel('-log10(p-valor)', fontsize=12, fontweight='bold')
    ax.set_title('Significância Estatística das Comparações Pareadas', fontsize=14, fontweight='bold', pad=20)
    ax.axvline(x=-np.log10(0.05), color='black', linestyle='--', linewidth=2, label='α = 0.05')
    ax.legend()
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    
    # Legenda
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='red', alpha=0.7, edgecolor='black', label='Significativo (p < 0.05)'),
        Patch(facecolor='green', alpha=0.7, edgecolor='black', label='Não significativo')
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "10_comparacoes_pareadas.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Salvo: 10_comparacoes_pareadas.png")

# ==================== 4. CORRELAÇÃO ENTRE PARÂMETROS ====================
print("\n[4/5] Análise de correlação entre parâmetros...")

# Selecionar variáveis numéricas
correlacao_vars = ['nClientes', 'raio', 'minDistCirculos', 'minCoverage', 
                   'tempo_num', 'numCirculos_num']
corr_data = success_data[correlacao_vars].dropna()

if len(corr_data) > 10:
    correlation_matrix = corr_data.corr()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, fmt='.3f', cmap='coolwarm', 
                center=0, square=True, linewidths=1, cbar_kws={"shrink": 0.8},
                vmin=-1, vmax=1, ax=ax)
    
    ax.set_title('Matriz de Correlação (Pearson)', fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "11_correlacao_parametros.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    correlation_matrix.to_csv(OUTPUT_DIR / "11_correlacao_parametros.csv")
    print(f"  ✓ Salvo: 11_correlacao_parametros.png e .csv")

# ==================== 5. ANÁLISE DE VARIABILIDADE (Repetições) ====================
print("\n[5/5] Análise de variabilidade entre repetições...")

# Calcular CV (coeficiente de variação) para cada instância e config
variabilidade = success_data.groupby(['instance_id', 'config']).agg({
    'tempo_num': ['mean', 'std', 'count']
}).reset_index()
variabilidade.columns = ['instance_id', 'config', 'media', 'desvio', 'n_repeticoes']
variabilidade['cv_percent'] = (variabilidade['desvio'] / variabilidade['media'] * 100).round(2)
variabilidade = variabilidade[variabilidade['n_repeticoes'] >= 2]  # Só com múltiplas repetições

cv_summary = variabilidade.groupby('config')['cv_percent'].agg(['mean', 'median', 'std', 'max']).reset_index()
cv_summary.columns = ['Configuração', 'CV Médio (%)', 'CV Mediana (%)', 'CV Desvio (%)', 'CV Máximo (%)']
cv_summary = cv_summary.round(2)

fig, ax = plt.subplots(figsize=(12, 6))

x = np.arange(len(cv_summary))
bars = ax.bar(x, cv_summary['CV Médio (%)'], 
              color=[COLORS[c] for c in cv_summary['Configuração']],
              edgecolor='black', linewidth=1.5, alpha=0.8)

# Adicionar barras de erro (desvio)
ax.errorbar(x, cv_summary['CV Médio (%)'], yerr=cv_summary['CV Desvio (%)'],
            fmt='none', ecolor='black', capsize=5, capthick=2)

for bar, max_cv in zip(bars, cv_summary['CV Máximo (%)']):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.1f}%\n(max:{max_cv:.1f}%)', 
            ha='center', va='bottom', fontsize=9, fontweight='bold')

ax.set_ylabel('Coeficiente de Variação (%)', fontsize=12, fontweight='bold')
ax.set_xlabel('Configuração', fontsize=12, fontweight='bold')
ax.set_title('Variabilidade do Tempo de Execução (entre repetições)', 
             fontsize=14, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(cv_summary['Configuração'])
ax.grid(axis='y', alpha=0.3, linestyle='--')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "12_variabilidade_repeticoes.png", dpi=300, bbox_inches='tight')
plt.close()

cv_summary.to_csv(OUTPUT_DIR / "12_variabilidade_repeticoes.csv", index=False)
print(f"  ✓ Salvo: 12_variabilidade_repeticoes.png e .csv")

# ==================== RELATÓRIO FINAL ====================
print("\n" + "=" * 80)
print("ANÁLISE ESTATÍSTICA COMPLETA")
print("=" * 80)
print(f"\nArquivos salvos em: {OUTPUT_DIR}")
print("\nArquivos gerados:")
print("  8.  8_teste_normalidade.csv")
print("  9.  9_teste_friedman.csv")
print("  10. 10_comparacoes_pareadas.png / .csv")
print("  11. 11_correlacao_parametros.png / .csv")
print("  12. 12_variabilidade_repeticoes.png / .csv")
print("\n" + "=" * 80)
print("✓ Análise estatística concluída!")
print("=" * 80)

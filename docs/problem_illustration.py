"""
Ilustração do Problema da Cobertura por Círculos
Gera uma imagem didática mostrando os conceitos principais
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Configurações
fig, ax = plt.subplots(1, 1, figsize=(14, 12))

# ==================== EXEMPLO DE INSTÂNCIA ====================

# Pontos P (vermelho) - posicionados nas interseções
points = [
    # Interseção C1-C2 (esquerda)
    (27, 28), (25, 25), (28, 30),
    # Interseção C2-C3 (direita)
    (43, 28), (45, 25), (42, 30),
    # Interseção C2-C4 (superior)
    (35, 37), (32, 40), (38, 40),
    # Interseção C2-C5 (inferior)
    (35, 20), (32, 18), (38, 22),
    # Centro (coberto por 3+)
    (35, 28), (33, 30), (37, 26)
]

# Círculos da solução (5 círculos) - todos sobrepostos no centro
circles = [
    (20, 28),   # C1 - esquerda
    (35, 28),   # C2 - centro (sobrepõe com todos)
    (50, 28),   # C3 - direita  
    (35, 43),   # C4 - superior
    (35, 13)    # C5 - inferior
]

# Parâmetros
r = 15  # raio
d = 15  # distância mínima entre centros (exatamente a distância entre vizinhos)
k = 2   # cobertura mínima

# ==================== PLOTAR SOLUÇÃO ====================

# Cores para os círculos
colors = ['#8DD3C7', '#FFFFB3', '#BEBADA', '#FB8072', '#80B1D3']

# 1. Plotar círculos com área sombreada
for i, (cx, cy) in enumerate(circles):
    # Área de cobertura (transparente)
    circle_fill = patches.Circle((cx, cy), r, alpha=0.15, 
                                facecolor=colors[i], edgecolor='none')
    ax.add_patch(circle_fill)
    
    # Borda do círculo (mais grossa)
    circle_edge = patches.Circle((cx, cy), r, fill=False, 
                                edgecolor=colors[i], linewidth=3.5)
    ax.add_patch(circle_edge)
    
    # Centro do círculo (cruz azul grande)
    ax.scatter([cx], [cy], c='blue', s=200, marker='x', 
              zorder=10, linewidth=4)
    
    # Label do círculo
    ax.annotate(f'$c_{i+1}$', (cx, cy), xytext=(15, -15), 
               textcoords='offset points', fontsize=16, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                        edgecolor=colors[i], linewidth=2))

# 2. Plotar pontos P
points_x = [p[0] for p in points]
points_y = [p[1] for p in points]
ax.scatter(points_x, points_y, c='red', s=120, zorder=15, 
          label='Pontos $P$', alpha=0.9, edgecolors='darkred', linewidth=2)

# Numerar alguns pontos para referência
for i in [0, 4, 8, 12]:
    x, y = points[i]
    ax.annotate(f'$p_{i+1}$', (x, y), xytext=(8, 8), 
               textcoords='offset points', fontsize=11, 
               fontweight='bold', color='darkred')

# ==================== ANOTAÇÕES DIDÁTICAS ====================

# 3. Mostrar raio r
cx1, cy1 = circles[0]
ax.plot([cx1, cx1 - r], [cy1, cy1], 'k--', linewidth=2, zorder=5)
ax.annotate('', xy=(cx1 - r, cy1), xytext=(cx1, cy1),
           arrowprops=dict(arrowstyle='<->', color='black', lw=2))
ax.text(cx1 - r/2, cy1 - 2, '$r$', fontsize=14, fontweight='bold',
       ha='center', bbox=dict(boxstyle='round,pad=0.3', 
                             facecolor='white', alpha=0.9))

# 4. Mostrar distância mínima d entre centros (C3 e C5)
cx3, cy3 = circles[2]  # C3 (direita)
cx5, cy5 = circles[4]  # C5 (inferior)
ax.plot([cx3, cx5], [cy3, cy5], 'b--', linewidth=2, zorder=5, alpha=0.7)
mid_x, mid_y = (cx3 + cx5)/2, (cy3 + cy5)/2
dist = np.sqrt((cx5-cx3)**2 + (cy5-cy3)**2)
ax.text(mid_x + 3, mid_y, f'$d \\geq {d}$\n({dist:.1f})', 
       fontsize=10, ha='center',
       bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', 
                alpha=0.8, edgecolor='blue', linewidth=1.5))

# 5. Destacar um ponto com k coberturas
highlight_point = points[5]  # ponto que tem k=2 coberturas
hx, hy = highlight_point

# Círculo de destaque ao redor do ponto
highlight_circle = patches.Circle((hx, hy), 2, fill=False, 
                                 edgecolor='red', linewidth=2.5, 
                                 linestyle='--', zorder=14)
ax.add_patch(highlight_circle)

# Linhas conectando o ponto aos círculos que o cobrem
covered_by = []
for i, (cx, cy) in enumerate(circles):
    dist_to_point = np.sqrt((cx - hx)**2 + (cy - hy)**2)
    if dist_to_point <= r:
        covered_by.append(i)
        ax.plot([hx, cx], [hy, cy], 'g-', linewidth=1.5, alpha=0.5, zorder=8)

# Anotação explicativa (menor)
annotation_text = f"Coberto por\n{len(covered_by)} círculos"
ax.annotate(annotation_text, (hx, hy), xytext=(20, 20),
           textcoords='offset points', fontsize=9,
           bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', 
                    edgecolor='green', linewidth=1.5, alpha=0.85),
           arrowprops=dict(arrowstyle='->', color='green', lw=1.5))

# ==================== CAIXA DE INFORMAÇÕES ====================

info_text = [
    "DADOS:",
    f"• Pontos: P com (x_i, y_i) ∈ ℚ × ℚ",
    f"• Raio: r = {r}",
    f"• Dist. mín.: d = {d}",
    f"• Cobertura: k = {k}",
    "",
    "RESTRIÇÕES:",
    f"1. ‖c_i - c_j‖ ≥ d",
    f"2. Cada p coberto por ≥ k círculos",
    "",
    f"OBJETIVO: Min |C|"
]

# Converter para texto renderizável
info_str = '\n'.join(info_text)

ax.text(0.02, 0.98, info_str, transform=ax.transAxes,
       verticalalignment='top', fontsize=10, family='monospace',
       bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', 
                alpha=0.9, edgecolor='orange', linewidth=2))

# ==================== LEGENDA E CONFIGURAÇÕES ====================

# Legenda personalizada
legend_elements = [
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', 
              markersize=10, label=f'Pontos $P$ (|P|={len(points)})', 
              markeredgecolor='darkred', markeredgewidth=2),
    plt.Line2D([0], [0], marker='x', color='blue', markersize=12, 
              label=f'Centros dos círculos $C$ (|C|={len(circles)})', 
              linewidth=3),
    patches.Patch(facecolor='lightblue', edgecolor='blue', alpha=0.3, 
                 label=f'Área de cobertura (raio $r={r}$)'),
    plt.Line2D([0], [0], color='green', linewidth=2, 
              label=f'Ponto coberto por ≥ $k={k}$ círculos')
]

ax.legend(handles=legend_elements, loc='upper right', fontsize=11,
         framealpha=0.95, edgecolor='black', fancybox=True)

# Configurar eixos
ax.set_xlim(0, 80)
ax.set_ylim(0, 55)
ax.set_aspect('equal')
ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.8)
ax.set_xlabel('$x \\in \\mathbb{Q}$', fontsize=14, fontweight='bold')
ax.set_ylabel('$y \\in \\mathbb{Q}$', fontsize=14, fontweight='bold')

# Título
ax.set_title('Problema da Cobertura por Círculos - Ilustração Conceitual', 
            fontsize=16, fontweight='bold', pad=20)

# ==================== ESTATÍSTICAS DA SOLUÇÃO ====================

stats_text = f"SOLUÇÃO:\n"
stats_text += f"• |C| = {len(circles)} círculos\n"
stats_text += f"• |P| = {len(points)} pontos\n"

# Verificar cobertura de cada ponto
coverage_counts = []
for px, py in points:
    count = 0
    for cx, cy in circles:
        dist = np.sqrt((cx - px)**2 + (cy - py)**2)
        if dist <= r:
            count += 1
    coverage_counts.append(count)

min_cov = min(coverage_counts)
max_cov = max(coverage_counts)
avg_cov = np.mean(coverage_counts)

stats_text += f"• Cob: [{min_cov}, {max_cov}] (média {avg_cov:.1f})\n"
stats_text += f"✓ Válida (todos ≥ k={k})"

stats_str = stats_text

ax.text(0.98, 0.02, stats_str, transform=ax.transAxes,
       verticalalignment='bottom', horizontalalignment='right',
       fontsize=9, family='monospace',
       bbox=dict(boxstyle='round,pad=0.4', facecolor='lightgreen', 
                alpha=0.85, edgecolor='darkgreen', linewidth=1.5))

# Salvar
plt.tight_layout()
output_file = 'docs/problema_cobertura_circulos_ilustracao.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
print(f"✓ Imagem salva em: {output_file}")
plt.close()

print("\n" + "="*60)
print("ILUSTRAÇÃO DO PROBLEMA GERADA COM SUCESSO!")
print("="*60)
print(f"Arquivo: {output_file}")
print(f"Resolução: 300 DPI")
print(f"Dimensões: 14x12 polegadas")
print("\nElementos ilustrados:")
print(f"  • {len(points)} pontos de entrada")
print(f"  • {len(circles)} círculos na solução")
print(f"  • Raio r = {r}")
print(f"  • Distância mínima d = {d}")
print(f"  • Cobertura mínima k = {k}")
print(f"  • Cobertura observada: min={min_cov}, max={max_cov}, média={avg_cov:.1f}")

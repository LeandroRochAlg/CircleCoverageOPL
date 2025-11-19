"""
Gerador de Relatório LaTeX - Circle Coverage
Cria um relatório completo em LaTeX para inclusão no TCC
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

# Configurações
SCRIPT_DIR = Path(__file__).parent
TABLES_DIR = SCRIPT_DIR.parent / "tables"
RESULTS_DIR = SCRIPT_DIR / "results"
OUTPUT_TEX = RESULTS_DIR / "relatorio_benchmark.tex"

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

# Estatísticas gerais
n_instances = len(instances_df)
n_executions = len(results_df)
n_configs = data['config'].nunique()
success_rate_global = (data['status'] == 'SUCCESS').sum() / len(data) * 100

# Resumo por configuração
resumo = []
for cfg in sorted(data['config'].unique()):
    cfg_data = data[data['config'] == cfg]
    success_cfg = cfg_data[cfg_data['status'] == 'SUCCESS']
    
    resumo.append({
        'config': cfg,
        'total': len(cfg_data),
        'success': len(success_cfg),
        'success_rate': len(success_cfg)/len(cfg_data)*100,
        'tempo_mean': success_cfg['tempo_num'].mean() if len(success_cfg) > 0 else 0,
        'tempo_median': success_cfg['tempo_num'].median() if len(success_cfg) > 0 else 0,
        'tempo_std': success_cfg['tempo_num'].std() if len(success_cfg) > 0 else 0,
        'circulos_mean': success_cfg['numCirculos_num'].mean() if len(success_cfg) > 0 else 0,
        'circulos_min': success_cfg['numCirculos_num'].min() if len(success_cfg) > 0 else 0,
        'circulos_max': success_cfg['numCirculos_num'].max() if len(success_cfg) > 0 else 0,
    })

resumo_df = pd.DataFrame(resumo)

# Gerar LaTeX
latex_content = r"""\documentclass[12pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[brazilian]{babel}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{float}
\usepackage{geometry}
\usepackage{hyperref}
\usepackage{caption}

\geometry{margin=2.5cm}

\title{Relatório de Benchmark\\Circle Coverage Problem}
\author{Análise Automatizada}
\date{""" + datetime.now().strftime("%d de %B de %Y") + r"""}

\begin{document}

\maketitle
\tableofcontents
\newpage

\section{Resumo Executivo}

Este relatório apresenta a análise detalhada dos resultados obtidos no benchmark automatizado 
do problema Circle Coverage. O benchmark foi executado em """ + str(n_instances) + r""" instâncias 
distintas, testando """ + str(n_configs) + r""" configurações diferentes, totalizando """ + str(n_executions) + r""" execuções.

\subsection{Estatísticas Gerais}

\begin{itemize}
    \item \textbf{Total de Instâncias:} """ + str(n_instances) + r"""
    \item \textbf{Total de Execuções:} """ + str(n_executions) + r"""
    \item \textbf{Configurações Testadas:} """ + str(n_configs) + r"""
    \item \textbf{Taxa de Sucesso Global:} """ + f"{success_rate_global:.1f}" + r"""\%
\end{itemize}

\section{Resultados por Configuração}

\subsection{Tabela Resumo}

A Tabela~\ref{tab:resumo} apresenta as estatísticas de desempenho para cada configuração testada.

\begin{table}[H]
\centering
\caption{Resumo de Desempenho por Configuração}
\label{tab:resumo}
\small
\begin{tabular}{lrrrrrr}
\toprule
\textbf{Config} & \textbf{Sucesso} & \textbf{Taxa (\%)} & \textbf{Tempo Méd.} & \textbf{Tempo Med.} & \textbf{Círculos Méd.} & \textbf{Círculos Min-Max} \\
\midrule
"""

for _, row in resumo_df.iterrows():
    latex_content += f"{row['config']} & "
    latex_content += f"{int(row['success'])}/{int(row['total'])} & "
    latex_content += f"{row['success_rate']:.1f} & "
    latex_content += f"{row['tempo_mean']:.2f}s & "
    latex_content += f"{row['tempo_median']:.2f}s & "
    latex_content += f"{row['circulos_mean']:.1f} & "
    latex_content += f"{int(row['circulos_min'])}-{int(row['circulos_max'])} \\\\\n"

latex_content += r"""\bottomrule
\end{tabular}
\end{table}

\subsection{Análise Gráfica}

\subsubsection{Taxa de Sucesso}

A Figura~\ref{fig:taxa_sucesso} ilustra a taxa de sucesso de cada configuração. 
Configurações com taxa inferior a 100\% indicam dificuldade em resolver todas as instâncias 
dentro do tempo limite estabelecido.

\begin{figure}[H]
\centering
\includegraphics[width=0.8\textwidth]{1_taxa_sucesso.png}
\caption{Taxa de sucesso por configuração}
\label{fig:taxa_sucesso}
\end{figure}

\subsubsection{Tempo de Execução}

A Figura~\ref{fig:tempo} apresenta a análise de tempo de execução. O gráfico à esquerda 
mostra o tempo médio, enquanto o gráfico à direita apresenta a distribuição completa 
dos tempos através de boxplots (escala logarítmica).

\begin{figure}[H]
\centering
\includegraphics[width=\textwidth]{2_tempo_execucao.png}
\caption{Análise de tempo de execução}
\label{fig:tempo}
\end{figure}

\subsubsection{Qualidade da Solução}

A Figura~\ref{fig:qualidade} compara a qualidade das soluções obtidas por cada 
configuração, medida pelo número de círculos necessários. Menores valores indicam 
soluções mais eficientes.

\begin{figure}[H]
\centering
\includegraphics[width=0.9\textwidth]{3_qualidade_solucao.png}
\caption{Qualidade da solução (número de círculos)}
\label{fig:qualidade}
\end{figure}

\section{Análise de Escalabilidade}

A Figura~\ref{fig:escalabilidade} demonstra como o desempenho de cada configuração 
varia em função do tamanho da instância (número de pontos $n$).

\begin{figure}[H]
\centering
\includegraphics[width=\textwidth]{4_escalabilidade.png}
\caption{Escalabilidade: tempo e círculos × tamanho da instância}
\label{fig:escalabilidade}
\end{figure}

\section{Comparação Head-to-Head}

\subsection{Speedup Relativo}

A Figura~\ref{fig:speedup} mostra o speedup de cada configuração em relação ao 
Teste1 (baseline). Valores menores que 1 indicam melhor desempenho.

\begin{figure}[H]
\centering
\includegraphics[width=0.8\textwidth]{5_speedup_relativo.png}
\caption{Speedup relativo ao Teste1 (baseline)}
\label{fig:speedup}
\end{figure}

\subsection{Heatmap de Desempenho}

A Figura~\ref{fig:heatmap} apresenta um heatmap normalizado do tempo de execução 
para as primeiras 30 instâncias. Cores mais escuras (vermelhas) indicam pior desempenho 
relativo naquela instância.

\begin{figure}[H]
\centering
\includegraphics[width=0.9\textwidth]{6_heatmap_desempenho.png}
\caption{Heatmap de desempenho normalizado}
\label{fig:heatmap}
\end{figure}

\section{Análise Estatística}

\subsection{Comparações Pareadas}

A Figura~\ref{fig:comparacoes} apresenta os resultados dos testes estatísticos 
Mann-Whitney U para comparações pareadas entre configurações. Barras vermelhas 
indicam diferenças estatisticamente significativas ($p < 0.05$).

\begin{figure}[H]
\centering
\includegraphics[width=\textwidth]{10_comparacoes_pareadas.png}
\caption{Significância estatística das comparações pareadas}
\label{fig:comparacoes}
\end{figure}

\subsection{Correlação entre Parâmetros}

A Figura~\ref{fig:correlacao} mostra a matriz de correlação de Pearson entre 
os principais parâmetros das instâncias e métricas de desempenho.

\begin{figure}[H]
\centering
\includegraphics[width=0.8\textwidth]{11_correlacao_parametros.png}
\caption{Matriz de correlação entre parâmetros}
\label{fig:correlacao}
\end{figure}

\subsection{Variabilidade entre Repetições}

A Figura~\ref{fig:variabilidade} ilustra o coeficiente de variação (CV) do tempo 
de execução entre repetições da mesma configuração na mesma instância. Valores 
menores indicam maior estabilidade.

\begin{figure}[H]
\centering
\includegraphics[width=\textwidth]{12_variabilidade_repeticoes.png}
\caption{Variabilidade do tempo de execução entre repetições}
\label{fig:variabilidade}
\end{figure}

\section{Análise de Instâncias}

\subsection{Distribuição de Características}

A Figura~\ref{fig:distribuicao} apresenta a distribuição das principais 
características das instâncias testadas.

\begin{figure}[H]
\centering
\includegraphics[width=\textwidth]{13_distribuicao_caracteristicas.png}
\caption{Distribuição das características das instâncias}
\label{fig:distribuicao}
\end{figure}

\subsection{Instâncias Mais Difíceis}

A Figura~\ref{fig:dificeis} identifica as instâncias mais desafiadoras, 
tanto em termos de tempo de execução quanto de taxa de sucesso.

\begin{figure}[H]
\centering
\includegraphics[width=\textwidth]{14_instancias_dificeis.png}
\caption{Instâncias mais difíceis}
\label{fig:dificeis}
\end{figure}

\subsection{Relação Características × Tempo}

A Figura~\ref{fig:carac_tempo} explora a relação entre diferentes características 
das instâncias e o tempo de execução.

\begin{figure}[H]
\centering
\includegraphics[width=\textwidth]{15_caracteristicas_vs_tempo.png}
\caption{Relação entre características e tempo de execução}
\label{fig:carac_tempo}
\end{figure}

\subsection{Perfil de Complexidade}

A Figura~\ref{fig:perfil} classifica as instâncias em categorias de dificuldade 
e analisa as características médias de cada categoria.

\begin{figure}[H]
\centering
\includegraphics[width=\textwidth]{16_perfil_complexidade.png}
\caption{Perfil de complexidade das instâncias}
\label{fig:perfil}
\end{figure}

\section{Conclusões}

\subsection{Principais Resultados}

\begin{enumerate}
"""

# Identificar melhor configuração por tempo
best_time_cfg = resumo_df.loc[resumo_df['tempo_mean'].idxmin()]
latex_content += f"\\item \\textbf{{Configuração mais rápida:}} {best_time_cfg['config']} "
latex_content += f"(tempo médio: {best_time_cfg['tempo_mean']:.2f}s)\n"

# Identificar melhor por taxa de sucesso
best_success_cfg = resumo_df.loc[resumo_df['success_rate'].idxmax()]
latex_content += f"\\item \\textbf{{Maior taxa de sucesso:}} {best_success_cfg['config']} "
latex_content += f"({best_success_cfg['success_rate']:.1f}\\%)\n"

# Identificar melhor qualidade
best_quality_cfg = resumo_df.loc[resumo_df['circulos_mean'].idxmin()]
latex_content += f"\\item \\textbf{{Melhor qualidade média:}} {best_quality_cfg['config']} "
latex_content += f"({best_quality_cfg['circulos_mean']:.1f} círculos)\n"

latex_content += r"""\end{enumerate}

\subsection{Recomendações}

Com base nos resultados obtidos, recomenda-se:

\begin{itemize}
    \item Para instâncias pequenas (n $\leq$ 50): priorizar qualidade da solução
    \item Para instâncias médias (50 < n $\leq$ 100): balancear tempo e qualidade
    \item Para instâncias grandes (n > 100): priorizar tempo de execução
    \item Considerar timeout adaptativo baseado no tamanho da instância
\end{itemize}

\section{Arquivos Gerados}

Todos os dados e gráficos estão disponíveis no diretório \texttt{tests/analysis/results/}:

\begin{itemize}
    \item Gráficos: arquivos PNG em alta resolução (300 DPI)
    \item Dados: arquivos CSV com estatísticas detalhadas
    \item Este relatório: \texttt{relatorio\_benchmark.tex}
\end{itemize}

\end{document}
"""

# Salvar arquivo
with open(OUTPUT_TEX, 'w', encoding='utf-8') as f:
    f.write(latex_content)

print("=" * 80)
print("GERADOR DE RELATÓRIO LaTeX")
print("=" * 80)
print(f"\n✓ Relatório LaTeX gerado: {OUTPUT_TEX}")
print("\nPara compilar:")
print(f"  cd {RESULTS_DIR}")
print("  pdflatex relatorio_benchmark.tex")
print("  pdflatex relatorio_benchmark.tex  (segunda vez para referências)")
print("\n" + "=" * 80)

# Análise de Resultados - Circle Coverage Benchmark

Este diretório contém scripts Python para análise completa dos resultados do benchmark automatizado.

## 📁 Estrutura

```
analysis/
├── run_all_analysis.py          # Script principal - executa tudo
├── benchmark_analyzer.py         # Análise geral de desempenho
├── statistical_analysis.py       # Testes estatísticos
├── instance_analysis.py          # Análise de instâncias
├── generate_latex_report.py      # Gera relatório LaTeX
├── results/                      # Saída (criado automaticamente)
│   ├── *.png                    # Gráficos em alta resolução
│   ├── *.csv                    # Tabelas de dados
│   └── relatorio_benchmark.tex  # Relatório LaTeX
└── README.md                     # Este arquivo
```

## 🚀 Como Usar

### Execução Completa (Recomendado)

Execute o script principal que roda todas as análises:

```bash
cd tests/analysis
python run_all_analysis.py
```

Isso gerará **automaticamente**:
- 16 gráficos PNG (300 DPI)
- 15+ tabelas CSV
- 1 relatório LaTeX completo

### Execução Individual

Você também pode executar cada script separadamente:

```bash
python benchmark_analyzer.py      # Análise principal
python statistical_analysis.py    # Testes estatísticos
python instance_analysis.py       # Análise de instâncias
python generate_latex_report.py   # Relatório LaTeX
```

## 📊 Arquivos Gerados

### Gráficos PNG (300 DPI - prontos para TCC)

| Arquivo | Descrição |
|---------|-----------|
| `1_taxa_sucesso.png` | Taxa de sucesso por configuração |
| `2_tempo_execucao.png` | Tempo médio e distribuição (boxplot) |
| `3_qualidade_solucao.png` | Número de círculos (média e mediana) |
| `4_escalabilidade.png` | Tempo e círculos vs tamanho da instância |
| `5_speedup_relativo.png` | Speedup em relação ao baseline (Teste1) |
| `6_heatmap_desempenho.png` | Heatmap normalizado de tempo |
| `7_resumo_geral.png` | Tabela visual com resumo geral |
| `10_comparacoes_pareadas.png` | Testes Mann-Whitney U |
| `11_correlacao_parametros.png` | Matriz de correlação de Pearson |
| `12_variabilidade_repeticoes.png` | Coeficiente de variação (CV) |
| `13_distribuicao_caracteristicas.png` | Histogramas das características |
| `14_instancias_dificeis.png` | Top 10 instâncias mais difíceis |
| `15_caracteristicas_vs_tempo.png` | Scatter plots (n, raio, densidade, etc.) |
| `16_perfil_complexidade.png` | Distribuição por classe de dificuldade |

### Tabelas CSV (dados brutos)

Todas as tabelas incluem estatísticas detalhadas:
- Médias, medianas, desvios padrão
- Valores mínimos e máximos
- Testes estatísticos (p-valores, estatísticas)
- Características das instâncias

### Relatório LaTeX

O arquivo `relatorio_benchmark.tex` é um documento completo pronto para inclusão no TCC:

```bash
cd results
pdflatex relatorio_benchmark.tex
pdflatex relatorio_benchmark.tex  # Segunda vez para referências
```

Inclui:
- Resumo executivo
- Todas as análises com figuras
- Tabelas formatadas
- Análise estatística
- Conclusões e recomendações

## 📈 Análises Realizadas

### 1. Benchmark Analyzer
- Taxa de sucesso por configuração
- Tempo de execução (média, mediana, distribuição)
- Qualidade da solução (número de círculos)
- Análise de escalabilidade
- Speedup relativo
- Heatmap de desempenho

### 2. Statistical Analysis
- Teste de normalidade (Shapiro-Wilk)
- Teste de Friedman (comparação múltipla)
- Testes pareados Mann-Whitney U
- Correlação de Pearson entre parâmetros
- Análise de variabilidade entre repetições (CV)

### 3. Instance Analysis
- Distribuição das características (n, raio, densidade, etc.)
- Identificação de instâncias mais difíceis
- Relação características vs tempo
- Perfil de complexidade (classificação por dificuldade)

### 4. LaTeX Report Generator
- Relatório completo formatado
- Todas as figuras incluídas
- Tabelas LaTeX profissionais
- Seções organizadas
- Pronto para compilação

## 🎨 Identidade Visual

Os gráficos mantêm a mesma identidade visual das visualizações de círculos:
- Cores consistentes por configuração
- DPI 300 (alta qualidade para impressão)
- Fontes em negrito para títulos
- Grid suave com alpha 0.3
- Bordas pretas nos elementos

### Cores por Configuração:
- **Teste1**: Cyan claro (#8DD3C7)
- **Teste2**: Amarelo claro (#FFFFB3)
- **Teste3**: Roxo claro (#BEBADA)
- **Teste4**: Vermelho claro (#FB8072)
- **Teste5**: Azul claro (#80B1D3)
- **Teste6**: Laranja claro (#FDB462)

## 📋 Requisitos

```bash
pip install pandas matplotlib seaborn numpy scipy
```

Todos já incluídos no ambiente padrão Python científico.

## 💡 Dicas para o TCC

1. **Figuras**: Todos os PNGs são 300 DPI, prontos para impressão
2. **Dados**: Use os CSVs para criar suas próprias tabelas/gráficos
3. **LaTeX**: O relatório pode ser usado como apêndice ou capítulo
4. **Comparações**: Os testes estatísticos dão rigor científico
5. **Escalabilidade**: Mostre como cada abordagem escala com n

## 🔍 Exemplo de Uso no TCC

### Incluir Figura no LaTeX:

```latex
\begin{figure}[H]
\centering
\includegraphics[width=0.8\textwidth]{results/1_taxa_sucesso.png}
\caption{Taxa de sucesso das configurações testadas}
\label{fig:taxa_sucesso}
\end{figure}
```

### Incluir Tabela CSV:

Use os dados dos CSVs para criar tabelas formatadas com `pandas.DataFrame.to_latex()`.

## 📞 Suporte

Em caso de erros:
1. Verifique se os arquivos CSV estão em `tests/tables/`
2. Certifique-se de ter as bibliotecas instaladas
3. Execute `run_all_analysis.py` para gerar tudo de uma vez

---

**Gerado automaticamente** pelo sistema de análise de benchmark.

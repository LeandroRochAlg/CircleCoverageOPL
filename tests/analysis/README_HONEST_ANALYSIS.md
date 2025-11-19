# Análise Honesta e Transparente - Circle Coverage Benchmark

## 📊 Sobre Esta Análise

Esta análise foi criada com um princípio fundamental: **100% de honestidade com os dados**.

### Por que "Honesta"?

Durante o desenvolvimento do TCC, percebemos que os benchmarks rodaram diferentes configurações em diferentes conjuntos de instâncias:

- **Teste1, Teste2, Teste3**: Testaram 58 instâncias (n entre 10 e 180)
- **Teste4, Teste5, Teste6**: Testaram 23 instâncias diferentes (n entre 12 e 355)

**Problema**: Comparar taxas de sucesso globais seria DESONESTO, pois:
- Teste1 poderia parecer ter 100% de sucesso apenas porque foi testado em instâncias menores
- Teste4-6 poderiam parecer piores apenas porque enfrentaram instâncias maiores

### Nossa Solução: Transparência Total

✅ **Mostramos claramente quais instâncias foram testadas em cada configuração**
✅ **Analisamos taxa de sucesso POR FAIXA DE TAMANHO**
✅ **Comparações justas: apenas instâncias testadas em TODAS as configs**
✅ **Foco em CARACTERÍSTICAS (número de clientes, raio, cobertura) não em IDs**
✅ **Média das repetições ao invés de dados individuais**

---

## 🎯 Arquivos Gerados

### 1. COBERTURA_TESTES
**O que mostra**: Quais instâncias foram testadas em cada configuração
- Histograma da distribuição de tamanhos (n) por config
- Tabela com min/max/média de n por config
- **Insight**: Demonstra que Teste1-3 e Teste4-6 foram testados em conjuntos diferentes

### 2. TAXA_SUCESSO_HONESTA
**O que mostra**: Taxa de sucesso dividida por faixa de tamanho
- Pequena (≤25), Média (26-50), Grande (51-100), Muito Grande (101-200), Extra Grande (>200)
- Cada barra mostra **n = quantidade testada naquela faixa**
- **Insight**: Revela que problemas de Teste2-3 acontecem em instâncias grandes (51-100)

### 3. COMPARACAO_JUSTA
**O que mostra**: Comparação usando APENAS as 8 instâncias testadas em TODAS as configs
- Tempo de execução
- Número de círculos
- **Insight**: Comparação verdadeiramente justa, sem viés de seleção de instâncias

### 4. TABELA_MESTRE_INSTANCIAS
**O que mostra**: Todas as 72 instâncias com suas características legíveis
- Número de Clientes, Raio, Distância Mínima entre Círculos, Cobertura k
- Densidade (clientes/área)
- Tempo Médio e Círculos Médios
- Classe de Dificuldade (Fácil, Média, Difícil, Muito Difícil)
- **Quais configs testaram aquela instância**

### 5. DESEMPENHO_POR_CARACTERISTICAS
**O que mostra**: 6 gráficos scatter relacionando características com tempo
- Número de Clientes × Tempo
- Raio × Tempo
- Distância Mínima × Tempo
- Cobertura k × Tempo
- Densidade × Tempo
- Área × Tempo
- Cada ponto é rotulado com **(n = quantidade testada)**
- **Insight**: Visualiza qual característica mais impacta o desempenho

### 6. TOP_INSTANCIAS_DIFICEIS
**O que mostra**: Top 15 instâncias mais desafiadoras COM suas características
- Formato: `n=50, r=75.0, k=3, d=0.0089`
- Mostra tempo, número de círculos e quais configs testaram
- **Insight**: Identifica perfil das instâncias problemáticas

### 7. IMPACTO_COBERTURA_K
**O que mostra**: Como o parâmetro k (cobertura mínima) afeta desempenho
- Tempo médio × k
- Número de círculos × k
- **Insight**: Quantifica o impacto de exigir maior cobertura

### 8. RESUMO_EXECUTIVO
**O que mostra**: Tabela consolidada colorida por configuração
- Instâncias testadas
- Taxa de sucesso
- Range de n (mínimo e máximo)
- Tempo médio e mediana
- Número médio de círculos
- **Insight**: Overview completo respeitando os dados

### 9. CORRELACAO
**O que mostra**: Matriz de correlação (heatmap)
- Correlação entre todas características e métricas
- Valores de -1 (correlação negativa) a +1 (correlação positiva)
- **Insight**: Identifica quais características estão relacionadas

---

## 🚀 Como Usar

```bash
python tests/analysis/honest_analysis.py
```

**Pré-requisitos**:
```bash
pip install pandas matplotlib seaborn numpy scipy
```

**Entrada**:
- `tests/results_table.csv` - Resultados dos benchmarks
- `tests/instances_table.csv` - Características das instâncias

**Saída**:
- `tests/analysis/results_v2/` - 9 PNGs (300 DPI) + 9 CSVs

---

## 📈 Principais Insights da Análise

### Descoberta 1: Teste2 e Teste3 Falham em Instâncias Grandes
- Taxa de sucesso 100% para n ≤ 50
- Taxa de sucesso 0% para n entre 51-100
- **Conclusão**: Heurísticas funcionam bem em pequenas instâncias, mas não escalam

### Descoberta 2: Apenas 8 Instâncias São Comparáveis
- Das 73 instâncias, apenas 8 foram testadas em todas as 6 configurações
- **Conclusão**: Comparações globais seriam enganosas

### Descoberta 3: CP Puro é Mais Lento mas Mais Confiável
- Tempo médio: 418.04s (mais lento)
- Taxa de sucesso: 98.28% (mais alto entre Teste1-3)
- **Conclusão**: Trade-off entre velocidade e confiabilidade

### Descoberta 4: Fix Circ v3 é o Melhor para Instâncias Grandes
- Taxa de sucesso: 95.65% em n até 355
- Tempo mediana: 8.21s (rápido)
- **Conclusão**: Melhor abordagem para instâncias grandes

---

## 🎨 Identidade Visual

Todos os gráficos seguem a identidade visual do visualizador de círculos:

- **Teste1 (CP Puro)**: #8DD3C7 (turquesa)
- **Teste2 (Heurística 2.3)**: #FFFFB3 (amarelo claro)
- **Teste3 (Heurística 3)**: #BEBADA (lilás)
- **Teste4 (K-Coverage)**: #FB8072 (coral)
- **Teste5 (Fix Circ v3)**: #80B1D3 (azul)
- **Teste6 (Fix Circ v4)**: #FDB462 (laranja)

300 DPI, pronto para publicação no TCC.

---

## 🎓 Para o TCC

### O que INCLUIR na dissertação:

1. **Gráfico 01_COBERTURA** para mostrar transparência metodológica
2. **Tabela 02_TAXA_SUCESSO** para análise por faixa
3. **Gráfico 03_COMPARACAO_JUSTA** para comparação válida
4. **Tabela 04_MESTRE** para consulta de características
5. **Gráfico 05_CARACTERISTICAS** (escolha 2-3 mais relevantes)
6. **Tabela 08_RESUMO** como síntese geral
7. **Heatmap 09_CORRELACAO** para análise estatística

### O que DIZER no texto:

> "É importante ressaltar que as diferentes configurações foram testadas em conjuntos 
> distintos de instâncias, com os Testes 1-3 focando em instâncias menores (n ≤ 180) 
> e os Testes 4-6 abrangendo instâncias maiores (n até 355). Portanto, comparações 
> diretas de taxa de sucesso global seriam inadequadas. Para análises comparativas 
> válidas, utilizamos apenas o subconjunto de 8 instâncias testadas em todas as 
> configurações."

---

## ✅ Checklist de Honestidade

- [x] Mostramos quais instâncias foram testadas onde
- [x] Não comparamos configs em instâncias diferentes
- [x] Usamos nomes legíveis (não IDs ou nomes de variáveis)
- [x] Agregamos repetições (média)
- [x] Mostramos sample sizes (n = X)
- [x] Adicionamos avisos de transparência
- [x] Classificamos por características, não por nomes
- [x] Exportamos tabelas para verificação
- [x] Geramos gráficos de alta qualidade (300 DPI)

---

## 🤝 Contribuindo para a Ciência

Esta análise serve como exemplo de como apresentar resultados de benchmarks de forma ética e transparente, evitando:

- ❌ Cherry-picking de resultados favoráveis
- ❌ Comparações injustas (apples-to-oranges)
- ❌ Omissão de falhas ou limitações
- ❌ Uso de nomes técnicos incompreensíveis

E promovendo:

- ✅ Transparência metodológica completa
- ✅ Comparações válidas e justas
- ✅ Comunicação clara e acessível
- ✅ Reprodutibilidade e verificabilidade

---

**Autor**: Análise Honesta v2.0  
**Data**: 2024  
**Licença**: Use livremente no seu TCC, cite a metodologia de transparência! 🎓

# Interpretação dos Resultados - Circle Coverage Benchmark

## 📋 Configurações Testadas

### Testes 1-3 (Instâncias Pequenas/Médias: n=10 a 180)
1. **CP Puro** (`circle_k_coverage.mod`)
   - Constraint Programming puro, sem heurísticas
   - Baseline para comparação
   
2. **Heurística 3 + CP** (`exemplo_modular_real.mod` com `modular_heuristic3.mod`)
   - Heurística inicial para definir upper bound
   - CP refina a solução
   
3. **Heurística 4 + CP** (`exemplo_modular_real2.mod` com `modular_heuristic4.mod`)
   - Versão melhorada da heurística 3
   - CP refina a solução

### Testes 4-6 (Instâncias Médias/Grandes: n=12 a 355)
4. **CP Pontos Fixos + Quebra Entre** (`modelo_fix_circ_preprocessing_v4.mod`)
   - Pontos fixos (clientes) pré-processados
   - Quebra de simetria entre círculos

5. **CP Pontos Fixos + Quebra Intra** (`modelo_fix_circ_preprocessing_v5.mod`)
   - Pontos fixos pré-processados
   - Quebra de simetria intra-círculo (ordenação de pontos dentro do mesmo círculo)

6. **CP Pontos Fixos + Quebra Entre+Intra** (`modelo_fix_circ_preprocessing_v6.mod`)
   - Combina ambas quebras de simetria
   - Abordagem mais agressiva

---

## 🎯 Principais Descobertas

### 1. Escalabilidade das Heurísticas 3 e 4

**Observação:**
- ✅ **100% de sucesso** em instâncias pequenas (n ≤ 25)
- ✅ **89.3% de sucesso** em instâncias médias (26 ≤ n ≤ 50)
- ❌ **0% de sucesso** em instâncias grandes (51 ≤ n ≤ 100)

**Interpretação:**
As heurísticas 3 e 4 (quando combinadas com CP) funcionam perfeitamente para problemas pequenos e têm bom desempenho em problemas médios, mas **não escalam** para instâncias maiores. Isso indica que:
- A fase de construção da heurística pode estar criando soluções infactíveis
- O CP não consegue corrigir as infactibilidades em tempo razoável
- Há necessidade de heurísticas mais robustas ou timeouts maiores

### 2. CP Puro é Lento mas Confiável

**Observação:**
- Taxa de sucesso: **98.28%** (melhor entre Testes 1-3)
- Tempo médio: **418.04 segundos** (mais lento)
- Tempo mediana: **19.34 segundos**

**Interpretação:**
O CP Puro resolve quase todas as instâncias mas é lento. A alta diferença entre média (418s) e mediana (19s) indica que:
- A maioria das instâncias é resolvida rapidamente
- Algumas instâncias extremamente difíceis inflam a média
- É a abordagem mais **confiável** quando tempo não é crítico

### 3. Pontos Fixos + Quebra Intra é o Melhor Overall

**Observação:**
- **CP Pontos Fixos + Quebra Intra** (Teste5):
  - Taxa de sucesso: **95.65%** (melhor para instâncias grandes)
  - Tempo mediana: **8.21 segundos** (muito rápido)
  - Tempo médio: **419.31 segundos** (afetado por outliers)

**Interpretação:**
Esta configuração é a **mais balanceada**:
- Alta taxa de sucesso mesmo em instâncias grandes (n até 355)
- Mediana de tempo baixa indica que maioria resolve rápido
- A quebra de simetria intra-círculo é mais efetiva que entre-círculos

### 4. Quebra Entre+Intra Não é Sempre Melhor

**Observação:**
- **CP Pontos Fixos + Quebra Entre+Intra** (Teste6):
  - Taxa de sucesso: **82.61%** (pior que Teste5)
  - Tempo mediana: **4.05 segundos** (mais rápido quando resolve)

**Interpretação:**
Combinar ambas as quebras de simetria **não melhora** os resultados:
- Quando resolve, é mais rápido (4.05s vs 8.21s)
- Mas resolve **menos instâncias** (82.61% vs 95.65%)
- Possível causa: Restrições excessivas podem eliminar soluções viáveis ou tornar o espaço de busca mais difícil de explorar

---

## 📊 Análise de Correlações (O Que Realmente Importa)

### Forte Impacto no Número de Círculos:

1. **Raio dos Círculos** → correlação **-0.501** (negativa forte)
   - **Interpretação:** Círculos maiores cobrem mais área, então precisamos de MENOS círculos
   - **Prático:** Aumentar raio de 50 para 100 pode reduzir círculos necessários pela metade

2. **Cobertura Mínima (k)** → correlação **+0.575** (positiva forte)
   - **Interpretação:** Exigir que cada cliente seja coberto k vezes aumenta MUITO o número de círculos
   - **Prático:** k=3 pode precisar do triplo de círculos que k=1

3. **Área da Região** → correlação **+0.512** (positiva forte)
   - **Interpretação:** Regiões maiores precisam de mais círculos
   - **Prático:** Área 2x maior ≈ 1.5x mais círculos

### Impacto no Tempo de Execução:

1. **Número de Círculos** → correlação **+0.510** (positiva forte)
   - **Interpretação:** Mais círculos na solução = mais variáveis de decisão = mais tempo
   - **Prático:** Soluções com 20 círculos demoram muito mais que soluções com 5 círculos

### Relações Entre Características:

1. **Nº Clientes ↔ Densidade** → correlação **+0.956** (MUITO forte)
   - **Interpretação:** Mais clientes na mesma área = maior densidade (óbvio matematicamente)
   
2. **Nº Clientes ↔ Raio** → correlação **-0.699** (negativa forte)
   - **Interpretação:** O algoritmo de geração ajusta o raio inversamente ao número de clientes
   - **Prático:** Instâncias com muitos clientes tendem a ter círculos menores

3. **Raio ↔ Densidade** → correlação **-0.719** (negativa forte)
   - **Interpretação:** Círculos maiores cobrem mais área com menos densidade de clientes

---

## 🎓 Para o TCC: Conclusões e Recomendações

### Qual Configuração Usar?

| Cenário | Configuração Recomendada | Justificativa |
|---------|------------------------|---------------|
| **Instâncias pequenas (n ≤ 50)** | Heurística 4 + CP | Rápido (4.91s mediana) e confiável (89.3% sucesso) |
| **Instâncias grandes (n > 100)** | CP Pontos Fixos + Quebra Intra | Melhor taxa (95.65%) e tempo razoável (8.21s mediana) |
| **Quando tempo não importa** | CP Puro | Taxa mais alta (98.28%) mas lento (19.34s mediana) |
| **Quando precisa de velocidade** | CP Pontos Fixos + Quebra Entre+Intra | Mais rápido (4.05s) mas menos confiável (82.61%) |

### Limitações Importantes

1. **Datasets Diferentes**: Testes 1-3 e 4-6 foram executados em instâncias diferentes
   - Comparação direta de taxas globais seria **enganosa**
   - Análise por faixa de tamanho é mais **honesta**

2. **Apenas 8 Instâncias Comparáveis**: Das 73 instâncias, apenas 8 foram testadas em todas as 6 configurações
   - Comparações devem ser feitas com **cautela**
   - Resultados em instâncias comuns mostram tendências, não verdades absolutas

3. **Variabilidade Alta**: Diferença grande entre média e mediana
   - Algumas instâncias são **extremamente difíceis**
   - Tempo de execução não é previsível apenas pelas características básicas

### Trabalhos Futuros

1. **Heurísticas Mais Robustas**: Desenvolver heurísticas que escalem melhor para n > 50
2. **Timeout Adaptativo**: Ajustar timeout baseado nas características da instância
3. **Pré-processamento Inteligente**: Identificar instâncias difíceis antes da execução
4. **Hibridização**: Combinar múltiplas heurísticas (portfolio approach)
5. **Paralelização**: Executar múltiplas configurações em paralelo e pegar a primeira que resolver

---

## 📈 Gráficos Essenciais para o TCC

### Obrigatórios:
1. **02_TAXA_SUCESSO_HONESTA.png** - Mostra que diferentes configs funcionam para diferentes tamanhos
2. **08_RESUMO_EXECUTIVO.png** - Tabela completa comparativa
3. **09_CORRELACAO.png** - Heatmap mostrando o que realmente importa

### Recomendados:
4. **01_COBERTURA_TESTES.png** - Transparência metodológica
5. **06_TOP_INSTANCIAS_DIFICEIS.png** - Perfil das instâncias problemáticas
6. **07_IMPACTO_COBERTURA_K.png** - Efeito do parâmetro k

### Opcionais (Apêndice):
7. **03_COMPARACAO_JUSTA.png** - Comparação nas 8 instâncias comuns
8. **05_DESEMPENHO_POR_CARACTERISTICAS.png** - Análise detalhada

---

## 🔬 Explicação Científica (Para a Dissertação)

### Por que CP Pontos Fixos + Quebra Intra funciona melhor?

**Teoria:**
- **Pontos Fixos**: Pré-atribuir clientes a círculos reduz o espaço de busca drasticamente
- **Quebra Intra**: Ordenar pontos dentro do mesmo círculo elimina permutações equivalentes
- **Sinergia**: Ambas técnicas atacam diferentes fontes de simetria

**Evidência Empírica:**
- Teste5 (Quebra Intra): 95.65% sucesso
- Teste4 (Quebra Entre): 91.30% sucesso
- Teste6 (Ambas): 82.61% sucesso ← overconstraining?

**Hipótese:**
Quebrar simetria em excesso pode **rigidificar** o problema, tornando-o mais difícil para o solver explorar. O equilíbrio entre redução do espaço de busca e manutenção de flexibilidade é crucial.

---

## 📝 Texto Sugerido para o TCC

> "Realizamos experimentos comparando seis configurações diferentes em um conjunto de 73 instâncias do problema de cobertura por círculos com cobertura mínima k. É importante ressaltar que, devido a limitações computacionais, as configurações foram testadas em subconjuntos distintos: as abordagens baseadas em heurísticas (Testes 1-3) foram avaliadas em 58 instâncias de pequeno a médio porte (10 ≤ n ≤ 180), enquanto as abordagens de pontos fixos (Testes 4-6) foram testadas em 23 instâncias de médio a grande porte (12 ≤ n ≤ 355). Portanto, comparações diretas de taxas de sucesso globais seriam metodologicamente inadequadas.
>
> Nossa análise revela que as heurísticas combinadas com CP (Testes 2-3) apresentam excelente desempenho para instâncias pequenas (100% de sucesso para n ≤ 25), mas não escalam para instâncias maiores (0% de sucesso para 51 ≤ n ≤ 100). Por outro lado, a abordagem de CP com pontos fixos e quebra de simetria intra-círculo (Teste 5) demonstrou o melhor equilíbrio entre taxa de sucesso (95.65%) e eficiência (mediana de 8.21 segundos) para instâncias de maior porte.
>
> A análise de correlação revelou que o raio dos círculos (r = -0.501) e a cobertura mínima exigida (k = +0.575) são os fatores que mais influenciam o número de círculos necessários na solução, enquanto o próprio número de círculos (r = +0.510) é o principal preditor do tempo de execução."

---

**Última atualização:** 18 de novembro de 2025  
**Análise gerada por:** honest_analysis.py v2.0

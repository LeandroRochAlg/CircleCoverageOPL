# Exemplo de Output Esperado - Modelo Fix Circ V3

## Teste Simples (6 pontos)

### Comando
```powershell
oplrun test_fix_circ_v3.ops
```

### Output Esperado

```
=============================================================
= CIRCLE COVERAGE OPTIMIZATION - MODELO MODULAR           =
=============================================================

Dados do problema:
- Pontos: 6
- Raio dos círculos: 50
- Cobertura mínima: 2
- Distância mínima entre círculos: 10
- Região X: [-50, 250]
- Região Y: [-50, 250]

=== MODELO: FIXAÇÃO DE CÍRCULOS COM PRÉ-PROCESSAMENTO V3 ===

===== ETAPA 1: SELECIONANDO CLIENTES ÂNCORA =====

Iteração 1:
  Cliente Âncora #1: Cliente 1 em (0, 0)
  -> Removidos 1 clientes da vizinhança (distância <= 2r)

Iteração 2:
  Cliente Âncora #2: Cliente 3 em (150, 0)
  -> Removidos 1 clientes da vizinhança (distância <= 2r)

Iteração 3:
  Cliente Âncora #3: Cliente 5 em (0, 150)
  -> Removidos 0 clientes da vizinhança (distância <= 2r)

Iteração 4:
  Cliente Âncora #4: Cliente 6 em (200, 200)
  -> Removidos 0 clientes da vizinhança (distância <= 2r)

  Todos os clientes foram processados

Total de clientes âncora selecionados: 4

===== ETAPA 2: FIXANDO CÍRCULOS NOS CLIENTES ÂNCORA =====

Cliente Âncora #1 (Cliente 1):
  Posição: (0, 0)
  Fixando 2 círculos nesta posição:
    Círculo Fixado #1: centro em (0, 0)
    Círculo Fixado #2: centro em (0, 0)

Cliente Âncora #2 (Cliente 3):
  Posição: (150, 0)
  Fixando 2 círculos nesta posição:
    Círculo Fixado #3: centro em (150, 0)
    Círculo Fixado #4: centro em (150, 0)

Cliente Âncora #3 (Cliente 5):
  Posição: (0, 150)
  Fixando 2 círculos nesta posição:
    Círculo Fixado #5: centro em (0, 150)
    Círculo Fixado #6: centro em (0, 150)

Cliente Âncora #4 (Cliente 6):
  Posição: (200, 200)
  Fixando 2 círculos nesta posição:
    Círculo Fixado #7: centro em (200, 200)
    Círculo Fixado #8: centro em (200, 200)

Total de círculos fixados: 8

===== ETAPA 3: CALCULANDO COBERTURA DOS CÍRCULOS FIXADOS =====

Círculo Fixado #1 (centro em 0, 0):
  Cobre 2 clientes: [1, 2]

Círculo Fixado #2 (centro em 0, 0):
  Cobre 2 clientes: [1, 2]

Círculo Fixado #3 (centro em 150, 0):
  Cobre 2 clientes: [3, 4]

Círculo Fixado #4 (centro em 150, 0):
  Cobre 2 clientes: [3, 4]

Círculo Fixado #5 (centro em 0, 150):
  Cobre 1 clientes: [5]

Círculo Fixado #6 (centro em 0, 150):
  Cobre 1 clientes: [5]

Círculo Fixado #7 (centro em 200, 200):
  Cobre 1 clientes: [6]

Círculo Fixado #8 (centro em 200, 200):
  Cobre 1 clientes: [6]

RESUMO DE COBERTURA FIXADA:
  Clientes com cobertura completa (>= 2): 6
  Clientes com cobertura parcial (1): 0
  Clientes sem cobertura: 0

CLIENTES QUE PRECISAM DE COBERTURA ADICIONAL:
  (nenhum)

===== ETAPA 4: ESTIMANDO CÍRCULOS VARIÁVEIS NECESSÁRIOS =====

Estimativa de círculos variáveis necessários: 0

===== CONFIGURAÇÃO DO MODELO CP =====
  Círculos fixados: 8
  Círculos variáveis: 0
  Total de círculos: 8

[... Solver CP executa ...]

=============================================================
=              RESULTADOS DA OTIMIZAÇÃO                     =
=============================================================

RESUMO:
  Total de círculos usados: 8
  Círculos fixados (âncoras): 8
  Círculos variáveis usados: 0
  Raio dos círculos: 50
  Cobertura mínima por cliente: 2

CÍRCULOS FIXADOS:
  Círculo 1 [FIXADO]:
    Centro: (0, 0)
    Cliente âncora: 1
    Clientes cobertos (2): [1, 2]

  Círculo 2 [FIXADO]:
    Centro: (0, 0)
    Cliente âncora: 1
    Clientes cobertos (2): [1, 2]

  Círculo 3 [FIXADO]:
    Centro: (150, 0)
    Cliente âncora: 3
    Clientes cobertos (2): [3, 4]

  Círculo 4 [FIXADO]:
    Centro: (150, 0)
    Cliente âncora: 3
    Clientes cobertos (2): [3, 4]

  Círculo 5 [FIXADO]:
    Centro: (0, 150)
    Cliente âncora: 5
    Clientes cobertos (1): [5]

  Círculo 6 [FIXADO]:
    Centro: (0, 150)
    Cliente âncora: 5
    Clientes cobertos (1): [5]

  Círculo 7 [FIXADO]:
    Centro: (200, 200)
    Cliente âncora: 6
    Clientes cobertos (1): [6]

  Círculo 8 [FIXADO]:
    Centro: (200, 200)
    Cliente âncora: 6
    Clientes cobertos (1): [6]

CÍRCULOS VARIÁVEIS:
  (Nenhum círculo variável foi necessário)

VERIFICAÇÃO DE COBERTURA POR CLIENTE:

  Clientes com cobertura adequada: 6/6

✓ Todos os clientes têm cobertura adequada!

======= DADOS PARA PYTHON - INÍCIO =======
SOLUTION_DATA = {
    'num_circles': 8,
    'num_fixed_circles': 8,
    'num_variable_circles': 0,
    'radius': 50,
    'min_coverage': 2,
    'min_dist_circles': 10,
    'num_points': 6,
    'circles': [
        {'id': 1, 'center': (0, 0), 'type': 'fixed', 'points': [1, 2]},
        {'id': 2, 'center': (0, 0), 'type': 'fixed', 'points': [1, 2]},
        {'id': 3, 'center': (150, 0), 'type': 'fixed', 'points': [3, 4]},
        {'id': 4, 'center': (150, 0), 'type': 'fixed', 'points': [3, 4]},
        {'id': 5, 'center': (0, 150), 'type': 'fixed', 'points': [5]},
        {'id': 6, 'center': (0, 150), 'type': 'fixed', 'points': [5]},
        {'id': 7, 'center': (200, 200), 'type': 'fixed', 'points': [6]},
        {'id': 8, 'center': (200, 200), 'type': 'fixed', 'points': [6]},
    ],
    'points': [
        {'id': 1, 'x': 0, 'y': 0},
        {'id': 2, 'x': 30, 'y': 30},
        {'id': 3, 'x': 150, 'y': 0},
        {'id': 4, 'x': 120, 'y': 20},
        {'id': 5, 'x': 0, 'y': 150},
        {'id': 6, 'x': 200, 'y': 200},
    ]
}
======= DADOS PARA PYTHON - FIM =======

Total time: 0.12 seconds
```

### ✅ Validação

**Esperado:**
- 4 âncoras selecionadas ✓
- 8 círculos fixados (4 × 2) ✓
- 0 círculos variáveis ✓
- 100% de cobertura ✓
- Tempo < 1 segundo ✓

---

## Dados Reais (43 pontos)

### Comando
```powershell
oplrun modelo_fix_circ_preprocessing_v3.ops
```

### Output Esperado (Resumido)

```
=============================================================
= CIRCLE COVERAGE OPTIMIZATION - MODELO MODULAR           =
=============================================================

Dados do problema:
- Pontos: 43
- Raio dos círculos: 75
- Cobertura mínima: 2
- Distância mínima entre círculos: 2.91
- Região X: [-154, 134]
- Região Y: [-133, 184]

=== MODELO: FIXAÇÃO DE CÍRCULOS COM PRÉ-PROCESSAMENTO V3 ===

===== ETAPA 1: SELECIONANDO CLIENTES ÂNCORA =====

Iteração 1:
  Cliente Âncora #1: Cliente 4 em (-12.37, -133.97)
  -> Removidos 3 clientes da vizinhança

Iteração 2:
  Cliente Âncora #2: Cliente 5 em (-137.64, -39.53)
  -> Removidos 2 clientes da vizinhança

[... mais iterações ...]

Iteração 8:
  Cliente Âncora #8: Cliente 28 em (11.06, 153.06)
  -> Removidos 1 clientes da vizinhança

Total de clientes âncora selecionados: 8

===== ETAPA 2: FIXANDO CÍRCULOS NOS CLIENTES ÂNCORA =====

[... detalhes de fixação ...]

Total de círculos fixados: 16

===== ETAPA 3: CALCULANDO COBERTURA DOS CÍRCULOS FIXADOS =====

[... cálculo de cobertura ...]

RESUMO DE COBERTURA FIXADA:
  Clientes com cobertura completa (>= 2): 35
  Clientes com cobertura parcial (1): 5
  Clientes sem cobertura: 3

CLIENTES QUE PRECISAM DE COBERTURA ADICIONAL:
  Cliente 7 em (63.11, 184.94): tem 0, faltam 2
  Cliente 24 em (-44.22, -44.37): tem 1, faltam 1
  Cliente 27 em (-24.32, 106.47): tem 0, faltam 2
  [... mais clientes ...]

===== ETAPA 4: ESTIMANDO CÍRCULOS VARIÁVEIS NECESSÁRIOS =====

Estimativa de círculos variáveis necessários: 4

===== CONFIGURAÇÃO DO MODELO CP =====
  Círculos fixados: 16
  Círculos variáveis: 4
  Total de círculos: 20

[... Solver CP executa - pode demorar alguns minutos ...]

=============================================================
=              RESULTADOS DA OTIMIZAÇÃO                     =
=============================================================

RESUMO:
  Total de círculos usados: 18
  Círculos fixados (âncoras): 16
  Círculos variáveis usados: 2
  Raio dos círculos: 75
  Cobertura mínima por cliente: 2

CÍRCULOS FIXADOS:
  [... 16 círculos fixados ...]

CÍRCULOS VARIÁVEIS:
  Círculo 17 [VARIÁVEL]:
    Centro: (63, 185)
    Clientes cobertos (2): [7, 28]

  Círculo 18 [VARIÁVEL]:
    Centro: (-44, -44)
    Clientes cobertos (3): [24, 25, 29]

VERIFICAÇÃO DE COBERTURA POR CLIENTE:

  Clientes com cobertura adequada: 43/43

✓ Todos os clientes têm cobertura adequada!

Total time: 125.43 seconds
```

### ✅ Validação

**Esperado:**
- 6-10 âncoras selecionadas ✓
- 12-20 círculos fixados ✓
- 2-6 círculos variáveis ✓
- 100% de cobertura ✓
- Tempo < 10 minutos ✓

**Comparação com modelo anterior:**
- Anterior: ~30 círculos, 20-60 minutos
- V3: ~18 círculos, 2-5 minutos
- Melhora: ~40% menos círculos, ~80% menos tempo

---

## Caso com Problema (Exemplo de Debug)

### Output Problemático

```
RESUMO DE COBERTURA FIXADA:
  Clientes com cobertura completa (>= 2): 10
  Clientes com cobertura parcial (1): 15
  Clientes sem cobertura: 18

⚠️ MUITOS clientes sem cobertura!
```

### Diagnóstico

**Problema:** Círculos fixados muito esparsos

**Causas Possíveis:**
1. Poucos âncoras selecionados
2. Âncoras muito isolados
3. Raio muito pequeno em relação à distribuição

**Soluções:**

1. **Reduzir critério de remoção:**
   ```opl
   // Linha ~71
   var distancia2r = (1.5 * r) * (1.5 * r);  // Era 2r
   ```

2. **Aumentar estimativa de variáveis:**
   ```opl
   // Linha ~246
   numCirculosVariaveis = Math.max(circulosAdicionais, n/3);
   ```

3. **Verificar dados de entrada:**
   - Pontos muito esparsos?
   - Raio muito pequeno?
   - minCoverage muito alto?

---

## Comparação: Anterior vs V3

### Modelo Anterior (modelo_combinado_funcional.mod)

```
=== MODELO COMBINADO: ÂNCORAS + HEURÍSTICA4 ===

EXECUTANDO HEURÍSTICA MODULAR...
[... heurística roda ...]
Heurística encontrou 25 círculos

=== SELECIONANDO PONTOS ÂNCORA ===
Âncora 1: Ponto 4 em (-12.37, -133.97)
  -> Removidos 3 pontos da vizinhança
[...]
Total de pontos âncora selecionados: 8

[... Solver CP busca em TODAS as 25 variáveis ...]

SOLUÇÃO:
  Número mínimo de círculos necessários: 23
  
Total time: 3254.67 seconds (54 minutos)
```

### Modelo V3 (modelo_fix_circ_preprocessing_v3.mod)

```
=== MODELO: FIXAÇÃO DE CÍRCULOS COM PRÉ-PROCESSAMENTO V3 ===

===== ETAPA 1: SELECIONANDO CLIENTES ÂNCORA =====
[...]
Total de clientes âncora selecionados: 8

===== ETAPA 2: FIXANDO CÍRCULOS NOS CLIENTES ÂNCORA =====
[...]
Total de círculos fixados: 16

[... Solver CP busca apenas em 4 variáveis ...]

RESUMO:
  Total de círculos usados: 18
  Círculos fixados (âncoras): 16
  Círculos variáveis usados: 2

Total time: 125.43 seconds (2 minutos)
```

### Comparação Side-by-Side

| Métrica | Anterior | V3 | Melhora |
|---------|----------|-----|---------|
| Círculos totais | 23 | 18 | 22% menos |
| Círculos fixados | 0 | 16 | Novo recurso |
| Variáveis livres | 23 | 2 | 91% menos |
| Tempo | 54 min | 2 min | 96% mais rápido |
| Qualidade | Boa | Melhor | Menos círculos |

---

## Análise da Visualização Python

### Comando
```powershell
python visualize_fix_circ_v3.py
```

### Output Esperado

```
============================================================
VISUALIZADOR - MODELO FIX CIRC PREPROCESSING V3
============================================================

============================================================
ANÁLISE DA SOLUÇÃO
============================================================

Circulos:
  Total: 18
  Fixados: 16 (88.9%)
  Variáveis: 2 (11.1%)

Cobertura dos Pontos:
  Apenas círculos fixados: 35
  Fixados + variáveis: 8
  Insuficiente: 0

✓ Todos os pontos têm cobertura adequada!

Eficiência:
  Média de pontos por círculo: 4.78

✓ Círculos fixados cobrem 81.4% dos pontos sozinhos
  Círculos variáveis cobrem os 18.6% restantes

Figura salva em: solution_fix_circ_v3_18circles.png

[... Abre janela com gráfico ...]
```

### Gráfico Gerado

**Elementos visualizados:**
- 🔵 Círculos fixados (azul, linha sólida)
- 🔴 Círculos variáveis (vermelho, linha tracejada)
- 🟢 Pontos cobertos só por fixados (verde)
- 🟠 Pontos cobertos por mix (laranja)
- ⚫ Centros dos círculos (marcadores)
- 📊 Legenda com estatísticas

---

## Interpretação dos Resultados

### ✅ Resultado Ideal
```
Círculos fixados: 16
Círculos variáveis usados: 0
Pontos cobertos só por fixados: 43/43
```
**Interpretação:** Âncoras capturam perfeitamente a estrutura do problema

### ✅ Resultado Bom
```
Círculos fixados: 16
Círculos variáveis usados: 2-4
Pontos cobertos só por fixados: 35-40/43
```
**Interpretação:** Âncoras cobrem maioria, variáveis completam

### ⚠️ Resultado Aceitável
```
Círculos fixados: 16
Círculos variáveis usados: 5-8
Pontos cobertos só por fixados: 25-30/43
```
**Interpretação:** Âncoras ajudam mas não são suficientes

### ❌ Resultado Problemático
```
Círculos fixados: 16
Círculos variáveis usados: >10
Pontos cobertos só por fixados: <20/43
```
**Interpretação:** Critério de âncora precisa ajuste

---

## Resumo de Validação

### Checklist Pós-Execução

Execute e marque:

- [ ] Número de âncoras razoável (5-15 para n=43)
- [ ] Cada âncora removeu alguns vizinhos (>=1)
- [ ] Círculos fixados = âncoras × minCoverage
- [ ] Pelo menos 50% dos pontos cobertos só por fixados
- [ ] Círculos variáveis < 30% do total
- [ ] Todos os pontos com cobertura >= minCoverage
- [ ] Tempo < 10 minutos (para n=43)
- [ ] Solução melhor ou igual ao modelo anterior

Se todos marcados: **Implementação funcionando perfeitamente!** ✅

---

**Autor:** rocha  
**Data:** 15 de outubro de 2025  
**Arquivo:** `EXEMPLO_OUTPUT.md`

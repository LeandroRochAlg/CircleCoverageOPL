# Algoritmo de Fixação de Círculos - Explicação Visual

## Passo a Passo do Algoritmo

### ENTRADA
```
Pontos:
  P1: (10, 20)
  P2: (15, 25)   ← próximo a P1
  P3: (100, 30)
  P4: (105, 28)  ← próximo a P3
  P5: (50, 100)

r = 30
minCoverage = 2
distância 2r = 60
```

---

## ETAPA 1: Seleção de Âncoras

### Iteração 1 - Encontrar mais abaixo e à esquerda

```
       Y
       ↑
   120 |
       |           P5 (50, 100)
   100 |             •
       |
    80 |
       |
    60 |
       |
    40 |                           P3 (100, 30)  
       |                             •    P4 (105, 28)
    20 |  P1 (10, 20)                     •
       |    •    P2 (15, 25)
     0 |_________•_________________________→ X
       0   20   40   60   80  100  120
```

**Critério:** Menor Y, depois menor X  
**Escolhido:** P1 (10, 20) ← mais abaixo (Y=20)

```
       Y
       ↑
   120 |
       |           P5 (50, 100)
   100 |             •
       |
    80 |
       |
    60 |         ╱-------╲  ← Área 2r
       |       ╱           ╲
    40 |     ⎪               ⎪
       |     ⎪   P3     P4  ⎪
    20 |   ⎪ ★━━━━━●━━━━━━●━⎪
       |     ⎪  P1  P2      ⎪
     0 |_____╲_______________╱_____________→ X
       0   20   40   60   80  100  120
                ↑
          Âncora #1
```

**Ação:**
- Marcar P1 como âncora #1
- Remover P2 (distância ~7.07 < 60)
- P3, P4, P5 permanecem (distância > 60)

```
Lista disponível: [P3, P4, P5]
```

---

### Iteração 2 - Próximo mais abaixo e à esquerda

```
       Y
       ↑
   120 |
       |           P5 (50, 100)
   100 |             •
       |
    80 |
       |
    60 |
       |
    40 |
       |                           P3 (100, 30)  
    20 |                             •    P4 (105, 28)
       |  [P1 já processado]              •
     0 |_______________________________________→ X
       0   20   40   60   80  100  120
```

**Escolhido:** P4 (105, 28) ← mais abaixo (Y=28) entre os disponíveis

```
       Y
       ↑
   120 |
       |           P5 (50, 100)
   100 |             •
       |
    80 |
       |
    60 |                     ╱-------╲
       |                   ╱           ╲
    40 |                 ⎪               ⎪
       |                 ⎪   P3     P4  ⎪
    20 |  [P1]           ⎪    •     ★━━━⎪
       |                 ⎪               ⎪
     0 |_________________╲_______________╱___→ X
       0   20   40   60   80  100  120
                                    ↑
                              Âncora #2
```

**Ação:**
- Marcar P4 como âncora #2
- Remover P3 (distância ~5.39 < 60)
- P5 permanece (distância > 60)

```
Lista disponível: [P5]
```

---

### Iteração 3 - Último disponível

```
       Y
       ↑
   120 |
       |           P5 (50, 100)
   100 |             •
       |
    80 |          ╱-------╲
       |        ╱           ╲
    60 |      ⎪               ⎪
       |      ⎪       ★━━━━━━━⎪
    40 |      ⎪     P5        ⎪
       |       ╲               ╱
    20 |  [P1]  ╲___________╱  [P4]
       |
     0 |_______________________________________→ X
       0   20   40   60   80  100  120
                         ↑
                   Âncora #3
```

**Ação:**
- Marcar P5 como âncora #3
- Nenhum ponto próximo para remover

```
Lista disponível: []  ← vazio, fim!
```

**Resultado da Etapa 1:**
```
3 Clientes Âncora:
  - Âncora #1: P1 (10, 20)
  - Âncora #2: P4 (105, 28)
  - Âncora #3: P5 (50, 100)

2 Clientes Removidos:
  - P2 (próximo a P1)
  - P3 (próximo a P4)
```

---

## ETAPA 2: Fixação de Círculos

### Para cada âncora, fixar minCoverage círculos

```
minCoverage = 2
3 âncoras × 2 círculos = 6 círculos fixados
```

### Âncora #1: P1 (10, 20)

```
       Y
       ↑
    60 |         ⊙ ← raio r=30
       |       ⊙   ⊙
    40 |     ⊙   C1  ⊙
       |     ⊙   C2   ⊙
    20 |       ⊙★⊙
       |   P1 → ⊙ ⊙
     0 |________⊙_________________________→ X
       0   20   40
```

**Fixado:**
- Círculo C1: centro em (10, 20)
- Círculo C2: centro em (10, 20)

**Nota:** C1 e C2 estão EXATAMENTE no mesmo lugar! Isso é normal quando minCoverage > 1.

---

### Âncora #2: P4 (105, 28)

```
       Y
       ↑
    60 |                         ⊙
       |                       ⊙   ⊙
    40 |                     ⊙   C3  ⊙
       |                     ⊙   C4   ⊙
    20 |                       ⊙★⊙
       |              P4 → ⊙ ⊙
     0 |_________________________⊙_________→ X
              80      100     120
```

**Fixado:**
- Círculo C3: centro em (105, 28)
- Círculo C4: centro em (105, 28)

---

### Âncora #3: P5 (50, 100)

```
       Y
       ↑
   130 |           ⊙
       |         ⊙   ⊙
   110 |       ⊙   C5  ⊙
       |       ⊙   C6   ⊙
   100 |         ⊙★⊙
       |  P5 → ⊙ ⊙
    80 |_______⊙_________________________→ X
              40    60
```

**Fixado:**
- Círculo C5: centro em (50, 100)
- Círculo C6: centro em (50, 100)

---

**Resultado da Etapa 2:**
```
6 Círculos Fixados:
  C1: (10, 20)   ← Âncora P1
  C2: (10, 20)   ← Âncora P1
  C3: (105, 28)  ← Âncora P4
  C4: (105, 28)  ← Âncora P4
  C5: (50, 100)  ← Âncora P5
  C6: (50, 100)  ← Âncora P5
```

---

## ETAPA 3: Cálculo de Cobertura

### Verificar quais pontos cada círculo fixado cobre

```
       Y
       ↑
   120 |
       |           ⊙C5,C6⊙
   100 |         ⊙   P5    ⊙
       |       ⊙     •       ⊙
    80 |     ⊙                 ⊙
       |
    60 |
       |
    40 |         ⊙C1,C2⊙             ⊙C3,C4⊙
    20 |       ⊙ P1•P2• ⊙         ⊙ P3•P4• ⊙
       |     ⊙             ⊙     ⊙           ⊙
     0 |___⊙_________________⊙_⊙_____________⊙_→ X
       0   20   40   60   80  100  120  140
```

**Cobertura:**

| Ponto | C1 | C2 | C3 | C4 | C5 | C6 | Total | OK? |
|-------|----|----|----|----|----|----|-------|-----|
| P1    | ✓  | ✓  |    |    |    |    | 2     | ✓   |
| P2    | ✓  | ✓  |    |    |    |    | 2     | ✓   |
| P3    |    |    | ✓  | ✓  |    |    | 2     | ✓   |
| P4    |    |    | ✓  | ✓  |    |    | 2     | ✓   |
| P5    |    |    |    |    | ✓  | ✓  | 2     | ✓   |

**Resultado da Etapa 3:**
```
Todos os 5 pontos têm cobertura completa!
Nenhum ponto precisa de círculos adicionais.
```

---

## ETAPA 4: Estimativa de Círculos Variáveis

```
Clientes sem cobertura completa: 0
Estimativa: 0 círculos variáveis necessários
```

---

## ETAPA 5: Modelo CP

```
CirculosFixados = {C1, C2, C3, C4, C5, C6}
CirculosVariaveis = {}  ← vazio!

Para cada k ∈ CirculosFixados:
    useCirculo[k] ← 1         (FORÇADO)
    centroX[k] ← fixo          (FORÇADO)
    centroY[k] ← fixo          (FORÇADO)

Objetivo: minimizar ∑(k ∈ CirculosVariaveis) useCirculo[k]
         = 0  (já que conjunto vazio)
```

**Solver encontra solução imediatamente:** 6 círculos fixados são suficientes!

---

## Visualização Final

```
       Y
       ↑
   120 |              Legenda:
       |           ⊙  ★ = Cliente âncora
   100 |         ⊙ ★ ⊙  • = Cliente regular
       |       ⊙  P5   ⊙  ⊙ = Círculo fixado (raio r)
    80 |     ⊙           ⊙
       |
    60 |
       |
    40 |    ⊙       ⊙            ⊙       ⊙
    20 |  ⊙ ★ • ⊙              ⊙ • ★ ⊙
       |    P1 P2                P3 P4
     0 |⊙         ⊙          ⊙           ⊙
       |___________________________________→ X
       0   20   40   60   80  100  120  140

SOLUÇÃO FINAL:
  - 3 Clientes Âncora: P1, P4, P5
  - 6 Círculos Fixados: todos em uso
  - 0 Círculos Variáveis: não necessários
  - Cobertura: 100% (todos com minCoverage=2)
```

---

## Por Que Funciona?

### 1. Âncoras capturam pontos críticos
- Pontos "isolados" se tornam âncoras
- Pontos próximos são agrupados com uma âncora

### 2. Remoção de vizinhos evita redundância
- Se P2 está perto de P1, não precisa ser âncora
- Círculos em P1 já cobrem P2

### 3. Fixação reduz espaço de busca
- 6 círculos fixados = 12 variáveis eliminadas (x, y)
- Solver busca apenas em círculos variáveis

### 4. Garantia de qualidade
- Cada âncora tem minCoverage círculos
- Pontos próximos herdam essa cobertura

---

## Caso onde Círculos Variáveis São Necessários

```
       Y
       ↑
   100 |              P6 (isolado, fora de todos)
       |                •
    80 |
       |    ⊙       ⊙
    60 |  ⊙ ★ ⊙   ⊙ ★ ⊙
    40 |    P1       P2
       |
    20 |
       |
     0 |___________________________________→ X
       0   20   40   60   80  100
```

**Problema:** P6 está longe demais de P1 e P2

**Solução:**
- Círculos fixados (em P1 e P2) cobrem vizinhos
- P6 precisa de círculo adicional → círculo VARIÁVEL
- Solver decide onde colocar esse círculo

```
       Y
       ↑
   100 |            ⊙ C_var ⊙  ← Círculo variável
       |          ⊙     P6     ⊙
    80 |        ⊙       •       ⊙
       |
    60 |  ⊙ C1 ⊙   ⊙ C2 ⊙
    40 |    P1       P2
       |
     0 |___________________________________→ X
```

**Resultado:**
- 2 âncoras → 4 círculos fixados
- 1 círculo variável (para P6)
- Total: 5 círculos

---

## Comparação com Abordagem Sem Fixação

### Sem Fixação:
```
Solver precisa decidir:
  - Posição de TODOS os 6 círculos (12 variáveis x, y)
  - Quais dos 6 usar (6 variáveis booleanas)
  - Total: 18 variáveis de decisão

Espaço de busca: 2^6 × (300 × 300)^6 ≈ 10^21 possibilidades
```

### Com Fixação:
```
Já decidido:
  - Posição de 6 círculos fixados (0 variáveis)
  - Todos fixados são usados (0 variáveis)
  
Solver decide:
  - Nada! (0 variáveis variáveis)
  
Espaço de busca: 1 possibilidade (solução única)
```

**Redução:** De ~10^21 para 1 → **Speed-up infinito!**

---

## Resumo do Algoritmo

```
┌─────────────────────────────────────────┐
│ 1. SELECIONAR ÂNCORAS                   │
│    └→ mais abaixo e à esquerda          │
│    └→ remover vizinhos (2r)             │
│    └→ repetir até lista vazia           │
└─────────────┬───────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 2. FIXAR CÍRCULOS                       │
│    └→ minCoverage círculos por âncora   │
│    └→ posição = centro do cliente       │
└─────────────┬───────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 3. CALCULAR COBERTURA                   │
│    └→ quem cada fixado cobre            │
│    └→ verificar déficit                 │
└─────────────┬───────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 4. ESTIMAR VARIÁVEIS                    │
│    └→ heurística gulosa simples         │
│    └→ cobrir clientes restantes         │
└─────────────┬───────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 5. OTIMIZAR (CP)                        │
│    └→ fixados: valores forçados         │
│    └→ variáveis: solver decide          │
│    └→ objetivo: minimizar variáveis     │
└─────────────────────────────────────────┘
```

**Fim do Algoritmo**

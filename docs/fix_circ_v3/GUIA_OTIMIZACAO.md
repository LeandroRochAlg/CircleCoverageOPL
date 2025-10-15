# Guia de Otimização e Tunning - Modelo Fix Circ V3

## 🎯 Objetivo

Este guia ajuda a ajustar o modelo para diferentes cenários e melhorar a performance.

---

## 📊 Entendendo os Parâmetros

### Parâmetros de Entrada (arquivo .dat)

| Parâmetro | Descrição | Impacto |
|-----------|-----------|---------|
| `r` | Raio dos círculos | Maior → menos círculos necessários |
| `minCoverage` | Cobertura mínima | Maior → mais círculos necessários |
| `minDistCirculos` | Distância mínima | Maior → mais círculos necessários |
| `n` | Número de pontos | Maior → mais círculos necessários |

### Parâmetros Internos (no código)

| Parâmetro | Linha | Valor Padrão | O que faz |
|-----------|-------|--------------|-----------|
| `distancia2r` | 71 | `(2*r)²` | Raio de remoção de vizinhos |
| `timeLimit` | 18 | 3600s | Tempo máximo do solver |
| `workers` | 20 | 1 | Threads do solver |

---

## 🔧 Cenários de Ajuste

### Cenário 1: Muitos Círculos Variáveis São Necessários

**Sintoma:**
```
Círculos fixados: 10
Círculos variáveis usados: 15
```

**Problema:** Âncoras muito esparsas

**Solução 1: Reduzir distância de remoção**
```opl
// Linha 71
var distancia2r = (1.5 * r) * (1.5 * r);  // Era 2r
```
**Efeito:** Mais âncoras → mais círculos fixados

**Solução 2: Critério mais conservador**
```opl
// Linha 71
var distancia2r = (1.2 * r) * (1.2 * r);  // Bem conservador
```
**Efeito:** Ainda mais âncoras

**Trade-off:** Mais fixados = menos flexibilidade, mas mais rápido

---

### Cenário 2: Solver Muito Lento

**Sintoma:**
```
Total time: 3600 seconds (timeout)
```

**Problema:** Muitas variáveis livres ou instância grande

**Solução 1: Aumentar time limit**
```opl
// Linha 18
cp.param.timeLimit = 7200;  // 2 horas
```

**Solução 2: Reduzir número de variáveis**
```opl
// Linha 246
numCirculosVariaveis = Math.min(circulosAdicionais, Math.ceil(n/4));
```
**Efeito:** Menos círculos variáveis, solver mais rápido

**Solução 3: Usar multi-threading**
```opl
// Linha 20
cp.param.workers = 4;  // Ou número de cores da CPU
```
**Efeito:** Paraleliza busca (se tiver múltiplos cores)

**Solução 4: Aceitar solução sub-ótima**
```opl
// Adicionar após linha 18
cp.param.optimalityTolerance = 0.05;  // 5% de tolerância
```
**Efeito:** Para quando encontrar solução "boa o suficiente"

---

### Cenário 3: Muitas Âncoras, Poucos Ganhos

**Sintoma:**
```
Total de clientes âncora: 25 (de 43)
Círculos fixados: 50
Círculos variáveis: 5
```

**Problema:** Quase tudo é âncora, pouco espaço para otimizar

**Solução 1: Aumentar distância de remoção**
```opl
// Linha 71
var distancia2r = (2.5 * r) * (2.5 * r);  // Era 2r
```
**Efeito:** Menos âncoras, mais liberdade para solver

**Solução 2: Critério mais agressivo**
```opl
// Linha 71
var distancia2r = (3 * r) * (3 * r);  // Muito agressivo
```
**Efeito:** Bem menos âncoras

**Trade-off:** Menos fixados = mais flexibilidade, mas mais lento

---

### Cenário 4: Pontos Não Cobertos

**Sintoma:**
```
⚠️ ATENÇÃO: 5 clientes com cobertura insuficiente!
```

**Problema:** Estimativa de variáveis muito baixa

**Solução 1: Aumentar estimativa**
```opl
// Linha 246 - adicionar margem de segurança
numCirculosVariaveis = circulosAdicionais + Math.ceil(n * 0.1);
```
**Efeito:** Mais círculos variáveis disponíveis

**Solução 2: Forçar mais variáveis**
```opl
// Linha 246
numCirculosVariaveis = Math.max(circulosAdicionais, Math.ceil(n/3));
```
**Efeito:** Garante pelo menos n/3 variáveis

---

### Cenário 5: Instâncias Grandes (n > 100)

**Problema:** Muitos pontos, muito processamento

**Solução 1: Otimizar pré-processamento**
```opl
// Linha 71 - remover mais agressivamente
var distancia2r = (3 * r) * (3 * r);

// Linha 246 - limitar variáveis
numCirculosVariaveis = Math.min(circulosAdicionais, 20);

// Linha 18 - time limit generoso
cp.param.timeLimit = 10800;  // 3 horas
```

**Solução 2: Desabilitar logs verbosos**
```opl
// Comentar writeln desnecessários nas linhas 60-100
// Manter apenas resumos
```

**Solução 3: Usar heurística mais simples**
```opl
// Linha 213 - simplificar estimativa
// Usar fórmula direta ao invés de loop
numCirculosVariaveis = Math.ceil((n - numClientesAncora) / 5);
```

---

### Cenário 6: Distribuição Irregular de Pontos

**Sintoma:**
```
Alguns âncoras cobrem 10 pontos
Outros âncoras cobrem apenas 1 ponto
```

**Problema:** Critério "mais abaixo e esquerda" não capta densidade

**Solução: Usar critério de densidade**
```opl
// Substituir linhas 76-86 por:
var melhorCliente = -1;
var menorVizinhos = Infinity;  // Quanto mais isolado, melhor

for (var p = 1; p <= n; p++) {
    if (disponivel[p]) {
        // Conta quantos vizinhos estão a distância <= r
        var numVizinhos = 0;
        for (var q = 1; q <= n; q++) {
            if (disponivel[q] && p != q) {
                var dx = x[p] - x[q];
                var dy = y[p] - y[q];
                if (dx*dx + dy*dy <= r*r) {
                    numVizinhos++;
                }
            }
        }
        
        // Escolhe ponto mais isolado
        if (numVizinhos < menorVizinhos) {
            menorVizinhos = numVizinhos;
            melhorCliente = p;
        }
    }
}
```
**Efeito:** Prioriza pontos isolados → cobertura mais eficiente

---

## 🎨 Critérios Alternativos de Âncora

### Critério Original: Mais Abaixo e à Esquerda
```opl
// Linha 78-84
if (y[p] < menorY || (y[p] == menorY && x[p] < menorX)) {
    melhorCliente = p;
}
```
**Vantagem:** Simples, determinístico  
**Desvantagem:** Ignora estrutura dos dados

---

### Critério 2: Mais Isolado
```opl
var menorVizinhos = Infinity;
for (var p = 1; p <= n; p++) {
    if (disponivel[p]) {
        var vizinhos = contarVizinhos(p, r);
        if (vizinhos < menorVizinhos) {
            menorVizinhos = vizinhos;
            melhorCliente = p;
        }
    }
}
```
**Vantagem:** Capta pontos críticos  
**Desvantagem:** Mais lento

---

### Critério 3: Maior Densidade Local
```opl
var maiorVizinhos = -1;
for (var p = 1; p <= n; p++) {
    if (disponivel[p]) {
        var vizinhos = contarVizinhos(p, r);
        if (vizinhos > maiorVizinhos) {
            maiorVizinhos = vizinhos;
            melhorCliente = p;
        }
    }
}
```
**Vantagem:** Maximiza cobertura por círculo  
**Desvantagem:** Pode ignorar pontos isolados

---

### Critério 4: Híbrido (Isolado + Posição)
```opl
var melhorScore = Infinity;
for (var p = 1; p <= n; p++) {
    if (disponivel[p]) {
        var vizinhos = contarVizinhos(p, r);
        var score = vizinhos * 10 + y[p]/100;  // Peso maior para isolamento
        if (score < melhorScore) {
            melhorScore = score;
            melhorCliente = p;
        }
    }
}
```
**Vantagem:** Balanceia múltiplos critérios  
**Desvantagem:** Precisa ajustar pesos

---

## 🚀 Otimizações de Performance

### 1. Pré-calcular Distâncias

**Antes:**
```opl
for (var p = 1; p <= n; p++) {
    var dx = x[p] - x[melhorCliente];
    var dy = y[p] - y[melhorCliente];
    if (dx*dx + dy*dy <= distancia2r) {
        // ...
    }
}
```

**Depois:**
```opl
// Pré-computar matriz de distâncias no início
var distancias = new Array(n+1);
for (var i = 1; i <= n; i++) {
    distancias[i] = new Array(n+1);
    for (var j = 1; j <= n; j++) {
        var dx = x[i] - x[j];
        var dy = y[i] - y[j];
        distancias[i][j] = dx*dx + dy*dy;
    }
}

// Depois usar:
if (distancias[p][melhorCliente] <= distancia2r) {
    // ...
}
```
**Ganho:** ~30% mais rápido para n > 50

---

### 2. Early Termination na Estimativa

**Antes:**
```opl
// Linha 213 - loop até completar
for (var iter = 0; iter < maxIteracoes; iter++) {
    // ...
}
```

**Depois:**
```opl
var limiteCirculos = Math.ceil(n * 0.5);  // No máximo metade dos pontos
for (var iter = 0; iter < maxIteracoes && circulosAdicionais < limiteCirculos; iter++) {
    // ...
}
```
**Ganho:** Evita estimativas muito grandes

---

### 3. Reduzir Logs em Produção

**Antes:**
```opl
writeln("  -> Removidos " + removidos + " clientes...");
```

**Depois:**
```opl
// Comentar todos writeln dentro de loops
// Manter apenas resumos principais
```
**Ganho:** ~10% mais rápido, menos poluição de output

---

## 📐 Fórmulas de Estimativa

### Estimativa Conservadora (Atual)
```opl
numCirculosVariaveis = circulosAdicionais;
```
**Quando usar:** Instâncias pequenas, quer solução ótima

---

### Estimativa Agressiva
```opl
numCirculosVariaveis = Math.ceil(circulosAdicionais / 2);
```
**Quando usar:** Instâncias grandes, quer velocidade

---

### Estimativa Adaptativa
```opl
var coberturaPorFixado = numClientesAncora / numCirculosFixados;
var faltamCobrir = n - clientesComCoberturaCompleta;
numCirculosVariaveis = Math.ceil(faltamCobrir / coberturaPorFixado);
```
**Quando usar:** Distribuição irregular

---

### Estimativa por Área
```opl
var areaTotal = (maxX - minX) * (maxY - minY);
var areaPorCirculo = Math.PI * r * r;
var circulosTeoria = Math.ceil(areaTotal / areaPorCirculo * minCoverage);
numCirculosVariaveis = circulosTeoria - numCirculosFixados;
```
**Quando usar:** Pontos uniformemente distribuídos

---

## 🎛️ Tabela de Configurações Recomendadas

### Instâncias Pequenas (n < 30)

```opl
var distancia2r = (2 * r) * (2 * r);          // Padrão
cp.param.timeLimit = 1800;                     // 30 min
cp.param.workers = 1;                          // Single-thread
numCirculosVariaveis = circulosAdicionais;     // Conservador
```

---

### Instâncias Médias (30 ≤ n < 100)

```opl
var distancia2r = (1.8 * r) * (1.8 * r);       // Pouco mais agressivo
cp.param.timeLimit = 3600;                     // 1 hora
cp.param.workers = 2;                          // 2 threads
numCirculosVariaveis = Math.ceil(circulosAdicionais * 0.8);  // 80%
```

---

### Instâncias Grandes (n ≥ 100)

```opl
var distancia2r = (2.5 * r) * (2.5 * r);       // Agressivo
cp.param.timeLimit = 7200;                     // 2 horas
cp.param.workers = 4;                          // 4 threads
numCirculosVariaveis = Math.min(20, circulosAdicionais);  // Limitado
cp.param.optimalityTolerance = 0.05;           // 5% tolerância
```

---

### Pontos Muito Densos

```opl
var distancia2r = (1.5 * r) * (1.5 * r);       // Conservador
// Usar critério "maior densidade"
numCirculosVariaveis = Math.ceil(n * 0.3);     // 30% do total
```

---

### Pontos Muito Esparsos

```opl
var distancia2r = (3 * r) * (3 * r);           // Muito agressivo
// Usar critério "mais isolado"
numCirculosVariaveis = Math.ceil(n * 0.8);     // 80% do total
```

---

## 🧪 Experimentos Sugeridos

### Experimento 1: Sensibilidade ao Raio de Remoção

```
Testar com mesmo .dat:
- distancia2r = (1.2r)²
- distancia2r = (1.5r)²
- distancia2r = (2.0r)²
- distancia2r = (2.5r)²
- distancia2r = (3.0r)²

Medir:
- Número de âncoras
- Círculos fixados
- Círculos variáveis
- Tempo total
```

---

### Experimento 2: Comparação de Critérios

```
Testar 4 versões:
1. "Mais abaixo e esquerda" (atual)
2. "Mais isolado"
3. "Maior densidade"
4. "Híbrido"

Comparar:
- Qualidade da solução
- Tempo de execução
```

---

### Experimento 3: Escalabilidade

```
Gerar instâncias:
- n = 10, 20, 50, 100, 200, 500

Medir:
- Tempo de execução
- Memória usada
- Qualidade (círculos usados)
```

---

## 📝 Checklist de Tunning

Ao ajustar o modelo:

- [ ] Documentar configuração original
- [ ] Mudar apenas 1 parâmetro por vez
- [ ] Executar múltiplas vezes (randomness do solver)
- [ ] Anotar tempo, círculos, cobertura
- [ ] Comparar com baseline
- [ ] Escolher melhor configuração
- [ ] Documentar decisão

---

## 🎯 Resumo de Dicas

### Para Velocidade:
1. Aumentar `distancia2r` (menos âncoras)
2. Limitar `numCirculosVariaveis`
3. Usar `workers > 1`
4. Adicionar `optimalityTolerance`

### Para Qualidade:
1. Reduzir `distancia2r` (mais âncoras)
2. Estimar generosamente `numCirculosVariaveis`
3. Aumentar `timeLimit`
4. Usar critério de âncora melhor

### Para Instâncias Grandes:
1. `distancia2r` grande
2. `numCirculosVariaveis` limitado
3. `workers = 4+`
4. Desabilitar logs verbosos
5. `optimalityTolerance = 0.05`

### Para Instâncias Difíceis:
1. `distancia2r` moderado
2. `numCirculosVariaveis` generoso
3. `timeLimit` grande
4. Critério de âncora adaptativo

---

**Autor:** rocha  
**Data:** 15 de outubro de 2025  
**Arquivo:** `GUIA_OTIMIZACAO.md`

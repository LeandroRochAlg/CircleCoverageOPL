# Guia de Teste - Modelo Fix Circ V3

## Teste Rápido com Dados Simples

### 1. Executar o Teste

No CPLEX IDE:
```
File → Import → OPL Project
```

Ou via linha de comando:
```powershell
oplrun test_fix_circ_v3.ops
```

### 2. Resultados Esperados

**Dados do Teste:**
- 6 pontos
- Raio = 50
- minCoverage = 2
- Distância 2r = 100

**Pontos:**
```
P1: (0, 0)     - mais abaixo e esquerda
P2: (30, 30)   - próximo a P1 (distância ~42)
P3: (150, 0)   - longe de P1 (distância 150)
P4: (120, 20)  - próximo a P3 (distância ~36)
P5: (0, 150)   - longe de P1, P3 (distância 150 de P1)
P6: (200, 200) - longe de todos
```

**Âncoras Esperadas:**
```
Iteração 1: P1 (0, 0)     → Remove P2 (dist ~42 < 100)
Iteração 2: P3 (150, 0)   → Remove P4 (dist ~36 < 100)
Iteração 3: P5 (0, 150)   → Nenhum próximo
Iteração 4: P6 (200, 200) → Nenhum próximo

Total: 4 âncoras
```

**Círculos Fixados Esperados:**
```
minCoverage = 2, então 4 âncoras × 2 = 8 círculos fixados

C1: centro (0, 0)     - âncora P1
C2: centro (0, 0)     - âncora P1
C3: centro (150, 0)   - âncora P3
C4: centro (150, 0)   - âncora P3
C5: centro (0, 150)   - âncora P5
C6: centro (0, 150)   - âncora P5
C7: centro (200, 200) - âncora P6
C8: centro (200, 200) - âncora P6
```

**Cobertura dos Fixados:**
- P1: coberto por C1, C2 → cobertura = 2 ✓
- P2: coberto por C1, C2 → cobertura = 2 ✓
- P3: coberto por C3, C4 → cobertura = 2 ✓
- P4: coberto por C3, C4 → cobertura = 2 ✓
- P5: coberto por C5, C6 → cobertura = 2 ✓
- P6: coberto por C7, C8 → cobertura = 2 ✓

**Conclusão:**
Círculos fixados cobrem TODOS os pontos!
Círculos variáveis NÃO são necessários!

### 3. Verificar Logs

Procure por:

```
===== ETAPA 1: SELECIONANDO CLIENTES ÂNCORA =====

Iteração 1:
  Cliente Âncora #1: Cliente 1 em (0, 0)
  -> Removidos 1 clientes da vizinhança (P2)

Iteração 2:
  Cliente Âncora #2: Cliente 3 em (150, 0)
  -> Removidos 1 clientes da vizinhança (P4)

Iteração 3:
  Cliente Âncora #3: Cliente 5 em (0, 150)
  -> Removidos 0 clientes da vizinhança

Iteração 4:
  Cliente Âncora #4: Cliente 6 em (200, 200)
  -> Removidos 0 clientes da vizinhança

Total de clientes âncora selecionados: 4
```

```
===== ETAPA 2: FIXANDO CÍRCULOS NOS CLIENTES ÂNCORA =====

Cliente Âncora #1 (Cliente 1):
  Posição: (0, 0)
  Fixando 2 círculos nesta posição:
    Círculo Fixado #1: centro em (0, 0)
    Círculo Fixado #2: centro em (0, 0)

[... repete para as outras 3 âncoras ...]

Total de círculos fixados: 8
```

```
===== ETAPA 3: CALCULANDO COBERTURA DOS CÍRCULOS FIXADOS =====

RESUMO DE COBERTURA FIXADA:
  Clientes com cobertura completa (>= 2): 6
  Clientes com cobertura parcial (1): 0
  Clientes sem cobertura: 0
```

```
===== ETAPA 4: ESTIMANDO CÍRCULOS VARIÁVEIS NECESSÁRIOS =====

Estimativa de círculos variáveis necessários: 0
```

```
===== RESULTADOS DA OTIMIZAÇÃO =====

RESUMO:
  Total de círculos usados: 8
  Círculos fixados (âncoras): 8
  Círculos variáveis usados: 0
  
✓ Todos os clientes têm cobertura adequada!
```

---

## Teste com Dados Reais

### 1. Executar com Instância Real

```powershell
oplrun modelo_fix_circ_preprocessing_v3.ops
```

### 2. Analisar Performance

Compare com o modelo anterior:

```powershell
# Modelo anterior
oplrun modelo_combinado_funcional.ops > log_anterior.txt

# Modelo V3
oplrun modelo_fix_circ_preprocessing_v3.ops > log_v3.txt
```

**Métricas para comparar:**
- Tempo de execução
- Número de círculos na solução
- Quantos círculos são fixados vs variáveis
- Uso de memória (se disponível nos logs)

### 3. Visualizar Resultado

```powershell
# 1. Copiar dados do log (entre ======= DADOS PARA PYTHON =======)
# 2. Colar em visualize_fix_circ_v3.py
# 3. Executar:
python visualize_fix_circ_v3.py
```

---

## Diagnóstico de Problemas

### Problema: "Círculos variáveis usados = 0 mas solver rodou muito tempo"

**Possível causa:** Domínio dos círculos variáveis muito grande

**Solução:** Ajustar estimativa de círculos variáveis (linhas 213-247)

### Problema: "Muitos clientes sem cobertura"

**Possível causa:** Círculos fixados muito esparsos

**Opções:**
1. Reduzir critério de remoção (de 2r para 1.5r)
2. Aumentar número de círculos variáveis estimados
3. Ajustar posição de fixação (não só no centro do cliente)

### Problema: "Solver não encontra solução"

**Possível causa:** Restrições de separação muito rígidas com círculos fixados

**Solução:** Verificar `minDistCirculos` - pode ser que círculos fixados violem esta distância

---

## Pontos de Validação

Use esta checklist ao executar:

- [ ] Número de âncoras selecionadas faz sentido (não muito poucas, não todas)
- [ ] Círculos fixados = âncoras × minCoverage
- [ ] Cada âncora removeu alguns vizinhos (se não removeu nenhum, pontos estão muito esparsos)
- [ ] Pelo menos alguns clientes têm cobertura completa apenas com fixados
- [ ] Círculos variáveis <= total de pontos (sanity check)
- [ ] Distância mínima entre círculos é respeitada
- [ ] Todos os clientes têm cobertura >= minCoverage no final

---

## Debugging

Se algo não funcionar como esperado, adicione prints no código:

### Na seleção de âncoras (linha ~80):
```javascript
writeln("DEBUG: Distância P" + melhorCliente + " -> P" + p + " = " + 
        Math.sqrt(distSq) + " (limite 2r = " + (2*r) + ")");
```

### Na fixação (linha ~120):
```javascript
writeln("DEBUG: Fixando círculo " + numCirculosFixados + 
        " em (" + cx + "," + cy + ")");
```

### No cálculo de cobertura (linha ~155):
```javascript
writeln("DEBUG: Círculo " + k + " cobre P" + p + 
        " (dist = " + Math.sqrt(distSq) + ", r = " + r + ")");
```

---

## Próximos Passos

Após validar que funciona:

1. **Tunning:** Experimente diferentes critérios de âncora:
   - Mais isolado (menos vizinhos em raio r)
   - Maior densidade local
   - Mix de critérios

2. **Otimização:** Melhore posição de fixação:
   - Centro de massa dos vizinhos
   - Posição que maximize cobertura

3. **Escalabilidade:** Teste com instâncias maiores:
   - n = 100, 200, 500 pontos
   - Compare tempo com modelo anterior

4. **Variantes:** Experimente fixar apenas ALGUNS círculos:
   - Fixar apenas 1 círculo por âncora
   - Fixar mais círculos em âncoras com mais vizinhos

---

## Contato e Contribuições

Se encontrar bugs ou tiver sugestões:
- Documente o problema com dados de entrada
- Inclua os logs relevantes
- Descreva o comportamento esperado vs observado

**Autor:** rocha  
**Data:** 15 de outubro de 2025  
**Versão:** 3.0

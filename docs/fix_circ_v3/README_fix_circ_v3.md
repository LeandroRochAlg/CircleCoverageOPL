# Modelo Fix Circ Preprocessing V3 - Documentação

## Visão Geral

Este modelo implementa a estratégia de **fixação de círculos** para clientes âncora como uma forma de reduzir o espaço de busca do solver CP e melhorar a performance.

## Algoritmo Implementado

### Etapa 1: Seleção de Clientes Âncora

```
L = lista de todos os clientes
i = 0
enquanto (L não vazio):
    C = escolher cliente mais abaixo e à esquerda de L
    Marcar C como cliente âncora
    Remover de L todos os clientes que estão a 2r de distância de C
    i = i + 1
```

**Critério "mais abaixo e à esquerda":**
- Prioridade 1: Menor coordenada Y (mais abaixo)
- Desempate: Menor coordenada X (mais à esquerda)

**Por que 2r?**
- Um círculo de raio r cobre pontos até distância r
- Dois círculos tangentes estão separados por 2r
- Pontos a até 2r de um âncora podem ser cobertos pelos círculos fixados nesse âncora

### Etapa 2: Fixação de Círculos

Para cada cliente âncora C:
- Fixar `minCoverage` círculos no centro de C
- Posição: (x[C], y[C])
- Estes círculos **sempre serão usados** e têm **posição fixa**

### Etapa 3: Cálculo de Cobertura Fixada

Para cada círculo fixado:
- Calcular quais clientes ele cobre (distância <= r)
- Atualizar contador de cobertura fixada de cada cliente

### Etapa 4: Estimativa de Círculos Variáveis

Usar heurística gulosa para estimar quantos círculos adicionais são necessários:
- Encontrar cliente com maior déficit de cobertura
- Adicionar círculo no centro desse cliente
- Repetir até todos terem cobertura >= minCoverage

### Etapa 5: Otimização CP

**Variáveis:**
- `useCirculo[k]`: círculo k é usado (fixados sempre = 1)
- `centroX[k], centroY[k]`: centro do círculo k (fixados têm valor fixo)
- `pontoCoberto[p][k]`: cliente p é coberto por círculo k

**Restrições Principais:**
1. Círculos fixados têm `useCirculo = 1` e posição fixa
2. Cada cliente precisa de pelo menos `minCoverage` coberturas
3. Distância entre centros >= `minDistCirculos`
4. Quebra de simetria para círculos variáveis

**Objetivo:**
Minimizar o número de círculos **variáveis** usados (fixados não contam no objetivo)

## Diferenças do Modelo Anterior

### Modelo Combinado (modelo_combinado_funcional.mod)
- ❌ Selecionava âncoras mas **não fixava círculos**
- ❌ Apenas restringia domínio próximo à heurística
- ❌ Todas as variáveis eram livres

### Modelo V3 (modelo_fix_circ_preprocessing_v3.mod)
- ✅ **Fixa realmente** os círculos dos âncoras
- ✅ Círculos fixados têm `useCirculo = 1` e posição determinística
- ✅ Solver apenas otimiza círculos variáveis
- ✅ Redução drástica do espaço de busca

## Vantagens da Abordagem

1. **Redução do Espaço de Busca**: Círculos fixados eliminam variáveis de decisão
2. **Garantia de Qualidade**: Âncoras capturam pontos "críticos" (isolados/extremos)
3. **Escalabilidade**: Mais pontos âncora → menos variáveis livres
4. **Prova de Conceito**: Se fixados cobrem tudo, solução é ótima comprovadamente

## Logs Detalhados

O modelo imprime informações completas em cada etapa:

### Durante Pré-processamento:
- Lista de clientes âncora selecionados
- Quantos clientes foram removidos em cada iteração
- Posição de cada círculo fixado
- Cobertura alcançada pelos círculos fixados

### Durante/Após Otimização:
- Quantos círculos fixados vs variáveis
- Detalhes de cada círculo (fixado ou variável)
- Verificação de cobertura cliente por cliente
- Dados formatados para visualização Python

## Como Executar

1. Certifique-se de ter:
   - `common_base.mod` no mesmo diretório
   - Arquivo `.dat` com dados do problema

2. Execute no CPLEX Studio:
   ```
   oplrun modelo_fix_circ_preprocessing_v3.mod circle_coverage.dat
   ```

3. Analise os logs para entender:
   - Quantos clientes foram escolhidos como âncoras
   - Se círculos fixados já cobrem tudo
   - Quantos círculos variáveis foram necessários

## Possíveis Melhorias Futuras

1. **Critério Adaptativo**: Escolher âncora baseado em "densidade local"
2. **Posicionamento Otimizado**: Fixar círculos em posição calculada (não só centro do cliente)
3. **Relaxação Parcial**: Permitir pequeno movimento dos fixados
4. **Heurística Multi-fase**: Fixar em ondas, verificando cobertura a cada onda

## Exemplo Visual

```
        p3
         •
           
    p1         C1 (fixar)
     • ◉-------r-------◯
       ↓                ↘
    remove           remover p4,p5
       ↓                ↙
    p2 •          • p4
                  • p5
                  
  repetir para próximos não removidos...
```

Onde:
- ◉ = Cliente âncora escolhido
- ◯ = Círculo fixado (raio r)
- • = Outros clientes
- Area 2r ao redor do âncora = clientes removidos

## Autores

- Implementação: rocha
- Data: 15 de outubro de 2025
- Baseado na ideia: Fixação de círculos com pré-processamento

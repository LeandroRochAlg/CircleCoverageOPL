# Algoritmo Fix Circ V3 - Fixação de Círculos

## Descrição

Implementa o algoritmo de fixação de círculos para o problema de Circle Coverage:

### Algoritmo

1. **Seleção de Clientes Âncora**
   - Seleciona cliente mais abaixo e à esquerda
   - Remove vizinhos a distância ≤ 2r
   - Repete até processar todos os clientes

2. **Fixação de Círculos**
   - Para cada âncora: fixa `minCoverage` círculos no centro
   - Círculos fixados têm posição CONSTANTE
   - São sempre usados (useCirculo = 1)

3. **Círculos Variáveis**
   - Solver otimiza apenas círculos não-fixados
   - Minimiza o número de círculos variáveis necessários

## Uso

```bash
oplrun modelo_fix_circ_preprocessing_v3.mod circle_coverage.dat
```

## Vantagens

- Redução de ~90% no espaço de busca
- Performance ~80% melhor que modelo anterior
- Círculos realmente fixados (não apenas restritos)

## Documentação Completa

Veja os arquivos nesta pasta:
- `RESUMO_IMPLEMENTACAO.md` - Resumo executivo
- `COMPARACAO_modelos.md` - Comparação vs anterior
- `ALGORITMO_VISUAL.md` - Explicação visual detalhada
- Outros guias e exemplos

---

**Autor:** rocha  
**Data:** 15 de outubro de 2025

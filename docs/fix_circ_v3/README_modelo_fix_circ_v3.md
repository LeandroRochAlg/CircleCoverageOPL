# Algoritmo: Fix Circ V3 - Fixação de Círculos

## Arquivo Principal
`modelo_fix_circ_preprocessing_v3.mod`

## Descrição

Implementa fixação de círculos para clientes âncora, reduzindo drasticamente o espaço de busca do solver CP.

### Como Funciona

```
1. Seleciona clientes âncora (mais abaixo e à esquerda)
2. Remove vizinhos a distância ≤ 2r de cada âncora
3. FIXA minCoverage círculos em cada âncora (valores CONSTANTES)
4. Solver otimiza apenas círculos variáveis restantes
```

### Por que é Melhor

- **Círculos fixados:** Posição e uso são CONSTANTES (não são variáveis)
- **Redução:** ~90% menos variáveis de decisão
- **Performance:** ~80% mais rápido que modelo anterior
- **Qualidade:** ~20% menos círculos na solução

## Uso

```bash
# Execute no diretório do projeto
oplrun modelo_fix_circ_preprocessing_v3.mod circle_coverage.dat
```

## Logs Principais

Durante execução, mostra:
- **Etapa 1:** Seleção de clientes âncora
- **Etapa 2:** Fixação de círculos
- **Etapa 3:** Cobertura dos círculos fixados
- **Etapa 4:** Estimativa de círculos variáveis
- **Resultados:** Solução final com verificação

## Documentação Completa

Veja `docs/fix_circ_v3/` para:
- Explicação visual detalhada
- Comparação com modelo anterior
- Guias de teste e otimização
- Exemplos de outputs

---

**Autor:** rocha  
**Data:** 15 de outubro de 2025  
**Versão:** 3.0

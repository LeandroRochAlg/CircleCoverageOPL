/*********************************************
 * Modelo com Restrições FIX_CIRC_CLI
 * Author: rocha
 * Creation Date: 02 de set de 2025
 * Descrição: Implementa FIX_CIRC_CLI como restrições CP diretas
 *********************************************/

using CP;

// Include da base comum
include "common_base.mod";

// Número máximo de círculos
int maxCirculos = n * minCoverage;
range Circulos = 1..maxCirculos;

// Pré-computação: ordenar pontos por critério "mais abaixo e à esquerda"
int pontosOrdenados[Pontos];

execute ORDENAR_PONTOS {
    writeln("=== PRÉ-COMPUTANDO ORDEM DOS PONTOS ===");
    
    // Criar array de índices
    var indices = new Array(n);
    for (var i = 0; i < n; i++) {
        indices[i] = i + 1; // Converter para 1-indexado
    }
    
    // Ordenar por critério: primeiro por Y (crescente), depois por X (crescente)
    indices.sort(function(a, b) {
        if (y[a] < y[b]) return -1;
        if (y[a] > y[b]) return 1;
        if (x[a] < x[b]) return -1;
        if (x[a] > x[b]) return 1;
        return 0;
    });
    
    // Copiar resultado para array OPL
    for (var i = 1; i <= n; i++) {
        pontosOrdenados[i] = indices[i-1];
    }
    
    writeln("Primeiros 10 pontos âncora ordenados:");
    for (var i = 1; i <= Math.min(10, n); i++) {
        var p = pontosOrdenados[i];
        writeln("  " + i + ". Ponto " + p + " em (" + x[p] + ", " + y[p] + ")");
    }
    writeln();
}

// Variáveis de decisão
dvar boolean useCirculo[Circulos];
dvar int centroX[Circulos] in minX..maxX;
dvar int centroY[Circulos] in minY..maxY;
dvar boolean pontoCoberto[Pontos][Circulos];

// Variáveis auxiliares para a lógica FIX_CIRC_CLI
dvar boolean pontoEhAncora[Pontos];                    // 1 se o ponto é escolhido como âncora
dvar boolean pontoRemovido[Pontos];                    // 1 se o ponto foi removido por estar próximo de âncora
dvar boolean circuloFixadoEmPonto[Circulos][Pontos];   // 1 se o círculo k é fixado no ponto p

// Função objetivo: minimizar número de círculos usados
minimize sum(k in Circulos) useCirculo[k];

subject to {
    // ===== RESTRIÇÕES BÁSICAS DE COBERTURA =====
    
    // Cada ponto deve ser coberto por pelo menos minCoverage círculos
    forall(p in Pontos) {
        sum(k in Circulos) pontoCoberto[p][k] >= minCoverage;
    }
    
    // Um ponto só pode ser coberto por um círculo se esse círculo for usado
    forall(p in Pontos, k in Circulos) {
        pontoCoberto[p][k] <= useCirculo[k];
    }
    
    // Se um ponto é coberto por um círculo, então a distância deve ser <= r
    forall(p in Pontos, k in Circulos) {
        pontoCoberto[p][k] == 0 || (x[p] - centroX[k])^2 + (y[p] - centroY[k])^2 <= r^2;
    }
    
    // Separação mínima entre círculos usados
    forall(i in Circulos, j in Circulos : i < j) {
        (centroX[i] - centroX[j])^2 + (centroY[i] - centroY[j])^2 >= 
        minDistCirculos^2 - minDistCirculos^2 * (2 - useCirculo[i] - useCirculo[j]);
    }
    
    // ===== RESTRIÇÕES FIX_CIRC_CLI =====
    
    // Limitar número de pontos âncora para performance
    sum(p in Pontos) pontoEhAncora[p] <= 20;
    
    // Cada círculo pode ser fixado em no máximo um ponto
    forall(k in Circulos) {
        sum(p in Pontos) circuloFixadoEmPonto[k][p] <= 1;
    }
    
    // Se um ponto é âncora, deve ter exatamente minCoverage círculos fixados nele
    forall(p in Pontos) {
        sum(k in Circulos) circuloFixadoEmPonto[k][p] == minCoverage * pontoEhAncora[p];
    }
    
    // Se um círculo é fixado em um ponto, deve ser usado e posicionado próximo ao ponto
    forall(k in Circulos, p in Pontos) {
        circuloFixadoEmPonto[k][p] => useCirculo[k];
        circuloFixadoEmPonto[k][p] => (x[p] - centroX[k])^2 + (y[p] - centroY[k])^2 <= r^2;
    }
    
    // Lógica de remoção: pontos próximos de âncoras não podem ser âncoras
    forall(p1 in Pontos, p2 in Pontos : p1 != p2) {
        ((x[p1] - x[p2])^2 + (y[p1] - y[p2])^2 <= (2*r)^2) && pontoEhAncora[p2] => pontoRemovido[p1];
    }
    
    // Pontos removidos não podem ser âncoras
    forall(p in Pontos) {
        pontoRemovido[p] => !pontoEhAncora[p];
    }
    
    // Priorização de pontos âncora baseada na ordem (mais abaixo/esquerda tem prioridade)
    // Se um ponto anterior na ordem pode ser âncora, os posteriores em sua vizinhança não devem ser
    forall(i in 1..(n-1), j in (i+1)..n) {
        // Se pontosOrdenados[i] está próximo de pontosOrdenados[j] e pontosOrdenados[i] é âncora, 
        // então pontosOrdenados[j] não deve ser âncora
        ((x[pontosOrdenados[i]] - x[pontosOrdenados[j]])^2 + 
         (y[pontosOrdenados[i]] - y[pontosOrdenados[j]])^2 <= (2*r)^2) && 
        pontoEhAncora[pontosOrdenados[i]] => !pontoEhAncora[pontosOrdenados[j]];
    }
    
    // Quebra de simetria: usar círculos em ordem
    forall(k in 1..(maxCirculos-1)) {
        useCirculo[k] >= useCirculo[k+1];
    }
    
    // Círculos fixados devem ser usados primeiro na ordem
    forall(k in Circulos) {
        sum(p in Pontos) circuloFixadoEmPonto[k][p] => useCirculo[k];
    }
}

// Configuração do CP
execute CP_CONFIG {
    cp.param.timeLimit = 1800; // 30 minutos
    cp.param.logVerbosity = "Quiet";
}

// Include display
include "modular_display.mod";

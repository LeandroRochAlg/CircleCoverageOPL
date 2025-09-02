/*********************************************
 * Módulo: Restrições CP Modulares
 * Author: rocha
 * Creation Date: 12 de ago de 2025
 * Descrição: Restrições organizadas para Circle Coverage
 *********************************************/

// === VARIÁVEIS DE DECISÃO CP ===
dvar boolean useCirculo[Circulos];
dvar int centroX[Circulos] in minX..maxX;
dvar int centroY[Circulos] in minY..maxY;
dvar boolean pontoCoberto[1..n][Circulos];

// === FUNÇÃO OBJETIVO ===
minimize sum(k in Circulos) useCirculo[k];

// === RESTRIÇÕES MODULARES ===
subject to {
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
        (centroX[i] - centroX[j])^2 + (centroY[i] - centroY[j])^2 >= minDistCirculos^2 - minDistCirculos^2 * (2 - useCirculo[i] - useCirculo[j]);
    }
    
    // Quebra de simetria: usar círculos em ordem
    forall(k in 1..maxCirculos-1) {
        useCirculo[k] >= useCirculo[k+1];
    }
    
    // RESTRIÇÕES DE FIXAÇÃO (FIX_CIRC_CLI)
    // Força círculos fixados a serem usados e próximos ao cliente correspondente
    forall(k in 1..numCirculosFixados) {
        if(clienteFixado[k] > 0) {
            useCirculo[k] == 1;
            // Permite flexibilidade ao redor do cliente (dentro do raio)
            (centroX[k] - x[clienteFixado[k]])^2 + (centroY[k] - y[clienteFixado[k]])^2 <= r^2;
        }
    }
}

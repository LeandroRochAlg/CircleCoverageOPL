/*********************************************
 * Modelo Combinado: Âncoras + Heurística4
 * Author: rocha
 * Creation Date: 02 de set de 2025
 * Descrição: Combina quebra de simetria com inicialização inteligente
 *********************************************/

using CP;

// Include da base comum
include "common_base.mod";

// Configuração CP
execute CP_CONFIG {
    cp.param.timeLimit = 3600;
    cp.param.logVerbosity = "Quiet";
    writeln("=== MODELO COMBINADO: ÂNCORAS + HEURÍSTICA4 ===");
}

// Include heuristic para obter solução inicial
include "modular_heuristic4.mod";

// Pré-computação: selecionar pontos âncora usando critério "mais abaixo e à esquerda"
int numPontosAncora = 0;
int pontosAncora[1..n];

execute SELECIONAR_ANCORAS {
    writeln("=== SELECIONANDO PONTOS ÂNCORA ===");
    
    // Array para rastrear pontos disponíveis
    var disponivel = new Array(n+1);
    for (var p = 1; p <= n; p++) {
        disponivel[p] = true;
    }
    
    var numAncorasLocal = 0;
    var distancia2r = (2 * r) * (2 * r);
    
    while (1) {
        var melhorPonto = -1;
        // Encontrar ponto disponível mais abaixo e à esquerda
        var menorY = Infinity;
        var menorX = Infinity;
        
        // tentar fazer para cada cliente quantos clientes estão a até 2r dele para usar um critério guloso ADAPTIVO para fixação de circulos
        for (var p = 1; p <= n; p++) {
            if (disponivel[p]) {
                if (y[p] < menorY || (y[p] == menorY && x[p] < menorX)) {
                    menorY = y[p];
                    menorX = x[p];
                    melhorPonto = p;
                }
            }
        }
        
        if (melhorPonto == -1) break; // Não há mais pontos disponíveis
        
        // Adicionar como âncora
        numAncorasLocal++;
        pontosAncora[numAncorasLocal] = melhorPonto;
        numPontosAncora = numAncorasLocal;
        
        writeln("Âncora " + numAncorasLocal + ": Ponto " + melhorPonto + 
                " em (" + x[melhorPonto] + ", " + y[melhorPonto] + ")");
        
        // Remover pontos próximos (dentro de 2r)
        var removidos = 0;
        for (var p = 1; p <= n; p++) {
            if (disponivel[p]) {
                var dx = x[p] - x[melhorPonto];
                var dy = y[p] - y[melhorPonto];
                if (dx*dx + dy*dy <= distancia2r) {
                    disponivel[p] = false;
                    removidos++;
                }
            }
        }
        
        writeln("  -> Removidos " + removidos + " pontos da vizinhança");
    }
    
    writeln("Total de pontos âncora selecionados: " + numPontosAncora);
    writeln();
}

// Usa o resultado da heurística para definir o range
int maxCirculos = circulosUsados;
range Circulos = 1..maxCirculos;

// Variáveis de decisão
dvar boolean useCirculo[Circulos];
dvar int centroX[Circulos] in minX..maxX;
dvar int centroY[Circulos] in minY..maxY;
dvar boolean pontoCoberto[Pontos][Circulos];

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
    
    // ===== RESTRIÇÕES DE QUEBRA DE SIMETRIA =====
    
    // Quebra de simetria: usar círculos em ordem
    forall(k in 1..(maxCirculos-1)) {
        useCirculo[k] >= useCirculo[k+1];
    }
    
    // Essa restrição só pode atingir círculos não fixados
    forall(k in 1..(maxCirculos-1)) {
      	useCirculo[k + 1] == 0 || centroX[k] < centroX[k+1] || (centroX[k] == centroX[k+1] && centroY[k] < centroY[k+1]);
    }
    
    // Incentiva cobertura prioritária dos pontos âncora
    forall(i in 1..numPontosAncora) {
        // Garante que cada ponto âncora tenha sua cobertura mínima
        sum(k in Circulos) pontoCoberto[pontosAncora[i]][k] >= minCoverage;
    }
    
    // ===== INICIALIZAÇÃO INTELIGENTE =====
    
    // Restringe domínio dos círculos próximo à solução heurística
//    forall(k in Circulos) {
        // Permite movimento em uma janela ao redor da solução heurística
//        centroX[k] >= centrosHeuristicoX[k] - r * 2;  // Aproximadamente r
//        centroX[k] <= centrosHeuristicoX[k] + r * 2;
//        centroY[k] >= centrosHeuristicoY[k] - r * 2;
//        centroY[k] <= centrosHeuristicoY[k] + r * 2;
//    }
}

// Include display
include "modular_display.mod";

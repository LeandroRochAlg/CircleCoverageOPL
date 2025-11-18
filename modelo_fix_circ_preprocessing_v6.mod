/*********************************************
 * Modelo: Alocação de Círculos com Restrições de Âncora V4
 * Author: rocha
 * Creation Date: 22 de out de 2025
 * Descrição: Círculos dedicados a âncoras DEVEM cobri-las, mas posição é LIVRE
 * 
 * DIFERENÇA DA V3:
 * - V3: Fixa posição dos círculos nos pontos âncora (centroX/Y == coordenadas)
 * - V4: Usa pontoCoberto para OBRIGAR círculos a cobrir âncoras (posição livre)
 * 
 * ALGORITMO:
 * 1. Seleciona clientes âncora (mais abaixo e à esquerda)
 * 2. Aloca minCoverage círculos para cada âncora
 * 3. RESTRIÇÃO: Cada círculo alocado DEVE cobrir sua âncora (pontoCoberto[ancora][k] == 1)
 * 4. Posição dos círculos é otimizada livremente pelo solver
 * 5. Círculos adicionais cobrem clientes restantes
 *********************************************/

using CP;

// Include da base comum
include "common_base.mod";

// Configuração CP
execute CP_CONFIG {
    cp.param.timeLimit = 900;
    cp.param.logVerbosity = "Quiet";
    cp.param.workers = 1;
    writeln("=== MODELO: ALOCAÇÃO DE CÍRCULOS COM RESTRIÇÕES DE ÂNCORA V4 ===");
    writeln("=== (Círculos DEVEM cobrir âncoras, mas posição é LIVRE) ===");
    writeln();
}

// ===== ESTRUTURAS DE DADOS PARA ALOCAÇÃO DE CÍRCULOS =====

// Arrays para armazenar informação sobre clientes âncora
int numClientesAncora = 0;
int clientesAncora[1..n];              // IDs dos clientes âncora
int numCirculosAncora = 0;             // Total de círculos alocados para âncoras
int circuloParaAncora[1..n*minCoverage]; // Qual cliente âncora cada círculo DEVE cobrir

// Arrays para controlar cobertura
int clienteEhAncora[Pontos];          // 1 se é âncora, 0 caso contrário
int clienteRemovidoPorAncora[Pontos]; // 1 se está a 2r de alguma âncora, 0 caso contrário

// ===== ETAPA 1: SELEÇÃO DE CLIENTES ÂNCORA =====
execute SELECIONAR_CLIENTES_ANCORAS {
    writeln("===== ETAPA 1: SELECIONANDO CLIENTES ÂNCORA =====");
    writeln();
    
    // Inicializa arrays
    for (var p = 1; p <= n; p++) {
        clienteEhAncora[p] = 0;
        clienteRemovidoPorAncora[p] = 0;
    }
    
    // Array para rastrear clientes disponíveis
    var disponivel = new Array(n+1);
    for (var p = 1; p <= n; p++) {
        disponivel[p] = true;
    }
    
    var numAncorasLocal = 0;
    var distancia2r = (2 * r) * (2 * r);
    
    var iteracao = 0;
    while (true) {
        iteracao++;
        
        // Encontrar cliente disponível mais abaixo e à esquerda
        var melhorCliente = -1;
        var menorY = Infinity;
        var menorX = Infinity;
        
        for (var p = 1; p <= n; p++) {
            if (disponivel[p]) {
                // Critério: menor Y (mais abaixo), desempate: menor X (mais à esquerda)
                if (y[p] < menorY || (y[p] == menorY && x[p] < menorX)) {
                    menorY = y[p];
                    menorX = x[p];
                    melhorCliente = p;
                }
            }
        }
        
        if (melhorCliente == -1) {
            writeln("  Todos os clientes foram processados");
            break; // Não há mais clientes disponíveis
        }
        
        // Adicionar como âncora
        numAncorasLocal++;
        clientesAncora[numAncorasLocal] = melhorCliente;
        numClientesAncora = numAncorasLocal;
        clienteEhAncora[melhorCliente] = 1;
        disponivel[melhorCliente] = false;
        
        writeln("Iteração " + iteracao + ":");
        writeln("  Cliente Âncora #" + numAncorasLocal + ": Cliente " + melhorCliente + 
                " em (" + x[melhorCliente] + ", " + y[melhorCliente] + ")");
        
        // Remover clientes próximos (dentro de 2r)
        var removidos = 0;
        for (var p = 1; p <= n; p++) {
            if (disponivel[p]) {
                var dx = x[p] - x[melhorCliente];
                var dy = y[p] - y[melhorCliente];
                var distSq = dx*dx + dy*dy;
                
                if (distSq <= distancia2r) {
                    disponivel[p] = false;
                    clienteRemovidoPorAncora[p] = 1;
                    removidos++;
                }
            }
        }
        
        writeln("  -> Removidos " + removidos + " clientes da vizinhança (distância <= 2r)");
        writeln();
    }
    
    writeln("Total de clientes âncora selecionados: " + numClientesAncora);
    writeln();
}

// ===== ETAPA 2: ALOCAÇÃO DE CÍRCULOS PARA CLIENTES ÂNCORA =====
execute ALOCAR_CIRCULOS_ANCORAS {
    writeln("===== ETAPA 2: ALOCANDO CÍRCULOS PARA CLIENTES ÂNCORA =====");
    writeln();
    
    numCirculosAncora = 0;
    
    for (var a = 1; a <= numClientesAncora; a++) {
        var clienteId = clientesAncora[a];
        
        writeln("Cliente Âncora #" + a + " (Cliente " + clienteId + "):");
        writeln("  Posição: (" + x[clienteId] + ", " + y[clienteId] + ")");
        writeln("  Alocando " + minCoverage + " círculos que DEVEM cobrir esta âncora:");
        
        // Alocar minCoverage círculos para este cliente
        // IMPORTANTE: Não fixamos a posição, apenas registramos que devem cobrir
        for (var i = 0; i < minCoverage; i++) {
            numCirculosAncora++;
            circuloParaAncora[numCirculosAncora] = clienteId;
            
            writeln("    Círculo #" + numCirculosAncora + " -> DEVE cobrir Cliente " + clienteId);
        }
        writeln();
    }
    
    writeln("Total de círculos alocados para âncoras: " + numCirculosAncora);
    writeln("NOTA: Posição destes círculos será otimizada livremente pelo solver");
    writeln("      com a RESTRIÇÃO de que DEVEM cobrir seus respectivos clientes âncora");
    writeln();
}

// ===== ETAPA 3: ANÁLISE DE COBERTURA POTENCIAL =====
execute ANALISAR_COBERTURA_POTENCIAL {
    writeln("===== ETAPA 3: ANÁLISE DE COBERTURA POTENCIAL =====");
    writeln();
    
    // Análise: cada âncora terá minCoverage círculos que DEVEM cobri-la
    writeln("Garantias de cobertura:");
    for (var a = 1; a <= numClientesAncora; a++) {
        var clienteId = clientesAncora[a];
        writeln("  Cliente Âncora " + clienteId + ": " + minCoverage + " círculos GARANTIDOS");
    }
    writeln();
    
    // Clientes NÃO-âncora precisam ser cobertos por círculos adicionais OU
    // por círculos de âncoras próximas (se estiverem dentro do raio)
    var clientesNaoAncora = 0;
    writeln("Clientes não-âncora que precisam de cobertura:");
    for (var p = 1; p <= n; p++) {
        if (clienteEhAncora[p] == 0) {
            clientesNaoAncora++;
            writeln("  Cliente " + p + " em (" + x[p] + ", " + y[p] + "): precisa de " + minCoverage + " círculos");
        }
    }
    writeln();
    writeln("Total de clientes não-âncora: " + clientesNaoAncora);
    writeln();
}

// ===== ETAPA 4: ESTIMAR CÍRCULOS VARIÁVEIS NECESSÁRIOS =====
// Usa heurística simples para estimar quantos círculos adicionais são necessários
int numCirculosVariaveis = 0;

execute ESTIMAR_CIRCULOS_VARIAVEIS {
    writeln("===== ETAPA 4: ESTIMANDO CÍRCULOS ADICIONAIS NECESSÁRIOS =====");
    writeln();
    
    // Algoritmo guloso simples: para cada cliente não-âncora,
    // estima quantos círculos adicionais são necessários
    var coberturaTentativa = new Array(n+1);
    for (var p = 1; p <= n; p++) {
        // Âncoras já têm minCoverage círculos garantidos
        if (clienteEhAncora[p] == 1) {
            coberturaTentativa[p] = minCoverage;
        } else {
            coberturaTentativa[p] = 0;
        }
    }
    
    var circulosAdicionais = 0;
    var maxIteracoes = n * minCoverage; // limite de segurança
    
    for (var iter = 0; iter < maxIteracoes; iter++) {
        // Encontra cliente com maior déficit de cobertura
        var piorCliente = -1;
        var maiorDeficit = 0;
        
        for (var p = 1; p <= n; p++) {
            var deficit = minCoverage - coberturaTentativa[p];
            if (deficit > maiorDeficit) {
                maiorDeficit = deficit;
                piorCliente = p;
            }
        }
        
        if (piorCliente == -1) {
            // Todos os clientes têm cobertura suficiente
            break;
        }
        
        // Adiciona um círculo no pior cliente
        circulosAdicionais++;
        var cx = Math.round(x[piorCliente]);
        var cy = Math.round(y[piorCliente]);
        
        // Atualiza cobertura de todos os clientes dentro do raio
        var r2 = r * r;
        for (var p = 1; p <= n; p++) {
            var dx = x[p] - cx;
            var dy = y[p] - cy;
            if (dx*dx + dy*dy <= r2) {
                coberturaTentativa[p]++;
            }
        }
    }
    
    numCirculosVariaveis = circulosAdicionais;
    writeln("Estimativa de círculos adicionais necessários: " + numCirculosVariaveis);
    writeln("  (além dos " + numCirculosAncora + " círculos para âncoras)");
    writeln();
}

// ===== DEFINIÇÃO DO MODELO CP =====

int totalCirculos = numCirculosAncora + numCirculosVariaveis;
int maxCirculos = totalCirculos;
range TodosCirculos = 1..totalCirculos;
range CirculosAncora = 1..numCirculosAncora;
range CirculosAdicionais = (numCirculosAncora + 1)..totalCirculos;

execute MODELO_INFO {
    writeln("===== CONFIGURAÇÃO DO MODELO CP =====");
    writeln("  Círculos para âncoras: " + numCirculosAncora);
    writeln("  Círculos adicionais: " + numCirculosVariaveis);
    writeln("  Total de círculos: " + totalCirculos);
    writeln("  Domínio X: [" + minX + ", " + maxX + "]");
    writeln("  Domínio Y: [" + minY + ", " + maxY + "]");
    writeln();
    writeln("ESTRATÉGIA:");
    writeln("  - Círculos 1-" + numCirculosAncora + 
            ": DEVEM cobrir suas âncoras (posição livre)");
    if (numCirculosVariaveis > 0) {
        writeln("  - Círculos " + (numCirculosAncora+1) + "-" + totalCirculos + 
                ": Cobertura livre (podem ou não ser usados)");
    }
    writeln();
}

// Variáveis de decisão
dvar boolean useCirculo[TodosCirculos];
dvar int centroX[TodosCirculos] in minX..maxX;
dvar int centroY[TodosCirculos] in minY..maxY;
dvar boolean pontoCoberto[Pontos][TodosCirculos];

// Função objetivo: minimizar número total de círculos usados
minimize sum(k in TodosCirculos) useCirculo[k];

subject to {
    // ===== RESTRIÇÕES DE ÂNCORA =====
    
    // Círculos alocados para âncoras SEMPRE estão ativos
    forall(k in CirculosAncora) {
        useCirculo[k] == 1;
    }
    
    // RESTRIÇÃO PRINCIPAL: Cada círculo de âncora DEVE cobrir sua âncora designada
    forall(k in CirculosAncora) {
        pontoCoberto[circuloParaAncora[k]][k] == 1;
        
        if(minCoverage > 1 && k < numCirculosAncora && circuloParaAncora[k] == circuloParaAncora[k+1])
       	    (centroX[k] < centroX[k+1] || (centroX[k] == centroX[k+1] && centroY[k] <= centroY[k+1]));
    }
    
    // QUEBRA DE SIMETRIA INTRA-ÂNCORA: 
    // Círculos dedicados à mesma âncora são ordenados lexicograficamente
    forall(k in CirculosAncora : k < numCirculosAncora) {
        (circuloParaAncora[k] != circuloParaAncora[k+1]) || 
        (centroX[k] < centroX[k+1] || 
         (centroX[k] == centroX[k+1] && centroY[k] <= centroY[k+1]));
    }
    
    // ===== RESTRIÇÕES DE COBERTURA =====
    
    // Cada cliente deve ser coberto por pelo menos minCoverage círculos
    forall(p in Pontos) {
        sum(k in TodosCirculos) pontoCoberto[p][k] >= minCoverage;
    }
    
    // Um cliente só pode ser coberto por um círculo se esse círculo for usado
    forall(p in Pontos, k in TodosCirculos) {
        pontoCoberto[p][k] <= useCirculo[k];
    }
    
    // Se um cliente é coberto por um círculo, a distância deve ser <= r
    forall(p in Pontos, k in TodosCirculos) {
        pontoCoberto[p][k] == 0 || 
        (x[p] - centroX[k])^2 + (y[p] - centroY[k])^2 <= r^2;
    }
    
    // ===== RESTRIÇÕES DE SEPARAÇÃO =====
    
    // Separação mínima entre círculos usados
    forall(i in TodosCirculos, j in TodosCirculos : i < j) {
        (centroX[i] - centroX[j])^2 + (centroY[i] - centroY[j])^2 >= 
        minDistCirculos^2 - minDistCirculos^2 * (2 - useCirculo[i] - useCirculo[j]);
    }
    
    // ===== QUEBRA DE SIMETRIA =====
    
    // Círculos adicionais são usados em ordem
    forall(k in CirculosAdicionais : k < totalCirculos) {
        useCirculo[k] >= useCirculo[k+1];
    }
    
    // Ordenação lexicográfica dos centros dos círculos adicionais
    forall(k in CirculosAdicionais : k < totalCirculos) {
        (useCirculo[k] == 0 || useCirculo[k+1] == 0) || 
        (centroX[k] < centroX[k+1] || 
            (centroX[k] == centroX[k+1] && centroY[k] <= centroY[k+1]));
    }
    
    // Ordenação lexicográfica dos centros dos círculos adicionais
    forall(k in CirculosAdicionais : k < totalCirculos) {
        (useCirculo[k] == 0 || useCirculo[k+1] == 0) || 
        (centroX[k] < centroX[k+1] || 
            (centroX[k] == centroX[k+1] && centroY[k] <= centroY[k+1]));
    }
}

// Include display
include "modular_display.mod";

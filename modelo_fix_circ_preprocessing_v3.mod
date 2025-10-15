/*********************************************
 * Modelo: Fixação de Círculos com Pré-processamento V3
 * Author: rocha
 * Creation Date: 15 de out de 2025
 * Descrição: Implementa corretamente a fixação de círculos para clientes âncora
 * 
 * ALGORITMO:
 * 1. Seleciona clientes âncora (mais abaixo e à esquerda)
 * 2. Para cada âncora, FIXA min_cover círculos no centro do cliente
 * 3. Remove clientes a até 2r de distância de cada âncora
 * 4. Círculos restantes cobrem os demais clientes (variáveis livres)
 *********************************************/

using CP;

// Include da base comum
include "common_base.mod";

// Configuração CP
execute CP_CONFIG {
    cp.param.timeLimit = 3600;
    cp.param.logVerbosity = "Quiet";
    cp.param.workers = 1;
    writeln("=== MODELO: FIXAÇÃO DE CÍRCULOS COM PRÉ-PROCESSAMENTO V3 ===");
    writeln();
}

// ===== ESTRUTURAS DE DADOS PARA FIXAÇÃO =====

// Arrays para armazenar informação sobre clientes âncora e círculos fixados
int numClientesAncora = 0;
int clientesAncora[1..n];              // IDs dos clientes âncora
int numCirculosFixados = 0;            // Total de círculos fixados
int circuloFixadoX[1..n*minCoverage]; // Coordenada X de cada círculo fixado
int circuloFixadoY[1..n*minCoverage]; // Coordenada Y de cada círculo fixado
int circuloFixadoCliente[1..n*minCoverage]; // Para qual cliente âncora este círculo foi fixado

// Arrays para controlar quais clientes são cobertos por círculos fixados
int clienteEhAncora[Pontos];          // 1 se é âncora, 0 caso contrário
int clienteRemovidoPorAncora[Pontos]; // 1 se está a 2r de alguma âncora, 0 caso contrário
int coberturaFixadaCliente[Pontos];   // Quantos círculos fixados cobrem cada cliente

// ===== ETAPA 1: SELEÇÃO DE CLIENTES ÂNCORA =====
execute SELECIONAR_CLIENTES_ANCORAS {
    writeln("===== ETAPA 1: SELECIONANDO CLIENTES ÂNCORA =====");
    writeln();
    
    // Inicializa arrays
    for (var p = 1; p <= n; p++) {
        clienteEhAncora[p] = 0;
        clienteRemovidoPorAncora[p] = 0;
        coberturaFixadaCliente[p] = 0;
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

// ===== ETAPA 2: FIXAÇÃO DE CÍRCULOS NOS CLIENTES ÂNCORA =====
execute FIXAR_CIRCULOS_ANCORAS {
    writeln("===== ETAPA 2: FIXANDO CÍRCULOS NOS CLIENTES ÂNCORA =====");
    writeln();
    
    numCirculosFixados = 0;
    
    for (var a = 1; a <= numClientesAncora; a++) {
        var clienteId = clientesAncora[a];
        
        // Arredonda e garante que está dentro do domínio
        var cx = Math.round(x[clienteId]);
        var cy = Math.round(y[clienteId]);
        
        // Clamp dentro dos limites
        if (cx < minX) cx = minX;
        if (cx > maxX) cx = maxX;
        if (cy < minY) cy = minY;
        if (cy > maxY) cy = maxY;
        
        writeln("Cliente Âncora #" + a + " (Cliente " + clienteId + "):");
        writeln("  Posição original: (" + x[clienteId] + ", " + y[clienteId] + ")");
        writeln("  Posição fixada: (" + cx + ", " + cy + ")");
        writeln("  Fixando " + minCoverage + " círculos nesta posição:");
        
        // Fixar minCoverage círculos neste cliente
        for (var i = 0; i < minCoverage; i++) {
            numCirculosFixados++;
            circuloFixadoX[numCirculosFixados] = cx;
            circuloFixadoY[numCirculosFixados] = cy;
            circuloFixadoCliente[numCirculosFixados] = clienteId;
            
            writeln("    Círculo Fixado #" + numCirculosFixados + ": centro em (" + cx + ", " + cy + ")");
        }
        writeln();
    }
    
    writeln("Total de círculos fixados: " + numCirculosFixados);
    writeln();
    
    // Verificar distância mínima entre círculos fixados
    writeln("Verificando distância entre círculos fixados:");
    var violacoes = 0;
    for (var i = 1; i <= numCirculosFixados; i++) {
        for (var j = i+1; j <= numCirculosFixados; j++) {
            var dx = circuloFixadoX[i] - circuloFixadoX[j];
            var dy = circuloFixadoY[i] - circuloFixadoY[j];
            var dist = Math.sqrt(dx*dx + dy*dy);
            if (dist < minDistCirculos) {
                writeln("  AVISO: Círculos " + i + " e " + j + " estão muito próximos (dist=" + dist + " < " + minDistCirculos + ")");
                violacoes++;
            }
        }
    }
    if (violacoes == 0) {
        writeln("  ✓ Todos os círculos fixados respeitam distância mínima");
    } else {
        writeln("  ⚠ " + violacoes + " violações de distância mínima!");
    }
    writeln();
}

// ===== ETAPA 3: CALCULAR COBERTURA DOS CÍRCULOS FIXADOS =====
execute CALCULAR_COBERTURA_FIXADA {
    writeln("===== ETAPA 3: CALCULANDO COBERTURA DOS CÍRCULOS FIXADOS =====");
    writeln();
    
    var r2 = r * r;
    
    // Para cada círculo fixado, calcular quais clientes ele cobre
    for (var k = 1; k <= numCirculosFixados; k++) {
        var cx = circuloFixadoX[k];
        var cy = circuloFixadoY[k];
        var numClientesCobertos = 0;
        
        for (var p = 1; p <= n; p++) {
            var dx = x[p] - cx;
            var dy = y[p] - cy;
            var distSq = dx*dx + dy*dy;
            
            if (distSq <= r2) {
                coberturaFixadaCliente[p]++;
                numClientesCobertos++;
            }
        }
        
        writeln("Círculo Fixado #" + k + " (centro em " + cx + ", " + cy + "): Cobre " + numClientesCobertos + " clientes");
    }
    writeln();
    
    // Resumo de cobertura
    writeln("RESUMO DE COBERTURA FIXADA:");
    var clientesComCoberturaCompleta = 0;
    var clientesComCoberturaParcial = 0;
    var clientesSemCobertura = 0;
    
    for (var p = 1; p <= n; p++) {
        var cobertura = coberturaFixadaCliente[p];
        if (cobertura >= minCoverage) {
            clientesComCoberturaCompleta++;
        } else if (cobertura > 0) {
            clientesComCoberturaParcial++;
        } else {
            clientesSemCobertura++;
        }
    }
    
    writeln("  Clientes com cobertura completa (>= " + minCoverage + "): " + clientesComCoberturaCompleta);
    writeln("  Clientes com cobertura parcial (1 a " + (minCoverage-1) + "): " + clientesComCoberturaParcial);
    writeln("  Clientes sem cobertura: " + clientesSemCobertura);
    writeln();
    
    // Lista clientes que ainda precisam de cobertura adicional
    writeln("CLIENTES QUE PRECISAM DE COBERTURA ADICIONAL:");
    for (var p = 1; p <= n; p++) {
        var falta = minCoverage - coberturaFixadaCliente[p];
        if (falta > 0) {
            writeln("  Cliente " + p + " em (" + x[p] + ", " + y[p] + "): " +
                    "tem " + coberturaFixadaCliente[p] + ", faltam " + falta);
        }
    }
    writeln();
}

// ===== ETAPA 4: ESTIMAR CÍRCULOS VARIÁVEIS NECESSÁRIOS =====
// Usa heurística simples para estimar quantos círculos adicionais são necessários
int numCirculosVariaveis = 0;

execute ESTIMAR_CIRCULOS_VARIAVEIS {
    writeln("===== ETAPA 4: ESTIMANDO CÍRCULOS VARIÁVEIS NECESSÁRIOS =====");
    writeln();
    
    // Algoritmo guloso simples: para cada cliente sem cobertura completa,
    // tenta adicionar círculos
    var coberturaTentativa = new Array(n+1);
    for (var p = 1; p <= n; p++) {
        coberturaTentativa[p] = coberturaFixadaCliente[p];
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
    writeln("Estimativa de círculos variáveis necessários: " + numCirculosVariaveis);
    writeln();
}

// ===== DEFINIÇÃO DO MODELO CP =====

int totalCirculos = numCirculosFixados + numCirculosVariaveis;
int maxCirculos = totalCirculos;
range TodosCirculos = 1..totalCirculos;
range CirculosFixados = 1..numCirculosFixados;
range CirculosVariaveis = (numCirculosFixados + 1)..totalCirculos;

execute MODELO_INFO {
    writeln("===== CONFIGURAÇÃO DO MODELO CP =====");
    writeln("  Círculos fixados: " + numCirculosFixados);
    writeln("  Círculos variáveis: " + numCirculosVariaveis);
    writeln("  Total de círculos: " + totalCirculos);
    writeln("  Domínio X: [" + minX + ", " + maxX + "]");
    writeln("  Domínio Y: [" + minY + ", " + maxY + "]");
    writeln();
}

// Variáveis de decisão
dvar boolean useCirculo[TodosCirculos];
dvar int centroX[TodosCirculos] in minX..maxX;
dvar int centroY[TodosCirculos] in minY..maxY;
dvar boolean pontoCoberto[Pontos][TodosCirculos];

// Função objetivo: minimizar número de círculos VARIÁVEIS usados
// (círculos fixados sempre são usados)
minimize sum(k in CirculosVariaveis) useCirculo[k];

subject to {
    // ===== FIXAÇÃO DOS CÍRCULOS ÂNCORA =====
    
    // Círculos fixados sempre estão ativos e têm posição fixa
    forall(k in CirculosFixados) {
        useCirculo[k] == 1;
        centroX[k] == circuloFixadoX[k];
        centroY[k] == circuloFixadoY[k];
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
    // EXCETO quando estão no mesmo ponto (círculos sobrepostos permitidos)
    forall(i in TodosCirculos, j in TodosCirculos : i < j) {
        (centroX[i] - centroX[j])^2 + (centroY[i] - centroY[j])^2 == 0 ||
        (centroX[i] - centroX[j])^2 + (centroY[i] - centroY[j])^2 >= 
        minDistCirculos^2 - minDistCirculos^2 * (2 - useCirculo[i] - useCirculo[j]);
    }
    
    // ===== QUEBRA DE SIMETRIA PARA CÍRCULOS VARIÁVEIS =====
    
    // Círculos variáveis são usados em ordem
    forall(k in CirculosVariaveis : k < totalCirculos) {
        useCirculo[k] >= useCirculo[k+1];
    }
    
    // Ordenação lexicográfica dos centros dos círculos variáveis
    forall(k in CirculosVariaveis : k < totalCirculos) {
        (useCirculo[k] == 0 || useCirculo[k+1] == 0) || 
        (centroX[k] < centroX[k+1] || 
         (centroX[k] == centroX[k+1] && centroY[k] <= centroY[k+1]));
    }
}

// Include display
include "modular_display.mod";

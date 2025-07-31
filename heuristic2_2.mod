/*********************************************
 * OPL 22.1.1.0 Model
 * Author: rocha
 * Creation Date: 24 de jun de 2025 at 17:56:38
 *********************************************/

using CP;

// Parâmetros de entrada
float r = ...;                    // Raio fixo dos círculos
int n = ...;                      // Número de pontos a serem cobertos
int minCoverage = ...;            // Cobertura mínima (quantos círculos devem cobrir cada ponto)
float minDistCirculos = ...;      // Distância mínima entre centros dos círculos
range Pontos = 1..n;
float x[Pontos] = ...;            // Coordenadas x dos pontos
float y[Pontos] = ...;            // Coordenadas y dos pontos
int minX = ...;
int minY = ...;
int maxX = ...;
int maxY = ...;

// Variáveis globais para armazenar resultado da heurística
int circulosUsados = 0;
int centrosHeuristicoX[1..n*minCoverage];  // Array para posições X encontradas pela heurística
int centrosHeuristicoY[1..n*minCoverage];  // Array para posições Y encontradas pela heurística

// Heurística gulosa inspirada no código Python - foca em pontos que precisam de cobertura
execute {
    // Estrutura para rastrear cobertura dos pontos
    var coberturaPontos = new Array(n+1);
    for(var i = 1; i <= n; i++) {
        coberturaPontos[i] = 0;
    }
    
    // Arrays para armazenar círculos já colocados
    var maxPossibleCircles = n * minCoverage;
    var centrosUsadosX = new Array(maxPossibleCircles);
    var centrosUsadosY = new Array(maxPossibleCircles);
    var numCentrosUsados = 0;
    
    // Itera por todos os pontos até que todos tenham cobertura mínima
    for(var p = 1; p <= n; p++) {
        writeln("Processando ponto " + p + " em (" + x[p] + ", " + y[p] + ")");
        
        // Adiciona círculos até que este ponto tenha cobertura mínima
        while(coberturaPontos[p] < minCoverage) {
            var melhorPosX = -1;
            var melhorPosY = -1;
            var melhorCobertura = -1;
            var melhorDesempate = -1;
            
            // Explora posições possíveis dentro do raio do ponto atual
            // Similar ao loop Python: for x in range(-alcance, alcance+1)
            for(var candidatoX = Math.floor(x[p] - r); candidatoX <= Math.floor(x[p] + r); candidatoX++) {
                for(var candidatoY = Math.floor(y[p] - r); candidatoY <= Math.floor(y[p] + r); candidatoY++) {
                    // Verifica se está dentro do alcance circular (como no Python)
                    if(Math.pow(candidatoX - x[p], 2) + Math.pow(candidatoY - y[p], 2) <= r*r) {                        
                        // Verifica se a posição está dentro dos limites
                        if(candidatoX < minX || candidatoX > maxX || 
                           candidatoY < minY || candidatoY > maxY) {
                            continue;
                        }
                        
                        // Verifica se não há círculo já muito próximo (restrição de distância mínima)
                        var muitoProximo = false;
                        for(var i = 0; i < numCentrosUsados; i++) {
                            var dx = candidatoX - centrosUsadosX[i];
                            var dy = candidatoY - centrosUsadosY[i];
                            if(dx*dx + dy*dy < minDistCirculos*minDistCirculos) {
                                muitoProximo = true;
                                break;
                            }
                        }
                        
                        if(muitoProximo) continue;
                        
                        // Calcula cobertura desta posição (similar ao calculaCobertura do Python)
                        var coberturaCalculada = 0;
                        var desempate = 0;
                        for(var ponto = 1; ponto <= n; ponto++) {
                            var distX = x[ponto] - candidatoX;
                            var distY = y[ponto] - candidatoY;
                            
                            // Se o ponto estaria dentro do alcance deste círculo
                            if(distX*distX + distY*distY <= r*r) {
                                // Prioriza pontos que precisam de mais cobertura
                                var faltaCobertura = Math.max(0, minCoverage - coberturaPontos[ponto]);
                                if(faltaCobertura > 0) {
                                    coberturaCalculada += faltaCobertura; // Peso alto para pontos sub-cobertos
                                }
                                desempate++; // Conta pontos cobertos para desempate
                            }
                        }
                        
                        // Escolhe a posição com melhor cobertura
                        if(coberturaCalculada > melhorCobertura) {
                            melhorCobertura = coberturaCalculada;
                            melhorPosX = candidatoX;
                            melhorPosY = candidatoY;
                            melhorDesempate = desempate;
                        } else if (coberturaCalculada == melhorCobertura) {
                            if (desempate > melhorDesempate) {
                                melhorDesempate = desempate;
                                melhorPosX = candidatoX;
                                melhorPosY = candidatoY;
                            }
                        }
                    }
                }
            }
            
            // Se ainda não encontrou posição, para para evitar loop infinito
            if(melhorCobertura == -1) {
                writeln("ERRO: Não foi possível encontrar posição válida para cobrir ponto " + p);
                writeln(x[p], y[p]);
                break;
            }
            
            // Adiciona o círculo encontrado
            centrosUsadosX[numCentrosUsados] = melhorPosX;
            centrosUsadosY[numCentrosUsados] = melhorPosY;
            numCentrosUsados++;
            circulosUsados++;
            
            // Armazena nas variáveis globais
            centrosHeuristicoX[circulosUsados] = melhorPosX;
            centrosHeuristicoY[circulosUsados] = melhorPosY;
            
            writeln("  Adicionado círculo " + circulosUsados + " em (" + melhorPosX + ", " + melhorPosY + ")");
            
            // Atualiza cobertura de todos os pontos afetados por este novo círculo
            for(var ponto = 1; ponto <= n; ponto++) {
                var dx = x[ponto] - melhorPosX;
                var dy = y[ponto] - melhorPosY;
                if(dx*dx + dy*dy <= r*r) {
                    coberturaPontos[ponto]++;
                }
            }
            
            writeln("    Ponto " + p + " agora tem cobertura: " + coberturaPontos[p]);
            
            // Limite de segurança
            if(circulosUsados > n * minCoverage) {
                writeln("AVISO: Atingido limite de segurança de círculos");
                break;
            }
        }
    }
    
    writeln("=== RESULTADO DA HEURÍSTICA ===");
    writeln("Total de círculos encontrados: " + circulosUsados);
    for(var i = 1; i <= circulosUsados; i++) {
        writeln("Círculo " + i + ": centro em (" + centrosHeuristicoX[i] + ", " + centrosHeuristicoY[i] + ")");
    }
    
    // Verifica cobertura final
    writeln("=== VERIFICAÇÃO DE COBERTURA ===");
    for(var p = 1; p <= n; p++) {
        writeln("Ponto " + p + " (" + x[p] + ", " + y[p] + "): cobertura = " + coberturaPontos[p] + 
                (coberturaPontos[p] >= minCoverage ? " ✓" : " ✗"));
    }
}

// Usa o resultado da heurística para definir o número máximo de círculos
int maxCirculos = circulosUsados;
range Circulos = 1..maxCirculos;

// Variáveis de decisão
dvar boolean useCirculo[Circulos];              // 1 se o círculo k é usado
dvar int centroX[Circulos] in minX..maxX;       // Coordenada x do centro do círculo k
dvar int centroY[Circulos] in minY..maxY;       // Coordenada y do centro do círculo k
dvar boolean pontoCoberto[Pontos][Circulos];    // 1 se o ponto p é coberto pelo círculo k

execute {
    cp.param.timeLimit=600;
    cp.param.logPeriod=100000;
}

// Função objetivo: minimizar número de círculos usados
minimize sum(k in Circulos) useCirculo[k];

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
    // Usando Big-M: se pontoCoberto[p][k] = 1, então distância <= r^2
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
    
    // Restrições de inicialização baseadas na heurística
    // Fixa as posições iniciais dos círculos com base na heurística
    forall(k in Circulos) {
        centroX[k] == centrosHeuristicoX[k];
        centroY[k] == centrosHeuristicoY[k];
    }
}

execute DISPLAY_RESULTS {
    var numCirculosUsados = 0;
    for (var k = 1; k <= maxCirculos; k++) {
        if (useCirculo[k] == 1) {
            numCirculosUsados++;
        }
    }
    
    writeln("=== SOLUÇÃO DE COBERTURA COM CÍRCULOS ===");
    writeln("Número mínimo de círculos necessários: ", numCirculosUsados);
    writeln("Raio dos círculos: ", r);
    writeln("Cobertura mínima por ponto: ", minCoverage);
    writeln("Distância mínima entre círculos: ", minDistCirculos);
    writeln();
    
    for (var k = 1; k <= maxCirculos; k++) {
        if (useCirculo[k] == 1) {
            writeln("Círculo ", k, ":");
            writeln("  Centro: (", centroX[k], ", ", centroY[k], ")");
            write("  Pontos cobertos: ");
            var pontosCobertos = 0;
            for (var p = 1; p <= n; p++) {
                if (pontoCoberto[p][k] == 1) {
                    write(p, " ");
                    pontosCobertos++;
                }
            }
            writeln("(total: ", pontosCobertos, ")");
            writeln();
        }
    }
    
    // ===== SEÇÃO PARA COPIAR E COLAR NO PYTHON =====
    writeln();
    writeln("======= DADOS PARA PYTHON - INÍCIO =======");
    writeln("SOLUTION_DATA = {");
    writeln("    'num_circles': ", numCirculosUsados, ",");
    writeln("    'radius': ", r, ",");
    writeln("    'min_coverage': ", minCoverage, ",");
    writeln("    'min_dist_circles': ", minDistCirculos, ",");
    writeln("    'num_points': ", n, ",");
    
    // Pontos
    write("    'points': [");
    for (var p = 1; p <= n; p++) {
        write("(", x[p], ", ", y[p], ")");
        if (p < n) write(", ");
    }
    writeln("],");
    
    // Círculos
    write("    'circles': [");
    var primeiro = true;
    for (var k = 1; k <= maxCirculos; k++) {
        if (useCirculo[k] == 1) {
            if (!primeiro) write(", ");
            write("(", centroX[k], ", ", centroY[k], ")");
            primeiro = false;
        }
    }
    writeln("],");
    
    // Cobertura por ponto
    writeln("    'coverage_per_point': [");
    for (var p = 1; p <= n; p++) {
        var coberturaReal = 0;
        for (var k = 1; k <= maxCirculos; k++) {
            if (useCirculo[k] == 1) {
                var dist = Math.sqrt((x[p] - centroX[k]) * (x[p] - centroX[k]) + 
                                   (y[p] - centroY[k]) * (y[p] - centroY[k]));
                if (dist <= r) {
                    coberturaReal++;
                }
            }
        }
        write("        ", coberturaReal);
        if (p < n) writeln(",");
        else writeln("");
    }
    writeln("    ]");
    writeln("}");
    writeln("======= DADOS PARA PYTHON - FIM =======");
    
    // Verificação de cobertura completa e mínima
    writeln("=== VERIFICAÇÃO DE COBERTURA ===");
    var todosCobertos = true;
    var coberturaInsuficiente = false;
    
    for (var p = 1; p <= n; p++) {
        var numCoberturas = 0;
        for (var k = 1; k <= maxCirculos; k++) {
            if (pontoCoberto[p][k] == 1) {
                numCoberturas++;
            }
        }
        
        if (numCoberturas == 0) {
            writeln("ERRO: Ponto ", p, " não foi coberto!");
            todosCobertos = false;
        } else if (numCoberturas < minCoverage) {
            writeln("ERRO: Ponto ", p, " tem apenas ", numCoberturas, " coberturas (mínimo: ", minCoverage, ")");
            coberturaInsuficiente = true;
        } else {
            writeln("✓ Ponto ", p, " coberto por ", numCoberturas, " círculos");
        }
    }
    
    if (todosCobertos && !coberturaInsuficiente) {
        writeln("✓ Todos os pontos foram cobertos com cobertura mínima adequada!");
    }
    
    // Verificação de separação entre círculos
    writeln();
    writeln("=== VERIFICAÇÃO DE SEPARAÇÃO ENTRE CÍRCULOS ===");
    var separacaoOk = true;
    for (var i = 1; i <= maxCirculos; i++) {
        if (useCirculo[i] == 1) {
            for (var j = i + 1; j <= maxCirculos; j++) {
                if (useCirculo[j] == 1) {
                    var distCentros = Math.sqrt((centroX[i] - centroX[j]) * (centroX[i] - centroX[j]) + 
                                              (centroY[i] - centroY[j]) * (centroY[i] - centroY[j]));
                    if (distCentros < minDistCirculos) {
                        writeln("AVISO: Círculos ", i, " e ", j, " estão muito próximos: distância = ", distCentros);
                        separacaoOk = false;
                    } else {
                        writeln("✓ Círculos ", i, " e ", j, " bem separados: distância = ", distCentros);
                    }
                }
            }
        }
    }
    
    if (separacaoOk) {
        writeln("✓ Todos os círculos respeitam a distância mínima!");
    }
    
    // Estatísticas detalhadas
    writeln();
    writeln("=== ESTATÍSTICAS ===");
    writeln("Total de pontos: ", n);
    writeln("Círculos utilizados: ", numCirculosUsados);
    writeln("Cobertura mínima requerida: ", minCoverage);
    writeln("Total de coberturas realizadas: ", n * minCoverage);
    if (numCirculosUsados > 0) {
        writeln("Eficiência: ", (n * 1.0 / numCirculosUsados), " pontos por círculo");
        writeln("Redundância média: ", (n * minCoverage * 1.0 / numCirculosUsados), " coberturas por círculo");
    }
    
    // Verificação manual das distâncias (debug)
    writeln();
    writeln("=== VERIFICAÇÃO DE DISTÂNCIAS PONTO-CÍRCULO ===");
    for (var k = 1; k <= maxCirculos; k++) {
        if (useCirculo[k] == 1) {
            writeln("Círculo ", k, " em (", centroX[k], ", ", centroY[k], "):");
            for (var p = 1; p <= n; p++) {
                var dist2 = (x[p] - centroX[k]) * (x[p] - centroX[k]) + 
                           (y[p] - centroY[k]) * (y[p] - centroY[k]);
                var dist = Math.sqrt(dist2);
                if (pontoCoberto[p][k] == 1) {
                    if (dist <= r) {
                        writeln("  ✓ Ponto ", p, ": distância = ", dist, " (dentro do raio)");
                    } else {
                        writeln("  ✗ Ponto ", p, ": distância = ", dist, " (FORA do raio!)");
                    }
                }
            }
        }
    }
}
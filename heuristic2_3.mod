/*********************************************
 * OPL 22.1.1.0 Model
 * Author: rocha
 * Creation Date: 19 de jul de 2025 at XX:XX:XX
 * Versão 2.3: Pré-calcula cobertura para todos os pontos da grade
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

// Estruturas para pré-computação
int totalPosicoes = (maxX - minX + 1) * (maxY - minY + 1);

// Heurística gulosa com pré-computação de cobertura
execute {
    writeln("=== INICIANDO HEURÍSTICA 2.3 COM PRÉ-COMPUTAÇÃO ===");
    writeln("Pré-calculando cobertura para todas as posições da grade...");
    writeln("Grade: (" + minX + "," + minY + ") até (" + maxX + "," + maxY + ")");
    writeln("Total de posições a analisar: " + totalPosicoes);
    
    // Estrutura para rastrear cobertura dos pontos
    var coberturaPontos = new Array(n+1);
    for(var i = 0; i <= n; i++) {
        coberturaPontos[i] = 0;
    }
    
    // Arrays para armazenar círculos já colocados
    var maxPossibleCircles = n * minCoverage;
    var centrosUsadosX = new Array(maxPossibleCircles);
    var centrosUsadosY = new Array(maxPossibleCircles);
    for(var i = 0; i < maxPossibleCircles; i++) {
        centrosUsadosX[i] = 0;
        centrosUsadosY[i] = 0;
    }
    var numCentrosUsados = 0;
    
    // PRÉ-COMPUTAÇÃO: Cria estrutura de cobertura para cada posição da grade
    writeln("Calculando matriz de cobertura...");
    
    // Arrays separados para armazenar informações de cada posição
    var posicaoX = new Array(totalPosicoes);
    var posicaoY = new Array(totalPosicoes);
    var posicaoNumPontos = new Array(totalPosicoes);
    var posicaoPontos = new Array(totalPosicoes); // Array de arrays com os pontos cobertos por cada posição
    var indicePosicao = 0;
    
    // Para cada posição possível na grade
    for(var gx = minX; gx <= maxX; gx++) {
        for(var gy = minY; gy <= maxY; gy++) {
            // Lista de pontos que seriam cobertos se um círculo fosse colocado em (gx, gy)
            var pontosCobertos = new Array(n);
            var numPontosCobertos = 0;
            
            // Verifica quais pontos estariam dentro do círculo
            for(var ponto = 1; ponto <= n; ponto++) {
                var distX = x[ponto] - gx;
                var distY = y[ponto] - gy;
                
                if(distX*distX + distY*distY <= r*r) {
                    pontosCobertos[numPontosCobertos] = ponto;
                    numPontosCobertos++;
                }
            }
            
            // Armazena a informação de cobertura para esta posição
            posicaoX[indicePosicao] = gx;
            posicaoY[indicePosicao] = gy;
            posicaoNumPontos[indicePosicao] = numPontosCobertos;
            posicaoPontos[indicePosicao] = pontosCobertos;
            indicePosicao++;
        }
        
        // Progresso a cada 50 colunas
        if((gx - minX) % 50 == 0) {
            writeln("  Processando coluna " + gx + " de " + maxX);
        }
    }
    
    writeln("Matriz de cobertura calculada! Total de posições: " + indicePosicao);
    writeln("Iniciando algoritmo heurístico...");
    
    // Itera por todos os pontos até que todos tenham cobertura mínima
    for(var p = 1; p <= n; p++) {
        writeln("Processando ponto " + p + " em (" + x[p] + ", " + y[p] + ")");
        
        // Adiciona círculos até que este ponto tenha cobertura mínima
        while(coberturaPontos[p] < minCoverage) {
            var melhorPosX = -1;
            var melhorPosY = -1;
            var melhorCobertura = -1;
            var melhorDesempate = -1;
            var melhorIndicePosicao = -1;
            
            // BUSCA LOCAL: Primeiro tenta posições próximas ao ponto atual
            var encontrouLocal = false;
            var raioLocal = Math.ceil(r);
            
            for(var candidatoX = Math.max(minX, Math.floor(x[p] - raioLocal)); 
                candidatoX <= Math.min(maxX, Math.floor(x[p] + raioLocal)); candidatoX++) {
                for(var candidatoY = Math.max(minY, Math.floor(y[p] - raioLocal)); 
                    candidatoY <= Math.min(maxY, Math.floor(y[p] + raioLocal)); candidatoY++) {
                    
                    // Verifica se está dentro do alcance circular do ponto atual
                    if(Math.pow(candidatoX - x[p], 2) + Math.pow(candidatoY - y[p], 2) > r*r) {
                        continue;
                    }
                    
                    // Verifica se não há círculo já muito próximo
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
                    
                    // Encontra a posição na matriz pré-computada
                    var indiceBusca = (candidatoX - minX) * (maxY - minY + 1) + (candidatoY - minY);
                    
                    // Calcula cobertura usando a informação pré-computada
                    var coberturaCalculada = 0;
                    var desempate = posicaoNumPontos[indiceBusca];
                    
                    for(var i = 0; i < posicaoNumPontos[indiceBusca]; i++) {
                        var pontoId = posicaoPontos[indiceBusca][i];
                        var faltaCobertura = Math.max(0, minCoverage - coberturaPontos[pontoId]);
                        if(faltaCobertura > 0) {
                            coberturaCalculada += faltaCobertura;
                        }
                    }
                    
                    // Escolhe a posição com melhor cobertura
                    if(coberturaCalculada > melhorCobertura) {
                        melhorCobertura = coberturaCalculada;
                        melhorPosX = candidatoX;
                        melhorPosY = candidatoY;
                        melhorDesempate = desempate;
                        melhorIndicePosicao = indiceBusca;
                        encontrouLocal = true;
                    } else if (coberturaCalculada == melhorCobertura) {
                        if (desempate > melhorDesempate) {
                            melhorDesempate = desempate;
                            melhorPosX = candidatoX;
                            melhorPosY = candidatoY;
                            melhorIndicePosicao = indiceBusca;
                            encontrouLocal = true;
                        }
                    }
                }
            }
            
            // BUSCA GLOBAL: Se não encontrou posição local, busca em toda a grade
            if(!encontrouLocal) {
                writeln("Busca local falhou para ponto " + p + ", executando busca global...");
                
                // Busca em todas as posições pré-computadas
                for(var idx = 0; idx < totalPosicoes; idx++) {
                    
                    // Verifica distância mínima
                    var muitoProximo = false;
                    for(var i = 0; i < numCentrosUsados; i++) {
                        var dx = posicaoX[idx] - centrosUsadosX[i];
                        var dy = posicaoY[idx] - centrosUsadosY[i];
                        if(dx*dx + dy*dy < minDistCirculos*minDistCirculos) {
                            muitoProximo = true;
                            break;
                        }
                    }
                    
                    if(muitoProximo) continue;
                    
                    // Calcula cobertura usando informação pré-computada
                    var coberturaCalculada = 0;
                    var desempate = posicaoNumPontos[idx];
                    
                    for(var i = 0; i < posicaoNumPontos[idx]; i++) {
                        var pontoId = posicaoPontos[idx][i];
                        var faltaCobertura = Math.max(0, minCoverage - coberturaPontos[pontoId]);
                        if(faltaCobertura > 0) {
                            coberturaCalculada += faltaCobertura;
                        }
                    }
                    
                    if(coberturaCalculada > melhorCobertura) {
                        melhorCobertura = coberturaCalculada;
                        melhorPosX = posicaoX[idx];
                        melhorPosY = posicaoY[idx];
                        melhorDesempate = desempate;
                        melhorIndicePosicao = idx;
                    } else if (coberturaCalculada == melhorCobertura) {
                        if (desempate > melhorDesempate) {
                            melhorDesempate = desempate;
                            melhorPosX = posicaoX[idx];
                            melhorPosY = posicaoY[idx];
                            melhorIndicePosicao = idx;
                        }
                    }
                }
            }
            
            // Se ainda não encontrou posição, para para evitar loop infinito
            if(melhorPosX == -1) {
                writeln("ERRO: Não foi possível encontrar posição válida para cobrir ponto " + p);
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
            
            // Atualiza cobertura usando a informação pré-computada
            for(var i = 0; i < posicaoNumPontos[melhorIndicePosicao]; i++) {
                var pontoId = posicaoPontos[melhorIndicePosicao][i];
                coberturaPontos[pontoId]++;
            }
            
            writeln("    Ponto " + p + " agora tem cobertura: " + coberturaPontos[p]);
            writeln("    Círculo cobre " + posicaoNumPontos[melhorIndicePosicao] + " pontos total");
            
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
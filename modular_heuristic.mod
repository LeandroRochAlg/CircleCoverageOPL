/*********************************************
 * Módulo: Heurística CP Modular
 * Author: rocha
 * Creation Date: 12 de ago de 2025
 * Descrição: Heurística para inicialização do CP
 *********************************************/

// === EXECUTA HEURÍSTICA MODULAR PARA SOLUÇÃO INICIAL ===
execute MODULAR_HEURISTIC {
    writeln("EXECUTANDO HEURÍSTICA MODULAR...");
    
    // Reset das variáveis globais
    circulosUsados = 0;
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
    
    writeln("Heurística modular encontrou " + circulosUsados + " círculos");
}

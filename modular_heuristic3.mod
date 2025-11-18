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
    var totalPosicoes = (maxX - minX + 1) * (maxY - minY + 1);
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
    
    // PRÉ-COMPUTAÇÃO: Cria estrutura de cobertura usando stepInteligente
    writeln("Calculando matriz de cobertura (step=" + stepInteligente + ")...");
    
    // Calcula número de posições com step
    var numPosX = Math.ceil((maxX - minX) / stepInteligente) + 1;
    var numPosY = Math.ceil((maxY - minY) / stepInteligente) + 1;
    var totalPosicoesStep = numPosX * numPosY;
    writeln("Posições com step: " + totalPosicoesStep + " (ao invés de " + totalPosicoes + ")");
    
    // Arrays separados para armazenar informações de cada posição
    var posicaoX = new Array(totalPosicoesStep);
    var posicaoY = new Array(totalPosicoesStep);
    var posicaoNumPontos = new Array(totalPosicoesStep);
    var posicaoPontos = new Array(totalPosicoesStep); // Array de arrays com os pontos cobertos por cada posição
    var indicePosicao = 0;
    
    // Para cada posição possível na grade (usando stepInteligente)
    for(var gx = minX; gx <= maxX; gx += stepInteligente) {
        for(var gy = minY; gy <= maxY; gy += stepInteligente) {
            var gxInt = Math.round(gx);
            var gyInt = Math.round(gy);
            // Lista de pontos que seriam cobertos se um círculo fosse colocado em (gx, gy)
            var pontosCobertos = new Array(n);
            var numPontosCobertos = 0;
            
            // Verifica quais pontos estariam dentro do círculo
            for(var ponto = 1; ponto <= n; ponto++) {
                var distX = x[ponto] - gxInt;
                var distY = y[ponto] - gyInt;
                
                if(distX*distX + distY*distY <= r*r) {
                    pontosCobertos[numPontosCobertos] = ponto;
                    numPontosCobertos++;
                }
            }
            
            // Armazena a informação de cobertura para esta posição
            posicaoX[indicePosicao] = gxInt;
            posicaoY[indicePosicao] = gyInt;
            posicaoNumPontos[indicePosicao] = numPontosCobertos;
            posicaoPontos[indicePosicao] = pontosCobertos;
            indicePosicao++;
        }
        
        // Progresso a cada 50 steps
        var stepsProcessados = Math.round((gx - minX) / stepInteligente);
        if(stepsProcessados % 50 == 0 && stepsProcessados > 0) {
            writeln("  Processando coluna gx=" + Math.round(gx) + "/" + maxX + " (step " + stepsProcessados + ")");
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
            
            // Se ainda não encontrou posição, para para evitar loop infinito
            if(melhorCobertura == -1) {
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

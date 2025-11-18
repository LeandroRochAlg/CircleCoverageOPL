/*********************************************
 * Módulo: Heurística CP Modular (pré-cálculo ponto->posições)
 * Author: rocha
 * Creation Date: 13 de ago de 2025
 * Descrição: Pré-computa, para cada ponto, as posições (gx, gy)
 *            da grade que ele cobre; então agrega por posição.
 *********************************************/

// === EXECUTA HEURÍSTICA MODULAR PARA SOLUÇÃO INICIAL ===
execute MODULAR_HEURISTIC {
    writeln("EXECUTANDO HEURÍSTICA MODULAR (ponto->posições)...");
    
    // Reset das variáveis globais
    circulosUsados = 0;
    var totalPosicoes = (maxX - minX + 1) * (maxY - minY + 1);
    writeln("=== INICIANDO HEURÍSTICA 3 (ponto->posições) ===");
    writeln("Grade: (" + minX + "," + minY + ") até (" + maxX + "," + maxY + ")");
    writeln("Total de posições na grade: " + totalPosicoes);
    
    // Estrutura para rastrear cobertura dos pontos já atingida
    var coberturaPontos = new Array(n+1);
    for (var i = 0; i <= n; i++) coberturaPontos[i] = 0;
    
    // Arrays para armazenar círculos já colocados
    var maxPossibleCircles = n * minCoverage;
    var centrosUsadosX = new Array(maxPossibleCircles);
    var centrosUsadosY = new Array(maxPossibleCircles);
    for (var i = 0; i < maxPossibleCircles; i++) { centrosUsadosX[i] = 0; centrosUsadosY[i] = 0; }
    var numCentrosUsados = 0;
    
    // PRÉ-COMPUTAÇÃO: construir mapa de posição -> lista de pontos cobertos
    writeln("Pré-computando cobertura por posição (via pontos)...");
    
    var larguraY = (maxY - minY + 1);
    
    var posicaoX = new Array(totalPosicoes);
    var posicaoY = new Array(totalPosicoes);
    var posicaoNumPontos = new Array(totalPosicoes);
    var posicaoPontos = new Array(totalPosicoes); // cada elemento é um array dinâmico
    
    // Inicializa metadados de cada posição uma única vez
    var idx = 0;
    for (var gx = minX; gx <= maxX; gx++) {
        for (var gy = minY; gy <= maxY; gy++) {
            posicaoX[idx] = gx;
            posicaoY[idx] = gy;
            posicaoNumPontos[idx] = 0;
            posicaoPontos[idx] = new Array(); // dinâmico
            idx++;
        }
        if (((gx - minX) % 100) == 0) {
            writeln("  Inicializadas posições até coluna gx=" + gx + "/" + maxX);
        }
    }
    
    // Para cada ponto, agregamos o ponto em todas as posições (gx,gy) dentro do raio r
    var raio = Math.ceil(r);
    for (var p = 1; p <= n; p++) {
        var xP = Math.round(x[p]);
        var yP = Math.round(y[p]);
        
        var xIni = Math.max(minX, xP - raio);
        var xFim = Math.min(maxX, xP + raio);
        var yIni = Math.max(minY, yP - raio);
        var yFim = Math.min(maxY, yP + raio);
        
        for (var gx = xIni; gx <= xFim; gx++) {
            var dx = gx - xP;
            var dx2 = dx*dx;
            for (var gy = yIni; gy <= yFim; gy++) {
                var dy = gy - yP;
                if (dx2 + dy*dy <= r*r) {
                    var indicePos = (gx - minX) * larguraY + (gy - minY);
                    var k = posicaoNumPontos[indicePos];
                    posicaoPontos[indicePos][k] = p; // append
                    posicaoNumPontos[indicePos] = k + 1;
                }
            }
        }
        if ((p % 50) == 0) {
            writeln("  Processados " + p + " pontos de " + n);
        }
    }
    writeln("Mapa posição->pontos pronto.");
    
    // Busca heurística: para cada ponto, enquanto faltar cobertura, adiciona círculo
    for (var p = 1; p <= n; p++) {
        // Adiciona círculos até que este ponto tenha cobertura mínima
        while (coberturaPontos[p] < minCoverage) {
            var melhorPosX = -1;
            var melhorPosY = -1;
            var melhorCobertura = -1;
            var melhorDesempate = -1;
            var melhorIndicePosicao = -1;
            
            // Busca local em torno do ponto p, restrita ao círculo de raio r
            var xP = Math.round(x[p]);
            var yP = Math.round(y[p]);
            var xIni = Math.max(minX, xP - raio);
            var xFim = Math.min(maxX, xP + raio);
            var yIni = Math.max(minY, yP - raio);
            var yFim = Math.min(maxY, yP + raio);
            
            for (var gx = xIni; gx <= xFim; gx++) {
                var dx = gx - xP;
                var dx2 = dx*dx;
                for (var gy = yIni; gy <= yFim; gy++) {
                    var dy = gy - yP;
                    if (dx2 + dy*dy > r*r) continue; // fora do círculo
                    
                    // Verifica distância mínima dos círculos já colocados
                    var muitoProximo = false;
                    for (var i = 0; i < numCentrosUsados; i++) {
                        var ddx = gx - centrosUsadosX[i];
                        var ddy = gy - centrosUsadosY[i];
                        if (ddx*ddx + ddy*ddy < minDistCirculos*minDistCirculos) { muitoProximo = true; break; }
                    }
                    if (muitoProximo) continue;
                    
                    var indiceBusca = (gx - minX) * larguraY + (gy - minY);
                    
                    // Cobertura potencial baseada no que falta em cada ponto coberto por (gx,gy)
                    var coberturaCalculada = 0;
                    var desempate = posicaoNumPontos[indiceBusca];
                    for (var i = 0; i < posicaoNumPontos[indiceBusca]; i++) {
                        var pontoId = posicaoPontos[indiceBusca][i];
                        var falta = minCoverage - coberturaPontos[pontoId];
                        if (falta > 0) coberturaCalculada += falta;
                    }
                    
                    // Melhor escolha
                    if (coberturaCalculada > melhorCobertura ||
                       (coberturaCalculada == melhorCobertura && desempate > melhorDesempate)) {
                        melhorCobertura = coberturaCalculada;
                        melhorDesempate = desempate;
                        melhorPosX = gx;
                        melhorPosY = gy;
                        melhorIndicePosicao = indiceBusca;
                    }
                }
            }
            
            if (melhorCobertura <= 0) {
                // Sem ganho adicional; evita loop infinito
                // coloca um círculo diretamente no ponto como fallback
                melhorPosX = xP;
                melhorPosY = yP;
                melhorIndicePosicao = (Math.round(melhorPosX) - minX) * larguraY + (Math.round(melhorPosY) - minY);
            }
            
            // Adiciona o círculo
            centrosUsadosX[numCentrosUsados] = melhorPosX;
            centrosUsadosY[numCentrosUsados] = melhorPosY;
            numCentrosUsados++;
            circulosUsados++;
            centrosHeuristicoX[circulosUsados] = melhorPosX;
            centrosHeuristicoY[circulosUsados] = melhorPosY;
            
            // Atualiza cobertura com a lista pré-computada daquela posição
            var cobertos = posicaoNumPontos[melhorIndicePosicao];
            for (var i = 0; i < cobertos; i++) {
                var pontoId = posicaoPontos[melhorIndicePosicao][i];
                coberturaPontos[pontoId]++;
            }
            
            // Limite de segurança
            if (circulosUsados > n * minCoverage) {
                writeln("AVISO: Atingido limite de segurança de círculos");
                break;
            }
        }
    }
    
    // Log final enxuto
    writeln("Heurística (ponto->posições) encontrou " + circulosUsados + " círculos");
}

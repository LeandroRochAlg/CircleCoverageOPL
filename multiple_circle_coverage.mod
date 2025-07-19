/*********************************************
 * OPL 22.1.1.0 Model
 * Author: rocha
 * Creation Date: 3 de jun de 2025 at 20:53:18
 *********************************************/
 
// Parâmetros de entrada
float r = ...;                    // Raio fixo dos círculos
int n = ...;                      // Número de pontos a serem cobertos
range Pontos = 1..n;
float x[Pontos] = ...;            // Coordenadas x dos pontos
float y[Pontos] = ...;            // Coordenadas y dos pontos

// Número máximo de círculos necessários (no pior caso, um por ponto)
int maxCirculos = n;
range Circulos = 1..maxCirculos;

// Constante grande para Big-M method
float M = 10000;

// Variáveis de decisão
dvar boolean useCirculo[Circulos];              // 1 se o círculo k é usado
dvar float centroX[Circulos];                   // Coordenada x do centro do círculo k
dvar float centroY[Circulos];                   // Coordenada y do centro do círculo k
dvar boolean pontoCoberto[Pontos][Circulos];    // 1 se o ponto p é coberto pelo círculo k

// Função objetivo: minimizar número de círculos usados
minimize sum(k in Circulos) useCirculo[k];

subject to {
    // Cada ponto deve ser coberto por pelo menos um círculo
    forall(p in Pontos) {
        sum(k in Circulos) pontoCoberto[p][k] >= 1;
    }
    
    // Um ponto só pode ser coberto por um círculo se esse círculo for usado
    forall(p in Pontos, k in Circulos) {
        pontoCoberto[p][k] <= useCirculo[k];
    }
    
    // Se um ponto é coberto por um círculo, então a distância deve ser <= r
    // Usando Big-M: se pontoCoberto[p][k] = 1, então distância <= r^2
    forall(p in Pontos, k in Circulos) {
        (x[p] - centroX[k])^2 + (y[p] - centroY[k])^2 <= r^2 + M*(1 - pontoCoberto[p][k]);
    }
    

    
    // Quebra de simetria: usar círculos em ordem
    forall(k in 1..maxCirculos-1) {
        useCirculo[k] >= useCirculo[k+1];
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
    
    // Verificação de cobertura completa
    writeln("=== VERIFICAÇÃO DE COBERTURA ===");
    var todosCobertos = true;
    for (var p = 1; p <= n; p++) {
        var coberto = false;
        for (var k = 1; k <= maxCirculos; k++) {
            if (pontoCoberto[p][k] == 1) {
                coberto = true;
                break;
            }
        }
        if (!coberto) {
            writeln("ERRO: Ponto ", p, " não foi coberto!");
            todosCobertos = false;
        }
    }
    
    if (todosCobertos) {
        writeln("✓ Todos os pontos foram cobertos com sucesso!");
    }
    
    // Estatísticas detalhadas
    writeln();
    writeln("=== ESTATÍSTICAS ===");
    writeln("Total de pontos: ", n);
    writeln("Círculos utilizados: ", numCirculosUsados);
    if (numCirculosUsados > 0) {
        writeln("Eficiência: ", (n * 1.0 / numCirculosUsados), " pontos por círculo");
    }
    
    // Verificação manual das distâncias (debug)
    writeln();
    writeln("=== VERIFICAÇÃO DE DISTÂNCIAS ===");
    for (var k = 1; k <= maxCirculos; k++) {
        if (useCirculo[k] == 1) {
            writeln("Círculo ", k, " em (", centroX[k], ", ", centroY[k], "):");
            for (var p = 1; p <= n; p++) {
                var dist2 = (x[p] - centroX[k]) * (x[p] - centroX[k]) + 
                           (y[p] - centroY[k]) * (y[p] - centroY[k]);
                var dist = Math.sqrt(dist2);
                if (pontoCoberto[p][k] == 1) {
                    writeln("  Ponto ", p, ": distância = ", dist, " (coberto)");
                }
            }
        }
    }
}
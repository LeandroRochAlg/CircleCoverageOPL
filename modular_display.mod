/*********************************************
 * Módulo: Display Modular
 * Author: rocha
 * Creation Date: 12 de ago de 2025
 * Descrição: Exibição de resultados modulares
 *********************************************/

// === PÓS-PROCESSAMENTO MODULAR ===
execute MODULAR_RESULTS {
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

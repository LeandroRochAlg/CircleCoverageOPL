/*********************************************
 * Modelo Base para Circle Coverage
 * Author: rocha
 * Creation Date: 11 de ago de 2025
 * Descrição: Estrutura base reutilizável para todos os modelos
 *********************************************/

// Declarações básicas de dados
int n = ...;
range Pontos = 1..n;
float x[Pontos] = ...;
float y[Pontos] = ...;
float r = ...;
int minCoverage = ...;
float minDistCirculos = ...;  // Mudado de int para float
int minX = ...;
int maxX = ...;
int minY = ...;
int maxY = ...;

// Variáveis globais para heurísticas
int circulosUsados = 0;
float centrosHeuristicoX[1..n*minCoverage];  // Array para posições X encontradas pela heurística
float centrosHeuristicoY[1..n*minCoverage];  // Array para posições Y encontradas pela heurística

execute MAIN_HEADER {
    writeln("=============================================================");
    writeln("= CIRCLE COVERAGE OPTIMIZATION - MODELO MODULAR           =");
    writeln("=============================================================");
    writeln();
    
    writeln("Dados do problema:");
    writeln("- Pontos: " + n);
    writeln("- Raio dos círculos: " + r);
    writeln("- Cobertura mínima: " + minCoverage);
    writeln("- Distância mínima entre círculos: " + minDistCirculos);
    writeln("- Região X: [" + minX + ", " + maxX + "]");
    writeln("- Região Y: [" + minY + ", " + maxY + "]");
    writeln();
}

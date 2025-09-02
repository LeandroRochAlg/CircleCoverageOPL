/*********************************************
 * Módulo: Pré-processamento FIX_CIRC_CLI
 * Author: rocha
 * Creation Date: 02 de set de 2025
 * Descrição: Implementa o algoritmo para fixar círculos em clientes âncora
 *********************************************/

// Variáveis calculadas pelo pré-processamento
int numCirculosFixados = 0;
int clienteFixado[Circulos];

execute PREPROCESSAMENTO_FIX_CIRC {
    writeln("=== EXECUTANDO FIX_CIRC_CLI ===");
    
    // Inicializar array
    for(var k in Circulos) {
        clienteFixado[k] = 0;
    }
    
    // Lista L dos clientes (1=ativo, 0=removido)
    var L = new Array(n+1);
    for(var p = 1; p <= n; p++) {
        L[p] = 1;
    }
    var clientesRestantes = n;
    
    var indiceCirculo = 1;
    var distancia2r = (2 * r) * (2 * r); // (2r)²
    
    while(clientesRestantes > 0 && indiceCirculo <= maxCirculos && numCirculosFixados < 20) {
        // Escolher cliente C mais abaixo e à esquerda
        var clienteC = -1;
        var menorY = Infinity;
        var menorX = Infinity;
        
        for(var p = 1; p <= n; p++) {
            if(L[p] == 1) { // Cliente ainda na lista
                if(y[p] < menorY || (y[p] == menorY && x[p] < menorX)) {
                    menorY = y[p];
                    menorX = x[p];
                    clienteC = p;
                }
            }
        }
        
        if(clienteC == -1) break; // Não há mais clientes
        
        writeln("Cliente âncora: " + clienteC + " em (" + x[clienteC] + ", " + y[clienteC] + ")");
        
        // Fixar círculos i, ..., i + minCoverage - 1 para C
        for(var k = 0; k < minCoverage; k++) {
            if(indiceCirculo + k <= maxCirculos) {
                clienteFixado[indiceCirculo + k] = clienteC;
                numCirculosFixados++;
            }
        }
        
        writeln("  -> Fixados círculos " + indiceCirculo + " a " + 
                (indiceCirculo + minCoverage - 1) + " no cliente " + clienteC);
        
        // Remover clientes dentro da distância 2r
        var removidos = 0;
        for(var p = 1; p <= n; p++) {
            if(L[p] == 1) {
                var dx = x[p] - x[clienteC];
                var dy = y[p] - y[clienteC];
                if(dx*dx + dy*dy <= distancia2r) {
                    L[p] = 0;
                    clientesRestantes--;
                    removidos++;
                }
            }
        }
        
        writeln("  -> Removidos " + removidos + " clientes. Restam: " + clientesRestantes);
        
        indiceCirculo += minCoverage;
    }
    
    writeln("Total de círculos fixados: " + numCirculosFixados);
    writeln("=== FIM FIX_CIRC_CLI ===");
    writeln();
}

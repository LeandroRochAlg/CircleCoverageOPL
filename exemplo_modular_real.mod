/*********************************************
 * Exemplo Modular Real - Estrutura com Includes
 * Author: rocha
 * Creation Date: 12 de ago de 2025
 * Descrição: Arquitetura modular verdadeira com includes
 *********************************************/

using CP;

// Include common_base
include "common_base.mod";

// Cálculo de ajuste fino, step e outros parâmetros
float ajusteFino = 0.5;
float stepInteligente = ((r * sqrt(2) - minDistCirculos) / 2) * ajusteFino;

// Configuração CP
execute CP_CONFIG {
    cp.param.timeLimit = 3600;
    cp.param.logVerbosity = "Quiet";
    writeln("=== EXEMPLO MODULAR REAL ===");
    writeln("Ajuste Fino: " + ajusteFino);
    writeln("Step Inteligente: " + stepInteligente);
}

// Include heuristic
include "modular_heuristic4.mod";

// Usa o resultado da heurística para definir o range (mais conservador)
int maxCirculos = circulosUsados;
range Circulos = 1..maxCirculos;

// Include constraints
include "modular_constraints.mod";

// Include display
include "modular_display.mod";

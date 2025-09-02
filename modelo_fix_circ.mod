/*********************************************
 * Modelo com Fixação de Círculos (FIX_CIRC_CLI)
 * Author: rocha
 * Creation Date: 02 de set de 2025
 * Descrição: Demonstra a estratégia de quebra de simetria
 *********************************************/

using CP;

// Include da base comum
include "common_base.mod";

// Definir range de círculos
int maxCirculos = n * minCoverage;
range Circulos = 1..maxCirculos;

// Pré-processamento para fixar círculos
include "fix_circ_preprocessing.mod";

// Restrições com fixação
include "modular_constraints2.mod";

// Configuração do CP
execute CP_CONFIG {
    cp.param.timeLimit = 3600;
    cp.param.logVerbosity = "Quiet";
}

// Include display
include "modular_display.mod";

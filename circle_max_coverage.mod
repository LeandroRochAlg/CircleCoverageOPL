/*********************************************
 * OPL 22.1.1.0 Model
 * Author: rocha
 * Creation Date: 20 de mai de 2025 at 15:36:21
 *********************************************/

// Definir parâmetros de entrada
float r = ...;         // Raio fixo do círculo
int n = ...;           // Número de pontos
range Pontos = 1..n;
float x[Pontos] = ...; // Coordenadas x dos pontos
float y[Pontos] = ...; // Coordenadas y dos pontos

// Variáveis de decisão
dvar float a;          // Coordenada x do centro
dvar float b;          // Coordenada y do centro
dvar boolean coverage[Pontos]; // 1 se o ponto está coberto

// Constante grande para Big-M method
float M = 1000; // Deve ser um valor grande o suficiente

// Função objetivo: maximizar pontos cobertos
dexpr int coverageCount = sum(i in Pontos) coverage[i];
maximize coverageCount;

// Restrições
subject to {
  // Relacionar coverage com a posição do círculo usando Big-M method
  forall (i in Pontos) {
    // Se coverage[i] = 1, então a distância deve ser <= r^2
    (x[i] - a)^2 + (y[i] - b)^2 <= r^2 + M*(1-coverage[i]);
  }
}

execute DISPLAY_RESULTS{
  writeln("Centro x = ", a);
  writeln("Centro y = ", b);
  writeln("Pontos cobertos: ", coverageCount, "/", n);
  writeln("Detalhes:");
  for(var i = 1; i <= n; i++)
    if(coverage[i] == 1)
      writeln("  Ponto ", i, " (", x[i], ",", y[i], ") coberto");
}
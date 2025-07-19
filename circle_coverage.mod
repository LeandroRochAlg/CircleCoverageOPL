/*********************************************
 * OPL 22.1.1.0 Model
 * Author: rocha
 * Creation Date: 20 de mai de 2025 at 15:06:42
 *********************************************/

// Definir parâmetros de entrada
float r = ...; // Raio fixo do círculo
int n = ...;   // Número de pontos
range Pontos = 1..n;
float x[Pontos] = ...; // Coordenadas x dos pontos
float y[Pontos] = ...; // Coordenadas y dos pontos

// Variáveis de decisão: coordenadas (a, b) do centro do círculo
dvar int a; 
dvar int b;

// Restrições: todos os pontos devem estar dentro do círculo
subject to {
  forall (i in Pontos)
    (x[i] - a)^2 + (y[i] - b)^2 <= r^2;
}

execute DISPLAY_RESULTS{
  writeln("Centro x = ", a);
  writeln("Centro y = ", b);
}
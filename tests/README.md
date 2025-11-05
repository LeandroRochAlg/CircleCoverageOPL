# CircleCoverageTest

## Descrição

Este projeto implementa um gerador de instâncias e um visualizador para o problema de cobertura por círculos. O objetivo é encontrar o número mínimo de círculos necessários para cobrir um conjunto de pontos, respeitando restrições de cobertura mínima e distância entre círculos.

## Estrutura do Projeto

```
circlecoveragetest/
├── circle_data_generator.py  # Gerador de instâncias do problema
├── circle_visualizer.py      # Visualizador de soluções
├── instances/                # Diretório com instâncias geradas
└── solutions/                # Diretório com soluções visualizadas
```

## Funcionalidades

### Gerador de Dados (`circle_data_generator.py`)

Gera instâncias do problema de cobertura por círculos com as seguintes características:

- **Geração de pontos**: Cria pontos com distribuição normal concentrados em torno de um centro
- **Parâmetros calculados automaticamente**:
  - Raio dos círculos (r)
  - Cobertura mínima por círculo (min_coverage)
  - Distância mínima entre círculos (min_dist_circles)
- **Validação**: Garante que a instância gerada seja viável
- **Saída**: Gera arquivos de dados e modelo CPLEX (.dat e .mod)

**Como usar:**
```powershell
python circle_data_generator.py
```

O programa irá solicitar:
1. Número de pontos a serem gerados
2. Raio de dispersão dos pontos (opcional)

### Visualizador de Soluções (`circle_visualizer.py`)

Visualiza as soluções do problema de cobertura por círculos com recursos avançados:

- **Visualização gráfica**: Plota pontos e círculos da solução
- **Análise de cobertura**: Mostra quais pontos são cobertos por quais círculos
- **Estatísticas detalhadas**: 
  - Número de círculos utilizados
  - Cobertura média por círculo
  - Distâncias entre círculos
  - Utilização de cobertura
- **Entrada flexível**: Suporta entrada manual ou carregamento de arquivo JSON
- **Exportação**: Salva a visualização e análise em diretórios organizados

**Como usar:**
```powershell
python circle_visualizer.py
```

O programa oferece duas opções:
1. Entrada manual dos dados do CPLEX
2. Carregamento de arquivo JSON com a solução

## Formato dos Dados

### Arquivo de Instância (.dat)

Os arquivos de instância contêm:
- `n`: número de pontos
- `r`: raio dos círculos
- `min_coverage`: cobertura mínima exigida por círculo
- `min_dist_circles`: distância mínima entre círculos
- `points_x`: coordenadas X dos pontos
- `points_y`: coordenadas Y dos pontos

### Arquivo de Solução (JSON)

```json
{
  "num_circles": 5,
  "circles": [
    {"id": 1, "x": 10.5, "y": 20.3, "covered_points": [1, 2, 3]},
    ...
  ]
}
```

## Organização dos Diretórios

### Instâncias (`instances/`)

Cada instância é salva em um diretório com timestamp único contendo:
- `generation_data.txt`: Parâmetros da instância
- `data.dat`: Arquivo de dados para CPLEX
- `model.mod`: Modelo de otimização

### Soluções (`solutions/`)

Cada solução é salva em um diretório com timestamp único contendo:
- `visualization.png`: Gráfico da solução
- `analysis.txt`: Análise detalhada da solução
- `solution.json`: Dados da solução em formato JSON

## Requisitos

```
python >= 3.7
numpy
matplotlib
```

### Instalação de Dependências

```powershell
pip install numpy matplotlib
```

## Exemplos de Uso

### 1. Gerar uma nova instância
```powershell
python circle_data_generator.py
# Digite o número de pontos: 50
# Digite o raio de dispersão (ou Enter para padrão): 100
```

### 2. Visualizar uma solução
```powershell
python circle_visualizer.py
# Escolha a opção de entrada de dados
# Cole os resultados do CPLEX ou carregue um arquivo JSON
```

## Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:
- Reportar bugs
- Sugerir novas funcionalidades
- Enviar pull requests

## Licença

Este projeto está licenciado sob os termos especificados no arquivo [LICENSE](LICENSE).

## Autor

Desenvolvido como ferramenta para estudo e resolução de problemas de cobertura por círculos.
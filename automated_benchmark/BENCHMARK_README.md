# Sistema de Benchmark Automatizado - Cobertura de Círculos

Sistema completo para execução automatizada de testes de desempenho dos algoritmos de cobertura de círculos.

## 📋 Funcionalidades

- ✅ Geração automática de dados de teste
- ✅ Atualização do arquivo `.dat` automaticamente
- ✅ Execução sequencial das 6 configurações de teste
- ✅ Controle de timeout (1h10min por teste)
- ✅ Registro automático de resultados em CSV
- ✅ Execução contínua até interrupção manual
- ✅ Reserva de 1 núcleo da CPU (se disponível)
- ✅ Monitoramento em tempo real

## 🚀 Como Usar

### 1. Setup Inicial

Execute o script de setup para instalar dependências e verificar configuração:

```powershell
python setup_benchmark.py
```

Este script irá:
- Instalar `numpy` e `psutil`
- Verificar se o `oplrun.exe` está acessível
- Validar a estrutura do projeto

### 2. Iniciar Benchmark

Para iniciar o benchmark automatizado:

```powershell
python automated_benchmark.py
```

O script irá:
1. Gerar dados aleatórios de teste (n ≤ 200, minCoverage 1-5)
2. Escrever no `circle_coverage.dat`
3. Executar Teste1, Teste2, ..., Teste6 sequencialmente
4. Salvar resultados individuais e atualizar tabela CSV
5. Repetir indefinidamente até você pressionar `Ctrl+C`

### 3. Monitorar Progresso (Opcional)

Em outro terminal, você pode monitorar o progresso:

```powershell
python monitor_benchmark.py
```

Ou para ver apenas os últimos resultados:

```powershell
python monitor_benchmark.py --latest 10
```

## 📊 Resultados

Os resultados são salvos em `tests/automated_results/`:

- **`results_table.csv`**: Tabela consolidada com todos os resultados
- **`result_XXXX_TesteY_*.txt`**: Resultados individuais de cada execução

### Formato da Tabela CSV

| TestID | nClientes | raio | minDistCirculos | minCoverage | Teste1_numCirculos | Teste1_tempo | Teste1_resultado | ... |
|--------|-----------|------|-----------------|-------------|-------------------|--------------|------------------|-----|
| Test_0001 | 45 | 15.2 | 1.85 | 3 | 12 | 245.67 | OK | ... |

## ⚙️ Configurações

### Parâmetros Principais (em `automated_benchmark.py`)

```python
MAX_EXECUTION_TIME = 3600      # 1 hora (tempo teórico)
TIMEOUT_KILL = 4200            # 1h10min (timeout real para forçar parada)
MAX_N = 200                    # Máximo de pontos
MIN_COVERAGE_RANGE = (1, 5)    # Range para minCoverage
```

### Configurações de Teste

As 6 configurações são executadas nesta ordem:
1. Teste1
2. Teste2
3. Teste3
4. Teste4
5. Teste5
6. Teste6

Estas configurações devem estar definidas no arquivo `.oplproject`.

## 🔧 Ajustes Necessários

### Caminho do OPLRUN

Se o CPLEX estiver em um local diferente, edite em `automated_benchmark.py`:

```python
OPLRUN_PATH = r"C:\Program Files\IBM\ILOG\CPLEX_Studio2211\opl\bin\x64_win64\oplrun.exe"
```

### Limites de CPU

O script tenta reservar 1 núcleo da CPU automaticamente usando `psutil`. Se você tiver problemas:

1. Instale psutil: `pip install psutil`
2. Ou remova essa funcionalidade (comentar seção no final do arquivo)

## 📈 Estatísticas do Monitor

O monitor exibe:
- Total de testes executados
- Total de execuções (testes × 6 configs)
- Por configuração:
  - Número de sucessos
  - Número de timeouts
  - Taxa de sucesso (%)
  - Tempo médio de execução
  - Número médio de círculos

## 🛑 Como Parar

Pressione `Ctrl+C` no terminal onde o benchmark está rodando.

O script irá:
- Tentar terminar o processo atual graciosamente
- Salvar todos os resultados coletados até o momento
- Exibir resumo final

## ⚠️ Observações Importantes

1. **Não interfira durante a execução**: O script foi projetado para rodar sozinho
2. **Espaço em disco**: Cada teste gera arquivos de resultado (alguns KB cada)
3. **Tempo de execução**: Cada rodada completa pode levar até ~7 horas (6 configs × 1h10min)
4. **Timeout rigoroso**: Se um teste ultrapassar 1h10min, será forçadamente terminado
5. **Arquivo .dat**: Será sobrescrito a cada novo teste

## 🐛 Troubleshooting

### Erro: "oplrun não encontrado"
- Verifique o caminho do CPLEX no script
- Certifique-se de que o CPLEX está instalado

### Erro: "Módulo numpy não encontrado"
- Execute: `pip install numpy psutil`

### Timeout não funciona
- Verifique se tem permissões para terminar processos
- No Windows, pode ser necessário executar como Administrador

### Resultados não aparecem na tabela
- Verifique se o diretório `tests/automated_results/` foi criado
- Verifique permissões de escrita

## 📝 Logs

Cada execução exibe no terminal:
- Progresso atual
- Parâmetros da instância
- Resultado de cada configuração
- Tempo de execução
- Resumo ao final de cada teste completo

## 🔄 Fluxo de Execução

```
┌─────────────────────────┐
│  Gerar Dados Aleatórios │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Escrever .dat          │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Executar Teste1        │───► Timeout? ─► Matar processo
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Executar Teste2        │───► Timeout? ─► Matar processo
└───────────┬─────────────┘
            │
            ▼
            ⋮
            │
            ▼
┌─────────────────────────┐
│  Executar Teste6        │───► Timeout? ─► Matar processo
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Salvar Resultados      │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Atualizar Tabela CSV   │
└───────────┬─────────────┘
            │
            └────► Repetir (loop infinito)
```

## 📞 Suporte

Se encontrar problemas, verifique:
1. Logs no terminal
2. Arquivo `results_table.csv` para ver se está sendo atualizado
3. Arquivos individuais em `tests/automated_results/`

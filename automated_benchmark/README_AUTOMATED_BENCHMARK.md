# 🤖 Sistema de Benchmark Automatizado

Sistema completo para teste automatizado e contínuo de algoritmos de cobertura de círculos.

## 📚 Documentação

- **[QUICKSTART.md](QUICKSTART.md)** - Guia rápido de início (COMECE AQUI!)
- **[BENCHMARK_README.md](BENCHMARK_README.md)** - Documentação completa e detalhada
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Soluções para problemas comuns

## 🚀 Início Rápido (3 Passos)

### 1️⃣ Setup
```powershell
python setup_benchmark.py
```

### 2️⃣ Executar
```powershell
python automated_benchmark.py
```

### 3️⃣ Analisar
```powershell
python analyze_results.py
```

**OU use o menu interativo:**
```powershell
.\benchmark_menu.bat
```

## 📦 Arquivos Incluídos

### Scripts Principais
- **`automated_benchmark.py`** - Motor principal do benchmark (execução contínua)
- **`setup_benchmark.py`** - Script de configuração inicial
- **`monitor_benchmark.py`** - Monitor de progresso em tempo real
- **`analyze_results.py`** - Análise estatística dos resultados
- **`test_system.py`** - Teste de verificação do sistema

### Scripts Auxiliares
- **`benchmark_menu.bat`** - Menu interativo no Windows
- **`circle_data_generator.py`** - Gerador de dados (legado, integrado no main)
- **`circle_visualizer.py`** - Visualizador de resultados (legado)

### Documentação
- **`QUICKSTART.md`** - Guia de início rápido
- **`BENCHMARK_README.md`** - Documentação completa
- **`TROUBLESHOOTING.md`** - Soluções de problemas

## ⚙️ Configurações Padrão

| Parâmetro | Valor | Descrição |
|-----------|-------|-----------|
| Tempo limite teórico | 1 hora | Configurado no CPLEX |
| Timeout real (kill) | 1h10min | Força parada após este tempo |
| Máximo de pontos (n) | 200 | Tamanho máximo da instância |
| Range minCoverage | 1-5 | Cobertura mínima aleatória |
| Configurações testadas | 6 | Teste1 até Teste6 |

## 📊 Estrutura de Resultados

```
tests/
└── automated_results/
    ├── results_table.csv              # Tabela consolidada
    ├── analysis_summary.json          # Resumo estatístico
    ├── result_Test_0001_Teste1_*.txt  # Resultados individuais
    ├── result_Test_0001_Teste2_*.txt
    └── ...
```

## 🎯 Funcionalidades

### ✅ Geração Automática de Dados
- Distribuição normal concentrada
- Parâmetros calculados automaticamente
- N entre 5 e 200 pontos
- MinCoverage entre 1 e 5

### ✅ Execução Automatizada
- Loop infinito até interrupção manual
- 6 configurações testadas sequencialmente
- Timeout rigoroso (1h10min)
- Kill forçado de processos travados

### ✅ Controle de Recursos
- Tenta reservar 1 núcleo da CPU (requer psutil)
- Gerenciamento de memória
- Cleanup automático de processos

### ✅ Registro Completo
- CSV com todos os resultados
- Arquivos individuais por teste
- Timestamps e metadados
- JSON para análise programática

### ✅ Monitoramento em Tempo Real
- Atualização a cada 10 segundos
- Estatísticas por configuração
- Taxa de sucesso e tempos médios
- Sem interferência na execução

### ✅ Análise Estatística
- Estatísticas descritivas completas
- Comparação entre configurações
- Análise por tamanho de instância
- Identificação de melhores/piores casos

## 🔧 Requisitos

### Obrigatório
- Python 3.6+
- NumPy
- IBM ILOG CPLEX Optimization Studio

### Opcional
- psutil (para afinidade de CPU)

### Instalação
```powershell
pip install numpy psutil
```

## 📈 Exemplo de Uso Típico

```powershell
# Terminal 1: Executar benchmark
python automated_benchmark.py

# Terminal 2: Monitorar progresso
python monitor_benchmark.py

# Após algumas horas, analisar resultados
python analyze_results.py
```

## 🎬 Fluxo de Execução

```
Início
  ↓
Gerar Dados Aleatórios (n, r, minCoverage, etc.)
  ↓
Escrever circle_coverage.dat
  ↓
Para cada configuração (Teste1 até Teste6):
  ↓
  Executar com oplrun (timeout 1h10min)
  ↓
  Extrair resultados (num círculos, tempo)
  ↓
  Salvar resultado individual
  ↓
Atualizar results_table.csv
  ↓
Aguardar 10 segundos
  ↓
Repetir (loop infinito até Ctrl+C)
```

## 📱 Interface do Menu

```
1. Setup inicial (instalar dependências)
2. Iniciar benchmark (execução contínua)
3. Monitorar progresso (em tempo real)
4. Analisar resultados
5. Ver últimos resultados
6. Abrir pasta de resultados
7. Sair
```

## 🔍 Diagnóstico e Teste

Execute o teste de sistema antes de rodadas longas:
```powershell
python test_system.py
```

Verifica:
- ✓ Bibliotecas instaladas
- ✓ OPLRUN acessível
- ✓ Arquivos do projeto
- ✓ Geração de dados
- ✓ Execução básica

## 💡 Dicas de Uso

1. **Primeira vez:** Execute `test_system.py` para verificar tudo
2. **Overnight:** Deixe rodando durante a noite para acumular resultados
3. **Monitoramento:** Use terminal separado para monitor
4. **Backup:** Faça backup periódico de `automated_results/`
5. **Análise:** Analise resultados periodicamente para detectar padrões

## ⚠️ Observações Importantes

- ⚠️ O arquivo `circle_coverage.dat` é sobrescrito a cada teste
- ⚠️ Feche o CPLEX IDE durante a execução
- ⚠️ Não execute múltiplas instâncias simultaneamente
- ⚠️ Cada rodada completa pode levar até ~7 horas
- ⚠️ Resultados "Sem resultado" indicam timeout

## 🐛 Problemas Comuns

| Problema | Solução Rápida |
|----------|----------------|
| Module not found | `pip install numpy psutil` |
| oplrun não encontrado | Ajustar OPLRUN_PATH |
| Timeout não funciona | Executar como Admin |
| CSV vazio | Aguardar teste completar |
| PC lento | Verificar psutil instalado |

Ver [TROUBLESHOOTING.md](TROUBLESHOOTING.md) para detalhes.

## 📊 Exemplo de Saída (Monitor)

```
================================================================================
ESTATÍSTICAS DO BENCHMARK
================================================================================
Total de testes executados: 25
Total de execuções: 150

Config          Sucessos    Timeouts    Taxa Sucesso    Tempo Médio     Círc. Médio
------------------------------------------------------------------------------------------------
Teste1          18          7           72.0%           845.23s         24.3
Teste2          23          2           92.0%           234.56s         22.1
Teste3          15          10          60.0%           1234.78s        28.7
Teste4          20          5           80.0%           567.89s         23.5
Teste5          22          3           88.0%           345.67s         21.8
Teste6          19          6           76.0%           678.90s         25.2
================================================================================
```

## 🔄 Atualizações e Melhorias

Para ajustar o comportamento do benchmark, edite `automated_benchmark.py`:

```python
# Linha ~18-22
MAX_EXECUTION_TIME = 3600      # Ajustar tempo teórico
TIMEOUT_KILL = 4200           # Ajustar timeout real
MAX_N = 200                   # Ajustar tamanho máximo
MIN_COVERAGE_RANGE = (1, 5)   # Ajustar range de cobertura
```

## 📞 Suporte

1. Verifique [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Execute `python test_system.py`
3. Revise os logs de execução
4. Verifique arquivos em `automated_results/`

## 📝 Notas de Versão

**v1.0** (04/11/2025)
- ✅ Sistema completo de benchmark automatizado
- ✅ 6 configurações de teste
- ✅ Monitoramento em tempo real
- ✅ Análise estatística
- ✅ Documentação completa
- ✅ Menu interativo
- ✅ Sistema de troubleshooting

## 🎯 Roadmap Futuro

- [ ] Gráficos automáticos de comparação
- [ ] Exportação para Excel formatado
- [ ] Detecção automática de configurações
- [ ] Interface web para monitoramento
- [ ] Notificações por email ao completar
- [ ] Paralelização de testes independentes

---

**🚀 Pronto para começar? Leia [QUICKSTART.md](QUICKSTART.md) e execute `python setup_benchmark.py`!**

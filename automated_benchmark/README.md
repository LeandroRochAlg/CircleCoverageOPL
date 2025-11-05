# 🤖 Sistema de Benchmark Automatizado

**Localização:** `automated_benchmark/`

Sistema completo para teste automatizado e contínuo de algoritmos de cobertura de círculos.

## 🚀 Início Rápido

### Opção 1: Menu Interativo (Recomendado)
```powershell
cd automated_benchmark
.\benchmark_menu.bat
```

### Opção 2: Linha de Comando
```powershell
cd automated_benchmark

# 1. Setup (primeira vez)
python setup_benchmark.py

# 2. Verificar sistema
python preflight_check.py

# 3. Executar benchmark
python automated_benchmark.py
```

## 📁 Estrutura da Subpasta

```
automated_benchmark/
├── automated_benchmark.py      ← Script principal
├── monitor_benchmark.py        ← Monitor em tempo real
├── analyze_results.py          ← Análise de resultados
├── setup_benchmark.py          ← Setup inicial
├── preflight_check.py          ← Verificação pré-voo
├── test_system.py              ← Teste rápido
├── benchmark_menu.bat          ← Menu interativo
│
├── README.md                   ← Este arquivo
├── QUICKSTART.md               ← Guia rápido (3 passos)
├── BENCHMARK_README.md         ← Documentação técnica
├── TROUBLESHOOTING.md          ← Soluções de problemas
├── INDEX.md                    ← Índice completo
└── README_AUTOMATED_BENCHMARK.md  ← Visão geral
```

## 📊 Resultados

Os resultados são salvos em: `../tests/automated_results/`
- `results_table.csv` - Tabela consolidada
- `analysis_summary.json` - Resumo estatístico
- `result_*.txt` - Detalhes individuais

## 🎯 Comandos Principais

Todos executados a partir de `automated_benchmark/`:

```powershell
# Executar benchmark
python automated_benchmark.py

# Monitorar progresso
python monitor_benchmark.py

# Ver últimos 10 resultados
python monitor_benchmark.py --latest 10

# Analisar resultados
python analyze_results.py

# Menu interativo
.\benchmark_menu.bat
```

## 📚 Documentação

- **QUICKSTART.md** - Para iniciantes, guia em 3 passos
- **BENCHMARK_README.md** - Documentação técnica completa
- **TROUBLESHOOTING.md** - Soluções para problemas comuns
- **INDEX.md** - Índice de todos os arquivos

## ⚙️ Configuração

Todos os caminhos foram ajustados para funcionar da subpasta:
- ✅ Acessa `../circle_coverage.dat` (raiz do projeto)
- ✅ Salva resultados em `../tests/automated_results/`
- ✅ Executa oplrun com path correto do projeto

## 🔧 Ajustes para Subpasta

Os seguintes arquivos foram ajustados:
- `automated_benchmark.py` - PROJECT_DIR = SCRIPT_DIR.parent
- `monitor_benchmark.py` - PROJECT_DIR = SCRIPT_DIR.parent
- `analyze_results.py` - PROJECT_DIR = SCRIPT_DIR.parent
- `setup_benchmark.py` - project_dir = Path(__file__).parent.parent
- `preflight_check.py` - project_dir = Path(__file__).parent.parent
- `test_system.py` - Imports ajustados
- `benchmark_menu.bat` - Usa %~dp0 para caminhos relativos

## 🎁 Funcionalidades

✅ **100% Automatizado** - Roda sem intervenção  
✅ **Gera dados** - n ≤ 200, minCoverage 1-5  
✅ **6 configurações** - Teste1 a Teste6  
✅ **Timeout** - 1h10min, mata processos travados  
✅ **Loop infinito** - Repete até parar (Ctrl+C)  
✅ **Monitoramento** - Tempo real sem interferir  
✅ **Análise** - Relatórios estatísticos  

## 🚦 Status

- ✅ Todos os arquivos movidos para `automated_benchmark/`
- ✅ Todos os caminhos ajustados
- ✅ Menu .bat ajustado
- ✅ Scripts Python ajustados
- ✅ Documentação organizada

## 💡 Dicas

1. **Sempre execute a partir da subpasta** `automated_benchmark/`
2. **Use o menu** `.\benchmark_menu.bat` para facilitar
3. **Resultados** ficam em `../tests/automated_results/`
4. **Backup** os resultados periodicamente

## 📞 Ajuda

Consulte a documentação na ordem:
1. `QUICKSTART.md` - Começar rapidamente
2. `BENCHMARK_README.md` - Detalhes técnicos
3. `TROUBLESHOOTING.md` - Problemas comuns

---

**Versão:** 1.0 (Organizada em subpasta)  
**Data:** 04/11/2025

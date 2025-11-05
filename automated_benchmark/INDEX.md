# 📋 ÍNDICE DE ARQUIVOS DO SISTEMA DE BENCHMARK

## 🎯 Arquivos Principais de Execução

| Arquivo | Descrição | Quando Usar |
|---------|-----------|-------------|
| **`automated_benchmark.py`** | Motor principal do benchmark | Executar testes automatizados |
| **`monitor_benchmark.py`** | Monitor em tempo real | Acompanhar progresso |
| **`analyze_results.py`** | Análise estatística | Após acumular resultados |

## 🔧 Arquivos de Setup e Teste

| Arquivo | Descrição | Quando Usar |
|---------|-----------|-------------|
| **`setup_benchmark.py`** | Instalação de dependências | Primeira vez / após reinstalar Python |
| **`preflight_check.py`** | Verificação completa do sistema | Antes de rodadas longas |
| **`test_system.py`** | Teste rápido de funcionamento | Diagnosticar problemas |

## 🖥️ Interface e Utilidades

| Arquivo | Descrição | Quando Usar |
|---------|-----------|-------------|
| **`benchmark_menu.bat`** | Menu interativo (Windows) | Acesso fácil a todas as funções |

## 📚 Documentação

| Arquivo | Descrição | Para Quem |
|---------|-----------|-----------|
| **`README_AUTOMATED_BENCHMARK.md`** | Visão geral completa | Todos (overview) |
| **`QUICKSTART.md`** | Guia rápido de início | Iniciantes |
| **`BENCHMARK_README.md`** | Documentação técnica detalhada | Usuários avançados |
| **`TROUBLESHOOTING.md`** | Soluções de problemas | Quando houver erros |
| **`INDEX.md`** | Este arquivo | Referência rápida |

## 🗂️ Estrutura de Diretórios

```
circlecoverageopl/
│
├── automated_benchmark.py          ← Executar benchmark
├── monitor_benchmark.py            ← Monitorar progresso
├── analyze_results.py              ← Analisar resultados
│
├── setup_benchmark.py              ← Setup inicial
├── preflight_check.py              ← Verificação pré-voo
├── test_system.py                  ← Teste rápido
│
├── benchmark_menu.bat              ← Menu interativo
│
├── README_AUTOMATED_BENCHMARK.md   ← README principal
├── QUICKSTART.md                   ← Guia rápido
├── BENCHMARK_README.md             ← Docs técnicas
├── TROUBLESHOOTING.md              ← Soluções
├── INDEX.md                        ← Este arquivo
│
├── circle_coverage.dat             ← Dados (sobrescrito)
├── .oplproject                     ← Configurações OPL
│
├── tests/
│   └── automated_results/          ← Resultados salvos aqui
│       ├── results_table.csv       ← Tabela consolidada
│       ├── analysis_summary.json   ← Resumo estatístico
│       └── result_*.txt            ← Resultados individuais
│
└── ... (outros arquivos do projeto)
```

## 🎬 Fluxo de Uso Típico

### 1️⃣ Primeira Vez (Setup)
```
preflight_check.py
    ↓
setup_benchmark.py
    ↓
test_system.py
```

### 2️⃣ Executar Benchmark
```
Terminal 1: automated_benchmark.py
Terminal 2: monitor_benchmark.py (opcional)
```

### 3️⃣ Analisar Resultados
```
analyze_results.py
```

## 🔍 Guia Rápido de Escolha

### "Quero começar agora!"
→ `QUICKSTART.md`

### "Preciso entender tudo antes"
→ `BENCHMARK_README.md`

### "Está dando erro"
→ `TROUBLESHOOTING.md`

### "Quero verificar se está tudo ok"
→ `python preflight_check.py`

### "Quero rodar o benchmark"
→ `python automated_benchmark.py`

### "Quero ver o progresso"
→ `python monitor_benchmark.py`

### "Quero analisar os resultados"
→ `python analyze_results.py`

### "Quero usar interface visual"
→ `.\benchmark_menu.bat`

## 📊 Arquivos de Saída

Todos os resultados são salvos em `tests/automated_results/`:

### `results_table.csv`
Tabela principal com todos os testes

**Colunas:**
- TestID
- nClientes, raio, minDistCirculos, minCoverage
- Para cada Teste (1-6): numCirculos, tempo, resultado

### `analysis_summary.json`
Resumo estatístico em JSON

**Contém:**
- Estatísticas por configuração
- Estatísticas por tamanho de instância
- Timestamp da análise

### `result_XXXX_TesteY_ZZZZZ.txt`
Resultado individual de cada execução

**Contém:**
- Test ID e Config
- Sucesso/Falha
- Número de círculos
- Tempo de execução
- Parâmetros da instância

## 🎯 Comandos Rápidos

```powershell
# Setup completo
python setup_benchmark.py

# Verificação pré-voo
python preflight_check.py

# Executar benchmark
python automated_benchmark.py

# Monitorar (terminal separado)
python monitor_benchmark.py

# Ver últimos 10 resultados
python monitor_benchmark.py --latest 10

# Análise completa
python analyze_results.py

# Menu interativo
.\benchmark_menu.bat

# Teste de sistema
python test_system.py
```

## 📞 Ajuda Rápida

| Problema | Consultar |
|----------|-----------|
| Não sei por onde começar | `QUICKSTART.md` |
| Preciso de detalhes técnicos | `BENCHMARK_README.md` |
| Está dando erro | `TROUBLESHOOTING.md` |
| Quer verificar sistema | `python preflight_check.py` |
| Quer testar rapidamente | `python test_system.py` |

## 🔄 Ciclo de Vida Típico

```
Dia 1: Setup
├── Ler QUICKSTART.md
├── Executar setup_benchmark.py
├── Executar preflight_check.py
└── Testar com test_system.py

Dia 2-N: Execução
├── Iniciar automated_benchmark.py
├── Monitorar com monitor_benchmark.py
└── Deixar rodando

Após acumular dados: Análise
├── Parar benchmark (Ctrl+C)
├── Executar analyze_results.py
├── Revisar results_table.csv
└── Exportar/compartilhar resultados
```

## 💾 Backup Recomendado

Periodicamente, faça backup de:
- `tests/automated_results/results_table.csv`
- `tests/automated_results/analysis_summary.json`
- `tests/automated_results/*.txt` (opcional)

## 📈 Expansões Futuras

Arquivos planejados para versões futuras:
- `plot_results.py` - Geração de gráficos
- `export_excel.py` - Exportação para Excel
- `web_monitor.py` - Interface web
- `email_notifier.py` - Notificações por email

## 🏁 Conclusão

Este sistema foi projetado para ser:
- ✅ **Completamente automatizado** - Roda sem intervenção
- ✅ **Robusto** - Lida com erros e timeouts
- ✅ **Documentado** - Documentação completa incluída
- ✅ **Extensível** - Fácil de adicionar novas funcionalidades
- ✅ **Monitorável** - Acompanhamento em tempo real

**Pronto para começar? Execute `python preflight_check.py`!**

---

**Última atualização:** 04/11/2025  
**Versão do sistema:** 1.0  
**Autor:** Sistema Automatizado

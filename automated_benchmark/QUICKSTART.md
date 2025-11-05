# 🚀 GUIA RÁPIDO DE INÍCIO

## Passo 1: Setup

Execute o menu interativo:
```powershell
.\benchmark_menu.bat
```

Escolha opção **1** (Setup inicial) para instalar dependências.

## Passo 2: Iniciar Benchmark

No menu, escolha opção **2** (Iniciar benchmark).

O sistema irá:
- ✅ Gerar dados aleatórios
- ✅ Testar todas as 6 configurações
- ✅ Salvar resultados automaticamente
- ✅ Repetir indefinidamente

**Para parar:** Pressione `Ctrl+C`

## Passo 3: Monitorar (Opcional)

Abra **outro terminal** e execute:
```powershell
python monitor_benchmark.py
```

Você verá estatísticas em tempo real atualizando a cada 10 segundos.

## Passo 4: Analisar Resultados

Quando quiser ver análises detalhadas:
```powershell
python analyze_results.py
```

---

## 📁 Onde Estão os Resultados?

```
tests/
└── automated_results/
    ├── results_table.csv          ← Tabela principal
    ├── analysis_summary.json      ← Resumo estatístico
    └── result_*.txt               ← Resultados individuais
```

---

## ⚙️ Ajustes Importantes

### Se o CPLEX estiver em outro local:

Edite `automated_benchmark.py`, linha ~30:
```python
OPLRUN_PATH = r"SEU_CAMINHO_AQUI\oplrun.exe"
```

### Para mudar limites:

Edite `automated_benchmark.py`, linhas 18-22:
```python
MAX_EXECUTION_TIME = 3600    # Tempo teórico
TIMEOUT_KILL = 4200         # Timeout real
MAX_N = 200                 # Máximo de pontos
MIN_COVERAGE_RANGE = (1, 5) # Range de cobertura
```

---

## 🔥 Atalhos Rápidos

| Comando | O que faz |
|---------|-----------|
| `python automated_benchmark.py` | Iniciar benchmark |
| `python monitor_benchmark.py` | Monitorar progresso |
| `python monitor_benchmark.py --latest 10` | Ver últimos 10 resultados |
| `python analyze_results.py` | Análise completa |
| `.\benchmark_menu.bat` | Menu interativo |

---

## 📊 Formato dos Dados Gerados

Cada teste gera:
- **n**: 5 a 200 clientes
- **r**: Calculado automaticamente baseado na distribuição
- **minCoverage**: 1 a 5 (aleatório)
- **minDistCirculos**: Proporcional ao raio

---

## ❓ Perguntas Frequentes

**P: Quanto tempo leva cada rodada completa?**  
R: Até ~7 horas (6 configs × 1h10min máx)

**P: Posso parar e retomar depois?**  
R: Sim! Os resultados são salvos continuamente. Ao retomar, novos testes serão adicionados.

**P: O que acontece se o PC desligar?**  
R: Todos os testes completos até o momento estarão salvos no CSV.

**P: Posso rodar vários benchmarks em paralelo?**  
R: Não recomendado - eles vão sobrescrever o mesmo `circle_coverage.dat`

**P: Como interpretar "Sem resultado"?**  
R: O teste excedeu o timeout de 1h10min sem encontrar solução.

---

## 🐛 Problemas Comuns

### "Module not found"
```powershell
pip install numpy psutil
```

### "oplrun não encontrado"
Ajuste o caminho em `automated_benchmark.py`

### Processo não termina no timeout
Execute como Administrador

---

## 📈 Exemplo de Saída

```
==================================================================================
INICIANDO Test_0001
==================================================================================

[1/3] Gerando dados de teste...
  - Pontos: 85
  - Raio: 18.5
  - Cobertura mínima: 3
  - Dist. mín. círculos: 2.15

[2/3] Escrevendo arquivo .dat...
  ✓ Arquivo atualizado

[3/3] Executando testes...

  [1/6] Testando Teste1...
      ✓ Concluído: 22 círculos em 345.67s

  [2/6] Testando Teste2...
      ✓ Concluído: 20 círculos em 128.45s

  ... (continua)
```

---

## 🎯 Dicas de Uso

1. **Deixe rodando overnight** para acumular muitos testes
2. **Use o monitor** para acompanhar sem interferir
3. **Analise periodicamente** para identificar tendências
4. **Faça backup** da pasta `automated_results` regularmente

---

**Pronto para começar? Execute `.\benchmark_menu.bat` e escolha opção 1!** 🚀

# 🤖 Sistema de Benchmark Automatizado

> **Nota:** Este sistema foi movido para melhor organização!

## 📁 Nova Localização

Todos os arquivos do sistema de benchmark foram movidos para:

```
automated_benchmark/
```

## 🚀 Como Usar

### Acesse a subpasta:
```powershell
cd automated_benchmark
```

### Depois execute:

**Opção 1 - Menu Interativo (Recomendado):**
```powershell
.\benchmark_menu.bat
```

**Opção 2 - Direto:**
```powershell
python automated_benchmark.py
```

## 📚 Documentação

Toda a documentação está em `automated_benchmark/`:

- **`README.md`** - Visão geral da subpasta
- **`QUICKSTART.md`** - Guia rápido de início
- **`BENCHMARK_README.md`** - Documentação técnica completa
- **`TROUBLESHOOTING.md`** - Soluções de problemas
- **`INDEX.md`** - Índice completo de arquivos

## 🎯 Atalho Rápido

Execute direto da raiz do projeto (sem entrar na pasta):

### Windows PowerShell:
```powershell
# Executar benchmark
python automated_benchmark\automated_benchmark.py

# Menu interativo
automated_benchmark\benchmark_menu.bat

# Monitorar
python automated_benchmark\monitor_benchmark.py

# Analisar
python automated_benchmark\analyze_results.py
```

## 📊 Resultados

Os resultados continuam sendo salvos em:
```
tests/automated_results/
```

## ⚙️ O que mudou?

- ✅ Todos os scripts Python movidos para `automated_benchmark/`
- ✅ Toda documentação movida para `automated_benchmark/`
- ✅ Arquivos .bat ajustados para nova estrutura
- ✅ Caminhos nos scripts ajustados automaticamente
- ✅ Tudo funciona perfeitamente da subpasta

## 🔧 Por que a mudança?

Para manter o projeto organizado:
- ✅ Separa sistema de benchmark dos modelos OPL
- ✅ Facilita manutenção e versionamento
- ✅ Evita poluir raiz do projeto
- ✅ Agrupa código relacionado

## 💡 Dica

Adicione aos seus favoritos:
```powershell
# Criar alias (PowerShell profile)
Set-Alias -Name benchmark -Value "automated_benchmark\automated_benchmark.py"
```

---

**Para começar:** `cd automated_benchmark` e leia o `README.md` lá!

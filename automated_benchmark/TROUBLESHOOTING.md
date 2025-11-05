# 🔧 TROUBLESHOOTING - Soluções para Problemas Comuns

## 🚨 Problemas de Instalação

### Erro: "Module 'numpy' not found"
**Solução:**
```powershell
pip install numpy
```

Se não funcionar:
```powershell
python -m pip install --upgrade pip
python -m pip install numpy
```

### Erro: "Module 'psutil' not found"
**Solução:**
```powershell
pip install psutil
```

**Nota:** psutil é opcional (usado apenas para afinidade de CPU)

---

## 🔴 Problemas com OPLRUN

### Erro: "oplrun não encontrado"
**Causa:** Caminho do CPLEX está incorreto

**Solução:**
1. Localize onde o CPLEX está instalado
2. Procure por `oplrun.exe`
3. Edite `automated_benchmark.py` (linha ~30):
```python
OPLRUN_PATH = r"C:\Seu\Caminho\Para\oplrun.exe"
```

**Caminhos comuns:**
- `C:\Program Files\IBM\ILOG\CPLEX_Studio2211\opl\bin\x64_win64\oplrun.exe`
- `C:\Program Files (x86)\IBM\ILOG\CPLEX_Studio2211\opl\bin\x64_win64\oplrun.exe`
- `C:\IBM\ILOG\CPLEX_Studio2211\opl\bin\x64_win64\oplrun.exe`

**Verificar:**
```powershell
dir "C:\Program Files\IBM\ILOG\" /s /b | findstr oplrun.exe
```

---

## ⏱️ Problemas de Timeout

### Processo não termina após timeout
**Causa:** Permissões insuficientes para matar processos

**Solução 1:** Executar como Administrador
- Clique direito no PowerShell → "Executar como Administrador"

**Solução 2:** Aumentar timeout
Edite `automated_benchmark.py`:
```python
TIMEOUT_KILL = 5400  # 1h30min
```

### Todos os testes dão timeout
**Causa:** Instâncias muito difíceis ou configuração inadequada

**Solução:** Reduzir complexidade temporariamente
```python
MAX_N = 50  # Reduzir de 200 para 50
MIN_COVERAGE_RANGE = (1, 2)  # Reduzir de (1,5) para (1,2)
```

---

## 💾 Problemas de Arquivo

### Erro: "Permission denied" ao escrever .dat
**Causa:** Arquivo está aberto em outro programa

**Solução:**
1. Feche o CPLEX IDE
2. Feche qualquer editor que tenha o arquivo aberto
3. Verifique no Gerenciador de Tarefas se há processos do CPLEX rodando

### Erro: "File not found: circle_coverage.dat"
**Causa:** Script não está na pasta correta

**Solução:**
Execute o script a partir da raiz do projeto:
```powershell
cd C:\Users\rocha\Documents\GitHub\circlecoverageopl
python automated_benchmark.py
```

### Pasta de resultados não é criada
**Causa:** Permissões de escrita

**Solução:**
```powershell
mkdir tests\automated_results
icacls tests\automated_results /grant Everyone:(OI)(CI)F
```

---

## 📊 Problemas de Resultados

### CSV vazio ou sem dados
**Causa:** Nenhum teste foi concluído

**Verificar:**
1. Olhe os arquivos individuais: `tests\automated_results\result_*.txt`
2. Verifique se há timeouts nos logs
3. Reduza complexidade das instâncias

### Números de círculos não aparecem
**Causa:** Parser não está reconhecendo a saída

**Solução:** Edite `extract_num_circles()` em `automated_benchmark.py`

Adicione prints para debug:
```python
def extract_num_circles(output):
    print("DEBUG: Output recebido:")
    print(output[:500])  # Primeiros 500 chars
    # ... resto do código
```

### Monitor não atualiza
**Causa:** CSV não está sendo escrito

**Verificar:**
```powershell
dir tests\automated_results\results_table.csv
```

Se não existir, verifique logs do benchmark.

---

## 🖥️ Problemas de Desempenho

### PC ficando lento durante execução
**Causa:** Todos os núcleos sendo usados

**Solução 1:** Verificar se psutil está instalado
```powershell
pip install psutil
```

**Solução 2:** Configurar afinidade manualmente

No Gerenciador de Tarefas:
1. Detalhes → oplrun.exe
2. Clique direito → Definir afinidade
3. Desmarque um núcleo

### Memória enchendo
**Causa:** Muitos resultados acumulados

**Solução:**
Periodicamente, mova resultados antigos:
```powershell
mkdir tests\archived_results
move tests\automated_results\result_* tests\archived_results\
```

---

## 🔄 Problemas de Execução

### Script para inesperadamente
**Debug:**
Adicione logs detalhados editando o início de `main_loop()`:
```python
import logging
logging.basicConfig(
    filename='benchmark_debug.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

### Configuração não é encontrada
**Causa:** Nome da configuração no .oplproject está diferente

**Verificar:**
Abra `.oplproject` e veja os nomes exatos das configurações.

Edite `TEST_CONFIGS` em `automated_benchmark.py`:
```python
TEST_CONFIGS = [
    "NomeExatoDaConfig1",
    "NomeExatoDaConfig2",
    # ...
]
```

---

## 🐍 Problemas com Python

### "python" não é reconhecido
**Solução:**
Use `python3` ou `py`:
```powershell
py automated_benchmark.py
```

### Versão errada do Python
**Verificar:**
```powershell
python --version
```

Requerido: Python 3.6+

**Usar versão específica:**
```powershell
py -3.9 automated_benchmark.py
```

---

## 🔥 Emergência: Como Parar Tudo

### Método 1: Ctrl+C
Pressione `Ctrl+C` no terminal

### Método 2: Gerenciador de Tarefas
1. Abrir Gerenciador de Tarefas (Ctrl+Shift+Esc)
2. Detalhes
3. Procurar por `python.exe` e `oplrun.exe`
4. Finalizar tarefa

### Método 3: PowerShell
```powershell
taskkill /F /IM python.exe
taskkill /F /IM oplrun.exe
```

---

## 📝 Logs e Debug

### Habilitar logs detalhados
Edite `automated_benchmark.py`, adicione no início de `main_loop()`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Salvar logs em arquivo
```python
import logging
logging.basicConfig(
    filename='benchmark.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
```

### Ver o que está sendo executado
Adicione prints:
```python
print(f"Executando comando: {cmd}")
print(f"Diretório: {os.getcwd()}")
```

---

## 🆘 Ainda com Problemas?

### Teste Sistema Básico
```powershell
python test_system.py
```

Este script verificará:
- ✓ Imports
- ✓ OPLRUN
- ✓ Arquivos do projeto
- ✓ Geração de dados
- ✓ Execução básica

### Informações para Debug
Execute e salve a saída:
```powershell
python test_system.py > debug_info.txt 2>&1
```

### Teste Manual
Tente executar manualmente:
```powershell
cd C:\Users\rocha\Documents\GitHub\circlecoverageopl
"C:\Program Files\IBM\ILOG\CPLEX_Studio2211\opl\bin\x64_win64\oplrun.exe" -p . Teste1
```

Se funcionar, o problema está no script Python.

---

## 📞 Checklist de Verificação

Antes de pedir ajuda, verifique:

- [ ] Python 3.6+ instalado
- [ ] numpy e psutil instalados (`pip list`)
- [ ] OPLRUN acessível (teste manual)
- [ ] Arquivo circle_coverage.dat existe
- [ ] Arquivo .oplproject existe
- [ ] Configurações Teste1-6 estão no .oplproject
- [ ] Executando a partir da raiz do projeto
- [ ] Permissões de escrita na pasta tests/
- [ ] Nenhum processo do CPLEX travado
- [ ] Espaço em disco suficiente

---

## 💡 Dicas de Prevenção

1. **Sempre execute a partir da raiz do projeto**
2. **Feche o CPLEX IDE durante execução**
3. **Não edite arquivos enquanto o benchmark roda**
4. **Faça backup dos resultados periodicamente**
5. **Monitore espaço em disco**
6. **Use o test_system.py antes de rodadas longas**

---

## 🎯 Erros Conhecidos e Soluções

| Erro | Causa | Solução |
|------|-------|---------|
| "Access denied" | Sem permissão admin | Executar como Admin |
| "Module not found" | Biblioteca não instalada | `pip install <lib>` |
| "File in use" | Arquivo aberto | Fechar editores |
| "Timeout expired" | Instância difícil | Normal, próximo teste |
| "Invalid path" | Caminho do CPLEX errado | Ajustar OPLRUN_PATH |

---

**Última atualização:** 04/11/2025

Para mais ajuda, verifique os logs e a saída do `test_system.py`.

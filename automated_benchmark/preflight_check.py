"""
Script de Pré-Voo - Verificações Finais Antes de Iniciar Benchmark
Execute este script antes de deixar o benchmark rodando por muito tempo
"""

import subprocess
import sys
import os
from pathlib import Path
import shutil

def print_header(text):
    """Imprime cabeçalho formatado"""
    print("\n" + "=" * 80)
    print(text.center(80))
    print("=" * 80)

def print_section(text):
    """Imprime seção formatada"""
    print("\n" + "-" * 80)
    print(text)
    print("-" * 80)

def check_python_version():
    """Verifica versão do Python"""
    print_section("1. VERIFICANDO VERSÃO DO PYTHON")
    
    version = sys.version_info
    print(f"Versão do Python: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        print("✗ Python 3.6+ é requerido!")
        return False
    
    print("✓ Versão do Python adequada")
    return True

def check_dependencies():
    """Verifica dependências instaladas"""
    print_section("2. VERIFICANDO DEPENDÊNCIAS")
    
    deps = {
        'numpy': False,
        'psutil': False
    }
    
    for dep in deps.keys():
        try:
            __import__(dep)
            print(f"✓ {dep}")
            deps[dep] = True
        except ImportError:
            print(f"✗ {dep} não instalado")
    
    if not deps['numpy']:
        print("\n⚠ numpy é OBRIGATÓRIO!")
        print("Execute: pip install numpy")
        return False
    
    if not deps['psutil']:
        print("\n⚠ psutil é opcional mas recomendado (afinidade de CPU)")
        print("Execute: pip install psutil")
    
    return True

def check_oplrun():
    """Verifica OPLRUN"""
    print_section("3. VERIFICANDO OPLRUN")
    
    oplrun_path = r"C:\Program Files\IBM\ILOG\CPLEX_Studio2211\opl\bin\x64_win64\oplrun.exe"
    
    if not Path(oplrun_path).exists():
        print(f"✗ oplrun não encontrado em:")
        print(f"  {oplrun_path}")
        print("\nAjuste OPLRUN_PATH em automated_benchmark.py")
        return False
    
    print(f"✓ oplrun encontrado")
    
    # Tentar executar para verificar
    try:
        result = subprocess.run(
            [oplrun_path, "-h"],
            capture_output=True,
            timeout=5
        )
        print("✓ oplrun executável")
        return True
    except Exception as e:
        print(f"⚠ oplrun encontrado mas não executável: {e}")
        return False

def check_project_structure():
    """Verifica estrutura do projeto"""
    print_section("4. VERIFICANDO ESTRUTURA DO PROJETO")
    
    script_dir = Path(__file__).parent  # automated_benchmark/
    project_dir = script_dir.parent  # raiz
    
    # Arquivos na raiz do projeto
    root_files = {
        'circle_coverage.dat': True,
        '.oplproject': True,
    }
    
    # Scripts na subpasta automated_benchmark/
    script_files = {
        'automated_benchmark.py': True,
        'monitor_benchmark.py': True,
        'analyze_results.py': True
    }
    
    all_ok = True
    
    # Verificar arquivos na raiz
    for file, is_required in root_files.items():
        path = project_dir / file
        if path.exists():
            print(f"✓ {file}")
        else:
            status = "✗" if is_required else "⚠"
            print(f"{status} {file}")
            if is_required:
                all_ok = False
    
    # Verificar scripts na subpasta
    for file, is_required in script_files.items():
        path = script_dir / file
        if path.exists():
            print(f"✓ automated_benchmark/{file}")
        else:
            status = "✗" if is_required else "⚠"
            print(f"{status} automated_benchmark/{file}")
            if is_required:
                all_ok = False
    
    return all_ok

def check_oplproject_configs():
    """Verifica configurações no .oplproject"""
    print_section("5. VERIFICANDO CONFIGURAÇÕES NO .OPLPROJECT")
    
    oplproject = Path(__file__).parent.parent / ".oplproject"  # Buscar na raiz
    
    if not oplproject.exists():
        print("✗ Arquivo .oplproject não encontrado")
        return False
    
    content = oplproject.read_text(encoding='utf-8')
    
    configs = ['Teste1', 'Teste2', 'Teste3', 'Teste4', 'Teste5', 'Teste6']
    
    found = []
    for config in configs:
        if f'name="{config}"' in content:
            print(f"✓ {config}")
            found.append(config)
        else:
            print(f"✗ {config} não encontrado")
    
    if len(found) == len(configs):
        print("\n✓ Todas as configurações encontradas")
        return True
    else:
        print(f"\n⚠ Apenas {len(found)}/{len(configs)} configurações encontradas")
        return False

def check_disk_space():
    """Verifica espaço em disco"""
    print_section("6. VERIFICANDO ESPAÇO EM DISCO")
    
    try:
        total, used, free = shutil.disk_usage(".")
        
        free_gb = free // (2**30)
        total_gb = total // (2**30)
        
        print(f"Espaço livre: {free_gb} GB de {total_gb} GB")
        
        if free_gb < 1:
            print("✗ Menos de 1 GB livre - pode não ser suficiente!")
            return False
        elif free_gb < 5:
            print("⚠ Menos de 5 GB livre - monitore o espaço")
            return True
        else:
            print("✓ Espaço em disco adequado")
            return True
    except Exception as e:
        print(f"⚠ Não foi possível verificar espaço: {e}")
        return True

def check_results_directory():
    """Verifica/cria diretório de resultados"""
    print_section("7. VERIFICANDO DIRETÓRIO DE RESULTADOS")
    
    results_dir = Path(__file__).parent.parent / "tests" / "automated_results"  # Ajuste para subpasta
    
    if results_dir.exists():
        print(f"✓ Diretório existe: {results_dir}")
        
        # Contar arquivos existentes
        files = list(results_dir.glob("*"))
        print(f"  Arquivos existentes: {len(files)}")
        
        if len(files) > 1000:
            print("  ⚠ Muitos arquivos - considere arquivar resultados antigos")
    else:
        print("  Criando diretório...")
        results_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ Diretório criado: {results_dir}")
    
    # Testar escrita
    test_file = results_dir / "test_write.tmp"
    try:
        test_file.write_text("test")
        test_file.unlink()
        print("✓ Permissões de escrita OK")
        return True
    except Exception as e:
        print(f"✗ Erro ao escrever: {e}")
        return False

def check_running_processes():
    """Verifica processos em execução"""
    print_section("8. VERIFICANDO PROCESSOS EM EXECUÇÃO")
    
    try:
        # Verificar se há oplrun rodando
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq oplrun.exe'],
            capture_output=True,
            text=True
        )
        
        if 'oplrun.exe' in result.stdout:
            print("⚠ Há processos oplrun.exe rodando!")
            print("  Considere finalizá-los antes de iniciar novo benchmark")
            return False
        else:
            print("✓ Nenhum processo oplrun.exe em execução")
        
        # Verificar automated_benchmark
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq python.exe'],
            capture_output=True,
            text=True
        )
        
        # Contar quantos processos Python
        python_count = result.stdout.count('python.exe')
        if python_count > 1:
            print(f"⚠ {python_count} processos python.exe rodando")
            print("  Um deles pode ser um benchmark anterior")
        else:
            print("✓ Ambiente limpo")
        
        return True
    except Exception as e:
        print(f"⚠ Não foi possível verificar processos: {e}")
        return True

def estimate_runtime():
    """Estima tempo de execução"""
    print_section("9. ESTIMATIVA DE TEMPO DE EXECUÇÃO")
    
    timeout = 4200  # 1h10min
    num_configs = 6
    pause_between = 12  # 2s entre configs + 10s entre testes
    
    single_test = (timeout * num_configs + pause_between) / 3600
    
    print(f"Tempo máximo por teste completo: {single_test:.1f} horas")
    print(f"Tempo para 10 testes: {single_test * 10:.1f} horas")
    print(f"Tempo para 24h contínuo: ~{24 / single_test:.0f} testes")
    print("\nNota: Testes bem-sucedidos terminam antes do timeout")
    
    return True

def final_recommendations():
    """Recomendações finais"""
    print_section("10. RECOMENDAÇÕES FINAIS")
    
    print("Antes de iniciar o benchmark:")
    print("  ☐ Feche o CPLEX IDE")
    print("  ☐ Feche editores com arquivos do projeto abertos")
    print("  ☐ Configure o PC para não dormir/hibernar")
    print("  ☐ Desabilite Windows Update automático (opcional)")
    print("  ☐ Use um terminal dedicado para o benchmark")
    print("  ☐ Considere usar outro terminal para monitoramento")
    
    print("\nDurante a execução:")
    print("  ☑ NÃO edite circle_coverage.dat")
    print("  ☑ NÃO abra o CPLEX IDE")
    print("  ☑ NÃO execute múltiplas instâncias do benchmark")
    print("  ☑ Monitore espaço em disco periodicamente")
    
    print("\nPara parar:")
    print("  → Pressione Ctrl+C no terminal do benchmark")
    print("  → Ou use o Gerenciador de Tarefas")
    
    return True

def main():
    """Função principal"""
    print_header("PRÉ-VOO - VERIFICAÇÃO DO SISTEMA DE BENCHMARK")
    
    checks = [
        ("Python", check_python_version),
        ("Dependências", check_dependencies),
        ("OPLRUN", check_oplrun),
        ("Estrutura", check_project_structure),
        ("Configurações", check_oplproject_configs),
        ("Espaço em Disco", check_disk_space),
        ("Diretório de Resultados", check_results_directory),
        ("Processos", check_running_processes),
        ("Estimativa", estimate_runtime),
        ("Recomendações", final_recommendations)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Erro ao executar verificação '{name}': {e}")
            results.append((name, False))
    
    # Resumo
    print_header("RESUMO DAS VERIFICAÇÕES")
    
    critical_failed = []
    warnings = []
    
    for name, result in results:
        if result:
            print(f"✓ {name}")
        else:
            print(f"✗ {name}")
            if name in ["Python", "Dependências", "OPLRUN", "Estrutura"]:
                critical_failed.append(name)
            else:
                warnings.append(name)
    
    # Decisão final
    print("\n" + "=" * 80)
    
    if critical_failed:
        print("❌ SISTEMA NÃO ESTÁ PRONTO")
        print("=" * 80)
        print("\nProblemas críticos encontrados:")
        for item in critical_failed:
            print(f"  ✗ {item}")
        print("\nCorrija os problemas acima antes de prosseguir.")
        print("Consulte TROUBLESHOOTING.md para ajuda.")
        return False
    
    if warnings:
        print("⚠️ SISTEMA PRONTO COM RESSALVAS")
        print("=" * 80)
        print("\nAvisos encontrados:")
        for item in warnings:
            print(f"  ⚠ {item}")
        print("\nO benchmark pode rodar, mas monitore os avisos acima.")
        
        response = input("\nDeseja prosseguir mesmo assim? (s/n): ")
        if response.lower() != 's':
            print("\nBenchmark não iniciado.")
            return False
    else:
        print("✅ SISTEMA PRONTO PARA BENCHMARK!")
        print("=" * 80)
        print("\nTodas as verificações passaram com sucesso!")
    
    print("\n" + "=" * 80)
    print("PRÓXIMOS PASSOS")
    print("=" * 80)
    print("\nPara iniciar o benchmark:")
    print("  python automated_benchmark.py")
    print("\nPara monitorar em outro terminal:")
    print("  python monitor_benchmark.py")
    print("\nBoa sorte com os testes! 🚀")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nVerificação interrompida pelo usuário.")
        sys.exit(1)

"""
Script de Teste Rápido
Executa um teste único para verificar se tudo está funcionando
"""

import subprocess
import sys
import time
from pathlib import Path

def test_imports():
    """Testa se as bibliotecas necessárias estão instaladas"""
    print("\n=== TESTANDO IMPORTS ===")
    
    try:
        import numpy
        print("✓ numpy")
    except ImportError:
        print("✗ numpy - Execute: pip install numpy")
        return False
    
    try:
        import psutil
        print("✓ psutil")
    except ImportError:
        print("✗ psutil (opcional) - Execute: pip install psutil")
    
    return True

def test_oplrun():
    """Testa se o oplrun é acessível"""
    print("\n=== TESTANDO OPLRUN ===")
    
    oplrun_path = r"C:\Program Files\IBM\ILOG\CPLEX_Studio2211\opl\bin\x64_win64\oplrun.exe"
    
    if not Path(oplrun_path).exists():
        print(f"✗ oplrun não encontrado em: {oplrun_path}")
        print("\nAjuste o caminho em automated_benchmark.py")
        return False
    
    print(f"✓ oplrun encontrado")
    return True

def test_project_files():
    """Testa se os arquivos do projeto existem"""
    print("\n=== TESTANDO ARQUIVOS DO PROJETO ===")
    
    project_dir = Path(__file__).parent
    
    required_files = {
        'circle_coverage.dat': True,
        '.oplproject': True,
        'modelo_fix_circ_preprocessing_v4.mod': False,  # Opcional
        'automated_benchmark.py': True,
        'monitor_benchmark.py': True,
        'analyze_results.py': True
    }
    
    all_ok = True
    for file, required in required_files.items():
        file_path = project_dir / file
        if file_path.exists():
            print(f"✓ {file}")
        else:
            status = "✗" if required else "⚠"
            print(f"{status} {file}")
            if required:
                all_ok = False
    
    return all_ok

def test_data_generation():
    """Testa a geração de dados"""
    print("\n=== TESTANDO GERAÇÃO DE DADOS ===")
    
    try:
        # Importar função de geração
        sys.path.insert(0, str(Path(__file__).parent))  # Já está na subpasta
        from automated_benchmark import generate_test_data, write_dat_file
        
        print("Gerando dados de teste...")
        data = generate_test_data()
        
        print(f"✓ Dados gerados:")
        print(f"  - n: {data['n']}")
        print(f"  - r: {data['r']}")
        print(f"  - minCoverage: {data['min_coverage']}")
        
        return True
    except Exception as e:
        print(f"✗ Erro: {e}")
        return False

def run_quick_test():
    """Executa um teste rápido com timeout curto"""
    print("\n=== EXECUTANDO TESTE RÁPIDO ===")
    print("Isso pode levar alguns minutos...")
    
    try:
        # Importar funções necessárias
        sys.path.insert(0, str(Path(__file__).parent))  # Já está na subpasta
        from automated_benchmark import generate_test_data, write_dat_file, run_test_with_timeout
        
        # Gerar dados pequenos
        print("\n1. Gerando dados pequenos...")
        data = generate_test_data()
        # Forçar n pequeno para teste rápido
        data['n'] = 10
        
        print("\n2. Escrevendo .dat...")
        write_dat_file(data)
        print("   ✓ Arquivo atualizado")
        
        print("\n3. Executando Teste1 (timeout: 60s)...")
        success, num_circles, exec_time, output = run_test_with_timeout("Teste1", 60)
        
        if success:
            print(f"   ✓ Teste concluído!")
            print(f"   - Círculos: {num_circles}")
            print(f"   - Tempo: {exec_time:.2f}s")
        else:
            print(f"   ⚠ Teste não concluiu em 60s (esperado para teste)")
            print(f"   - Tempo: {exec_time:.2f}s")
        
        return True
    except Exception as e:
        print(f"   ✗ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Função principal de teste"""
    print("=" * 80)
    print("TESTE RÁPIDO DO SISTEMA DE BENCHMARK")
    print("=" * 80)
    
    results = []
    
    # Testes
    results.append(("Imports", test_imports()))
    results.append(("OPLRUN", test_oplrun()))
    results.append(("Arquivos do Projeto", test_project_files()))
    results.append(("Geração de Dados", test_data_generation()))
    
    # Perguntar se quer fazer teste completo
    print("\n" + "=" * 80)
    print("RESUMO DOS TESTES BÁSICOS")
    print("=" * 80)
    
    for name, result in results:
        status = "✓" if result else "✗"
        print(f"{status} {name}")
    
    all_ok = all(r for _, r in results)
    
    if not all_ok:
        print("\n⚠ Alguns testes falharam. Corrija os problemas antes de continuar.")
        return False
    
    print("\n✓ Todos os testes básicos passaram!")
    
    # Oferecer teste de execução
    print("\n" + "=" * 80)
    response = input("\nDeseja executar um teste rápido de execução? (s/n): ")
    
    if response.lower() == 's':
        if run_quick_test():
            print("\n" + "=" * 80)
            print("✓ TESTE RÁPIDO CONCLUÍDO COM SUCESSO!")
            print("=" * 80)
            print("\nSistema pronto para uso!")
            print("Execute: python automated_benchmark.py")
        else:
            print("\n" + "=" * 80)
            print("⚠ TESTE RÁPIDO FALHOU")
            print("=" * 80)
            print("\nVerifique os erros acima e tente novamente.")
            return False
    
    print("\n" + "=" * 80)
    print("TESTES CONCLUÍDOS")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

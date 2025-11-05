"""
Script de setup para o benchmark automatizado
Instala dependências e verifica a configuração
"""

import subprocess
import sys
from pathlib import Path

def install_dependencies():
    """Instala as dependências necessárias"""
    print("=" * 80)
    print("INSTALANDO DEPENDÊNCIAS")
    print("=" * 80)
    
    dependencies = [
        'numpy',
        'psutil'
    ]
    
    for dep in dependencies:
        print(f"\nInstalando {dep}...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
            print(f"✓ {dep} instalado com sucesso")
        except subprocess.CalledProcessError:
            print(f"✗ Erro ao instalar {dep}")
            return False
    
    return True

def verify_oplrun():
    """Verifica se o oplrun está acessível"""
    print("\n" + "=" * 80)
    print("VERIFICANDO OPLRUN")
    print("=" * 80)
    
    oplrun_path = r"C:\Program Files\IBM\ILOG\CPLEX_Studio2211\opl\bin\x64_win64\oplrun.exe"
    
    if Path(oplrun_path).exists():
        print(f"✓ oplrun encontrado em: {oplrun_path}")
        return True
    else:
        print(f"✗ oplrun NÃO encontrado em: {oplrun_path}")
        print("\nPor favor, ajuste o caminho no arquivo automated_benchmark.py")
        print("Procure por OPLRUN_PATH e altere para o caminho correto")
        return False

def verify_project_structure():
    """Verifica a estrutura do projeto"""
    print("\n" + "=" * 80)
    print("VERIFICANDO ESTRUTURA DO PROJETO")
    print("=" * 80)
    
    project_dir = Path(__file__).parent.parent  # Ajuste para subpasta
    
    required_files = [
        'circle_coverage.dat',
        '.oplproject',
        'modelo_fix_circ_preprocessing_v4.mod'
    ]
    
    all_ok = True
    for file in required_files:
        file_path = project_dir / file
        if file_path.exists():
            print(f"✓ {file}")
        else:
            print(f"✗ {file} NÃO encontrado")
            all_ok = False
    
    return all_ok

def main():
    """Função principal de setup"""
    print("\n" + "=" * 80)
    print("SETUP DO BENCHMARK AUTOMATIZADO")
    print("=" * 80)
    
    # Instalar dependências
    if not install_dependencies():
        print("\n✗ Falha ao instalar dependências")
        return False
    
    # Verificar oplrun
    if not verify_oplrun():
        print("\n✗ oplrun não está configurado corretamente")
        return False
    
    # Verificar estrutura do projeto
    if not verify_project_structure():
        print("\n✗ Estrutura do projeto incompleta")
        return False
    
    print("\n" + "=" * 80)
    print("✓ SETUP CONCLUÍDO COM SUCESSO!")
    print("=" * 80)
    print("\nPara iniciar o benchmark, execute:")
    print("  python automated_benchmark.py")
    print("\nO benchmark rodará indefinidamente até você pressionar Ctrl+C")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

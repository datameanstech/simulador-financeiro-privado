#!/usr/bin/env python3
"""
🔍 Script de verificação para deploy
Verifica se todos os arquivos necessários estão presentes
"""

import os
import sys
from pathlib import Path

def check_file(filename, required=True):
    """Verifica se um arquivo existe"""
    exists = os.path.exists(filename)
    status = "✅" if exists else ("❌" if required else "⚠️")
    print(f"{status} {filename}")
    return exists

def check_file_size(filename, max_mb=250):
    """Verifica tamanho do arquivo"""
    if os.path.exists(filename):
        size_mb = os.path.getsize(filename) / (1024 * 1024)
        if size_mb > max_mb:
            print(f"⚠️  {filename} é muito grande ({size_mb:.1f}MB > {max_mb}MB)")
            return False
        else:
            print(f"✅ {filename} tamanho OK ({size_mb:.1f}MB)")
            return True
    return False

def main():
    print("🚀 VERIFICAÇÃO DE DEPLOY - Simulador Financeiro")
    print("=" * 50)
    
    # Arquivos essenciais
    print("\n📁 Arquivos essenciais:")
    essential_files = [
        ("app.py", True),
        ("requirements.txt", True),
        ("Procfile", True),
        ("render.yaml", False),
        ("railway.json", False),
    ]
    
    all_essential = True
    for filename, required in essential_files:
        if not check_file(filename, required) and required:
            all_essential = False
    
    # Templates
    print("\n🎨 Templates:")
    template_files = [
        "templates/base.html",
        "templates/dashboard.html",
        "templates/login.html",
        "templates/home.html"
    ]
    
    all_templates = True
    for template in template_files:
        if not check_file(template):
            all_templates = False
    
    # Dados
    print("\n📊 Arquivos de dados:")
    data_files = [
        "dados_grandes_litigantes.parquet",
        "tabela_cnae_classe_subclasse.csv"
    ]
    
    data_ok = True
    for data_file in data_files:
        if not check_file(data_file):
            data_ok = False
        else:
            check_file_size(data_file)
    
    # Verificar requirements.txt
    print("\n📦 Dependências:")
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r") as f:
            content = f.read()
            required_deps = ["flask", "polars", "gunicorn"]
            for dep in required_deps:
                if dep in content.lower():
                    print(f"✅ {dep}")
                else:
                    print(f"❌ {dep} não encontrado em requirements.txt")
                    all_essential = False
    
    # Verificar estrutura de diretórios
    print("\n📂 Estrutura:")
    check_file("templates/", True)
    check_file("static/", False)
    
    # Resultado final
    print("\n" + "=" * 50)
    print("📋 RESUMO:")
    
    if all_essential and all_templates and data_ok:
        print("🎉 ✅ PRONTO PARA DEPLOY!")
        print("\n🚀 Próximos passos:")
        print("1. Fazer commit de todas as mudanças")
        print("2. Push para GitHub")
        print("3. Escolher plataforma de deploy (ver DEPLOY.md)")
        print("4. Configurar variáveis de ambiente")
        print("\n💡 Recomendação: Render.com (gratuito e fácil)")
    else:
        print("❌ AINDA NÃO ESTÁ PRONTO")
        print("\n🔧 Corrija os problemas acima antes do deploy")
        
    print("\n📖 Ver DEPLOY.md para instruções completas")

if __name__ == "__main__":
    main() 
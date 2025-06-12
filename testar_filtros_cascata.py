#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para demonstrar os filtros cascateados funcionando
"""

import subprocess
import time
import threading
import os
import sys

def iniciar_servidor():
    """Inicia o servidor Flask em uma thread separada"""
    print("🚀 Iniciando servidor Flask...")
    
    # Configurar ambiente
    env = os.environ.copy()
    env['FLASK_ENV'] = 'development'
    env['FLASK_DEBUG'] = '0'  # Desabilitar debug para teste
    
    try:
        # Iniciar servidor
        processo = subprocess.Popen(
            [sys.executable, 'app.py'], 
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("⏳ Aguardando servidor inicializar...")
        time.sleep(10)  # Aguardar inicialização
        
        return processo
        
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        return None

def main():
    print("🔧 DEMONSTRAÇÃO - FILTROS CASCATEADOS")
    print("=" * 50)
    
    # Iniciar servidor
    servidor = iniciar_servidor()
    
    if not servidor:
        print("❌ Não foi possível iniciar o servidor")
        return
    
    try:
        # Aguardar um pouco mais
        print("⏳ Aguardando carregamento dos dados...")
        time.sleep(5)
        
        # Executar testes
        print("\n🧪 Executando testes dos filtros...")
        from teste_filtros_cascateados_novo import testar_filtros_cascateados
        testar_filtros_cascateados()
        
        print("\n🌐 COMO TESTAR MANUALMENTE:")
        print("1. Abra seu navegador")
        print("2. Vá para: http://127.0.0.1:5000")
        print("3. Faça login (admin/123)")
        print("4. Aguarde os dados carregarem")
        print("5. Teste os filtros cascateados:")
        print("   - Selecione um tribunal")
        print("   - Veja como os outros filtros se atualizam automaticamente")
        print("   - Use Ctrl+clique para múltipla seleção")
        print("   - Cada mudança atualiza as opções disponíveis")
        
        print("\n⏱️ Servidor rodando. Pressione Ctrl+C para parar...")
        
        # Manter servidor rodando
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Parando servidor...")
    finally:
        if servidor:
            servidor.terminate()
            servidor.wait()
        print("✅ Servidor parado")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time

def verificar_servidor():
    """Verifica se o servidor está funcionando e dados carregados"""
    
    base_url = "http://127.0.0.1:5000"
    
    print("🔍 VERIFICAÇÃO DO SERVIDOR")
    print("=" * 40)
    
    with requests.Session() as session:
        try:
            # 1. Verificar se servidor responde
            print("1. Testando conexão...")
            response = session.get(base_url)
            if response.status_code == 200:
                print("✅ Servidor respondendo")
            else:
                print(f"❌ Erro HTTP: {response.status_code}")
                return False
                
            # 2. Fazer login
            print("2. Fazendo login...")
            login_data = {
                'username': 'admin',
                'password': '123'
            }
            
            login_response = session.post(f"{base_url}/login", data=login_data)
            if login_response.status_code == 200:
                print("✅ Login realizado")
            else:
                print(f"❌ Erro no login: {login_response.status_code}")
                return False
            
            # 3. Verificar dashboard
            print("3. Acessando dashboard...")
            dashboard_response = session.get(f"{base_url}/dashboard")
            if dashboard_response.status_code == 200:
                print("✅ Dashboard acessível")
            else:
                print(f"❌ Erro no dashboard: {dashboard_response.status_code}")
                return False
                
            # 4. Aguardar carregamento dos dados
            print("4. Aguardando dados carregarem...")
            for i in range(30):  # Tentar por 30 segundos
                try:
                    filtros_response = session.get(f"{base_url}/api/filtros", timeout=2)
                    if filtros_response.status_code == 200:
                        filtros_data = filtros_response.json()
                        if filtros_data.get('success') and filtros_data.get('filtros'):
                            print("✅ Dados carregados com sucesso!")
                            f = filtros_data['filtros']
                            print(f"   - Tribunais: {len(f.get('tribunais', []))}")
                            print(f"   - Graus: {len(f.get('graus', []))}")
                            print(f"   - Segmentos: {len(f.get('segmentos', []))}")
                            print(f"   - Ramos: {len(f.get('ramos', []))}")
                            
                            # 5. Testar filtros cascateados
                            print("\n5. Testando filtros cascateados...")
                            cascata_response = session.post(f"{base_url}/api/filtros-disponiveis", 
                                json={"filtros": {}}, timeout=5)
                            
                            if cascata_response.status_code == 200:
                                cascata_data = cascata_response.json()
                                if cascata_data.get('success'):
                                    print("✅ Filtros cascateados funcionando!")
                                    print(f"   Total registros: {cascata_data.get('total_registros', 'N/A')}")
                                    return True
                            
                            print("⚠️ Filtros cascateados com problema")
                            return False
                            
                except Exception as e:
                    print(f"   ⏳ Aguardando... ({i+1}/30) - {e}")
                    time.sleep(1)
                    continue
            
            print("❌ Timeout - dados não carregaram em 30 segundos")
            return False
            
        except Exception as e:
            print(f"❌ Erro geral: {e}")
            return False

if __name__ == "__main__":
    if verificar_servidor():
        print("\n🎉 SERVIDOR FUNCIONANDO PERFEITAMENTE!")
        print("🌐 Acesse: http://127.0.0.1:5000")
        print("👤 Login: admin / 123")
        print("🔄 Filtros cascateados estão funcionando!")
    else:
        print("\n❌ Problemas encontrados no servidor") 
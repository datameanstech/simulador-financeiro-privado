#!/usr/bin/env python3
"""
Teste da API de filtros cascateados
"""

import requests
import json

def test_filtros_cascateados():
    print("🧪 Testando API de filtros cascateados...")
    
    # URL da API
    base_url = "http://127.0.0.1:5000"
    
    # Fazer login primeiro
    session = requests.Session()
    
    login_data = {
        'username': 'admin',
        'password': 'pdpj2024'
    }
    
    try:
        # Login
        login_response = session.post(f"{base_url}/login", data=login_data)
        print(f"🔐 Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            
            # Carregar dados primeiro
            print("📁 Carregando dados...")
            carregar_response = session.post(f"{base_url}/api/carregar-dados", json={})
            print(f"📊 Carregar dados Status: {carregar_response.status_code}")
            
            # Aguardar carregamento
            import time
            time.sleep(5)
            
            # Teste 1: Filtros iniciais (sem filtros)
            print("\n🔍 Teste 1: Filtros iniciais (todos disponíveis)")
            filtros_iniciais = session.post(f"{base_url}/api/filtros-disponiveis", json={
                "filtros": {}
            })
            
            if filtros_iniciais.status_code == 200:
                data = filtros_iniciais.json()
                print(f"✅ Total registros iniciais: {data.get('total_registros', 'N/A')}")
                
                filtros = data.get('filtros_disponiveis', {})
                print(f"   - Tribunais: {len(filtros.get('tribunais', []))}")
                print(f"   - Graus: {len(filtros.get('graus', []))}")
                print(f"   - Segmentos: {len(filtros.get('segmentos', []))}")
                print(f"   - Ramos: {len(filtros.get('ramos', []))}")
                print(f"   - CNAEs: {len(filtros.get('cnaes', []))}")
                
                # Teste 2: Filtro com 1 tribunal
                if filtros.get('tribunais') and len(filtros['tribunais']) > 0:
                    primeiro_tribunal = filtros['tribunais'][0]
                    print(f"\n🔍 Teste 2: Filtrando por tribunal '{primeiro_tribunal}'")
                    
                    filtros_tribunal = session.post(f"{base_url}/api/filtros-disponiveis", json={
                        "filtros": {
                            "tribunais": [primeiro_tribunal]
                        }
                    })
                    
                    if filtros_tribunal.status_code == 200:
                        data_tribunal = filtros_tribunal.json()
                        print(f"✅ Registros após filtro tribunal: {data_tribunal.get('total_registros', 'N/A')}")
                        
                        filtros_trib = data_tribunal.get('filtros_disponiveis', {})
                        print(f"   - Tribunais disponíveis: {len(filtros_trib.get('tribunais', []))}")
                        print(f"   - Graus disponíveis: {len(filtros_trib.get('graus', []))}")
                        print(f"   - Segmentos disponíveis: {len(filtros_trib.get('segmentos', []))}")
                        print(f"   - CNAEs disponíveis: {len(filtros_trib.get('cnaes', []))}")
                        
                        # Teste 3: Adicionando filtro de segmento
                        if filtros_trib.get('segmentos') and len(filtros_trib['segmentos']) > 0:
                            primeiro_segmento = filtros_trib['segmentos'][0]
                            print(f"\n🔍 Teste 3: Adicionando segmento '{primeiro_segmento}'")
                            
                            filtros_combinados = session.post(f"{base_url}/api/filtros-disponiveis", json={
                                "filtros": {
                                    "tribunais": [primeiro_tribunal],
                                    "segmentos": [primeiro_segmento]
                                }
                            })
                            
                            if filtros_combinados.status_code == 200:
                                data_comb = filtros_combinados.json()
                                print(f"✅ Registros após filtros combinados: {data_comb.get('total_registros', 'N/A')}")
                                
                                filtros_cb = data_comb.get('filtros_disponiveis', {})
                                print(f"   - Tribunais disponíveis: {len(filtros_cb.get('tribunais', []))}")
                                print(f"   - Graus disponíveis: {len(filtros_cb.get('graus', []))}")
                                print(f"   - CNAEs disponíveis: {len(filtros_cb.get('cnaes', []))}")
                            else:
                                print(f"❌ Erro no teste 3: {filtros_combinados.status_code}")
                    else:
                        print(f"❌ Erro no teste 2: {filtros_tribunal.status_code}")
            else:
                print(f"❌ Erro no teste 1: {filtros_iniciais.status_code}")
        else:
            print("❌ Falha no login")
            
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_filtros_cascateados() 
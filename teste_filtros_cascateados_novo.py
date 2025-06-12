#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste simples dos filtros cascateados após atualização
"""

import requests
import json

def testar_filtros_cascateados():
    base_url = "http://127.0.0.1:5000"
    
    print("🔍 TESTE RÁPIDO - FILTROS CASCATEADOS")
    print("=" * 50)
    
    with requests.Session() as session:
        try:
            # 1. Verificar se servidor está rodando
            print("1. Verificando servidor...")
            response = session.get(base_url, timeout=5)
            if response.status_code != 200:
                print(f"❌ Servidor não está respondendo: {response.status_code}")
                return
            print("✅ Servidor funcionando")
            
            # 2. Testar API de filtros
            print("\n2. Testando API de filtros...")
            filtros_response = session.get(f"{base_url}/api/filtros")
            if filtros_response.status_code == 200:
                filtros = filtros_response.json()
                print("✅ API filtros funcionando")
                
                if filtros.get('success') and filtros.get('filtros'):
                    f = filtros['filtros']
                    print(f"   - Tribunais: {len(f.get('tribunais', []))}")
                    print(f"   - Graus: {len(f.get('graus', []))}")
                    print(f"   - Segmentos: {len(f.get('segmentos', []))}")
                    print(f"   - Ramos: {len(f.get('ramos', []))}")
                else:
                    print("⚠️ Resposta de filtros sem dados")
                    return
            else:
                print(f"❌ Erro na API filtros: {filtros_response.status_code}")
                return
            
            # 3. Testar filtros cascateados (vazio - deve retornar tudo)
            print("\n3. Testando filtros cascateados (vazio)...")
            cascata_response = session.post(f"{base_url}/api/filtros-disponiveis", 
                json={"filtros": {}})
            
            if cascata_response.status_code == 200:
                cascata_data = cascata_response.json()
                if cascata_data.get('success'):
                    print("✅ API filtros cascateados funcionando")
                    print(f"   - Total registros: {cascata_data.get('total_registros', 'N/A')}")
                    
                    f_disp = cascata_data.get('filtros_disponiveis', {})
                    print(f"   - Tribunais disponíveis: {len(f_disp.get('tribunais', []))}")
                    print(f"   - Graus disponíveis: {len(f_disp.get('graus', []))}")
                    print(f"   - Segmentos disponíveis: {len(f_disp.get('segmentos', []))}")
                    print(f"   - Ramos disponíveis: {len(f_disp.get('ramos', []))}")
                else:
                    print(f"❌ API cascateada retornou erro: {cascata_data}")
                    return
            else:
                print(f"❌ Erro na API cascateada: {cascata_response.status_code}")
                return
            
            # 4. Testar filtro específico com múltipla seleção
            print("\n4. Testando filtro com múltipla seleção...")
            
            # Pegar alguns tribunais para testar
            tribunais = f_disp.get('tribunais', [])[:2]  # Pegar 2 primeiros
            if tribunais:
                print(f"   Testando com tribunais: {tribunais}")
                
                cascata_multi = session.post(f"{base_url}/api/filtros-disponiveis", 
                    json={"filtros": {"tribunais": tribunais}})
                
                if cascata_multi.status_code == 200:
                    multi_data = cascata_multi.json()
                    if multi_data.get('success'):
                        print("✅ Filtro múltiplo funcionando")
                        print(f"   - Registros filtrados: {multi_data.get('total_registros', 'N/A')}")
                        
                        f_multi = multi_data.get('filtros_disponiveis', {})
                        print(f"   - Graus disponíveis após filtro: {len(f_multi.get('graus', []))}")
                        print(f"   - Segmentos disponíveis após filtro: {len(f_multi.get('segmentos', []))}")
                    else:
                        print(f"❌ Erro no filtro múltiplo: {multi_data}")
                else:
                    print(f"❌ Erro HTTP no filtro múltiplo: {cascata_multi.status_code}")
            else:
                print("⚠️ Não há tribunais para testar múltipla seleção")
            
            print("\n✅ TESTE CONCLUÍDO - Filtros cascateados parecem estar funcionando!")
            
        except requests.exceptions.ConnectionError:
            print("❌ Erro: Não foi possível conectar ao servidor")
            print("   Certifique-se de que o servidor Flask está rodando em http://127.0.0.1:5000")
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    testar_filtros_cascateados() 
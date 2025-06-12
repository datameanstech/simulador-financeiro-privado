import requests
import time
import json

def testar_filtros_cascateados():
    # Aguardar servidor inicializar
    time.sleep(3)
    
    # Testar login
    session = requests.Session()
    login_data = {'username': 'admin', 'password': 'pdpj2024'}
    login_resp = session.post('http://127.0.0.1:5000/login', data=login_data)
    
    if login_resp.status_code == 200:
        print('✅ Login realizado com sucesso')
        
        # Testar filtros cascateados - sem filtros
        print('\n🔍 Testando filtros cascateados sem seleção...')
        filtros_resp = session.post('http://127.0.0.1:5000/api/filtros-disponiveis', 
                                   json={'filtros': {}})
        
        if filtros_resp.status_code == 200:
            data = filtros_resp.json()
            if data.get('success'):
                filtros = data['filtros_disponiveis']
                print(f'📊 Total registros: {data.get("total_registros", "N/A")}')
                print(f'🏛️ Tribunais disponíveis: {len(filtros.get("tribunais", []))}')
                print(f'⚖️ Graus disponíveis: {len(filtros.get("graus", []))}')
                print(f'🏢 Segmentos disponíveis: {len(filtros.get("segmentos", []))}')
                print(f'🌿 Ramos disponíveis: {len(filtros.get("ramos", []))}')
                print(f'🏷️ CNAEs disponíveis: {len(filtros.get("cnaes", []))}')
                
                # Testar com filtro específico (usar plural)
                print('\n🔍 Testando com filtro TRT1...')
                filtros_trt1 = session.post('http://127.0.0.1:5000/api/filtros-disponiveis',
                                           json={'filtros': {'tribunais': ['TRT1']}})
                
                if filtros_trt1.status_code == 200:
                    data_trt1 = filtros_trt1.json()
                    if data_trt1.get('success'):
                        filtros_trt1_data = data_trt1['filtros_disponiveis']
                        print(f'📊 Total registros com TRT1: {data_trt1.get("total_registros", "N/A")}')
                        print(f'🏛️ Tribunais após filtro: {len(filtros_trt1_data.get("tribunais", []))}')
                        print(f'⚖️ Graus após filtro: {len(filtros_trt1_data.get("graus", []))}')
                        print(f'🏢 Segmentos após filtro: {len(filtros_trt1_data.get("segmentos", []))}')
                        
                        # Verificar se o efeito cascata funcionou
                        total_original = data.get("total_registros", 0)
                        total_filtrado = data_trt1.get("total_registros", 0)
                        
                        if total_filtrado < total_original:
                            print('\n✅ FILTROS CASCATEADOS FUNCIONANDO!')
                            print(f'   Registros reduziram de {total_original:,} para {total_filtrado:,}')
                        else:
                            print('\n❌ Filtros cascateados não estão funcionando')
                    else:
                        print('❌ Erro na resposta dos filtros TRT1')
                else:
                    print(f'❌ Erro HTTP nos filtros TRT1: {filtros_trt1.status_code}')
            else:
                print('❌ Erro na resposta dos filtros')
        else:
            print(f'❌ Erro HTTP nos filtros: {filtros_resp.status_code}')
    else:
        print(f'❌ Erro no login: {login_resp.status_code}')

if __name__ == '__main__':
    testar_filtros_cascateados() 
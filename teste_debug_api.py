import requests
import json

def testar_api_debug():
    try:
        # Testar login
        session = requests.Session()
        login_data = {'username': 'admin', 'password': 'pdpj2024'}
        login_resp = session.post('http://127.0.0.1:5000/login', data=login_data)
        
        print(f"Login status: {login_resp.status_code}")
        
        if login_resp.status_code == 200:
            # Testar API de teste de dados
            test_resp = session.get('http://127.0.0.1:5000/api/test-dados')
            print(f"Test dados status: {test_resp.status_code}")
            if test_resp.status_code == 200:
                test_data = test_resp.json()
                print(f"Dados carregados: {test_data.get('data_loaded')}")
                print(f"Contagem de dados: {test_data.get('data_count')}")
                print(f"Colunas: {test_data.get('columns')}")
            
            # Testar filtros disponíveis
            print("\n--- Testando filtros disponíveis ---")
            filtros_resp = session.post('http://127.0.0.1:5000/api/filtros-disponiveis', 
                                       json={'filtros': {}})
            print(f"Filtros status: {filtros_resp.status_code}")
            print(f"Filtros response: {filtros_resp.text[:500]}")
            
        else:
            print(f"Erro no login: {login_resp.text}")
            
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == '__main__':
    testar_api_debug() 
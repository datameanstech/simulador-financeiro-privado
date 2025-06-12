import requests
import time

def testar_servidor_logs():
    try:
        print("Fazendo login...")
        session = requests.Session()
        login_data = {'username': 'admin', 'password': 'pdpj2024'}
        login_resp = session.post('http://127.0.0.1:5000/login', data=login_data)
        
        if login_resp.status_code == 200:
            print("Login OK. Fazendo requisição para filtros disponíveis...")
            
            # Fazer requisição e aguardar logs
            filtros_resp = session.post('http://127.0.0.1:5000/api/filtros-disponiveis', 
                                       json={'filtros': {}})
            
            print(f"Status da resposta: {filtros_resp.status_code}")
            
            if filtros_resp.status_code == 200:
                try:
                    data = filtros_resp.json()
                    print(f"Resposta JSON válida: {data.get('success', False)}")
                    
                    if 'filtros_disponiveis' in data:
                        filtros = data['filtros_disponiveis']
                        print(f"Filtros na resposta:")
                        for chave, valores in filtros.items():
                            if isinstance(valores, list):
                                print(f"  {chave}: {len(valores)} valores")
                            else:
                                print(f"  {chave}: {type(valores)}")
                    else:
                        print("Chave 'filtros_disponiveis' não encontrada na resposta")
                        
                except Exception as e:
                    print(f"Erro ao processar JSON: {e}")
                    print(f"Resposta raw: {filtros_resp.text[:200]}")
            else:
                print(f"Erro HTTP: {filtros_resp.status_code}")
                print(f"Resposta: {filtros_resp.text}")
        else:
            print(f"Erro no login: {login_resp.status_code}")
            
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == '__main__':
    testar_servidor_logs() 
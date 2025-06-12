import requests
import json

def testar_colunas():
    try:
        # Testar login
        session = requests.Session()
        login_data = {'username': 'admin', 'password': 'pdpj2024'}
        login_resp = session.post('http://127.0.0.1:5000/login', data=login_data)
        
        if login_resp.status_code == 200:
            # Testar API de teste de dados para ver as colunas
            test_resp = session.get('http://127.0.0.1:5000/api/test-dados')
            if test_resp.status_code == 200:
                test_data = test_resp.json()
                colunas = test_data.get('columns', [])
                print(f"Total de colunas: {len(colunas)}")
                print("Colunas disponíveis:")
                for i, col in enumerate(colunas):
                    print(f"  {i+1:2d}. {col}")
                
                # Verificar se as colunas esperadas existem
                colunas_esperadas = ['TRIBUNAL', 'GRAU', 'SEGMENTO', 'RAMO', 'CNAE']
                print(f"\nVerificação das colunas esperadas:")
                for col in colunas_esperadas:
                    existe = col in colunas
                    print(f"  {col}: {'✅' if existe else '❌'}")
            
        else:
            print(f"Erro no login: {login_resp.status_code}")
            
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == '__main__':
    testar_colunas() 
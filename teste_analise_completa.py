#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time

def teste_analise_completa():
    """Testar a nova funcionalidade de análise completa"""
    
    base_url = 'http://127.0.0.1:5000'
    
    print("🧪 TESTE: Análise Completa (Porte, Ramo, Segmento, CNAE)")
    print("=" * 60)
    
    try:
        # 1. Fazer login
        session = requests.Session()
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        login_response = session.post(f'{base_url}/login', data=login_data)
        if login_response.status_code != 200:
            print("❌ Erro no login")
            return
        
        print("✅ Login realizado com sucesso")
        
        # 2. Testar API de relatório detalhado
        print("\n📊 Testando análise completa...")
        
        payload = {
            'filtros': {
                'tribunal': [],  # Todos os tribunais
                'grau': [],     # Todos os graus
                'segmento': [], # Todos os segmentos
                'ramo': [],     # Todos os ramos
                'cnae': ''      # Todos os CNAEs
            }
        }
        
        headers = {'Content-Type': 'application/json'}
        response = session.post(
            f'{base_url}/api/relatorio-detalhado',
            data=json.dumps(payload),
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API respondeu com sucesso")
            
            # Verificar se retornou dados de porte
            if 'porte' in data and data['porte']:
                print(f"✅ Análise por Porte: {len(data['porte'])} categorias")
                for item in data['porte'][:3]:  # Mostrar primeiros 3
                    print(f"   📏 {item['faixa']}: {item['quantidade']} empresas")
            else:
                print("⚠️ Nenhum dado de porte encontrado")
            
            # Verificar se retornou dados de ramo
            if 'ramo' in data and data['ramo']:
                print(f"✅ Análise por Ramo: {len(data['ramo'])} categorias")
                for item in data['ramo'][:3]:  # Mostrar primeiros 3
                    print(f"   🌿 {item['ramo']}: {item['quantidade']} empresas")
            else:
                print("⚠️ Nenhum dado de ramo encontrado")
            
            # Verificar se retornou dados de segmento
            if 'segmento' in data and data['segmento']:
                print(f"✅ Análise por Segmento: {len(data['segmento'])} categorias")
                for item in data['segmento'][:3]:  # Mostrar primeiros 3
                    print(f"   📈 {item['segmento']}: {item['quantidade']} empresas")
            else:
                print("⚠️ Nenhum dado de segmento encontrado")
            
            # Verificar se retornou dados de classes CNAE
            if 'cnae_classes' in data and data['cnae_classes']:
                print(f"✅ Análise por Classe CNAE: {len(data['cnae_classes'])} classes")
                for item in data['cnae_classes'][:3]:  # Mostrar primeiros 3
                    print(f"   📊 {item.get('codigo_classe', 'N/A')} - {item['classe']}: {item['quantidade']} empresas")
            else:
                print("⚠️ Nenhum dado de classe CNAE encontrado")
            
            # Verificar se retornou dados de subclasses CNAE
            if 'cnae_subclasses' in data and data['cnae_subclasses']:
                print(f"✅ Análise por Subclasse CNAE: {len(data['cnae_subclasses'])} subclasses")
                for item in data['cnae_subclasses'][:3]:  # Mostrar primeiros 3
                    print(f"   🔍 {item.get('codigo_subclasse', 'N/A')} - {item['subclasse']}: {item['quantidade']} empresas")
            else:
                print("⚠️ Nenhum dado de subclasse CNAE encontrado")
            
            print(f"\n📊 RESUMO DO TESTE:")
            print(f"   • Porte: {'✅' if data.get('porte') else '❌'}")
            print(f"   • Ramo: {'✅' if data.get('ramo') else '❌'}")
            print(f"   • Segmento: {'✅' if data.get('segmento') else '❌'}")
            print(f"   • Classes CNAE: {'✅' if data.get('cnae_classes') else '❌'}")
            print(f"   • Subclasses CNAE: {'✅' if data.get('cnae_subclasses') else '❌'}")
            
        else:
            print(f"❌ Erro na API: {response.status_code}")
            print(f"   Resposta: {response.text}")
        
    except requests.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor")
        print("   Certifique-se de que o Flask está rodando em http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    teste_analise_completa() 
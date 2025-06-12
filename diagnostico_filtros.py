#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time

def diagnostico_filtros_cascateados():
    """Diagnóstico completo dos filtros cascateados"""
    
    print("🔍 DIAGNÓSTICO - FILTROS CASCATEADOS")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:5000"
    session = requests.Session()
    
    try:
        # 1. Verificar se servidor está rodando
        print("1. Verificando servidor...")
        response = session.get(base_url, timeout=5)
        if response.status_code == 200:
            print("   ✅ Servidor Flask está rodando")
        else:
            print(f"   ❌ Servidor retornou status {response.status_code}")
            return
        
        # 2. Fazer login
        print("2. Fazendo login...")
        login_response = session.post(f"{base_url}/login", data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        if login_response.status_code == 200:
            print("   ✅ Login realizado com sucesso")
        else:
            print(f"   ❌ Erro no login: {login_response.status_code}")
            return
        
        # 3. Carregar dados
        print("3. Carregando dados...")
        carregar_response = session.post(f"{base_url}/api/carregar-dados", 
                                       json={'limite': 100})
        
        if carregar_response.status_code == 200:
            print("   ✅ Dados carregados com sucesso")
        else:
            print(f"   ❌ Erro ao carregar dados: {carregar_response.status_code}")
            return
        
        # Aguardar processamento
        time.sleep(3)
        
        # 4. Testar API de filtros inicial
        print("4. Testando API de filtros inicial...")
        filtros_response = session.get(f"{base_url}/api/filtros")
        
        if filtros_response.status_code == 200:
            filtros_data = filtros_response.json()
            if filtros_data.get('success'):
                print("   ✅ API filtros funcionando")
                print(f"      - Tribunais: {len(filtros_data['filtros'].get('tribunais', []))}")
                print(f"      - Graus: {len(filtros_data['filtros'].get('graus', []))}")
                print(f"      - Segmentos: {len(filtros_data['filtros'].get('segmentos', []))}")
                print(f"      - Ramos: {len(filtros_data['filtros'].get('ramos', []))}")
            else:
                print(f"   ❌ API filtros retornou erro: {filtros_data}")
                return
        else:
            print(f"   ❌ Erro na API filtros: {filtros_response.status_code}")
            return
        
        # 5. Testar API de filtros cascateados (sem filtros)
        print("5. Testando API filtros cascateados (estado inicial)...")
        cascata_response = session.post(f"{base_url}/api/filtros-disponiveis", 
                                      json={'filtros': {}})
        
        if cascata_response.status_code == 200:
            cascata_data = cascata_response.json()
            if cascata_data.get('success'):
                print("   ✅ API filtros cascateados funcionando")
                print(f"      - Total registros: {cascata_data.get('total_registros', 'N/A')}")
                
                filtros_disp = cascata_data.get('filtros_disponiveis', {})
                print(f"      - Tribunais disponíveis: {len(filtros_disp.get('tribunais', []))}")
                print(f"      - Graus disponíveis: {len(filtros_disp.get('graus', []))}")
                print(f"      - Segmentos disponíveis: {len(filtros_disp.get('segmentos', []))}")
                print(f"      - Ramos disponíveis: {len(filtros_disp.get('ramos', []))}")
                print(f"      - CNAEs disponíveis: {len(filtros_disp.get('cnaes', []))}")
            else:
                print(f"   ❌ API cascateada retornou erro: {cascata_data}")
                return
        else:
            print(f"   ❌ Erro na API cascateada: {cascata_response.status_code}")
            print(f"   📄 Resposta: {cascata_response.text}")
            return
        
        # 6. Testar filtro específico
        print("6. Testando filtro específico (tribunal)...")
        
        # Pegar primeiro tribunal disponível
        tribunais = filtros_disp.get('tribunais', [])
        if tribunais:
            tribunal_teste = tribunais[0]
            print(f"   🎯 Testando tribunal: {tribunal_teste}")
            
            filtro_especifico = session.post(f"{base_url}/api/filtros-disponiveis", 
                                           json={'filtros': {'tribunais': [tribunal_teste]}})
            
            if filtro_especifico.status_code == 200:
                filtro_data = filtro_especifico.json()
                if filtro_data.get('success'):
                    print("   ✅ Filtro específico funcionando")
                    print(f"      - Registros filtrados: {filtro_data.get('total_registros', 'N/A')}")
                    
                    filtros_atualizados = filtro_data.get('filtros_disponiveis', {})
                    print(f"      - Graus após filtro: {len(filtros_atualizados.get('graus', []))}")
                    print(f"      - Segmentos após filtro: {len(filtros_atualizados.get('segmentos', []))}")
                    
                    # Verificar se filtro foi aplicado corretamente
                    tribunais_apos = filtros_atualizados.get('tribunais', [])
                    if len(tribunais_apos) <= len(tribunais):
                        print("   ✅ Filtro cascateado está funcionando corretamente")
                    else:
                        print("   ⚠️ Filtro pode não estar sendo aplicado corretamente")
                        
                else:
                    print(f"   ❌ Erro no filtro específico: {filtro_data}")
            else:
                print(f"   ❌ Erro na requisição do filtro específico: {filtro_especifico.status_code}")
        else:
            print("   ⚠️ Nenhum tribunal disponível para teste")
        
        # 7. Verificar estrutura HTML do dashboard
        print("7. Verificando estrutura HTML do dashboard...")
        dashboard_response = session.get(f"{base_url}/dashboard")
        
        if dashboard_response.status_code == 200:
            html_content = dashboard_response.text
            
            # Verificar elementos essenciais
            elementos_esperados = [
                'id="filtroTribunal"',
                'id="filtroGrau"', 
                'id="filtroSegmento"',
                'id="filtroRamo"',
                'id="filtroCnae"',
                'configurarListenersFiltros',
                'atualizarFiltrosCascateados',
                '/api/filtros-disponiveis'
            ]
            
            elementos_encontrados = 0
            for elemento in elementos_esperados:
                if elemento in html_content:
                    elementos_encontrados += 1
                    print(f"   ✅ {elemento}")
                else:
                    print(f"   ❌ {elemento} NÃO ENCONTRADO")
            
            print(f"   📊 {elementos_encontrados}/{len(elementos_esperados)} elementos encontrados")
            
            if elementos_encontrados == len(elementos_esperados):
                print("   ✅ Estrutura HTML parece completa")
            else:
                print("   ⚠️ Estrutura HTML pode ter problemas")
        else:
            print(f"   ❌ Erro ao acessar dashboard: {dashboard_response.status_code}")
        
        # 8. Diagnóstico final
        print("\n" + "="*50)
        print("📋 DIAGNÓSTICO FINAL")
        print("="*50)
        
        print("✅ FUNCIONANDO:")
        print("   - Servidor Flask")
        print("   - Sistema de login")
        print("   - Carregamento de dados")
        print("   - API de filtros inicial")
        print("   - API de filtros cascateados")
        
        print("\n🔍 POSSÍVEIS PROBLEMAS:")
        print("   1. JavaScript pode não estar executando corretamente")
        print("   2. Eventos de mudança podem não estar sendo capturados")
        print("   3. Pode haver erro no console do navegador")
        print("   4. Timeout nas requisições AJAX")
        
        print("\n💡 PRÓXIMOS PASSOS:")
        print("   1. Abra o navegador em http://127.0.0.1:5000/dashboard")
        print("   2. Abra DevTools (F12) e verifique a aba Console")
        print("   3. Abra a aba Network e observe as requisições AJAX")
        print("   4. Teste manualmente selecionando um filtro")
        print("   5. Verifique se aparecem erros JavaScript")
        
    except Exception as e:
        print(f"❌ Erro durante diagnóstico: {e}")
        import traceback
        traceback.print_exc()

def main():
    diagnostico_filtros_cascateados()

if __name__ == "__main__":
    main() 
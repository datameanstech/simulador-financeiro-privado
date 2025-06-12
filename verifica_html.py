#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests

def verifica_html():
    """Verifica se o HTML está sendo servido corretamente"""
    
    print("🔍 VERIFICAÇÃO DO HTML")
    print("=" * 30)
    
    session = requests.Session()
    
    # Login
    login_response = session.post("http://127.0.0.1:5000/login", data={
        'username': 'admin',
        'password': 'admin123'
    })
    
    if login_response.status_code != 200:
        print("❌ Erro no login")
        return
    
    # Buscar dashboard
    dashboard_response = session.get("http://127.0.0.1:5000/dashboard")
    
    if dashboard_response.status_code != 200:
        print("❌ Erro ao acessar dashboard")
        return
    
    html = dashboard_response.text
    
    # Verificar funções JavaScript
    funcoes = [
        'configurarListenersFiltros',
        'atualizarFiltrosCascateados', 
        'atualizarOpcoesDisponiveis',
        'renderizarCnaes',
        'mostrarInfoRegistrosDisponiveis'
    ]
    
    print("Verificando funções JavaScript:")
    for funcao in funcoes:
        count = html.count(funcao)
        if count > 0:
            print(f"✅ {funcao}: {count} ocorrências")
        else:
            print(f"❌ {funcao}: não encontrada")
    
    # Verificar se há erros de sintaxe
    print("\nVerificando possíveis erros:")
    
    # Contar chaves e parênteses
    chaves_abertas = html.count('{')
    chaves_fechadas = html.count('}')
    parenteses_abertos = html.count('(')
    parenteses_fechados = html.count(')')
    
    print(f"Chaves: {chaves_abertas} abertas, {chaves_fechadas} fechadas")
    print(f"Parênteses: {parenteses_abertos} abertos, {parenteses_fechados} fechados")
    
    if chaves_abertas != chaves_fechadas:
        print("⚠️ Possível erro de sintaxe: chaves desbalanceadas")
    
    if parenteses_abertos != parenteses_fechados:
        print("⚠️ Possível erro de sintaxe: parênteses desbalanceados")
    
    # Verificar se jQuery está carregado
    if 'jquery' in html.lower():
        print("✅ jQuery detectado")
    else:
        print("❌ jQuery não detectado")
    
    # Procurar por erros JavaScript comuns
    erros_comuns = [
        'SyntaxError',
        'ReferenceError', 
        'TypeError',
        'undefined is not a function',
        'Cannot read property'
    ]
    
    for erro in erros_comuns:
        if erro in html:
            print(f"⚠️ Possível erro JavaScript: {erro}")
    
    # Verificar se os IDs dos filtros existem
    filtros_ids = [
        'filtroTribunal',
        'filtroGrau',
        'filtroSegmento', 
        'filtroRamo',
        'filtroCnae'
    ]
    
    print("\nVerificando elementos de filtros:")
    for filtro_id in filtros_ids:
        if f'id="{filtro_id}"' in html:
            print(f"✅ {filtro_id}: elemento encontrado")
        else:
            print(f"❌ {filtro_id}: elemento não encontrado")
    
    # Salvar HTML para análise
    with open('dashboard_debug.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n📄 HTML salvo em 'dashboard_debug.html' ({len(html)} caracteres)")
    
    # Verificar seção específica dos filtros cascateados
    inicio_filtros = html.find('configurarListenersFiltros')
    if inicio_filtros != -1:
        fim_secao = html.find('</script>', inicio_filtros)
        if fim_secao != -1:
            secao_filtros = html[max(0, inicio_filtros-500):fim_secao+10]
            
            print("\n🔍 Seção dos filtros cascateados:")
            print("-" * 40)
            print(secao_filtros[-1000:])  # Últimos 1000 caracteres
    
if __name__ == "__main__":
    verifica_html() 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
EXEMPLO DE USO - ANÁLISE DE HEAP TIMELINE
Simulador Financeiro

Este script demonstra como usar os analisadores de heap
para otimizar performance do seu simulador.
"""

import os
import time
from datetime import datetime

def demonstrar_uso():
    print("🔍 ANÁLISE DE HEAP TIMELINE - GUIA DE USO")
    print("=" * 60)
    
    print("\n📋 PASSO A PASSO PARA ANÁLISE:")
    print("-" * 40)
    
    passos = [
        {
            "num": 1,
            "titulo": "Coletar HEAPTIMELINE no Chrome DevTools",
            "descricao": [
                "• Abra Chrome DevTools (F12)",
                "• Vá para aba 'Memory'",
                "• Selecione 'Allocation instrumentation on timeline'",
                "• Clique 'Start' e use sua aplicação",
                "• Clique 'Stop' e salve como .heaptimeline"
            ]
        },
        {
            "num": 2,
            "titulo": "Executar análise do arquivo",
            "descricao": [
                "python analisador_heap.py meu_arquivo.heaptimeline",
                "# ou sem gráficos:",
                "python analisador_heap.py --sem-graficos meu_arquivo.heaptimeline"
            ]
        },
        {
            "num": 3,
            "titulo": "Monitoramento em tempo real",
            "descricao": [
                "# Monitor automático (encontra processo Flask)",
                "python monitor_memoria_tempo_real.py",
                "",
                "# Monitor específico por PID",
                "python monitor_memoria_tempo_real.py --pid 1234",
                "",
                "# Com teste de stress",
                "python monitor_memoria_tempo_real.py --teste-stress"
            ]
        }
    ]
    
    for passo in passos:
        print(f"\n{passo['num']}. {passo['titulo']}")
        print("   " + "-" * len(passo['titulo']))
        for desc in passo['descricao']:
            print(f"   {desc}")
    
    print("\n📊 EXEMPLO DE SAÍDA ESPERADA:")
    print("-" * 30)
    
    exemplo_saida = """
📊 Heap Máximo:      2,347.5 MB
📊 Heap Mínimo:        156.2 MB  
📊 Heap Médio:         834.3 MB
📊 Crescimento:      +1,891.3 MB
📊 Crescimento %:       +89.2%
📊 Picos de Memória:        12 eventos

🚨 VAZAMENTO DE MEMÓRIA DETECTADO: Crescimento de 89.2%

🎯 RECOMENDAÇÕES PRIORITÁRIAS:
 1. 🚀 Use Polars .lazy() para queries nos 14.7M registros
 2. 🚀 Implemente cache Redis para filtros CNAE (1,311 únicos)
 3. 🔧 OTIMIZAÇÃO POLARS: Use .lazy() e .streaming() para datasets grandes
 4. 🔧 FLASK: Desabilite debug mode em produção (debug=False)
"""
    
    print(exemplo_saida)
    
    print("\n🔧 OTIMIZAÇÕES ESPECÍFICAS IDENTIFICADAS:")
    print("-" * 45)
    
    otimizacoes = {
        "Polars": [
            "df.lazy().filter(...).collect() em vez de df.filter(...)",
            "df.lazy().group_by(...).agg(...).collect() para agregações",
            "Use .streaming() para datasets > 1GB"
        ],
        "Flask": [
            "app.config['DEBUG'] = False em produção",
            "Use gunicorn: gunicorn -w 4 -b 0.0.0.0:5000 app:app",
            "Implemente cache com @lru_cache ou Redis"
        ],
        "Memória": [
            "del variáveis_grandes após uso",
            "Use generators em vez de listas grandes",
            "Processe dados em chunks de 10k-50k registros"
        ]
    }
    
    for categoria, dicas in otimizacoes.items():
        print(f"\n📋 {categoria}:")
        for dica in dicas:
            print(f"   • {dica}")
    
    print("\n💡 EXEMPLO DE CÓDIGO OTIMIZADO:")
    print("-" * 35)
    
    codigo_exemplo = '''
# ❌ ANTES (problemático para 14.7M registros)
df_filtrado = df.filter(pl.col("tribunal").is_in(tribunais_selecionados))
result = df_filtrado.group_by("cnae").agg([
    pl.count().alias("quantidade"),
    pl.sum("valor").alias("total")
]).collect()

# ✅ DEPOIS (otimizado)
result = (
    df.lazy()
    .filter(pl.col("tribunal").is_in(tribunais_selecionados))
    .group_by("cnae")
    .agg([
        pl.count().alias("quantidade"), 
        pl.sum("valor").alias("total")
    ])
    .collect(streaming=True)  # Processa em chunks
)
'''
    
    print(codigo_exemplo)
    
    print("\n📈 MÉTRICAS DE SUCESSO:")
    print("-" * 25)
    
    metricas = [
        "Redução de 50%+ no uso de memória",
        "Tempo de resposta < 2s para queries complexas",
        "Zero vazamentos de memória detectados",
        "CPU usage < 70% durante picos de uso"
    ]
    
    for metrica in metricas:
        print(f"   ✅ {metrica}")
    
    print(f"\n🕒 Última atualização: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def criar_scripts_exemplo():
    """Cria scripts de exemplo para testes"""
    
    # Script para gerar carga de trabalho
    script_carga = '''#!/usr/bin/env python3
import requests
import time
import random

def gerar_carga_trabalho():
    """Gera carga de trabalho para testar o simulador"""
    
    base_url = "http://127.0.0.1:5000"
    
    endpoints = [
        "/api/filtros",
        "/api/cnaes/todos", 
        "/api/ranking"
    ]
    
    print("🔄 Gerando carga de trabalho...")
    
    for i in range(50):  # 50 requisições
        endpoint = random.choice(endpoints)
        
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            print(f"Request {i+1}: {endpoint} -> {response.status_code}")
            
        except Exception as e:
            print(f"Erro request {i+1}: {e}")
        
        time.sleep(random.uniform(0.5, 2.0))  # Pausa aleatória

if __name__ == "__main__":
    gerar_carga_trabalho()
'''
    
    with open("gerar_carga_trabalho.py", "w", encoding="utf-8") as f:
        f.write(script_carga)
    
    # Script para análise automatizada
    script_auto = '''#!/usr/bin/env python3
import subprocess
import sys
import time
from pathlib import Path

def analise_automatizada():
    """Executa análise automatizada completa"""
    
    print("🚀 ANÁLISE AUTOMATIZADA - SIMULADOR FINANCEIRO")
    print("=" * 50)
    
    # 1. Iniciar monitoramento
    print("1. Iniciando monitoramento em background...")
    monitor_proc = subprocess.Popen([
        sys.executable, "monitor_memoria_tempo_real.py",
        "--duracao", "120",  # 2 minutos
        "--sem-graficos"
    ])
    
    # 2. Aguardar início do monitor
    time.sleep(5)
    
    # 3. Gerar carga de trabalho
    print("2. Gerando carga de trabalho...")
    subprocess.run([sys.executable, "gerar_carga_trabalho.py"])
    
    # 4. Aguardar conclusão do monitor
    print("3. Aguardando conclusão do monitoramento...")
    monitor_proc.wait()
    
    # 5. Analisar logs gerados
    print("4. Analisando logs...")
    today = time.strftime("%Y%m%d")
    log_file = f"monitor_memoria_{today}.jsonl"
    
    if Path(log_file).exists():
        print(f"✅ Log gerado: {log_file}")
        # Aqui você pode adicionar análise do log
    
    print("🎉 Análise automatizada concluída!")

if __name__ == "__main__":
    analise_automatizada()
'''
    
    with open("analise_automatizada.py", "w", encoding="utf-8") as f:
        f.write(script_auto)
    
    print("📁 Scripts de exemplo criados:")
    print("   • gerar_carga_trabalho.py")
    print("   • analise_automatizada.py")

def main():
    demonstrar_uso()
    
    print("\n❓ QUER CRIAR SCRIPTS DE EXEMPLO? (s/n): ", end="")
    resposta = input().lower()
    
    if resposta in ['s', 'sim', 'y', 'yes']:
        criar_scripts_exemplo()
    
    print("\n📚 PRÓXIMOS PASSOS:")
    print("1. Colete um HEAPTIMELINE do seu site")
    print("2. Execute: python analisador_heap.py seu_arquivo.heaptimeline")
    print("3. Execute: python monitor_memoria_tempo_real.py")
    print("4. Implemente as otimizações sugeridas")
    print("5. Repita o processo para validar melhorias")

if __name__ == "__main__":
    main() 
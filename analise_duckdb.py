#!/usr/bin/env python3
"""
🦆 ANÁLISE COM DUCKDB - SUPER RÁPIDO
📊 SQL nativo em arquivos Parquet
⚡ Processamento em segundos mesmo com milhões de registros
"""

import duckdb
import pandas as pd
import plotly.express as px
from pathlib import Path

def conectar_duckdb(arquivo_parquet: str = "dados.parquet"):
    """Conecta DuckDB diretamente ao arquivo Parquet"""
    
    if not Path(arquivo_parquet).exists():
        print(f"❌ Arquivo {arquivo_parquet} não encontrado")
        print("💡 Execute primeiro: python analise_robusta.py")
        return None
    
    # DuckDB conecta diretamente ao Parquet!
    conn = duckdb.connect()
    
    # Registrar o arquivo como uma tabela
    conn.execute(f"""
        CREATE VIEW litigantes AS 
        SELECT * FROM read_parquet('{arquivo_parquet}')
    """)
    
    print("✅ DuckDB conectado ao Parquet")
    return conn

def consultas_rapidas(conn):
    """Consultas SQL super rápidas"""
    
    print("🚀 EXECUTANDO CONSULTAS SQL ULTRA-RÁPIDAS")
    print("=" * 60)
    
    # 1. Estatísticas básicas
    print("\n📊 ESTATÍSTICAS BÁSICAS:")
    result = conn.execute("""
        SELECT 
            COUNT(*) as total_registros,
            COUNT(DISTINCT "ÓRGÃO") as empresas_unicas,
            SUM("NOVOS") as total_novos,
            AVG("NOVOS") as media_novos
        FROM litigantes 
        WHERE "NOVOS" > 0
    """).fetchone()
    
    print(f"Total registros: {result[0]:,}")
    print(f"Empresas únicas: {result[1]:,}")
    print(f"Total novos processos: {result[2]:,}")
    print(f"Média por registro: {result[3]:.1f}")
    
    # 2. Top 20 empresas
    print("\n🏆 TOP 20 EMPRESAS:")
    top_empresas = conn.execute("""
        SELECT 
            "ÓRGÃO",
            SUM("NOVOS") as total_novos,
            COUNT(*) as registros,
            AVG("NOVOS") as media_novos
        FROM litigantes 
        WHERE "NOVOS" > 0
        GROUP BY "ÓRGÃO"
        ORDER BY total_novos DESC
        LIMIT 20
    """).fetchdf()
    
    print(top_empresas.to_string(index=False))
    
    # 3. Análise por tribunal
    print("\n⚖️ ANÁLISE POR TRIBUNAL:")
    tribunal_stats = conn.execute("""
        SELECT 
            "TRIBUNAL",
            SUM("NOVOS") as total_novos,
            COUNT(DISTINCT "ÓRGÃO") as empresas_unicas,
            COUNT(*) as registros
        FROM litigantes 
        GROUP BY "TRIBUNAL"
        ORDER BY total_novos DESC
    """).fetchdf()
    
    print(tribunal_stats.to_string(index=False))
    
    return top_empresas, tribunal_stats

def buscar_empresa_sql(conn, empresa_nome: str):
    """Busca empresa específica com SQL"""
    
    print(f"\n🔍 BUSCANDO: {empresa_nome}")
    print("=" * 50)
    
    result = conn.execute(f"""
        SELECT 
            "ÓRGÃO",
            SUM("NOVOS") as total_novos,
            COUNT(*) as registros,
            SUM("NOVOS") * 75.0 as receita_estimada
        FROM litigantes 
        WHERE UPPER("ÓRGÃO") LIKE UPPER('%{empresa_nome}%')
        AND "NOVOS" > 0
        GROUP BY "ÓRGÃO"
        ORDER BY total_novos DESC
    """).fetchdf()
    
    if len(result) == 0:
        print(f"❌ Nenhuma empresa encontrada com '{empresa_nome}'")
    else:
        print(f"✅ {len(result)} empresa(s) encontrada(s):")
        print(result.to_string(index=False))
        
        total_processos = result['total_novos'].sum()
        receita_total = total_processos * 75.0
        print(f"\n💰 RESUMO FINANCEIRO:")
        print(f"Total processos: {total_processos:,}")
        print(f"Receita estimada: R$ {receita_total:,.2f}")
        print(f"Receita mensal: R$ {receita_total/12:,.2f}")

def main():
    """Análise completa com DuckDB"""
    
    print("🦆 ANÁLISE ROBUSTA COM DUCKDB")
    print("=" * 60)
    
    # Conectar ao arquivo
    conn = conectar_duckdb()
    if not conn:
        return
    
    # Executar consultas
    top_empresas, tribunal_stats = consultas_rapidas(conn)
    
    # Exemplos de busca
    buscar_empresa_sql(conn, "BANCO")
    buscar_empresa_sql(conn, "ITAU")
    buscar_empresa_sql(conn, "TELEFONICA")
    buscar_empresa_sql(conn, "PETROBRAS")
    
    # Gerar gráficos
    print("\n📊 Gerando gráficos...")
    
    fig1 = px.bar(
        top_empresas.head(15),
        x='total_novos',
        y='ÓRGÃO',
        title='Top 15 Empresas - DuckDB Analysis'
    )
    fig1.update_layout(yaxis={'categoryorder':'total ascending'})
    fig1.write_html("duckdb_top_empresas.html")
    
    fig2 = px.pie(
        tribunal_stats,
        values='total_novos',
        names='TRIBUNAL',
        title='Distribuição por Tribunal - DuckDB Analysis'
    )
    fig2.write_html("duckdb_tribunais.html")
    
    print("📄 Gráficos salvos: duckdb_top_empresas.html, duckdb_tribunais.html")
    
    # SQL interativo
    print("\n💡 Para consultas personalizadas:")
    print("import duckdb")
    print("conn = duckdb.connect()")
    print("conn.execute('SELECT * FROM read_parquet(\"dados.parquet\") LIMIT 10').fetchdf()")
    
    conn.close()

if __name__ == "__main__":
    main() 
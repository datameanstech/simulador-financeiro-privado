#!/usr/bin/env python3
"""
🔥 ANÁLISE ROBUSTA DE GRANDES LITIGANTES
📊 Processamento de 14+ milhões de registros
⚡ Otimizado para performance máxima
"""

import polars as pl
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests
from pathlib import Path
import time
from typing import Optional

def download_dados_drive(file_id: str = "1Ns07hTZaK4Ry6bFEHvLACZ5tHJ7b-C2E", 
                        output_path: str = "dados.parquet") -> bool:
    """Download robusto do Google Drive"""
    
    urls = [
        f"https://drive.usercontent.google.com/download?id={file_id}&export=download&authuser=0",
        f"https://drive.google.com/uc?id={file_id}&export=download&confirm=t"
    ]
    
    for i, url in enumerate(urls, 1):
        try:
            print(f"🔄 Tentativa {i}: Baixando arquivo...")
            
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r📥 Progresso: {progress:.1f}%", end="", flush=True)
            
            file_size = Path(output_path).stat().st_size / (1024**3)
            print(f"\n✅ Download concluído: {file_size:.1f}GB")
            return True
            
        except Exception as e:
            print(f"❌ Tentativa {i} falhou: {e}")
    
    return False

def carregar_dados_completos(arquivo_path: str = "dados.parquet", 
                           limite: Optional[int] = None) -> pl.DataFrame:
    """Carregamento otimizado com Polars - SEM limitações"""
    
    print("🚀 Iniciando carregamento com Polars (otimizado para big data)...")
    start_time = time.time()
    
    # Lazy loading - não carrega na memória ainda
    df_lazy = pl.scan_parquet(arquivo_path)
    
    # Verificar total sem carregar
    total_rows = df_lazy.select(pl.len()).collect().item()
    print(f"📊 Total de registros: {total_rows:,}")
    
    # Carregamento estratégico
    if limite and limite < total_rows:
        print(f"⚡ Carregando {limite:,} registros...")
        df = df_lazy.head(limite).collect()
    else:
        print(f"💪 Carregando TODOS os {total_rows:,} registros...")
        df = df_lazy.collect(streaming=True)
    
    elapsed = time.time() - start_time
    memory_mb = df.estimated_size('mb')
    
    print(f"✅ Carregamento concluído em {elapsed:.1f}s")
    print(f"📈 Registros: {len(df):,}")
    print(f"📋 Colunas: {len(df.columns)}")
    print(f"💾 Memória: {memory_mb:.1f}MB")
    
    return df

def analise_top_empresas(df: pl.DataFrame, top_n: int = 50) -> pl.DataFrame:
    """Análise super rápida das top empresas"""
    
    print(f"🏆 Analisando TOP {top_n} empresas...")
    
    if 'ÓRGÃO' not in df.columns or 'NOVOS' not in df.columns:
        print("❌ Colunas necessárias não encontradas")
        print(f"Colunas disponíveis: {df.columns}")
        return pl.DataFrame()
    
    # Análise ultra-rápida com Polars
    top_empresas = (
        df
        .filter(pl.col('NOVOS') > 0)
        .group_by('ÓRGÃO')
        .agg([
            pl.col('NOVOS').sum().alias('total_novos'),
            pl.col('NOVOS').count().alias('registros'),
            pl.col('NOVOS').mean().alias('media_novos')
        ])
        .sort('total_novos', descending=True)
        .head(top_n)
    )
    
    print(f"✅ Análise concluída: {len(top_empresas)} empresas")
    return top_empresas

def gerar_relatorio_completo(df: pl.DataFrame, salvar_html: bool = True):
    """Gera relatório completo com gráficos"""
    
    print("📊 Gerando relatório completo...")
    
    # 1. Estatísticas gerais
    print("\n" + "="*60)
    print("📈 ESTATÍSTICAS GERAIS")
    print("="*60)
    print(f"Total de registros: {len(df):,}")
    print(f"Total de colunas: {len(df.columns)}")
    
    if 'NOVOS' in df.columns:
        total_novos = df['NOVOS'].sum()
        media_novos = df['NOVOS'].mean()
        print(f"Total novos processos: {total_novos:,}")
        print(f"Média por registro: {media_novos:.1f}")
    
    # 2. Top empresas
    if 'ÓRGÃO' in df.columns:
        top_empresas = analise_top_empresas(df, 20)
        print("\n🏆 TOP 20 EMPRESAS:")
        print(top_empresas.to_pandas().to_string(index=False))
        
        # Gráfico das top empresas
        if salvar_html:
            fig_empresas = px.bar(
                top_empresas.to_pandas().head(15),
                x='total_novos',
                y='ÓRGÃO',
                title='Top 15 Empresas por Volume de Novos Processos',
                labels={'total_novos': 'Total de Novos Processos'},
                height=600
            )
            fig_empresas.update_layout(yaxis={'categoryorder':'total ascending'})
            fig_empresas.write_html("top_empresas.html")
            print("📄 Gráfico salvo: top_empresas.html")
    
    # 3. Análise por tribunal
    if 'TRIBUNAL' in df.columns:
        tribunal_stats = (
            df
            .group_by('TRIBUNAL')
            .agg([
                pl.col('NOVOS').sum().alias('total_novos'),
                pl.col('ÓRGÃO').n_unique().alias('empresas_unicas'),
                pl.len().alias('registros')
            ])
            .sort('total_novos', descending=True)
        )
        
        print("\n⚖️ ANÁLISE POR TRIBUNAL:")
        print(tribunal_stats.to_pandas().to_string(index=False))
        
        if salvar_html:
            fig_tribunal = px.pie(
                tribunal_stats.to_pandas(),
                values='total_novos',
                names='TRIBUNAL',
                title='Distribuição de Novos Processos por Tribunal'
            )
            fig_tribunal.write_html("tribunais.html")
            print("📄 Gráfico salvo: tribunais.html")

def simulador_financeiro(df: pl.DataFrame, empresa_busca: str, 
                        preco_processo: float = 50.0):
    """Simulador financeiro para empresa específica"""
    
    print(f"\n💰 SIMULADOR FINANCEIRO - {empresa_busca}")
    print("="*50)
    
    # Buscar empresa (busca flexível)
    empresa_data = df.filter(
        pl.col('ÓRGÃO').str.to_lowercase().str.contains(empresa_busca.lower())
    )
    
    if len(empresa_data) == 0:
        print(f"❌ Nenhuma empresa encontrada com '{empresa_busca}'")
        # Sugerir empresas similares
        empresas_sample = df.select('ÓRGÃO').unique().head(10)
        print("💡 Empresas disponíveis (amostra):")
        for empresa in empresas_sample['ÓRGÃO']:
            print(f"  • {empresa}")
        return
    
    # Calcular métricas financeiras
    total_novos = empresa_data['NOVOS'].sum()
    total_registros = len(empresa_data)
    receita_anual = total_novos * preco_processo
    receita_mensal = receita_anual / 12
    
    print(f"🏢 Empresa(s) encontrada(s): {len(empresa_data)} registros")
    print(f"📊 Total novos processos: {total_novos:,}")
    print(f"💵 Preço por processo: R$ {preco_processo:.2f}")
    print(f"💰 Receita anual estimada: R$ {receita_anual:,.2f}")
    print(f"📈 Receita mensal: R$ {receita_mensal:,.2f}")
    print(f"📅 Receita diária: R$ {receita_mensal/30:,.2f}")
    
    return {
        'empresa': empresa_busca,
        'registros_encontrados': total_registros,
        'novos_processos': total_novos,
        'receita_anual': receita_anual,
        'receita_mensal': receita_mensal
    }

def main():
    """Função principal - Execute este script!"""
    
    print("🔥 ANALISADOR ROBUSTO DE GRANDES LITIGANTES")
    print("=" * 60)
    
    arquivo = "dados.parquet"
    
    # 1. Download dos dados
    if not Path(arquivo).exists():
        print("📥 Baixando dados do Google Drive...")
        if not download_dados_drive():
            print("❌ Falha no download. Execute novamente.")
            return
    
    # 2. Carregar dados (TODOS os registros)
    print("\n📊 Carregando dados...")
    df = carregar_dados_completos(arquivo, limite=None)  # SEM limite!
    
    if df.is_empty():
        print("❌ Falha no carregamento")
        return
    
    # 3. Análise completa
    print("\n📈 Gerando análises...")
    gerar_relatorio_completo(df)
    
    # 4. Exemplos de simulação
    print("\n💰 EXEMPLOS DE SIMULAÇÃO FINANCEIRA:")
    simulador_financeiro(df, "BANCO", 75.0)
    simulador_financeiro(df, "ITAU", 100.0)
    simulador_financeiro(df, "TELEFONICA", 60.0)
    
    print("\n✅ Análise completa concluída!")
    print("📄 Arquivos gerados: top_empresas.html, tribunais.html")
    print("\n💡 Para análise interativa, use:")
    print("   jupyter notebook")

if __name__ == "__main__":
    main() 
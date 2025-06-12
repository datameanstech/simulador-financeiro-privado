#!/usr/bin/env python3
"""
Teste de Distribuição de Empresas por Faixa
Análise independente do arquivo parquet para verificar quantidades exatas
"""

import polars as pl
import sys

def main():
    print("🔍 TESTE DE DISTRIBUIÇÃO DE EMPRESAS POR FAIXA")
    print("=" * 60)
    
    try:
        # Carregar dados
        print("📁 Carregando arquivo parquet...")
        df = pl.read_parquet("dados_grandes_litigantes.parquet")
        
        print(f"📊 Total de registros carregados: {len(df):,}")
        print(f"📋 Colunas disponíveis: {list(df.columns)}")
        
        # Verificar coluna de empresa
        coluna_empresa = None
        if 'NOME' in df.columns:
            coluna_empresa = 'NOME'
        elif 'EMPRESA' in df.columns:
            coluna_empresa = 'EMPRESA'
        elif 'CNPJ' in df.columns:
            coluna_empresa = 'CNPJ'
        else:
            print("❌ Não foi possível encontrar coluna de empresa")
            return
        
        print(f"🏢 Usando coluna de empresa: {coluna_empresa}")
        
        # Verificar coluna de processos
        coluna_processos = None
        if 'NOVOS' in df.columns:
            coluna_processos = 'NOVOS'
        elif 'PROCESSOS' in df.columns:
            coluna_processos = 'PROCESSOS'
        else:
            print("❌ Não foi possível encontrar coluna de processos")
            return
            
        print(f"⚖️ Usando coluna de processos: {coluna_processos}")
        
        # Agrupar por empresa e somar processos
        print("\n🔄 Agrupando por empresa...")
        empresas_df = (
            df.group_by(coluna_empresa)
            .agg([pl.col(coluna_processos).sum().alias('total_processos')])
            .filter(pl.col('total_processos') > 0)  # Apenas empresas com processos
            .sort('total_processos', descending=True)
        )
        
        total_empresas = len(empresas_df)
        print(f"✅ Total de empresas únicas com processos: {total_empresas:,}")
        
        # Converter para processos por mês
        empresas_com_mensal = empresas_df.with_columns([
            (pl.col('total_processos') / 12).round().alias('processos_mes')
        ])
        
        # Extrair dados para análise
        processos_mes_lista = empresas_com_mensal.select('processos_mes').to_series().to_list()
        
        print(f"\n📈 Amostra dos 10 maiores (proc/mês): {sorted(processos_mes_lista, reverse=True)[:10]}")
        print(f"📉 Amostra dos 10 menores (proc/mês): {sorted(processos_mes_lista)[:10]}")
        
        # Definir faixas (incluindo 0 processos)
        faixas = [
            ('0 proc/mês', 0, 0),
            ('1-10 proc/mês', 1, 10),
            ('11-50 proc/mês', 11, 50),
            ('51-100 proc/mês', 51, 100),
            ('101-500 proc/mês', 101, 500),
            ('501-1000 proc/mês', 501, 1000),
            ('1001-5000 proc/mês', 1001, 5000),
            ('5000+ proc/mês', 5001, float('inf'))
        ]
        
        print(f"\n📊 DISTRIBUIÇÃO POR FAIXAS:")
        print("-" * 60)
        
        total_verificacao = 0
        resultados = []
        
        for label, min_val, max_val in faixas:
            if max_val == float('inf'):
                count = sum(1 for p in processos_mes_lista if p >= min_val)
                empresas_na_faixa = [p for p in processos_mes_lista if p >= min_val]
            else:
                count = sum(1 for p in processos_mes_lista if min_val <= p <= max_val)
                empresas_na_faixa = [p for p in processos_mes_lista if min_val <= p <= max_val]
            
            percentual = (count / total_empresas) * 100
            total_verificacao += count
            
            volume_total = sum(empresas_na_faixa)
            
            resultados.append({
                'faixa': label,
                'quantidade': count,
                'percentual': percentual,
                'volume_total': volume_total
            })
            
            print(f"{label:<20} | {count:>8,} empresas | {percentual:>6.1f}% | Vol: {volume_total:>10,}")
        
        print("-" * 60)
        print(f"{'TOTAL':<20} | {total_verificacao:>8,} empresas | {(total_verificacao/total_empresas)*100:>6.1f}%")
        
        # Verificar se soma 100%
        soma_percentuais = sum(r['percentual'] for r in resultados)
        print(f"\n✅ Soma dos percentuais: {soma_percentuais:.1f}%")
        
        if abs(soma_percentuais - 100.0) < 0.1:
            print("✅ Percentuais corretos (somam ~100%)")
        else:
            print(f"⚠️  Diferença: {100.0 - soma_percentuais:.1f}%")
        
        # Estatísticas adicionais
        volume_total_mensal = sum(processos_mes_lista)
        media_processos = volume_total_mensal / total_empresas if total_empresas > 0 else 0
        
        print(f"\n📈 ESTATÍSTICAS GERAIS:")
        print(f"Volume total mensal: {volume_total_mensal:,} processos")
        print(f"Média por empresa: {media_processos:.1f} proc/mês")
        
        # Top 10 empresas
        print(f"\n🏆 TOP 10 EMPRESAS:")
        top_10 = empresas_com_mensal.head(10)
        for i, row in enumerate(top_10.iter_rows(), 1):
            empresa, total, mensal = row
            empresa_str = str(empresa)[:50] + "..." if len(str(empresa)) > 50 else str(empresa)
            print(f"{i:>2}. {empresa_str:<50} | {int(mensal):>6,} proc/mês")
        
        print(f"\n✅ Teste concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 
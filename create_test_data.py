#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criar dados de teste em formato parquet
para validar o funcionamento da aplicação web
"""

import polars as pl
import random
from datetime import datetime

def create_test_data():
    """Criar dados de teste simulando os grandes litigantes"""
    
    print("📊 Criando dados de teste...")
    
    # Empresas fictícias baseadas em padrões reais
    empresas = [
        "BANCO DO BRASIL S.A.",
        "CAIXA ECONÔMICA FEDERAL",
        "BRADESCO S.A.",
        "ITAÚ UNIBANCO S.A.",
        "SANTANDER BRASIL S.A.",
        "BTG PACTUAL S.A.",
        "NUBANK S.A.",
        "MAGAZINE LUIZA S.A.",
        "VIA VAREJO S.A.",
        "MERCADOLIVRE BRASIL LTDA",
        "TELEFONICA BRASIL S.A.",
        "TIM S.A.",
        "CLARO S.A.",
        "OI S.A.",
        "NET SERVICOS LTDA",
        "NATURA COSMETICOS S.A.",
        "PETROBRAS S.A.",
        "VALE S.A.",
        "JBS S.A.",
        "AMBEV S.A.",
        "GERDAU S.A.",
        "USIMINAS S.A.",
        "SUZANO S.A.",
        "KLABIN S.A.",
        "WEG S.A.",
        "EMBRAER S.A.",
        "GOL LINHAS AEREAS S.A.",
        "AZUL S.A.",
        "LATAM AIRLINES BRASIL S.A.",
        "TAM LINHAS AEREAS S.A."
    ]
    
    tribunais = [
        "TJSP", "TJRJ", "TJMG", "TJRS", "TJPR", "TJSC", "TJBA", 
        "TJGO", "TJDF", "TJPE", "TJCE", "TJMA", "TJPB", "TJES",
        "TJMT", "TJMS", "TJTO", "TJAC", "TJAP", "TJRR", "TJRO",
        "TJAL", "TJRN", "TJSE", "TJPI", "TJAM", "TJPA"
    ]
    
    # Gerar dados
    n_records = 50000  # 50k registros para teste
    
    data = []
    for i in range(n_records):
        empresa = random.choice(empresas)
        tribunal = random.choice(tribunais)
        
        # Simular distribuição realista de processos
        if empresa.startswith("BANCO") or "CAIXA" in empresa:
            novos = random.randint(50, 500)  # Bancos têm mais processos
        elif "TELEFONICA" in empresa or "TIM" in empresa:
            novos = random.randint(30, 300)  # Telecoms também
        else:
            novos = random.randint(1, 100)   # Outros
        
        data.append({
            'NOME': empresa,
            'TRIBUNAL': tribunal,
            'NOVOS': novos,
            'ANO': 2024,
            'MES': random.randint(1, 12)
        })
    
    # Criar DataFrame
    df = pl.DataFrame(data)
    
    # Salvar como parquet
    output_file = "dados_litigantes.parquet"
    df.write_parquet(output_file)
    
    print(f"✅ Dados de teste criados: {output_file}")
    print(f"📊 Total de registros: {len(df):,}")
    print(f"🏢 Empresas únicas: {df.select('NOME').n_unique()}")
    print(f"⚖️ Tribunais únicos: {df.select('TRIBUNAL').n_unique()}")
    print(f"📈 Total de processos novos: {df.select(pl.col('NOVOS').sum()).item():,}")
    
    # Mostrar amostra
    print("\n📋 Amostra dos dados:")
    print(df.head(10).to_pandas().to_string(index=False))
    
    return output_file

if __name__ == "__main__":
    create_test_data() 
#!/usr/bin/env python3
"""
Criar dados de demonstração menores para deploy
"""
import polars as pl
import numpy as np
import random

def create_demo_data():
    """Cria dados de demonstração com ~1000 empresas"""
    # Usar seed fixa para consistência
    np.random.seed(42)
    random.seed(42)
    
    # Empresas brasileiras conhecidas (repetir para ter volume)
    empresas_base = [
        'BANCO DO BRASIL S.A.', 'ITAÚ UNIBANCO S.A.', 'BRADESCO S.A.', 'SANTANDER BRASIL S.A.',
        'TELEFÔNICA BRASIL S.A.', 'TIM S.A.', 'CLARO S.A.', 'OI S.A.',
        'PETROBRAS S.A.', 'VALE S.A.', 'AMBEV S.A.', 'JBS S.A.',
        'MAGAZINE LUIZA S.A.', 'VIA VAREJO S.A.', 'LOJAS AMERICANAS S.A.', 'B2W DIGITAL S.A.',
        'CARREFOUR BRASIL S.A.', 'WALMART BRASIL S.A.', 'ATACADÃO S.A.', 'GRUPO PÃO DE AÇÚCAR S.A.',
        'EMBRAER S.A.', 'GERDAU S.A.', 'USIMINAS S.A.', 'CSN S.A.',
        'NATURA S.A.', 'O BOTICÁRIO S.A.', 'LOCALIZA S.A.', 'MOVIDA S.A.'
    ]
    
    # Expandir lista para 1000 registros únicos
    empresas = []
    for i in range(1000):
        base = empresas_base[i % len(empresas_base)]
        if i >= len(empresas_base):
            # Adicionar variação para unicidade
            variacao = f" FILIAL {i//len(empresas_base)}"
            empresas.append(base.replace(' S.A.', variacao + ' S.A.'))
        else:
            empresas.append(base)
    
    # Dados simulados realistas
    tribunais = ['TJSP', 'TJRJ', 'TJMG', 'TJRS', 'TJPR', 'TJSC', 'TJBA', 'TJDF', 'TJGO', 'TJPE']
    graus = ['1º GRAU', '2º GRAU', 'INSTÂNCIA ÚNICA']
    ramos = [
        'BANCOS E SERVIÇOS FINANCEIROS', 'TELECOMUNICAÇÕES', 'ENERGIA E PETRÓLEO', 
        'VAREJO E COMÉRCIO', 'SIDERURGIA E MINERAÇÃO', 'ALIMENTAÇÃO E BEBIDAS',
        'TECNOLOGIA', 'CONSTRUÇÃO CIVIL', 'SAÚDE', 'EDUCAÇÃO'
    ]
    segmentos = [
        'ADMINISTRAÇÃO PÚBLICA', 'TELECOMUNICAÇÕES', 'BANCÁRIO', 'VAREJO', 
        'ENERGIA', 'MINERAÇÃO', 'ALIMENTÍCIO', 'SAÚDE', 'EDUCACIONAL'
    ]
    
    # Gerar CNAEs realistas
    cnaes_bancarios = [64191, 64192, 64194, 64631, 64632, 64633, 64634, 64635]
    cnaes_varejo = [47111, 47112, 47113, 47211, 47212, 47311, 47312, 47321]
    cnaes_telecom = [61101, 61102, 61201, 61202, 61301, 61302, 61401, 61402]
    cnaes_energia = [35111, 35112, 35113, 35121, 35122, 35131, 35132, 35140]
    
    todos_cnaes = cnaes_bancarios + cnaes_varejo + cnaes_telecom + cnaes_energia
    
    # Criar dataset
    dados = []
    for i, empresa in enumerate(empresas):
        # Determinar ramo baseado no nome da empresa
        if 'BANCO' in empresa or 'ITAÚ' in empresa or 'BRADESCO' in empresa:
            ramo = 'BANCOS E SERVIÇOS FINANCEIROS'
            segmento = 'BANCÁRIO'
            cnae = random.choice(cnaes_bancarios)
            novos_range = (200, 1500)  # Bancos têm mais processos
        elif 'TELEFÔNICA' in empresa or 'TIM' in empresa or 'CLARO' in empresa:
            ramo = 'TELECOMUNICAÇÕES'
            segmento = 'TELECOMUNICAÇÕES'
            cnae = random.choice(cnaes_telecom)
            novos_range = (150, 800)
        elif 'PETROBRAS' in empresa or 'VALE' in empresa:
            ramo = 'ENERGIA E PETRÓLEO'
            segmento = 'ENERGIA'
            cnae = random.choice(cnaes_energia)
            novos_range = (100, 600)
        else:
            ramo = random.choice(ramos)
            segmento = random.choice(segmentos)
            cnae = random.choice(todos_cnaes)
            novos_range = (50, 400)
        
        novos = random.randint(*novos_range)
        pendentes = novos * random.randint(8, 15)  # Pendentes = 8-15x novos
        
        registro = {
            'NOME': empresa,
            'TRIBUNAL': random.choice(tribunais),
            'GRAU': random.choice(graus),
            'RAMO': ramo,
            'SEGMENTO': segmento,
            'CNAE': cnae,
            'NOVOS': novos,
            'PENDENTES BRUTO': pendentes,
            'PENDENTES LÍQUIDO': int(pendentes * 0.8),  # 80% dos brutos
            'ANO': 2025,
            'MES': random.randint(1, 12)
        }
        dados.append(registro)
    
    # Criar DataFrame Polars
    df = pl.DataFrame(dados)
    
    # Salvar
    df.write_parquet('dados_grandes_litigantes_demo.parquet')
    print(f"✅ Dados de demo criados: {len(df):,} registros")
    print(f"📁 Arquivo: dados_grandes_litigantes_demo.parquet")
    
    # Estatísticas
    print(f"\n📊 Estatísticas:")
    print(f"   - Empresas únicas: {df['NOME'].n_unique():,}")
    print(f"   - Tribunais: {df['TRIBUNAL'].n_unique()}")
    print(f"   - Total processos novos: {df['NOVOS'].sum():,}")
    print(f"   - Tamanho arquivo: {df.estimated_size('mb'):.1f} MB")

if __name__ == "__main__":
    create_demo_data() 
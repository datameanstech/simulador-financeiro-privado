import polars as pl

print("Carregando dados...")
df = pl.read_parquet('dados_grandes_litigantes.parquet')
print(f"Dados carregados: {len(df)} registros")

# Verificar valores únicos para cada coluna
colunas_teste = ['TRIBUNAL', 'GRAU', 'SEGMENTO', 'RAMO']

for coluna in colunas_teste:
    if coluna in df.columns:
        valores_unicos = df.select(coluna).unique().sort(coluna).to_series().to_list()
        valores_nao_nulos = [v for v in valores_unicos if v is not None and str(v).strip() != '']
        
        print(f"\n{coluna}:")
        print(f"  Total únicos: {len(valores_unicos)}")
        print(f"  Não nulos/vazios: {len(valores_nao_nulos)}")
        if len(valores_nao_nulos) > 0:
            print(f"  Primeiros 5: {valores_nao_nulos[:5]}")
        else:
            print(f"  Todos os valores: {valores_unicos}")
    else:
        print(f"\n{coluna}: ❌ Coluna não encontrada")

def testar_valores_unicos():
    try:
        # Carregar dados diretamente
        print("Carregando dados...")
        df = pl.read_parquet('dados_grandes_litigantes.parquet')
        print(f"Dados carregados: {len(df)} registros")
        
        # Verificar valores únicos para cada coluna
        colunas_teste = ['TRIBUNAL', 'GRAU', 'SEGMENTO', 'RAMO', 'CNAE']
        
        for coluna in colunas_teste:
            if coluna in df.columns:
                valores_unicos = df.select(coluna).unique().sort(coluna).to_series().to_list()
                valores_nao_nulos = [v for v in valores_unicos if v is not None and str(v).strip() != '']
                
                print(f"\n{coluna}:")
                print(f"  Total únicos: {len(valores_unicos)}")
                print(f"  Não nulos/vazios: {len(valores_nao_nulos)}")
                if len(valores_nao_nulos) > 0:
                    print(f"  Primeiros 5: {valores_nao_nulos[:5]}")
                else:
                    print(f"  Todos os valores: {valores_unicos}")
            else:
                print(f"\n{coluna}: ❌ Coluna não encontrada")
                
    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    testar_valores_unicos() 
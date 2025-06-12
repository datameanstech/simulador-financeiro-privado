import polars as pl

def testar_api_direto():
    try:
        # Carregar dados como a API faz
        print("Carregando dados...")
        df = pl.read_parquet('dados_grandes_litigantes.parquet')
        print(f"Dados carregados: {len(df)} registros")
        
        # Simular filtros vazios
        filtros_selecionados = {}
        
        # Aplicar filtros (nenhum neste caso)
        df_filtrado = df
        
        print(f"Registros após filtros: {len(df_filtrado)}")
        print(f"Colunas disponíveis: {df_filtrado.columns}")
        
        # Obter valores únicos como a API faz
        filtros_disponiveis = {}
        
        # Tribunais
        if 'TRIBUNAL' in df_filtrado.columns:
            tribunais = df_filtrado.select('TRIBUNAL').unique().sort('TRIBUNAL').to_series().to_list()
            print(f"Tribunais únicos encontrados: {len(tribunais)}")
            if len(tribunais) > 0:
                print(f"Primeiros tribunais: {tribunais[:5]}")
            tribunais = [str(t) for t in tribunais if t is not None]
            filtros_disponiveis['tribunal'] = sorted(tribunais)
            print(f"Tribunais após processamento: {len(filtros_disponiveis['tribunal'])}")
        
        # Graus
        if 'GRAU' in df_filtrado.columns:
            graus = df_filtrado.select('GRAU').unique().sort('GRAU').to_series().to_list()
            print(f"Graus únicos encontrados: {len(graus)}")
            graus = [str(g) for g in graus if g is not None]
            filtros_disponiveis['grau'] = sorted(graus)
            print(f"Graus após processamento: {len(filtros_disponiveis['grau'])}")
        
        # Segmentos
        if 'SEGMENTO' in df_filtrado.columns:
            segmentos = df_filtrado.select('SEGMENTO').unique().sort('SEGMENTO').to_series().to_list()
            print(f"Segmentos únicos encontrados: {len(segmentos)}")
            segmentos = [str(s) for s in segmentos if s is not None]
            filtros_disponiveis['segmento'] = sorted(segmentos)
            print(f"Segmentos após processamento: {len(filtros_disponiveis['segmento'])}")
        
        # Ramos
        if 'RAMO' in df_filtrado.columns:
            ramos = df_filtrado.select('RAMO').unique().sort('RAMO').to_series().to_list()
            print(f"Ramos únicos encontrados: {len(ramos)}")
            ramos = [str(r) for r in ramos if r is not None]
            filtros_disponiveis['ramo'] = sorted(ramos)
            print(f"Ramos após processamento: {len(filtros_disponiveis['ramo'])}")
        
        print(f"\nResultado final:")
        for chave, valores in filtros_disponiveis.items():
            print(f"  {chave}: {len(valores)} valores")
            
    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    testar_api_direto() 
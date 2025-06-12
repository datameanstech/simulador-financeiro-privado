import polars as pl
import json

print("Carregando dados...")
df = pl.read_parquet('dados_grandes_litigantes.parquet')
print(f"Dados carregados: {len(df)} registros")

# Simular a lógica da API
df_filtrado = df
filtros_disponiveis = {}

# Tribunais
if 'TRIBUNAL' in df_filtrado.columns:
    tribunais = df_filtrado.select('TRIBUNAL').unique().sort('TRIBUNAL').to_series().to_list()
    tribunais = [str(t) for t in tribunais if t is not None]
    filtros_disponiveis['tribunal'] = sorted(tribunais)

# Graus
if 'GRAU' in df_filtrado.columns:
    graus = df_filtrado.select('GRAU').unique().sort('GRAU').to_series().to_list()
    graus = [str(g) for g in graus if g is not None]
    filtros_disponiveis['grau'] = sorted(graus)

# Segmentos
if 'SEGMENTO' in df_filtrado.columns:
    segmentos = df_filtrado.select('SEGMENTO').unique().sort('SEGMENTO').to_series().to_list()
    segmentos = [str(s) for s in segmentos if s is not None]
    filtros_disponiveis['segmento'] = sorted(segmentos)

# Ramos
if 'RAMO' in df_filtrado.columns:
    ramos = df_filtrado.select('RAMO').unique().sort('RAMO').to_series().to_list()
    ramos = [str(r) for r in ramos if r is not None]
    filtros_disponiveis['ramo'] = sorted(ramos)

print(f"\nResumo dos filtros:")
for chave, valores in filtros_disponiveis.items():
    print(f"  {chave}: {len(valores)} valores")

# Criar resposta como a API faz
response_data = {
    'success': True,
    'filtros_disponiveis': filtros_disponiveis,
    'total_registros': len(df_filtrado)
}

# Tentar serializar para JSON
json_response = json.dumps(response_data, ensure_ascii=False)
print(f"\nJSON serializado com sucesso!")
print(f"Tamanho da resposta: {len(json_response)} caracteres") 
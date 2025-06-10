#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulador Financeiro Python - Versão Polars
Processa arquivo de 3GB diretamente e oferece interface interativa
"""

import polars as pl
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from pathlib import Path
import numpy as np
from typing import Dict, List, Tuple, Optional
import requests
import io
import tempfile
import re

# Configuração da página
st.set_page_config(
    page_title="Simulador Financeiro - Grandes Litigantes",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def detectar_encoding(arquivo_path: str) -> str:
    """Detecta o encoding do arquivo CSV testando os primeiros bytes"""
    try:
        # Tentar importar chardet para detecção automática
        try:
            import chardet
            with open(arquivo_path, 'rb') as f:
                sample = f.read(10000)  # Ler primeiros 10KB
                result = chardet.detect(sample)
                encoding_detectado = result['encoding']
                confidence = result['confidence']
                st.info(f"🔍 Encoding detectado: {encoding_detectado} (confiança: {confidence:.2f})")
                return encoding_detectado
        except ImportError:
            st.warning("📦 chardet não instalado - usando detecção manual")
    except Exception as e:
        st.warning(f"⚠️ Erro na detecção automática: {e}")
    
    # Detecção manual - testar primeiros bytes
    try:
        with open(arquivo_path, 'rb') as f:
            sample = f.read(1000)
            
        # Verificar BOM UTF-8
        if sample.startswith(b'\xef\xbb\xbf'):
            return 'utf-8-sig'
        
        # Verificar se é UTF-8 válido
        try:
            sample.decode('utf-8')
            return 'utf-8'
        except UnicodeDecodeError:
            pass
        
        # Verificar se é Windows-1252
        try:
            sample.decode('windows-1252')
            return 'windows-1252'
        except UnicodeDecodeError:
            pass
        
        # Fallback para latin-1 (sempre funciona)
        return 'latin-1'
        
    except Exception:
        return 'utf-8'  # Fallback padrão

@st.cache_data
def carregar_dados_do_drive(file_id: str, nome_arquivo: str) -> pl.DataFrame:
    """Carrega dados diretamente do Google Drive com múltiplas estratégias"""
    
    # Estratégias de URL do Google Drive (ordem de prioridade)
    urls_para_tentar = [
        f"https://drive.usercontent.google.com/download?id={file_id}&export=download&authuser=0",
        f"https://drive.google.com/uc?id={file_id}&export=download&confirm=t",
        f"https://drive.google.com/uc?export=download&id={file_id}&confirm=t",
        f"https://docs.google.com/uc?export=download&id={file_id}&confirm=t"
    ]
    
    for i, drive_url in enumerate(urls_para_tentar, 1):
        try:
            st.info(f"📡 Tentativa {i}/3: Baixando {nome_arquivo} do Google Drive")
            st.info(f"🔗 URL: {drive_url}")
            
            # Configurar sessão com headers adequados
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            
            with st.spinner(f"⏳ Conectando ao Google Drive (tentativa {i})..."):
                # Primeira requisição para verificar se precisa de confirmação
                response = session.get(drive_url, stream=True)
                
                # Verificar se o Google Drive está pedindo confirmação de vírus
                response_text = response.text if hasattr(response, 'text') else ""
                
                if any(keyword in response_text.lower() for keyword in ['download_warning', 'virus scan', 'too large', 'can\'t scan']):
                    st.info("⚠️ Arquivo grande detectado - processando confirmação de vírus...")
                    
                    # Estratégias para contornar confirmação
                    confirmation_patterns = [
                        r'confirm=([^&"\s]+)',
                        r'"confirm":"([^"]+)"',
                        r'name="confirm" value="([^"]+)"'
                    ]
                    
                    confirm_token = None
                    for pattern in confirmation_patterns:
                        match = re.search(pattern, response_text)
                        if match:
                            confirm_token = match.group(1)
                            break
                    
                    if confirm_token:
                        # Tentar diferentes formatos de URL de confirmação
                        confirm_urls = [
                            f"{drive_url}&confirm={confirm_token}",
                            f"https://drive.usercontent.google.com/download?id={file_id}&export=download&confirm={confirm_token}&authuser=0",
                            f"https://drive.google.com/uc?export=download&confirm={confirm_token}&id={file_id}"
                        ]
                        
                        for confirm_url in confirm_urls:
                            try:
                                st.info(f"🔄 Tentando confirmação: {confirm_url[:80]}...")
                                response = session.get(confirm_url, stream=True)
                                if response.headers.get('content-type', '').startswith('application/'):
                                    st.success("✅ Confirmação aceita!")
                                    break
                            except:
                                continue
                    else:
                        # Se não encontrar token, tentar URLs pré-confirmadas
                        preconfirmed_urls = [
                            f"https://drive.usercontent.google.com/download?id={file_id}&export=download&confirm=t&authuser=0",
                            f"https://drive.google.com/uc?export=download&confirm=t&id={file_id}"
                        ]
                        
                        for confirm_url in preconfirmed_urls:
                            try:
                                st.info(f"🔄 Tentando pré-confirmação...")
                                response = session.get(confirm_url, stream=True)
                                if not 'text/html' in response.headers.get('content-type', ''):
                                    st.success("✅ Pré-confirmação aceita!")
                                    break
                            except:
                                continue
                
                response.raise_for_status()
            
            # Verificar se realmente baixou conteúdo
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) == 0:
                st.warning(f"⚠️ Tentativa {i} retornou arquivo vazio")
                continue
                
            # Verificar o Content-Type
            content_type = response.headers.get('content-type', '')
            st.info(f"📋 Content-Type: {content_type}")
            
            if 'text/html' in content_type:
                st.warning(f"⚠️ Tentativa {i} retornou HTML (provável página de erro)")
                continue
            
            # Calcular tamanho
            if content_length:
                size_mb = int(content_length) / (1024 * 1024)
                st.info(f"📊 Tamanho do arquivo: {size_mb:.1f} MB")
            
            # Salvar temporariamente
            with tempfile.NamedTemporaryFile(delete=False, suffix='.parquet') as tmp_file:
                st.info("💾 Salvando arquivo temporário...")
                
                total_size = int(content_length) if content_length else 0
                downloaded = 0
                
                if total_size > 1024*1024:  # > 1MB, mostrar progresso
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            tmp_file.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                progress = min(downloaded / total_size, 1.0)
                                progress_bar.progress(progress)
                                status_text.text(f"Baixado: {downloaded/(1024*1024):.1f}MB")
                    
                    progress_bar.empty()
                    status_text.empty()
                else:
                    # Arquivo pequeno, baixar sem progresso
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            tmp_file.write(chunk)
                            downloaded += len(chunk)
                
                tmp_file.flush()
                
                # Verificar se o arquivo foi realmente baixado
                file_size = Path(tmp_file.name).stat().st_size
                if file_size == 0:
                    st.error(f"❌ Tentativa {i}: Arquivo baixado está vazio")
                    Path(tmp_file.name).unlink()
                    continue
                
                st.success(f"✅ Arquivo baixado com sucesso! ({file_size/(1024*1024):.1f} MB)")
                
                # Verificar se é realmente um arquivo Parquet
                try:
                    with open(tmp_file.name, 'rb') as f:
                        # Verificar assinatura Parquet (PAR1 no início e fim)
                        header = f.read(4)
                        if header != b'PAR1':
                            st.error(f"❌ Tentativa {i}: Arquivo baixado não é um Parquet válido")
                            st.info(f"🔍 Header encontrado: {header}")
                            Path(tmp_file.name).unlink()
                            continue
                except Exception as e:
                    st.error(f"❌ Tentativa {i}: Erro ao verificar arquivo: {str(e)}")
                    Path(tmp_file.name).unlink()
                    continue
                
                # Carregar usando a função existente
                df = carregar_dados_grandes(tmp_file.name)
                
                # Limpar arquivo temporário
                try:
                    Path(tmp_file.name).unlink()
                except:
                    pass
                
                if not df.is_empty():
                    st.success(f"🎉 Dados carregados com sucesso da tentativa {i}!")
                    return df
                else:
                    st.warning(f"⚠️ Tentativa {i}: DataFrame vazio após carregamento")
                
        except requests.exceptions.RequestException as e:
            st.warning(f"⚠️ Tentativa {i} falhou: {str(e)}")
            continue
        except Exception as e:
            st.warning(f"⚠️ Tentativa {i} - erro inesperado: {str(e)}")
            continue
    
    # Se chegou aqui, todas as tentativas falharam
    st.error("❌ Todas as tentativas de download falharam")
    st.info("💡 Soluções:")
    st.info("• Verifique se o arquivo no Google Drive é público")
    st.info("• Tente a opção 'Upload de arquivo' como alternativa")
    st.info("• Use 'Dados simulados' para testar o sistema")
    
    return pl.DataFrame()

@st.cache_data  
def gerar_dados_simulados() -> pl.DataFrame:
    """Gera dados simulados para demonstração"""
    import random
    
    st.info("🎭 Gerando dados simulados com empresas brasileiras...")
    
    # Empresas brasileiras conhecidas
    empresas = [
        'BANCO DO BRASIL S.A.', 'ITAÚ UNIBANCO S.A.', 'BRADESCO S.A.', 'SANTANDER BRASIL S.A.',
        'TELEFÔNICA BRASIL S.A.', 'TIM S.A.', 'CLARO S.A.', 'OI S.A.',
        'PETROBRAS S.A.', 'VALE S.A.', 'AMBEV S.A.', 'JBS S.A.',
        'MAGAZINE LUIZA S.A.', 'VIA VAREJO S.A.', 'LOJAS AMERICANAS S.A.', 'B2W DIGITAL S.A.',
        'BANCO SANTANDER S.A.', 'CAIXA ECONÔMICA FEDERAL', 'BANCO INTER S.A.', 'NUBANK S.A.',
        'EMBRAER S.A.', 'GERDAU S.A.', 'USIMINAS S.A.', 'CSN S.A.',
        'CARREFOUR BRASIL S.A.', 'WALMART BRASIL S.A.', 'ATACADÃO S.A.', 'GRUPO PÃO DE AÇÚCAR S.A.'
    ] * 36  # Repetir para ter 1000 registros
    
    ramos = [
        'BANCOS E SERVIÇOS FINANCEIROS', 'TELECOMUNICAÇÕES', 'ENERGIA E PETRÓLEO', 
        'VAREJO E COMÉRCIO', 'SIDERURGIA E MINERAÇÃO', 'ALIMENTAÇÃO E BEBIDAS',
        'TECNOLOGIA', 'CONSTRUÇÃO CIVIL', 'SAÚDE', 'EDUCAÇÃO'
    ]
    
    # Usar seed fixa para dados consistentes
    np.random.seed(42)
    random.seed(42)
    
    dados_fake = {
        'ÓRGÃO': empresas[:1000],
        'TRIBUNAL': np.random.choice(['TRT1', 'TRT2', 'TJSP', 'TRF1', 'TST', 'TJRJ', 'TJMG'], 1000),
        'GRAU': np.random.choice(['1º GRAU', '2º GRAU', 'INSTÂNCIA ÚNICA'], 1000),
        'RAMO': np.random.choice(ramos, 1000),
        'NOVOS': np.random.randint(100, 5000, 1000),
        'PENDENTES BRUTO': np.random.randint(500, 20000, 1000),
        'PENDENTES LÍQUIDO': np.random.randint(300, 15000, 1000),
        'SEGMENTO': np.random.choice(['ADMINISTRAÇÃO PÚBLICA', 'TELECOMUNICAÇÕES', 'BANCÁRIO', 'VAREJO', 'ENERGIA'], 1000)
    }
    
    df = pl.DataFrame(dados_fake)
    st.success(f"✅ Dados simulados gerados: {len(df):,} registros")
    
    return df

@st.cache_data
def carregar_dados_grandes(arquivo_path: str) -> pl.DataFrame:
    """Carrega e processa o arquivo de 3GB com cache - versão otimizada para Parquet e CSV"""
    try:
        file_path = Path(arquivo_path)
        file_extension = file_path.suffix.lower()
        file_size = file_path.stat().st_size
        
        st.info(f"🔄 Carregando arquivo {file_extension.upper()} de {file_size/(1024**3):.1f}GB...")
        
        df = None
        n_rows = None  # Inicializar variável para evitar erro
        
        # PARQUET: Muito mais eficiente - carregar arquivo completo
        if file_extension == '.parquet':
            try:
                st.info("🚀 Carregando arquivo Parquet (formato otimizado)...")
                
                # Para arquivos muito grandes, usar lazy loading
                if file_size > 1024**3:  # > 1GB
                    df_lazy = pl.scan_parquet(arquivo_path)
                    df = df_lazy.collect(streaming=True)
                    st.success("✅ Arquivo Parquet carregado com lazy loading")
                else:
                    df = pl.read_parquet(arquivo_path)
                    st.success("✅ Arquivo Parquet carregado diretamente")
                    
            except Exception as e:
                st.error(f"❌ Erro ao carregar Parquet: {str(e)}")
                return pl.DataFrame()
        
        # CSV: Fallback para arquivos antigos
        else:
            # Primeiro, tentar detectar o encoding automaticamente
            encoding_detectado = detectar_encoding(arquivo_path)
            
            # Carregar apenas uma amostra para arquivos muito grandes (>1GB)
            if file_size > 1024**3:  # > 1GB
                st.warning("📊 Arquivo CSV muito grande! Carregando amostra otimizada para evitar problemas de memória...")
                n_rows = 100000  # Carregar apenas 100k linhas
            else:
                n_rows = None
            
            # ESTRATÉGIA 1: Tentar com scan_csv (mais eficiente)
            try:
                st.info("🚀 Tentando carregamento eficiente com scan_csv...")
                df_lazy = pl.scan_csv(
                    arquivo_path,
                    separator=";",
                    encoding="utf8-lossy",  # Polars scan_csv só aceita utf8 ou utf8-lossy
                    ignore_errors=True,
                    truncate_ragged_lines=True
                )
                if n_rows:
                    df = df_lazy.head(n_rows).collect()
                else:
                    df = df_lazy.collect()
                st.success("✅ Arquivo carregado com scan_csv (otimizado)")
                
            except Exception as e:
                st.warning(f"⚠️ scan_csv falhou: {str(e)[:100]}...")
                
                # ESTRATÉGIA 2: Fallback para read_csv com diferentes encodings
                encodings = [encoding_detectado, 'utf-8', 'iso-8859-1', 'latin-1', 'windows-1252', 'cp1252', 'utf-8-sig']
                # Remover duplicatas mantendo a ordem
                encodings = list(dict.fromkeys(encodings))
                
                for encoding in encodings:
                    try:
                        st.info(f"🧪 Tentando carregar com encoding: {encoding}")
                        df = pl.read_csv(
                            arquivo_path,
                            separator=";",
                            encoding=encoding,
                            ignore_errors=True,
                            truncate_ragged_lines=True,
                            n_rows=n_rows  # Limitar linhas para arquivos grandes
                        )
                        st.success(f"✅ Arquivo carregado com encoding: {encoding}")
                        break
                    except Exception as e2:
                        st.warning(f"⚠️ Falhou com {encoding}: {str(e2)[:100]}...")
                        continue
        
        if df is None:
            st.error("❌ Não foi possível carregar o arquivo com nenhuma estratégia")
            return pl.DataFrame()
        
        if n_rows:
            st.info(f"📈 Carregadas {len(df):,} linhas (amostra otimizada de arquivo {file_size/(1024**3):.1f}GB)")
        else:
            st.info(f"📈 Carregadas {len(df):,} linhas do arquivo {file_size/(1024**3):.1f}GB")
        
        # Limpeza básica
        st.info("🧹 Limpando e validando dados...")
        
        # Corrigir nomes de colunas com caracteres mal codificados
        colunas_corrigidas = {}
        for col in df.columns:
            if 'RG O' in col:
                colunas_corrigidas[col] = 'ÓRGÃO'
            elif 'CLASSIFICA' in col and ' ' in col:
                colunas_corrigidas[col] = 'CLASSIFICAÇÃO'
            elif 'PENDENTES' in col and 'LQUIDO' in col:
                colunas_corrigidas[col] = 'PENDENTES LÍQUIDO'
            elif 'DIFEREN' in col and 'LQUIDO' in col:
                colunas_corrigidas[col] = 'DIFERENCA_PENDENTES_LÍQUIDO'
        
        # Renomear colunas se necessário
        if colunas_corrigidas:
            df = df.rename(colunas_corrigidas)
            st.info(f"🔧 Colunas corrigidas: {', '.join(colunas_corrigidas.values())}")
        
        # Verificar se as colunas essenciais existem (flexível)
        colunas_essenciais = ['NOVOS', 'TRIBUNAL']
        
        # Para o nome da empresa, PREFERIR 'NOME' sobre 'ÓRGÃO'
        # Baseado na análise: ÓRGÃO = gabinetes/zonas eleitorais, NOME = empresas reais
        coluna_empresa = None
        for possivel_nome in ['NOME', 'EMPRESA', 'ÓRGÃO', 'ORGAO']:  # NOME primeiro!
            if possivel_nome in df.columns:
                coluna_empresa = possivel_nome
                break
        
        if not coluna_empresa:
            st.error("❌ Nenhuma coluna de empresa encontrada (NOME, EMPRESA, ÓRGÃO, ORGAO)")
            st.info(f"Colunas disponíveis: {', '.join(df.columns)}")
            return pl.DataFrame()
        
        # Adicionar coluna de empresa às essenciais
        colunas_essenciais.append(coluna_empresa)
        
        # Verificar todas as colunas essenciais
        colunas_existentes = df.columns
        for col in colunas_essenciais:
            if col not in colunas_existentes:
                st.error(f"❌ Coluna essencial '{col}' não encontrada no arquivo")
                st.info(f"Colunas disponíveis: {', '.join(colunas_existentes)}")
                return pl.DataFrame()
        
        # Se a coluna de empresa não é 'ÓRGÃO', criar um alias
        if coluna_empresa != 'ÓRGÃO':
            df = df.with_columns(pl.col(coluna_empresa).alias('ÓRGÃO'))
            st.info(f"✅ Usando coluna '{coluna_empresa}' como nome da empresa")
        
        # Filtrar apenas registros válidos
        # Baseado na análise: 35.7% têm NOVOS=0, então filtrar NOVOS > 0 é necessário
        df_validos = df.filter(
            (pl.col('NOVOS').is_not_null()) &
            (pl.col('NOVOS').cast(pl.Int32, strict=False) > 0) &  # Excluir NOVOS = 0
            (pl.col('ÓRGÃO').is_not_null()) &
            (pl.col('TRIBUNAL').is_not_null())
        )
        
        # Filtro adicional: remover gabinetes/zonas eleitorais se estiver usando coluna inadequada
        if coluna_empresa == 'ÓRGÃO':
            st.info("🔍 Aplicando filtro para remover gabinetes e zonas eleitorais...")
            df_validos = df_validos.filter(
                ~pl.col('ÓRGÃO').str.to_lowercase().str.contains('gabinete|zona eleitoral|juiz|jurista|tribunal|ministério|secretaria|prefeitura|câmara')
            )
            st.info(f"💡 Sugestão: Este arquivo parece ter coluna 'NOME' com empresas reais")
        
        # Se restaram poucos registros, avisar
        if len(df_validos) < len(df) * 0.1:  # Menos de 10%
            st.warning(f"⚠️ Apenas {len(df_validos):,} registros válidos de {len(df):,} total ({len(df_validos)/len(df)*100:.1f}%)")
            st.info("💡 Isso pode indicar que os dados são principalmente de órgãos públicos, não empresas privadas")
        
        st.success(f"✅ Dados carregados: {len(df_validos):,} registros válidos de {len(df):,} total")
        
        # Mostrar informações sobre as colunas
        st.info(f"📋 Colunas encontradas: {', '.join(df.columns)}")
        
        return df_validos
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar arquivo: {e}")
        st.info("💡 Dicas para resolver:")
        st.info("• Para arquivos >1GB: Usando amostra otimizada automaticamente")
        st.info("• Tente usar 'Upload de arquivo' em vez de 'Caminho local'")
        st.info("• Use 'Dados simulados' para testar o simulador")
        st.info("• Verifique se o arquivo não está aberto em outro programa")
        return pl.DataFrame()

def calcular_financas(volume: int, preco: float, custo_base: int, clientes: int, reinvestimento: float) -> Dict:
    """Cálculos financeiros baseados no simulador original"""
    
    # Custo progressivo por volume (10% do custo base a cada 1000 processos acima de 10.000)
    custo_progressivo = 0
    if volume > 10000:
        excesso = volume - 10000
        incrementos = np.ceil(excesso / 1000)
        custo_progressivo = incrementos * (custo_base * 0.10)
    
    # Custo de relacionamento (R$ 10.000 para cada 3 clientes)
    custo_relacionamento = 0
    if clientes >= 3:
        grupos = clientes // 3
        custo_relacionamento = grupos * 10000
    
    # Custo operacional (R$ 1,00 por processo)
    custo_operacional = volume * 1.0
    
    # Cálculos principais
    custo_total = custo_base + custo_progressivo + custo_relacionamento + custo_operacional
    receita_bruta = volume * preco
    lucro_bruto = receita_bruta - custo_total
    
    # Impostos (Simples Nacional)
    rbt12 = receita_bruta * 12
    if rbt12 <= 180000:
        aliquota, deducao = 0.155, 0
    elif rbt12 <= 360000:
        aliquota, deducao = 0.18, 4500
    elif rbt12 <= 720000:
        aliquota, deducao = 0.195, 9900
    elif rbt12 <= 1800000:
        aliquota, deducao = 0.205, 17100
    elif rbt12 <= 3600000:
        aliquota, deducao = 0.23, 62100
    else:
        aliquota, deducao = 0.305, 540000
    
    taxa_efetiva = ((rbt12 * aliquota) - deducao) / rbt12 if rbt12 > 0 else 0
    impostos = receita_bruta * taxa_efetiva
    
    lucro_liquido = lucro_bruto - impostos
    margem_liquida = (lucro_liquido / receita_bruta * 100) if receita_bruta > 0 else 0
    
    # Reinvestimento
    valor_reinvestimento = lucro_liquido * (reinvestimento / 100) if lucro_liquido > 0 else 0
    valor_distribuicao = lucro_liquido - valor_reinvestimento
    
    return {
        'receita_bruta': receita_bruta,
        'custo_total': custo_total,
        'custo_base': custo_base,
        'custo_progressivo': custo_progressivo,
        'custo_relacionamento': custo_relacionamento,
        'custo_operacional': custo_operacional,
        'lucro_bruto': lucro_bruto,
        'impostos': impostos,
        'lucro_liquido': lucro_liquido,
        'margem_liquida': margem_liquida,
        'valor_reinvestimento': valor_reinvestimento,
        'valor_distribuicao': valor_distribuicao
    }

def encontrar_break_even(preco: float, custo_base: int, clientes: int) -> int:
    """Encontra o ponto de equilíbrio"""
    for volume in range(0, 50000, 100):
        resultado = calcular_financas(volume, preco, custo_base, clientes, 0)
        if resultado['lucro_liquido'] >= 0:
            return volume
    return 0

def gerar_relatorio_detalhado(df: pl.DataFrame):
    """Gera relatório detalhado por porte de empresas, ramo e segmento"""
    
    st.title("📊 Relatório Detalhado - Análise de Empresas")
    st.markdown("---")
    
    # Botão para voltar
    if st.button("← Voltar ao Simulador"):
        st.session_state.pagina_atual = "simulador"
        st.rerun()
    
    # Filtros adicionais para relatório detalhado
    st.sidebar.header("🔍 Filtros do Relatório")
    
    # Filtro por tribunal
    if 'TRIBUNAL' in df.columns:
        tribunais_disponiveis = ['Todos'] + sorted(df['TRIBUNAL'].unique().to_list())
        tribunal_filtro = st.sidebar.selectbox("🏛️ Filtrar por Tribunal:", tribunais_disponiveis, key="relatorio_tribunal")
        if tribunal_filtro != 'Todos':
            df = df.filter(pl.col('TRIBUNAL') == tribunal_filtro)
    
    # Filtro por segmento
    if 'SEGMENTO' in df.columns:
        segmentos_disponiveis = df.filter(pl.col('SEGMENTO').is_not_null())['SEGMENTO'].unique().to_list()
        segmentos = ['Todos'] + sorted(segmentos_disponiveis)
        segmento_filtro = st.sidebar.selectbox("🏢 Filtrar por Segmento:", segmentos, key="relatorio_segmento")
        if segmento_filtro != 'Todos':
            df = df.filter(pl.col('SEGMENTO') == segmento_filtro)
    
    # Filtro por faixa de volume
    volume_minimo = st.sidebar.number_input("📊 Volume mínimo (proc/mês):", min_value=0, value=0, step=50, key="relatorio_volume_min")
    volume_maximo = st.sidebar.number_input("📊 Volume máximo (proc/mês):", min_value=0, value=10000, step=50, key="relatorio_volume_max")
    
    st.markdown("---")
    
    # Calcular processos mensais se não existir
    if 'processos_mensais_estimado' not in df.columns and 'volume_mensal' not in df.columns:
        df = calcular_processos_mensais(df)
    
    # Aplicar filtros de volume
    if 'volume_mensal' in df.columns:
        df = df.filter(
            (pl.col('volume_mensal') >= volume_minimo) & 
            (pl.col('volume_mensal') <= volume_maximo)
        )
    elif 'processos_mensais_estimado' in df.columns:
        df = df.filter(
            (pl.col('processos_mensais_estimado') >= volume_minimo) & 
            (pl.col('processos_mensais_estimado') <= volume_maximo)
        )
    
    # === 1. ANÁLISE POR PORTE DE EMPRESAS ===
    st.header("🏢 Distribuição de Empresas por Porte (Volume Mensal)")
    
    # Usar a coluna correta de volume mensal
    coluna_volume = 'volume_mensal' if 'volume_mensal' in df.columns else 'processos_mensais_estimado'
    
    # Definir faixas de porte
    df_com_faixas = df.with_columns([
        pl.when(pl.col(coluna_volume) >= 5000)
        .then(pl.lit("🚀 Acima de 5.000"))
        .when(pl.col(coluna_volume) >= 2000)
        .then(pl.lit("🏭 Entre 2.000 e 5.000"))
        .when(pl.col(coluna_volume) >= 1000)
        .then(pl.lit("🏢 Entre 1.000 e 2.000"))
        .when(pl.col(coluna_volume) >= 500)
        .then(pl.lit("🏬 Entre 500 e 1.000"))
        .otherwise(pl.lit("🏪 Menos de 500"))
        .alias("faixa_porte")
    ])
    
    # Calcular estatísticas por faixa
    analise_porte = df_com_faixas.group_by("faixa_porte").agg([
        pl.len().alias("Quantidade_Empresas"),
        pl.col(coluna_volume).sum().alias("Volume_Total_Mensal"),
        pl.col(coluna_volume).mean().alias("Volume_Medio_Mensal"),
        pl.col('NOVOS').sum().alias("Total_Novos"),
        pl.col('PENDENTES BRUTO').sum().alias("Total_Pendentes")
    ]).sort("Volume_Total_Mensal", descending=True)
    
    # Converter para pandas para visualização
    df_porte_pandas = analise_porte.to_pandas()
    
    # Adicionar percentuais
    total_empresas = df_porte_pandas['Quantidade_Empresas'].sum()
    df_porte_pandas['Percentual_Empresas'] = (df_porte_pandas['Quantidade_Empresas'] / total_empresas * 100).round(1)
    
    total_volume = df_porte_pandas['Volume_Total_Mensal'].sum()
    df_porte_pandas['Percentual_Volume'] = (df_porte_pandas['Volume_Total_Mensal'] / total_volume * 100).round(1)
    
    # Métricas gerais
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Total de Empresas", f"{total_empresas:,}")
    with col2:
        st.metric("📈 Volume Total/Mês", f"{total_volume:,.0f}")
    with col3:
        grandes_empresas = df_porte_pandas[df_porte_pandas['faixa_porte'].str.contains('Acima de 5.000')]['Quantidade_Empresas'].sum()
        st.metric("🚀 Grandes (>5k)", f"{grandes_empresas:,}")
    with col4:
        pequenas_empresas = df_porte_pandas[df_porte_pandas['faixa_porte'].str.contains('Menos de 500')]['Quantidade_Empresas'].sum()
        st.metric("🏪 Pequenas (<500)", f"{pequenas_empresas:,}")
    
    # Tabela principal
    st.subheader("📋 Distribuição por Faixas de Volume")
    
    # Formatar tabela para exibição
    df_display = df_porte_pandas.copy()
    df_display['Volume_Total_Mensal'] = df_display['Volume_Total_Mensal'].apply(lambda x: f"{x:,.0f}")
    df_display['Volume_Medio_Mensal'] = df_display['Volume_Medio_Mensal'].apply(lambda x: f"{x:,.0f}")
    df_display['Total_Novos'] = df_display['Total_Novos'].apply(lambda x: f"{x:,}")
    df_display['Total_Pendentes'] = df_display['Total_Pendentes'].apply(lambda x: f"{x:,}")
    df_display['Percentual_Empresas'] = df_display['Percentual_Empresas'].apply(lambda x: f"{x}%")
    df_display['Percentual_Volume'] = df_display['Percentual_Volume'].apply(lambda x: f"{x}%")
    
    # Renomear colunas
    df_display = df_display.rename(columns={
        'faixa_porte': 'Faixa de Porte',
        'Quantidade_Empresas': 'Qtd Empresas',
        'Volume_Total_Mensal': 'Volume Total/Mês',
        'Volume_Medio_Mensal': 'Volume Médio/Mês',
        'Total_Novos': 'Processos Novos',
        'Total_Pendentes': 'Processos Pendentes',
        'Percentual_Empresas': '% Empresas',
        'Percentual_Volume': '% Volume'
    })
    
    st.dataframe(df_display, use_container_width=True)
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Distribuição de Empresas")
        fig_empresas = px.pie(
            df_porte_pandas,
            values='Quantidade_Empresas',
            names='faixa_porte',
            title='Quantidade de Empresas por Porte'
        )
        st.plotly_chart(fig_empresas, use_container_width=True)
    
    with col2:
        st.subheader("📈 Concentração de Volume")
        fig_volume = px.pie(
            df_porte_pandas,
            values='Volume_Total_Mensal',
            names='faixa_porte',
            title='Volume de Processos por Porte'
        )
        st.plotly_chart(fig_volume, use_container_width=True)
    
    # === 2. ANÁLISE POR RAMO ===
    st.markdown("---")
    st.header("🌳 Análise por Ramo de Atividade")
    
    if 'RAMO' in df.columns:
        analise_ramo = df_com_faixas.group_by(['RAMO', 'faixa_porte']).agg([
            pl.len().alias("Quantidade_Empresas"),
            pl.col(coluna_volume).sum().alias("Volume_Total_Mensal"),
            pl.col('NOVOS').sum().alias("Total_Novos")
        ]).sort(['RAMO', 'Volume_Total_Mensal'], descending=[False, True])
        
        df_ramo_pandas = analise_ramo.to_pandas()
        
        if len(df_ramo_pandas) > 0:
            # Resumo por ramo
            resumo_ramo = df.group_by('RAMO').agg([
                pl.len().alias("Total_Empresas"),
                pl.col(coluna_volume).sum().alias("Volume_Total"),
                pl.col(coluna_volume).mean().alias("Volume_Medio")
            ]).sort("Volume_Total", descending=True).to_pandas()
            
            st.subheader("📊 Resumo por Ramo")
            st.dataframe(resumo_ramo, use_container_width=True)
            
            # Gráfico de barras por ramo
            fig_ramo = px.bar(
                df_ramo_pandas,
                x='RAMO',
                y='Volume_Total_Mensal',
                color='faixa_porte',
                title='Volume de Processos por Ramo e Porte',
                labels={'Volume_Total_Mensal': 'Volume Mensal', 'RAMO': 'Ramo'}
            )
            fig_ramo.update_layout(xaxis_tickangle=-45, height=600)
            st.plotly_chart(fig_ramo, use_container_width=True)
            
            # Tabela detalhada por ramo
            with st.expander("📋 Dados Detalhados por Ramo"):
                st.dataframe(df_ramo_pandas, use_container_width=True)
        else:
            st.info("Nenhum dado de ramo disponível.")
    else:
        st.info("⚠️ Coluna 'RAMO' não está disponível nos dados.")
    
    # === 3. ANÁLISE POR SEGMENTO ===
    st.markdown("---")
    st.header("🏭 Análise por Segmento")
    
    if 'SEGMENTO' in df.columns:
        analise_segmento = df_com_faixas.group_by(['SEGMENTO', 'faixa_porte']).agg([
            pl.len().alias("Quantidade_Empresas"),
            pl.col(coluna_volume).sum().alias("Volume_Total_Mensal"),
            pl.col('NOVOS').sum().alias("Total_Novos")
        ]).sort(['SEGMENTO', 'Volume_Total_Mensal'], descending=[False, True])
        
        df_segmento_pandas = analise_segmento.to_pandas()
        
        if len(df_segmento_pandas) > 0:
            # Resumo por segmento
            resumo_segmento = df.group_by('SEGMENTO').agg([
                pl.len().alias("Total_Empresas"),
                pl.col(coluna_volume).sum().alias("Volume_Total"),
                pl.col(coluna_volume).mean().alias("Volume_Medio")
            ]).sort("Volume_Total", descending=True).to_pandas()
            
            st.subheader("📊 Resumo por Segmento")
            st.dataframe(resumo_segmento, use_container_width=True)
            
            # Gráfico de barras por segmento
            fig_segmento = px.bar(
                df_segmento_pandas,
                x='SEGMENTO',
                y='Volume_Total_Mensal',
                color='faixa_porte',
                title='Volume de Processos por Segmento e Porte',
                labels={'Volume_Total_Mensal': 'Volume Mensal', 'SEGMENTO': 'Segmento'}
            )
            fig_segmento.update_layout(xaxis_tickangle=-45, height=600)
            st.plotly_chart(fig_segmento, use_container_width=True)
            
            # Tabela detalhada por segmento
            with st.expander("📋 Dados Detalhados por Segmento"):
                st.dataframe(df_segmento_pandas, use_container_width=True)
        else:
            st.info("Nenhum dado de segmento disponível.")
    else:
        st.info("⚠️ Coluna 'SEGMENTO' não está disponível nos dados.")
    
    # === 4. ANÁLISE CRUZADA RAMO vs SEGMENTO ===
    if 'RAMO' in df.columns and 'SEGMENTO' in df.columns:
        st.markdown("---")
        st.header("🔀 Análise Cruzada: Ramo vs Segmento")
        
        # Matriz ramo x segmento
        matriz_cruzada = df.group_by(['RAMO', 'SEGMENTO']).agg([
            pl.len().alias("Quantidade_Empresas"),
            pl.col('processos_mensais_estimado').sum().alias("Volume_Total")
        ])
        
        df_matriz_pandas = matriz_cruzada.to_pandas()
        
        if len(df_matriz_pandas) > 0:
            # Criar pivot table
            pivot_ramo_segmento = df_matriz_pandas.pivot(
                index='RAMO', 
                columns='SEGMENTO', 
                values='Volume_Total'
            ).fillna(0)
            
            # Mapa de calor
            fig_heatmap = px.imshow(
                pivot_ramo_segmento.values,
                x=pivot_ramo_segmento.columns,
                y=pivot_ramo_segmento.index,
                title='Mapa de Calor: Volume por Ramo vs Segmento',
                aspect="auto",
                color_continuous_scale='Blues'
            )
            fig_heatmap.update_layout(height=600)
            st.plotly_chart(fig_heatmap, use_container_width=True)
            
            # Tabela da matriz
            with st.expander("📋 Matriz Detalhada Ramo vs Segmento"):
                st.dataframe(df_matriz_pandas, use_container_width=True)

def verificar_senha():
    """Verifica se o usuário está autenticado"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.title("🔐 Acesso Restrito - Simulador Jurídico")
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### Entre com a senha de acesso:")
            
            senha_inserida = st.text_input(
                "Senha:", 
                type="password", 
                placeholder="Digite a senha...",
                key="senha_input"
            )
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
            with col_btn2:
                if st.button("🔑 Acessar", use_container_width=True, type="primary"):
                    # Buscar senha dos secrets (mais seguro) ou usar padrão
                    try:
                        SENHA_CORRETA = st.secrets["passwords"]["admin_password"]
                    except:
                        SENHA_CORRETA = "pdpj2024"  # ⚠️ Senha padrão - ALTERE!
                    
                    if senha_inserida == SENHA_CORRETA:
                        st.session_state.authenticated = True
                        st.success("✅ Acesso autorizado!")
                        st.rerun()
                    else:
                        st.error("❌ Senha incorreta!")
            
            st.markdown("---")
            st.info("💡 **Para administradores:** Entre em contato para obter acesso.")
            
        return False
    
    return True

def main():
    # Verificar autenticação antes de continuar
    if not verificar_senha():
        return
    
    st.title("🚀 Simulador Financeiro - Grandes Litigantes")
    st.markdown("**Versão Python com Polars** - Processa arquivos de 3GB+ diretamente")
    
    # Botão de logout na sidebar
    with st.sidebar:
        st.markdown("---")
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()
    
    # Inicializar estado da sessão
    if 'pagina_atual' not in st.session_state:
        st.session_state.pagina_atual = "simulador"
    
    # Verificar qual página mostrar
    if st.session_state.pagina_atual == "relatorio":
        # Carregar dados se necessário
        if 'dados_relatorio' in st.session_state:
            gerar_relatorio_detalhado(st.session_state.dados_relatorio)
        else:
            st.error("❌ Dados não encontrados. Volte ao simulador e carregue os dados primeiro.")
            if st.button("← Voltar ao Simulador"):
                st.session_state.pagina_atual = "simulador"
                st.rerun()
        return
    
    # Sidebar para controles
    st.sidebar.header("🎛️ Configurações")
    
    # Upload ou caminho do arquivo
    arquivo_opcao = st.sidebar.radio(
        "Fonte de dados:",
        ["🚀 Google Drive (Recomendado)", "📁 Upload de arquivo", "🔧 Caminho local", "🎭 Dados simulados"]
    )
    
    df = pl.DataFrame()
    
    if arquivo_opcao == "🚀 Google Drive (Recomendado)":
        st.sidebar.info("📡 Carregando do arquivo padrão no Google Drive")
        st.sidebar.markdown("**Arquivo:** `grandes_litigantes_202504.parquet` (237MB)")
        st.sidebar.markdown("**Status:** ✅ Público e verificado")
        
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            if st.button("🚀 Carregar do Drive", help="Carrega automaticamente do Google Drive"):
                file_id = "1Ns07hTZaK4Ry6bFEHvLACZ5tHJ7b-C2E"
                df = carregar_dados_do_drive(file_id, "grandes_litigantes_202504.parquet")
        
        with col2:
            if st.button("🎭 Usar Simulados", help="Usa dados simulados se o Drive falhar"):
                st.info("🎭 Carregando dados simulados...")
                df = gerar_dados_simulados()
        
        # Opções avançadas para Google Drive
        with st.sidebar.expander("🔧 Configurações do Drive"):
            st.markdown("**Problemas com Google Drive?**")
            
            custom_file_id = st.text_input(
                "ID do arquivo (se tiver outro link):",
                value="1Ns07hTZaK4Ry6bFEHvLACZ5tHJ7b-C2E",
                help="Cole aqui apenas o ID do arquivo do Google Drive"
            )
            
            if st.button("🔄 Tentar com ID personalizado"):
                if custom_file_id:
                    df = carregar_dados_do_drive(custom_file_id, "arquivo_personalizado.parquet")
            
            st.markdown("---")
            st.markdown("**💡 Como tornar arquivo público:**")
            st.markdown("1. Abra o Google Drive")
            st.markdown("2. Clique direito no arquivo → Compartilhar")
            st.markdown("3. Mude para 'Qualquer pessoa na internet'")
            st.markdown("4. Cole o novo ID do arquivo acima")
    
    elif arquivo_opcao == "📁 Upload de arquivo":
        uploaded_file = st.sidebar.file_uploader(
            "Escolha o arquivo (3GB+)",
            type=['csv', 'parquet'],
            help="Arquivo Parquet é mais eficiente que CSV"
        )
        if uploaded_file:
            df = carregar_dados_grandes(uploaded_file)
            
    elif arquivo_opcao == "🔧 Caminho local":
        st.sidebar.info("🗂️ Opções avançadas para arquivos locais")
        
        # OPÇÃO 1: Verificar se há arquivo local na pasta do deploy
        arquivos_locais = [
            "grandes_litigantes_202504.parquet",
            "grandes_litigantes_por_orgao 202504.parquet", 
            "dados.parquet",
            "dados.csv"
        ]
        
        arquivo_encontrado = None
        for arquivo in arquivos_locais:
            if Path(arquivo).exists():
                arquivo_encontrado = arquivo
                break
        
        if arquivo_encontrado:
            st.sidebar.success(f"📁 Arquivo local encontrado: {arquivo_encontrado}")
            if st.sidebar.button("🗂️ Carregar arquivo local"):
                df = carregar_dados_grandes(arquivo_encontrado)
        else:
            # OPÇÃO 2: Caminho manual
            with st.sidebar.expander("📝 Caminho personalizado"):
                caminho = st.text_input(
                    "Caminho do arquivo:",
                    value="grandes_litigantes_202504.parquet"
                )
                if caminho and Path(caminho).exists():
                    if st.button("📂 Carregar"):
                        df = carregar_dados_grandes(caminho)
                elif caminho:
                    st.error("Arquivo não encontrado")
            
    else:  # Dados simulados (🎭 Dados simulados)
        st.sidebar.info("Usando dados simulados para demonstração")
        # Criar dados fake para teste com empresas reais
        np.random.seed(42)
        
        # Empresas brasileiras conhecidas
        empresas = [
            'BANCO DO BRASIL S.A.', 'ITAÚ UNIBANCO S.A.', 'BRADESCO S.A.', 'SANTANDER BRASIL S.A.',
            'TELEFÔNICA BRASIL S.A.', 'TIM S.A.', 'CLARO S.A.', 'OI S.A.',
            'PETROBRAS S.A.', 'VALE S.A.', 'AMBEV S.A.', 'JBS S.A.',
            'MAGAZINE LUIZA S.A.', 'VIA VAREJO S.A.', 'LOJAS AMERICANAS S.A.', 'B2W DIGITAL S.A.',
            'BANCO SANTANDER S.A.', 'CAIXA ECONÔMICA FEDERAL', 'BANCO INTER S.A.', 'NUBANK S.A.',
            'EMBRAER S.A.', 'GERDAU S.A.', 'USIMINAS S.A.', 'CSN S.A.',
            'CARREFOUR BRASIL S.A.', 'WALMART BRASIL S.A.', 'ATACADÃO S.A.', 'GRUPO PÃO DE AÇÚCAR S.A.'
        ] * 36  # Repetir para ter 1000 registros
        
        ramos = [
            'BANCOS E SERVIÇOS FINANCEIROS', 'TELECOMUNICAÇÕES', 'ENERGIA E PETRÓLEO', 
            'VAREJO E COMÉRCIO', 'SIDERURGIA E MINERAÇÃO', 'ALIMENTAÇÃO E BEBIDAS',
            'TECNOLOGIA', 'CONSTRUÇÃO CIVIL', 'SAÚDE', 'EDUCAÇÃO'
        ]
        
        dados_fake = {
            'ÓRGÃO': empresas[:1000],
            'TRIBUNAL': np.random.choice(['TRT1', 'TRT2', 'TJSP', 'TRF1', 'TST', 'TJRJ', 'TJMG'], 1000),
            'GRAU': np.random.choice(['1º GRAU', '2º GRAU', 'INSTÂNCIA ÚNICA'], 1000),
            'RAMO': np.random.choice(ramos, 1000),
            'NOVOS': np.random.randint(100, 5000, 1000),
            'PENDENTES BRUTO': np.random.randint(500, 20000, 1000),
            'PENDENTES LÍQUIDO': np.random.randint(300, 15000, 1000),
            'SEGMENTO': np.random.choice(['ADMINISTRAÇÃO PÚBLICA', 'TELECOMUNICAÇÕES', 'BANCÁRIO', 'VAREJO', 'ENERGIA'], 1000)
        }
        df = pl.DataFrame(dados_fake)
    
    if df.is_empty():
        st.warning("⚠️ Carregue um arquivo para começar")
        return
    
    # Filtros principais
    st.sidebar.header("🔍 Filtros de Dados")
    
    # Opção de agrupamento
    agrupar_empresas = st.sidebar.checkbox(
        "🏢 Agrupar empresas duplicadas", 
        value=True,
        help="Remove duplicatas de empresas que aparecem em múltiplos tribunais/graus"
    )
    
    # Filtro por tribunal
    tribunais_disponiveis = ['Todos'] + sorted(df['TRIBUNAL'].unique().to_list())
    tribunal_selecionado = st.sidebar.selectbox("🏛️ Tribunal:", tribunais_disponiveis)
    
    # Filtro por grau (se existir)
    if 'GRAU' in df.columns:
        graus_disponiveis = ['Todos'] + sorted(df['GRAU'].unique().to_list())
        grau_selecionado = st.sidebar.selectbox("⚖️ Grau:", graus_disponiveis)
    else:
        grau_selecionado = 'Todos'
    
    # Filtro por segmento
    if 'SEGMENTO' in df.columns:
        segmentos_disponiveis = df.filter(pl.col('SEGMENTO').is_not_null())['SEGMENTO'].unique().to_list()
        segmentos = ['Todos'] + sorted(segmentos_disponiveis)
        segmento_selecionado = st.sidebar.selectbox("🏢 Segmento:", segmentos)
    else:
        segmento_selecionado = 'Todos'
    
    # Aplicar filtros
    df_filtrado = df
    if tribunal_selecionado != 'Todos':
        df_filtrado = df_filtrado.filter(pl.col('TRIBUNAL') == tribunal_selecionado)
    if grau_selecionado != 'Todos' and 'GRAU' in df.columns:
        df_filtrado = df_filtrado.filter(pl.col('GRAU') == grau_selecionado)
    if segmento_selecionado != 'Todos' and 'SEGMENTO' in df.columns:
        df_filtrado = df_filtrado.filter(pl.col('SEGMENTO') == segmento_selecionado)
    
    # Agrupar por empresa se solicitado
    if agrupar_empresas:
        df_processado = agrupar_por_empresa(df_filtrado)
    else:
        df_processado = df_filtrado
    
    # Calcular processos mensais para cada órgão
    df_com_mensal = calcular_processos_mensais(df_processado)
    
    # Seleção de empresa específica
    st.sidebar.header("🏢 Seleção por Empresa")
    
    # Buscar empresa por nome
    busca_empresa = st.sidebar.text_input(
        "🔍 Buscar empresa:",
        placeholder="Digite parte do nome da empresa..."
    )
    
    # Filtrar empresas pela busca
    if busca_empresa:
        df_empresas = df_com_mensal.filter(
            pl.col('ÓRGÃO').str.to_lowercase().str.contains(busca_empresa.lower())
        )
    else:
        df_empresas = df_com_mensal
    
    # Top empresas por volume
    df_top_empresas = df_empresas.sort('volume_mensal', descending=True).head(50)
    
    if len(df_top_empresas) > 0:
        # Lista de empresas para seleção com informações relevantes
        empresas_opcoes = ['Selecionar manualmente...']
        
        for row in df_top_empresas.to_dicts():
            # Extrair nome da empresa (limpar sufixos comuns)
            nome_empresa = row['ÓRGÃO']
            # Simplificar nome da empresa
            nome_empresa = nome_empresa.replace(' LTDA', '').replace(' S/A', '').replace(' S.A.', '').replace(' EIRELI', '')
            
            # Criar descrição completa
            info_empresa = []
            
            # Adicionar empresa
            info_empresa.append(f"🏢 {nome_empresa[:40]}{'...' if len(nome_empresa) > 40 else ''}")
            
            # Adicionar tribunal
            info_empresa.append(f"🏛️ {row['TRIBUNAL']}")
            
            # Adicionar grau se disponível
            if 'GRAU' in row and row['GRAU']:
                info_empresa.append(f"⚖️ {row['GRAU']}")
            
            # Adicionar segmento se disponível
            if 'SEGMENTO' in row and row['SEGMENTO']:
                info_empresa.append(f"🏭 {row['SEGMENTO']}")
            
            # Adicionar ramo se disponível
            if 'RAMO' in row and row['RAMO']:
                info_empresa.append(f"📊 {row['RAMO']}")
            
            # Adicionar volume estimado
            info_empresa.append(f"📈 {row['volume_mensal']:.0f} proc/mês")
            
            # Criar string final
            opcao_texto = ' | '.join(info_empresa)
            empresas_opcoes.append(opcao_texto)
        
        empresa_selecionada = st.sidebar.selectbox(
            "🎯 Empresa específica:",
            empresas_opcoes,
            help="Selecione uma empresa para aplicar automaticamente seu volume"
        )
        
        # Se uma empresa foi selecionada
        if empresa_selecionada != 'Selecionar manualmente...':
            # Extrair dados da empresa (usar índice da lista)
            indice_empresa = empresas_opcoes.index(empresa_selecionada) - 1  # -1 porque o primeiro é "Selecionar manualmente"
            dados_empresa = df_top_empresas.to_dicts()[indice_empresa]
            
            # Mostrar informações da empresa selecionada
            nome_empresa_limpo = dados_empresa['ÓRGÃO'].replace(' LTDA', '').replace(' S/A', '').replace(' S.A.', '').replace(' EIRELI', '')
            
            st.sidebar.success(f"✅ Empresa selecionada")
            st.sidebar.info(f"🏢 {nome_empresa_limpo}")
            st.sidebar.info(f"📊 Volume estimado: {dados_empresa['volume_mensal']:.0f} processos/mês")
            st.sidebar.info(f"🏛️ Tribunal: {dados_empresa['TRIBUNAL']}")
            
            if 'GRAU' in dados_empresa and dados_empresa['GRAU']:
                st.sidebar.info(f"⚖️ Grau: {dados_empresa['GRAU']}")
            if 'SEGMENTO' in dados_empresa and dados_empresa['SEGMENTO']:
                st.sidebar.info(f"🏭 Segmento: {dados_empresa['SEGMENTO']}")
            if 'RAMO' in dados_empresa and dados_empresa['RAMO']:
                st.sidebar.info(f"📊 Ramo: {dados_empresa['RAMO']}")
            
            # Definir volume automaticamente
            volume_automatico = int(dados_empresa['volume_mensal'])
            usar_volume_automatico = True
        else:
            volume_automatico = None
            usar_volume_automatico = False
    else:
        st.sidebar.warning("Nenhuma empresa encontrada com os filtros aplicados")
        volume_automatico = None
        usar_volume_automatico = False
    
    # Top N litigantes para visualização geral
    st.sidebar.header("👥 Análise Geral")
    top_n = st.sidebar.slider("Top N empresas para análise:", 10, 100, 20)
    df_top = df_com_mensal.sort('volume_mensal', descending=True).head(top_n)
    
    # Layout principal
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📊 Análise dos Dados Filtrados")
        
        # Mostrar filtros aplicados
        filtros_ativos = []
        if tribunal_selecionado != 'Todos':
            filtros_ativos.append(f"Tribunal: {tribunal_selecionado}")
        if grau_selecionado != 'Todos':
            filtros_ativos.append(f"Grau: {grau_selecionado}")
        if segmento_selecionado != 'Todos':
            filtros_ativos.append(f"Segmento: {segmento_selecionado}")
        
        if filtros_ativos:
            st.info(f"🔍 Filtros ativos: {' | '.join(filtros_ativos)}")
        
        # Tabela com checkboxes para seleção múltipla
        st.subheader("📋 Selecione Empresas para Simulação")
        
        # Inicializar seleções na sessão se não existirem
        if 'empresas_selecionadas' not in st.session_state:
            st.session_state.empresas_selecionadas = []
        
        # Botões de controle rápido
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn1:
            if st.button("✅ Selecionar Todas"):
                st.session_state.empresas_selecionadas = df_top['ÓRGÃO'].to_list()
                st.rerun()
        with col_btn2:
            if st.button("❌ Limpar Seleção"):
                st.session_state.empresas_selecionadas = []
                st.rerun()
        with col_btn3:
            if st.button("🔄 Inverter Seleção"):
                todas_empresas = set(df_top['ÓRGÃO'].to_list())
                selecionadas = set(st.session_state.empresas_selecionadas)
                st.session_state.empresas_selecionadas = list(todas_empresas - selecionadas)
                st.rerun()
        
        # Lista de empresas com checkboxes
        empresas_dados = df_top.to_dicts()
        
        for idx, empresa_info in enumerate(empresas_dados):
            nome_empresa = empresa_info['ÓRGÃO']
            volume_mensal = empresa_info['volume_mensal']
            
            # Simplificar nome da empresa para exibição
            nome_display = nome_empresa.replace(' LTDA', '').replace(' S/A', '').replace(' S.A.', '').replace(' EIRELI', '')
            if len(nome_display) > 50:
                nome_display = nome_display[:47] + "..."
            
            # Checkbox para cada empresa
            checkbox_key = f"checkbox_{idx}_{nome_empresa}"
            selecionada = st.checkbox(
                f"🏢 **{nome_display}** - {volume_mensal:.0f} processos/mês",
                value=nome_empresa in st.session_state.empresas_selecionadas,
                key=checkbox_key
            )
            
            # Atualizar lista de selecionadas
            if selecionada and nome_empresa not in st.session_state.empresas_selecionadas:
                st.session_state.empresas_selecionadas.append(nome_empresa)
            elif not selecionada and nome_empresa in st.session_state.empresas_selecionadas:
                st.session_state.empresas_selecionadas.remove(nome_empresa)
        
        # Resumo das seleções
        if st.session_state.empresas_selecionadas:
            st.success(f"✅ **{len(st.session_state.empresas_selecionadas)} empresas selecionadas**")
            
            # Calcular volume total das empresas selecionadas
            volume_total_selecionado = 0
            for empresa_selecionada in st.session_state.empresas_selecionadas:
                empresa_data = df_top.filter(pl.col('ÓRGÃO') == empresa_selecionada)
                if len(empresa_data) > 0:
                    volume_total_selecionado += empresa_data[0, 'volume_mensal']
            
            st.info(f"📊 **Volume total estimado: {volume_total_selecionado:.0f} processos/mês**")
            
            with st.expander("📋 Ver empresas selecionadas"):
                for empresa in st.session_state.empresas_selecionadas:
                    empresa_data = df_top.filter(pl.col('ÓRGÃO') == empresa)
                    if len(empresa_data) > 0:
                        volume = empresa_data[0, 'volume_mensal']
                        nome_clean = empresa.replace(' LTDA', '').replace(' S/A', '').replace(' S.A.', '').replace(' EIRELI', '')
                        st.write(f"• {nome_clean}: {volume:.0f} proc/mês")
        else:
            st.warning("⚠️ Selecione pelo menos uma empresa para simulação")
        
        # Botão para simulação rápida das empresas selecionadas
        if st.session_state.empresas_selecionadas:
            st.markdown("---")
            if st.button("🚀 Simular Empresas Selecionadas", type="primary", use_container_width=True):
                # Scroll para o simulador
                st.success("✅ Volume aplicado no simulador!")
                st.info("👉 Veja os resultados na seção 'Simulador Financeiro' ao lado →")
        
        # Informações sobre agrupamento
        if agrupar_empresas:
            with st.expander("🏢 Agrupamento de Empresas Ativado"):
                st.markdown("""
                **O que faz o agrupamento:**
                - ✅ **Remove duplicatas**: Empresas que aparecem em múltiplos tribunais/graus são consolidadas
                - ✅ **Soma volumes**: NOVOS e PENDENTES são somados para cada empresa única
                - ✅ **CNPJ inteligente**: Usa CNPJ quando disponível para agrupamento preciso
                - ✅ **Fallback por nome**: Se não há CNPJ, agrupa por nome da empresa
                
                **Exemplo**: AZUL que aparecia 10x com volumes diferentes → 1x com volume total consolidado
                """)
        
        # Metodologia de cálculo
        with st.expander("📖 Metodologia de Cálculo dos Processos Mensais"):
            st.markdown("""
            **Baseado na metodologia oficial CNJ - Painel dos Grandes Litigantes:**
            
            - **NOVOS ÷ 12**: Divide processos anuais por 12 para obter média mensal real
              (método correto agora que empresas duplicadas foram agrupadas)
            - **PENDENTES ÷ 10**: Para casos sem dados de NOVOS, estima pela rotatividade 
              (PENDENTES = snapshot atual, dividido pelo tempo médio de tramitação)
            - **Estimativa mínima**: 25 processos/mês para casos sem dados suficientes
            
            **Definições Oficiais CNJ:**
            - **NOVOS**: Processos cuja data de início da situação 88 (pendente) ocorre nos 12 meses anteriores
            - **PENDENTES**: Processos com situação 88 (pendente) em aberto no mês de referência
            
            **Fontes**: Metodologia Painel dos Grandes Litigantes CNJ, Resolução CNJ 331/2020
            """)
        
        # Estatísticas resumo
        volume_total = df_com_mensal['volume_mensal'].sum()
        volume_medio = df_com_mensal['volume_mensal'].mean()
        
        col_met1, col_met2, col_met3 = st.columns(3)
        with col_met1:
            st.metric("Empresas Encontradas", len(df_com_mensal))
        with col_met2:
            st.metric("Volume Total/Mês", f"{volume_total:,.0f}")
        with col_met3:
            st.metric("Volume Médio/Mês", f"{volume_medio:.0f}")
        
        # Botão para gerar relatório detalhado
        st.markdown("---")
        col_relatorio1, col_relatorio2, col_relatorio3 = st.columns([1, 2, 1])
        with col_relatorio2:
            if st.button("📊 Gerar Relatório Detalhado", use_container_width=True, type="primary"):
                # Salvar dados no estado da sessão
                st.session_state.dados_relatorio = df_com_mensal
                st.session_state.pagina_atual = "relatorio"
                st.rerun()
        
        st.info("💡 **Relatório Detalhado:** Análise por porte de empresas, ramo e segmento com gráficos e estatísticas completas.")
    
    with col2:
        st.header("🎛️ Simulador Financeiro")
        
        # Determinar volume inicial baseado nas seleções
        volume_inicial = None
        fonte_volume = ""
        
        # Prioridade 1: Empresas selecionadas com checkbox
        if st.session_state.empresas_selecionadas:
            volume_total_selecionado = 0
            for empresa_selecionada in st.session_state.empresas_selecionadas:
                empresa_data = df_top.filter(pl.col('ÓRGÃO') == empresa_selecionada)
                if len(empresa_data) > 0:
                    volume_total_selecionado += empresa_data[0, 'volume_mensal']
            
            volume_inicial = int(volume_total_selecionado)
            fonte_volume = f"🎯 Volume baseado em {len(st.session_state.empresas_selecionadas)} empresas selecionadas"
            
        # Prioridade 2: Empresa única selecionada no sidebar
        elif usar_volume_automatico and volume_automatico:
            volume_inicial = volume_automatico
            fonte_volume = f"🎯 Volume da empresa selecionada no sidebar"
            
        # Prioridade 3: Média dos dados filtrados
        else:
            volume_inicial = int(volume_medio) if len(df_com_mensal) > 0 else 1000
            fonte_volume = "📊 Volume baseado na média dos dados filtrados"
        
        # Mostrar fonte do volume
        if fonte_volume:
            st.success(fonte_volume)
            if st.session_state.empresas_selecionadas:
                st.info(f"💡 Volume total: {volume_inicial:,} processos/mês")
        
        # Input de volume (sempre editável)
        volume_simulacao = st.number_input(
            "Volume mensal:", 
            value=volume_inicial, 
            min_value=0, 
            step=100,
            help="Volume pode ser editado mesmo quando baseado em seleções"
        )
        
        preco = st.number_input("Preço por processo (R$):", value=50.0, min_value=1.0, step=1.0)
        custo_base = st.number_input("Custo fixo base (R$):", value=60000, min_value=0, step=1000)
        clientes = st.number_input("Número de clientes:", value=1, min_value=1, step=1)
        reinvestimento = st.slider("% Reinvestimento:", 0, 100, 30)
    
    # Calcular resultados
    resultados = calcular_financas(volume_simulacao, preco, custo_base, clientes, reinvestimento)
    break_even = encontrar_break_even(preco, custo_base, clientes)
    
    # Exibir resultados
    st.header("💰 Resultados Financeiros")
    
    # KPIs principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Receita Bruta Mensal",
            f"R$ {resultados['receita_bruta']:,.0f}",
            help="Volume × Preço"
        )
    
    with col2:
        st.metric(
            "Custo Total",
            f"R$ {resultados['custo_total']:,.0f}",
            help="Custo base + progressivo + relacionamento + operacional (R$1/processo)"
        )
    
    with col3:
        lucro_cor = "normal" if resultados['lucro_liquido'] >= 0 else "inverse"
        st.metric(
            "Lucro Líquido",
            f"R$ {resultados['lucro_liquido']:,.0f}",
            f"{resultados['margem_liquida']:.1f}%",
            delta_color=lucro_cor
        )
    
    with col4:
        st.metric(
            "Ponto de Equilíbrio",
            f"{break_even:,} proc/mês",
            help="Volume necessário para lucro = 0"
        )
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Composição Financeira")
        
        # Gráfico de barras
        valores = [
            resultados['receita_bruta'],
            resultados['custo_total'],
            max(0, resultados['lucro_liquido']),
            abs(min(0, resultados['lucro_liquido']))
        ]
        
        labels = ['Receita Bruta', 'Custo Total', 'Lucro', 'Prejuízo']
        cores = ['green', 'orange', 'blue', 'red']
        
        # Filtrar valores não-zero
        valores_filtrados = []
        labels_filtrados = []
        cores_filtradas = []
        for i, v in enumerate(valores):
            if v > 0:
                valores_filtrados.append(v)
                labels_filtrados.append(labels[i])
                cores_filtradas.append(cores[i])
        
        fig_bar = go.Figure(data=[
            go.Bar(x=labels_filtrados, y=valores_filtrados, marker_color=cores_filtradas)
        ])
        fig_bar.update_layout(title="Valores Mensais (R$)", yaxis_title="Valores (R$)")
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        st.subheader("🥧 Breakdown de Custos")
        
        # Gráfico de pizza dos custos
        custos = [
            resultados['custo_base'],
            resultados['custo_progressivo'],
            resultados['custo_relacionamento'],
            resultados['custo_operacional']
        ]
        labels_custos = ['Custo Base', 'Custo Progressivo', 'Custo Relacionamento', 'Custo Operacional']
        
        # Filtrar custos não-zero
        custos_filtrados = []
        labels_custos_filtrados = []
        for i, c in enumerate(custos):
            if c > 0:
                custos_filtrados.append(c)
                labels_custos_filtrados.append(labels_custos[i])
        
        if custos_filtrados:
            fig_pie = go.Figure(data=[
                go.Pie(labels=labels_custos_filtrados, values=custos_filtrados)
            ])
            fig_pie.update_layout(title="Composição dos Custos")
            st.plotly_chart(fig_pie, use_container_width=True)
    
    # Análise de sensibilidade
    st.header("🎯 Análise de Sensibilidade")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💹 Impacto do Volume")
        
        # Gerar cenários de volume
        volumes = range(500, min(50000, max(volume_simulacao * 3, 10000)), 500)
        lucros = []
        
        for vol in volumes:
            res = calcular_financas(vol, preco, custo_base, clientes, reinvestimento)
            lucros.append(res['lucro_liquido'])
        
        fig_sens = go.Figure()
        fig_sens.add_trace(go.Scatter(x=list(volumes), y=lucros, mode='lines', name='Lucro Líquido'))
        fig_sens.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Break-even")
        
        # Destacar volume atual
        resultado_atual = calcular_financas(volume_simulacao, preco, custo_base, clientes, reinvestimento)
        fig_sens.add_trace(go.Scatter(
            x=[volume_simulacao], 
            y=[resultado_atual['lucro_liquido']], 
            mode='markers', 
            marker=dict(size=12, color='red'),
            name='Volume Atual'
        ))
        
        fig_sens.update_layout(
            title="Lucro vs Volume",
            xaxis_title="Volume (processos/mês)",
            yaxis_title="Lucro Líquido (R$)"
        )
        st.plotly_chart(fig_sens, use_container_width=True)
    
    with col2:
        st.subheader("💰 Impacto do Preço")
        
        # Gerar cenários de preço
        precos = range(20, 101, 5)
        lucros_preco = []
        
        for p in precos:
            res = calcular_financas(volume_simulacao, p, custo_base, clientes, reinvestimento)
            lucros_preco.append(res['lucro_liquido'])
        
        fig_preco = go.Figure()
        fig_preco.add_trace(go.Scatter(x=list(precos), y=lucros_preco, mode='lines', name='Lucro Líquido'))
        fig_preco.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Break-even")
        
        # Destacar preço atual
        fig_preco.add_trace(go.Scatter(
            x=[preco], 
            y=[resultados['lucro_liquido']], 
            mode='markers', 
            marker=dict(size=12, color='red'),
            name='Preço Atual'
        ))
        
        fig_preco.update_layout(
            title="Lucro vs Preço",
            xaxis_title="Preço (R$/processo)",
            yaxis_title="Lucro Líquido (R$)"
        )
        st.plotly_chart(fig_preco, use_container_width=True)
    
    # Detalhamento
    with st.expander("📋 Detalhamento Completo"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Receitas:**")
            st.write(f"• Receita Bruta: R$ {resultados['receita_bruta']:,.0f}")
            
            st.write("**Custos:**")
            st.write(f"• Custo Base: R$ {resultados['custo_base']:,.0f}")
            st.write(f"• Custo Progressivo: R$ {resultados['custo_progressivo']:,.0f}")
            st.write(f"• Custo Relacionamento: R$ {resultados['custo_relacionamento']:,.0f}")
            st.write(f"• Custo Operacional (R$ 1,00/processo): R$ {resultados['custo_operacional']:,.0f}")
            st.write(f"• **Total Custos**: R$ {resultados['custo_total']:,.0f}")
        
        with col2:
            st.write("**Impostos e Lucros:**")
            st.write(f"• Impostos (Simples): R$ {resultados['impostos']:,.0f}")
            st.write(f"• Lucro Bruto: R$ {resultados['lucro_bruto']:,.0f}")
            st.write(f"• Lucro Líquido: R$ {resultados['lucro_liquido']:,.0f}")
            st.write(f"• Margem Líquida: {resultados['margem_liquida']:.1f}%")
            
            st.write("**Distribuição:**")
            st.write(f"• Reinvestimento: R$ {resultados['valor_reinvestimento']:,.0f}")
            st.write(f"• Distribuição: R$ {resultados['valor_distribuicao']:,.0f}")

def agrupar_por_empresa(df: pl.DataFrame) -> pl.DataFrame:
    """
    Agrupa dados por empresa, priorizando CNPJ quando disponível
    Remove duplicatas de empresas que aparecem em múltiplos tribunais/graus
    """
    
    # Detectar se existe coluna de CNPJ
    colunas_cnpj = [col for col in df.columns if 'CNPJ' in col.upper()]
    
    if colunas_cnpj:
        # Usar CNPJ para agrupamento (método mais preciso)
        coluna_cnpj = colunas_cnpj[0]  # Usar primeira coluna CNPJ encontrada
        
        # Definir agregações básicas
        agregacoes = [
            # Manter o primeiro nome da empresa
            pl.col('ÓRGÃO').first().alias('ÓRGÃO'),
            # Somar valores financeiros
            pl.col('NOVOS').sum().alias('NOVOS'),
            # Manter outros campos (primeiro valor)
            pl.col('TRIBUNAL').first().alias('TRIBUNAL'),
            # Contar registros agrupados
            pl.len().alias('REGISTROS_AGRUPADOS')
        ]
        
        # Adicionar PENDENTES BRUTO se existir
        if 'PENDENTES BRUTO' in df.columns:
            agregacoes.append(pl.col('PENDENTES BRUTO').sum().alias('PENDENTES BRUTO'))
        
        # Adicionar outras colunas
        colunas_excluidas = ['ÓRGÃO', 'NOVOS', 'TRIBUNAL', coluna_cnpj]
        if 'PENDENTES BRUTO' in df.columns:
            colunas_excluidas.append('PENDENTES BRUTO')
            
        agregacoes.extend([
            pl.col(col).first().alias(col) for col in df.columns 
            if col not in colunas_excluidas
        ])
        
        df_agrupado = df.group_by([coluna_cnpj]).agg(agregacoes)
        
        # Remover a coluna CNPJ da visualização (manter apenas para agrupamento)
        colunas_para_manter = [col for col in df_agrupado.columns if col != coluna_cnpj]
        df_agrupado = df_agrupado.select(colunas_para_manter)
        
        total_original = len(df)
        total_agrupado = len(df_agrupado)
        
        if total_agrupado < total_original:
            st.info(f"🏢 Agrupamento por CNPJ: {total_original:,} → {total_agrupado:,} empresas únicas")
        
    else:
        # Fallback: agrupar por nome da empresa + segmento (método menos preciso)
        colunas_agrupamento = ['ÓRGÃO']
        if 'SEGMENTO' in df.columns:
            colunas_agrupamento.append('SEGMENTO')
        
        # Definir agregações básicas
        agregacoes = [
            # Somar valores financeiros
            pl.col('NOVOS').sum().alias('NOVOS'),
            # Manter outros campos (primeiro valor)
            pl.col('TRIBUNAL').first().alias('TRIBUNAL'),
            # Contar registros agrupados
            pl.len().alias('REGISTROS_AGRUPADOS')
        ]
        
        # Adicionar PENDENTES BRUTO se existir
        if 'PENDENTES BRUTO' in df.columns:
            agregacoes.append(pl.col('PENDENTES BRUTO').sum().alias('PENDENTES BRUTO'))
        
        # Adicionar outras colunas
        colunas_excluidas = ['ÓRGÃO', 'NOVOS', 'TRIBUNAL'] + colunas_agrupamento
        if 'PENDENTES BRUTO' in df.columns:
            colunas_excluidas.append('PENDENTES BRUTO')
            
        agregacoes.extend([
            pl.col(col).first().alias(col) for col in df.columns 
            if col not in colunas_excluidas
        ])
        
        df_agrupado = df.group_by(colunas_agrupamento).agg(agregacoes)
        
        total_original = len(df)
        total_agrupado = len(df_agrupado)
        
        if total_agrupado < total_original:
            st.info(f"🏢 Agrupamento por nome: {total_original:,} → {total_agrupado:,} empresas únicas")
    
    return df_agrupado

def calcular_processos_mensais(df: pl.DataFrame) -> pl.DataFrame:
    """
    Calcula uma estimativa de processos mensais para cada órgão
    baseado nos dados de NOVOS, PENDENTES BRUTO e PENDENTES LÍQUIDO
    
    METODOLOGIA OFICIAL CNJ - PAINEL DOS GRANDES LITIGANTES:
    - NOVOS: Processos iniciados nos 12 MESES ANTERIORES ao mês de referência (PERÍODO ANUAL)
    - PENDENTES: Processos com situação 88 (pendente) em aberto no mês de referência (SNAPSHOT)
    - Fonte: Metodologia Painel dos Grandes Litigantes CNJ, Resolução CNJ 331/2020
    """
    
    # Cálculo da média mensal com agrupamento corrigido:
    # 1. NOVOS ÷ 12 = média mensal real (agora que empresas estão agrupadas)
    # 2. PENDENTES ÷ 10 = estimativa por rotatividade (fallback)
    # 3. Estimativa mínima para casos sem dados
    
    df_com_calculo = df.with_columns([
        # Média mensal baseada em NOVOS anuais ÷ 12 (método correto pós-agrupamento)
        pl.when(pl.col('NOVOS').is_not_null() & (pl.col('NOVOS') > 0))
        .then((pl.col('NOVOS').cast(pl.Float64) / 12).round())
        
        # Fallback: estimar pelos pendentes
        .when(pl.col('PENDENTES BRUTO').is_not_null() & (pl.col('PENDENTES BRUTO') > 0))
        .then((pl.col('PENDENTES BRUTO').cast(pl.Float64) / 10).round())
        
        # Estimativa mínima
        .otherwise(25)
        .alias('volume_mensal')
    ]).with_columns([
        # Manter compatibilidade com processos_mensais_estimado
        pl.col('volume_mensal').alias('processos_mensais_estimado')
    ]).with_columns([
        # Método usado para o cálculo
        pl.when(pl.col('NOVOS').is_not_null() & (pl.col('NOVOS') > 0))
        .then(pl.lit("NOVOS ÷ 12"))
        .when(pl.col('PENDENTES BRUTO').is_not_null() & (pl.col('PENDENTES BRUTO') > 0))
        .then(pl.lit("PENDENTES ÷ 10"))
        .otherwise(pl.lit("Estimativa mínima"))
        .alias('metodo_calculo')
    ])
    
    return df_com_calculo

if __name__ == "__main__":
    # Verificar dependências
    try:
        import streamlit as st
        import plotly.express as px
        import polars as pl
    except ImportError as e:
        print(f"❌ Dependência não encontrada: {e}")
        print("🔧 Instale com: pip install streamlit plotly polars")
        exit(1)
    
    # Página já configurada no topo do arquivo
    
    main() 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 SIMULADOR FINANCEIRO - GRANDES LITIGANTES
Aplicação Web Profissional

Features:
- Sistema de login seguro
- Dados em PostgreSQL
- Interface responsiva
- API REST completa
"""

import os
import secrets
from datetime import datetime
from functools import wraps

import polars as pl
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import tempfile
import re
from pathlib import Path
import numpy as np
from typing import Dict, List, Tuple, Optional
import json

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'pdpj2024-simulador-secreto')

# Configurações globais
SENHA_SISTEMA = "pdpj2024"
PARQUET_FILE = "dados_grandes_litigantes_demo.parquet"

# Cache global para dados
dados_cache = {
    'dataframe': None,
    'timestamp': None,
    'total_registros': 0
}

# Sistema de progresso
progress_data = {
    'percent': 0,
    'status': 'Aguardando...',
    'details': '',
    'speed': '',
    'bytes': '',
    'active': False
}

# Simulação de banco (em produção seria PostgreSQL)
users_db = {
    'admin': {
        'id': 1,
        'password_hash': generate_password_hash('123'),
        'email': 'admin@simulador.com'
    }
}

class DataManager:
    def __init__(self):
        self.parquet_file = "dados_grandes_litigantes_demo.parquet"
        self.cnae_file = "tabela_cnae_classe_subclasse.csv"
        self.df = None
        self.df_cnae = None
        
    def load_cnae_data(self):
        """Carrega dados de CNAE com descrições"""
        try:
            if not os.path.exists(self.cnae_file):
                print(f"⚠️ Arquivo CNAE não encontrado: {self.cnae_file}")
                return None
                
            # Carregar com tipos corretos
            self.df_cnae = pl.read_csv(
                self.cnae_file,
                separator=";",
                schema_overrides={
                    'Codigo_Classe': pl.Utf8,
                    'Codigo_Subclasse': pl.Utf8,
                    'Nome_Classe': pl.Utf8,
                    'Nome_Subclasse': pl.Utf8
                }
            )
            
            print(f"✅ Dados CNAE carregados: {len(self.df_cnae):,} registros")
            return self.df_cnae
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados CNAE: {e}")
            return None
    

    
    def load_data(self, limit=0):
        """Carrega dados do arquivo parquet local"""
        try:
            load_all = (limit == 0)
            
            # Verificar se arquivo existe
            if not os.path.exists(self.parquet_file):
                print(f"❌ Arquivo não encontrado: {self.parquet_file}")
                update_progress(30, 'Arquivo não encontrado', 'Gerando dados de demonstração')
                return self._create_fallback_data(limit if not load_all else 50000)
            
            print(f"📂 Procurando arquivo parquet local...")
            update_progress(20, 'Procurando arquivo parquet local...', f'Verificando {self.parquet_file}')
            
            # Verificar tamanho do arquivo
            file_size = os.path.getsize(self.parquet_file) / (1024 * 1024)  # MB
            print(f"📂 Arquivo encontrado: {self.parquet_file}")
            print(f"📊 Tamanho do arquivo: {file_size:.1f} MB")
            update_progress(30, 'Arquivo local encontrado!', f'{file_size:.1f} MB')
            
            # Carregar dados
            print(f"📊 Progresso: 40.0% - Carregando dados...")
            update_progress(40, 'Carregando dados...', 'Lendo arquivo parquet')
            
            if load_all:
                print("🔥 Carregando TODOS os registros do arquivo...")
                update_progress(60, 'Processando registros...', 'Carregando dados completos')
                self.df = pl.read_parquet(self.parquet_file)
                update_progress(75, 'Carregando CNAEs...', f'{len(self.df):,} registros carregados')
                print(f"✅ Dados COMPLETOS carregados: {len(self.df):,} registros")
            else:
                print(f"📊 Carregando {limit:,} registros...")
                update_progress(60, 'Processando registros...', f'Limitando a {limit:,} registros')
                df_lazy = pl.scan_parquet(self.parquet_file)
                self.df = df_lazy.head(limit).collect()
                update_progress(75, 'Carregando CNAEs...', f'{len(self.df):,} registros processados')
                print(f"✅ Dados carregados: {len(self.df):,} registros")
            
            # Carregar dados CNAE
            self.load_cnae_data()
            update_progress(90, 'Finalizando carregamento...', 'CNAEs integrados')
            
            return self.df
            
        except Exception as e:
            print(f"❌ Erro ao carregar arquivo local: {e}")
            update_progress(50, 'Erro no carregamento...', 'Gerando dados de demonstração')
            return self._create_fallback_data(limit if not load_all else 50000)
    
    def _create_fallback_data(self, limit):
        """Criar dados de demonstração em caso de falha"""
        try:
            import random
            
            print("📊 Gerando dados de demonstração...")
            
            empresas = [
                "BANCO DO BRASIL S.A.", "CAIXA ECONÔMICA FEDERAL", "BRADESCO S.A.",
                "ITAÚ UNIBANCO S.A.", "SANTANDER BRASIL S.A.", "NUBANK S.A.",
                "MAGAZINE LUIZA S.A.", "VIA VAREJO S.A.", "TELEFONICA BRASIL S.A.",
                "TIM S.A.", "CLARO S.A.", "PETROBRAS S.A.", "VALE S.A."
            ]
            
            tribunais = ["TJSP", "TJRJ", "TJMG", "TJRS", "TJPR", "TJSC", "TJBA", "TJDF"]
            
            data = []
            n_records = min(limit, 10000)  # Máximo 10k para demonstração
            
            for i in range(n_records):
                empresa = random.choice(empresas)
                tribunal = random.choice(tribunais)
                
                # Bancos têm mais processos
                if "BANCO" in empresa or "CAIXA" in empresa:
                    novos = random.randint(100, 800)
                else:
                    novos = random.randint(10, 200)
                
                data.append({
                    'NOME': empresa,
                    'TRIBUNAL': tribunal,
                    'NOVOS': novos
                })
            
            self.df = pl.DataFrame(data)
            print(f"✅ Dados de demonstração criados: {len(self.df):,} registros")
            print("ℹ️ Estes são dados fictícios para demonstração")
            
            return self.df
            
        except Exception as e:
            print(f"❌ Erro ao criar dados de fallback: {e}")
            return None

data_manager = DataManager()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = users_db.get(username)
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = username
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciais inválidas!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado!', 'info')
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Informações sobre dados em cache
    dados_info = {
        'carregados': data_manager.df is not None,
        'total_registros': len(data_manager.df) if data_manager.df is not None else 0,
        'timestamp': 'Nunca'
    }
    
    return render_template('dashboard.html', 
                         username=session.get('username'),
                         dados_info=dados_info)

@app.route('/api/carregar-dados', methods=['POST'])
@login_required
def api_carregar_dados():
    try:
        data = request.get_json()
        limit = data.get('limit', 0)
        
        # Inicializar progresso
        global progress_data
        progress_data['active'] = True
        update_progress(0, 'Iniciando carregamento...', 'Preparando sistema...')
        
        if limit == 0:
            print("🔄 Solicitação de carregamento: TODOS os registros (14M+)")
            update_progress(5, 'Carregamento completo iniciado', 'Verificando dados locais...')
        else:
            print(f"🔄 Solicitação de carregamento: {limit:,} registros")
            update_progress(5, f'Carregando {limit:,} registros', 'Verificando cache local...')
        
        update_progress(15, 'Processando dados...', 'Conectando ao sistema de arquivos...')
        
        df = data_manager.load_data(limit=limit)
        if df is None:
            update_progress(0, 'Erro no carregamento', 'Falha ao acessar dados')
            error_msg = 'Falha ao carregar os dados do arquivo local. Verifique se o arquivo dados_grandes_litigantes.parquet existe.'
            print(f"❌ {error_msg}")
            progress_data['active'] = False
            return jsonify({'error': error_msg}), 500
        
        update_progress(70, 'Processando registros...', f'Analisando {len(df):,} registros...')
        
        total_registros = len(df)
        total_processos = df.select(pl.col('NOVOS').sum()).item() if 'NOVOS' in df.columns else 0
        
        update_progress(85, 'Identificando colunas...', 'Verificando estrutura dos dados...')
        
        # A coluna principal de empresa é 'NOME'
        coluna_empresa = 'NOME' if 'NOME' in df.columns else None
        
        update_progress(95, 'Finalizando...', f'{total_registros:,} registros processados')
        
        print(f"✅ Dados carregados com sucesso: {total_registros:,} registros")
        
        # Debug: mostrar colunas disponíveis
        print(f"📋 Colunas disponíveis: {df.columns}")
        
        # Verificar se são dados de demonstração
        is_demo = total_registros <= 10000
        
        update_progress(100, 'Concluído!', f'Sucesso - {total_registros:,} registros carregados', 'Completo', f'{total_registros:,} registros')
        
        # Desativar progresso após um tempo
        import threading
        def clear_progress():
            import time
            time.sleep(2)
            progress_data['active'] = False
        
        threading.Thread(target=clear_progress).start()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_registros': total_registros,
                'total_processos': total_processos,
                'coluna_empresa': coluna_empresa,
                'is_demo': is_demo
            }
        })
    except Exception as e:
        update_progress(0, 'Erro crítico', f'Falha: {str(e)}')
        error_msg = f'Erro no carregamento: {str(e)}'
        print(f"❌ {error_msg}")
        progress_data['active'] = False
        return jsonify({'error': error_msg}), 500

@app.route('/api/filtros', methods=['GET'])
@login_required
def api_filtros():
    """API para obter opções de filtros disponíveis"""
    try:
        if data_manager.df is None:
            return jsonify({'error': 'Dados não carregados'}), 400
        
        df = data_manager.df
        
        # Obter valores únicos para filtros
        filtros = {}
        
        # Tribunais (retornar como 'tribunais' no plural para compatibilidade)
        if 'TRIBUNAL' in df.columns:
            tribunais = df.select('TRIBUNAL').unique().sort('TRIBUNAL').to_series().to_list()
            # Remover valores None e converter para string
            tribunais = [str(t) for t in tribunais if t is not None]
            filtros['tribunais'] = sorted(tribunais)
        
        # Graus (retornar como 'graus' no plural para compatibilidade)
        if 'GRAU' in df.columns:
            graus = df.select('GRAU').unique().sort('GRAU').to_series().to_list()
            # Remover valores None e converter para string
            graus = [str(g) for g in graus if g is not None]
            filtros['graus'] = sorted(graus)
        
        # Segmentos (retornar como 'segmentos' no plural para compatibilidade)
        if 'SEGMENTO' in df.columns:
            segmentos = df.select('SEGMENTO').unique().sort('SEGMENTO').to_series().to_list()
            # Remover valores None e converter para string
            segmentos = [str(s) for s in segmentos if s is not None]
            filtros['segmentos'] = sorted(segmentos)
        
        # Ramos (retornar como 'ramos' no plural para compatibilidade)
        if 'RAMO' in df.columns:
            ramos = df.select('RAMO').unique().sort('RAMO').to_series().to_list()
            # Remover valores None e converter para string
            ramos = [str(r) for r in ramos if r is not None]
            filtros['ramos'] = sorted(ramos)
        
        print(f"📊 Filtros gerados: {len(filtros)} categorias")
        for categoria, valores in filtros.items():
            print(f"  - {categoria}: {len(valores)} opções")
        
        return jsonify({'success': True, 'filtros': filtros})
    except Exception as e:
        print(f"❌ Erro na API filtros: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/filtros-disponiveis', methods=['POST'])
@login_required
def api_filtros_disponiveis():
    """API para obter filtros disponíveis baseados nas seleções atuais (filtros cascateados)"""
    try:
        if data_manager.df is None:
            return jsonify({'error': 'Dados não carregados'}), 400
        
        data = request.get_json() or {}
        filtros_selecionados = data.get('filtros', {})
        
        df = data_manager.df
        
        # Aplicar filtros já selecionados para determinar valores disponíveis
        df_filtrado = df
        
        # Aplicar cada filtro selecionado (usando nomes no plural)
        if filtros_selecionados.get('tribunais') and len(filtros_selecionados['tribunais']) > 0:
            df_filtrado = df_filtrado.filter(pl.col('TRIBUNAL').is_in(filtros_selecionados['tribunais']))
        
        if filtros_selecionados.get('graus') and len(filtros_selecionados['graus']) > 0:
            df_filtrado = df_filtrado.filter(pl.col('GRAU').is_in(filtros_selecionados['graus']))
        
        if filtros_selecionados.get('segmentos') and len(filtros_selecionados['segmentos']) > 0:
            df_filtrado = df_filtrado.filter(pl.col('SEGMENTO').is_in(filtros_selecionados['segmentos']))
        
        if filtros_selecionados.get('ramos') and len(filtros_selecionados['ramos']) > 0:
            df_filtrado = df_filtrado.filter(pl.col('RAMO').is_in(filtros_selecionados['ramos']))
        
        if filtros_selecionados.get('cnae') and len(filtros_selecionados['cnae']) > 0:
            # Converter CNAEs para string para comparação correta
            cnaes_str = []
            for cnae in filtros_selecionados['cnae']:
                try:
                    cnaes_str.append(str(cnae))
                except:
                    continue
            if cnaes_str:
                df_filtrado = df_filtrado.filter(pl.col('CNAE').cast(pl.Utf8).is_in(cnaes_str))
        
        # Aplicar filtros de classe e subclasse CNAE se disponíveis
        df_com_cnae = df_filtrado
        if data_manager.df_cnae is not None and 'CNAE' in df_filtrado.columns:
            # JOIN com dados CNAE para filtrar por classe/subclasse
            df_com_cnae = df_filtrado.join(
                data_manager.df_cnae,
                left_on=pl.col('CNAE').cast(pl.Utf8).str.zfill(7),
                right_on='Codigo_Subclasse',
                how='left'
            )
            
            # Aplicar filtro por classe CNAE
            if filtros_selecionados.get('classes_cnae') and len(filtros_selecionados['classes_cnae']) > 0:
                df_com_cnae = df_com_cnae.filter(pl.col('Nome_Classe').is_in(filtros_selecionados['classes_cnae']))
            
            # Aplicar filtro por subclasse CNAE
            if filtros_selecionados.get('subclasses_cnae') and len(filtros_selecionados['subclasses_cnae']) > 0:
                df_com_cnae = df_com_cnae.filter(pl.col('Nome_Subclasse').is_in(filtros_selecionados['subclasses_cnae']))
            
            # Manter apenas as colunas originais
            colunas_originais = [col for col in df_filtrado.columns if col in df_com_cnae.columns]
            df_filtrado = df_com_cnae.select(colunas_originais)
        
        # Obter valores únicos disponíveis para cada filtro baseado no dataset filtrado
        filtros_disponiveis = {}
        
        print(f"🔍 Debug - Colunas disponíveis: {df_filtrado.columns}")
        print(f"🔍 Debug - Registros no df_filtrado: {len(df_filtrado)}")
        
        # Tribunais (retornar como 'tribunais' no plural para compatibilidade)
        if 'TRIBUNAL' in df_filtrado.columns:
            tribunais = df_filtrado.select('TRIBUNAL').unique().sort('TRIBUNAL').to_series().to_list()
            print(f"🔍 Debug - Tribunais únicos encontrados: {len(tribunais)}")
            if len(tribunais) > 0:
                print(f"🔍 Debug - Primeiros tribunais: {tribunais[:5]}")
            tribunais = [str(t) for t in tribunais if t is not None]
            filtros_disponiveis['tribunais'] = sorted(tribunais)
        
        # Graus (retornar como 'graus' no plural para compatibilidade)
        if 'GRAU' in df_filtrado.columns:
            graus = df_filtrado.select('GRAU').unique().sort('GRAU').to_series().to_list()
            print(f"🔍 Debug - Graus únicos encontrados: {len(graus)}")
            graus = [str(g) for g in graus if g is not None]
            filtros_disponiveis['graus'] = sorted(graus)
        
        # Segmentos (retornar como 'segmentos' no plural para compatibilidade)
        if 'SEGMENTO' in df_filtrado.columns:
            segmentos = df_filtrado.select('SEGMENTO').unique().sort('SEGMENTO').to_series().to_list()
            print(f"🔍 Debug - Segmentos únicos encontrados: {len(segmentos)}")
            segmentos = [str(s) for s in segmentos if s is not None]
            filtros_disponiveis['segmentos'] = sorted(segmentos)
        
        # Ramos (retornar como 'ramos' no plural para compatibilidade)
        if 'RAMO' in df_filtrado.columns:
            ramos = df_filtrado.select('RAMO').unique().sort('RAMO').to_series().to_list()
            print(f"🔍 Debug - Ramos únicos encontrados: {len(ramos)}")
            ramos = [str(r) for r in ramos if r is not None]
            filtros_disponiveis['ramos'] = sorted(ramos)
        
        # Classes e Subclasses CNAE disponíveis
        classes_cnae_disponiveis = []
        subclasses_cnae_disponiveis = []
        
        if data_manager.df_cnae is not None and 'CNAE' in df_filtrado.columns:
            # JOIN para obter classes e subclasses disponíveis
            df_cnae_filtrado = df_filtrado.join(
                data_manager.df_cnae,
                left_on=pl.col('CNAE').cast(pl.Utf8).str.zfill(7),
                right_on='Codigo_Subclasse',
                how='left'
            )
            
            # Classes CNAE únicas
            if 'Nome_Classe' in df_cnae_filtrado.columns:
                classes = (
                    df_cnae_filtrado
                    .filter(pl.col('Nome_Classe').is_not_null())
                    .group_by('Nome_Classe')
                    .agg([pl.len().alias('registros')])
                    .sort(['registros', 'Nome_Classe'], descending=[True, False])
                )
                
                for row in classes.iter_rows():
                    nome_classe, registros = row
                    if nome_classe:
                        classes_cnae_disponiveis.append({
                            'nome': str(nome_classe),
                            'registros': registros
                        })
            
            # Subclasses CNAE únicas
            if 'Nome_Subclasse' in df_cnae_filtrado.columns:
                subclasses = (
                    df_cnae_filtrado
                    .filter(pl.col('Nome_Subclasse').is_not_null())
                    .group_by(['Nome_Subclasse', 'Nome_Classe'])
                    .agg([pl.len().alias('registros')])
                    .sort(['registros', 'Nome_Subclasse'], descending=[True, False])
                )
                
                for row in subclasses.iter_rows():
                    nome_subclasse, nome_classe, registros = row
                    if nome_subclasse:
                        subclasses_cnae_disponiveis.append({
                            'nome': str(nome_subclasse),
                            'classe_pai': str(nome_classe) if nome_classe else 'Sem classe',
                            'registros': registros
                        })
        
        filtros_disponiveis['classes_cnae'] = classes_cnae_disponiveis
        filtros_disponiveis['subclasses_cnae'] = subclasses_cnae_disponiveis
        
        # CNAEs disponíveis com contagem para organização hierárquica
        cnaes_disponiveis = []
        if 'CNAE' in df_filtrado.columns:
            cnaes_df = (
                df_filtrado
                .group_by(['CNAE'])
                .agg([pl.len().alias('registros')])
                .with_columns([
                    pl.col('CNAE').cast(pl.Utf8).str.zfill(7).alias('cnae_str')
                ])
                .sort(['registros'], descending=True)
            )
            
            if data_manager.df_cnae is not None:
                # JOIN com dados CNAE para obter descrições
                cnaes_com_desc = (
                    cnaes_df
                    .join(
                        data_manager.df_cnae,
                        left_on='cnae_str',
                        right_on='Codigo_Subclasse',
                        how='left'
                    )
                )
                
                # Agrupar por CLASSE para organização hierárquica
                classes_dict = {}
                
                for row in cnaes_com_desc.iter_rows():
                    # Adaptar baseado no número de colunas retornadas
                    if len(row) >= 7:
                        cnae, registros, cnae_str, codigo_classe, codigo_subclasse, nome_classe, nome_subclasse = row[:7]
                    elif len(row) >= 6:
                        cnae, registros, cnae_str, codigo_classe, codigo_subclasse, nome_classe = row[:6]
                        nome_subclasse = None
                    elif len(row) >= 3:
                        cnae, registros, cnae_str = row[:3]
                        codigo_classe = codigo_subclasse = nome_classe = nome_subclasse = None
                    else:
                        continue
                    
                    if cnae is None or str(cnae).strip() == '':
                        continue
                    
                    # Se não tem descrição, usar código
                    classe_nome = nome_classe if nome_classe else f"Classe {str(cnae)[:5]}"
                    subclasse_nome = nome_subclasse if nome_subclasse else f"CNAE {cnae}"
                    
                    # Agrupar por classe
                    if classe_nome not in classes_dict:
                        classes_dict[classe_nome] = {
                            'classe': classe_nome,
                            'codigo_classe': codigo_classe if codigo_classe else str(cnae)[:5],
                            'subclasses': [],
                            'total_registros': 0
                        }
                    
                    classes_dict[classe_nome]['subclasses'].append({
                        'cnae': str(cnae),
                        'nome': subclasse_nome,
                        'registros': registros
                    })
                    classes_dict[classe_nome]['total_registros'] += registros
                
                # Converter para lista e ordenar
                cnaes_disponiveis = list(classes_dict.values())
                cnaes_disponiveis.sort(key=lambda x: x['total_registros'], reverse=True)
                
                # Ordenar subclasses dentro de cada classe
                for classe in cnaes_disponiveis:
                    classe['subclasses'].sort(key=lambda x: x['registros'], reverse=True)
            else:
                # Fallback: sem descrições, apenas códigos
                for row in cnaes_df.iter_rows():
                    cnae, registros, cnae_str = row
                    if cnae is not None and str(cnae).strip() != '':
                        cnaes_disponiveis.append({
                            'cnae': str(cnae),
                            'nome': f"CNAE {cnae}",
                            'registros': registros
                        })
        
        filtros_disponiveis['cnaes'] = cnaes_disponiveis
        
        print(f"🔄 Filtros cascateados - Total registros disponíveis: {len(df_filtrado)}")
        print(f"🏷️ Classes CNAE disponíveis: {len(classes_cnae_disponiveis)}")
        print(f"🏷️ Subclasses CNAE disponíveis: {len(subclasses_cnae_disponiveis)}")
        
        return jsonify({
            'success': True,
            'filtros_disponiveis': filtros_disponiveis,
            'total_registros': len(df_filtrado)
        })
        
    except Exception as e:
        print(f"❌ Erro na API filtros disponíveis: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/test-dados', methods=['GET'])
@login_required
def api_test_dados():
    """Endpoint de teste para verificar status dos dados"""
    return jsonify({
        'data_loaded': data_manager.df is not None,
        'data_count': len(data_manager.df) if data_manager.df is not None else 0,
        'columns': list(data_manager.df.columns) if data_manager.df is not None else []
    })

@app.route('/api/estatisticas-gerais', methods=['POST'])
@login_required
def api_estatisticas_gerais():
    """API para obter estatísticas gerais baseadas nos filtros atuais"""
    try:
        print(f"🔍 Status dos dados: df é None? {data_manager.df is None}")
        if data_manager.df is not None:
            print(f"📊 Dados disponíveis: {len(data_manager.df)} registros")
        
        if data_manager.df is None:
            print("❌ data_manager.df é None - retornando erro 400")
            return jsonify({'error': 'Dados não carregados'}), 400
        
        data = request.get_json() or {}
        filtros = data.get('filtros', {})
        
        print(f"🔍 Filtros recebidos: {filtros}")
        
        # Aplicar filtros para obter dados filtrados
        df_filtrado = aplicar_filtros_avancados(data_manager.df, filtros)
        
        print(f"📊 Registros antes dos filtros: {len(data_manager.df)}")
        print(f"📊 Registros após filtros: {len(df_filtrado)}")
        
        # Calcular estatísticas por empresa
        if 'NOME' not in df_filtrado.columns:
            return jsonify({'error': 'Coluna NOME não encontrada'}), 400
        
        # Agrupar por empresa
        empresas_df = agrupar_por_empresa(df_filtrado)
        
        # Calcular processos mensais (adiciona coluna volume_mensal)
        empresas_df = calcular_processos_mensais(empresas_df)
        
        # Aplicar filtros de volume após criar a coluna volume_mensal
        empresas_df = aplicar_filtros_volume(empresas_df, filtros)
        
        # Calcular estatísticas
        total_empresas = len(empresas_df)
        
        # Calcular processos mensais total
        processos_mensais_total = int(empresas_df.select('volume_mensal').sum().item())
        
        # Calcular mediana mensal (usando Polars)
        if total_empresas > 0:
            mediana_mensal = int(empresas_df.select('volume_mensal').median().item())
        else:
            mediana_mensal = 0
        
        print(f"📊 Estatísticas gerais calculadas:")
        print(f"   - Total empresas: {total_empresas}")
        print(f"   - Processos mensais total: {processos_mensais_total}")
        print(f"   - Mediana mensal: {mediana_mensal}")
        
        return jsonify({
            'success': True,
            'estatisticas': {
                'total_empresas': total_empresas,
                'processos_mensais_total': processos_mensais_total,
                'mediana_mensal': mediana_mensal
            }
        })
        
    except Exception as e:
        print(f"❌ Erro na API estatísticas gerais: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/cnaes/<segmento>', methods=['GET'])
@login_required  
def api_cnaes_por_segmento(segmento):
    """API para obter CNAEs com descrições de um segmento específico"""
    try:
        if data_manager.df is None:
            return jsonify({'error': 'Dados não carregados'}), 400
        
        df = data_manager.df
        
        # Verificar se as colunas necessárias existem
        if 'SEGMENTO' not in df.columns or 'CNAE' not in df.columns:
            return jsonify({'error': 'Colunas SEGMENTO ou CNAE não encontradas'}), 400
        
        # Filtrar CNAEs do segmento específico
        cnaes_df = (
            df.filter(pl.col('SEGMENTO') == segmento)
            .group_by(['CNAE'])
            .agg([pl.len().alias('registros')])
            .with_columns([
                pl.col('CNAE').cast(pl.Utf8).alias('CNAE_STR')
            ])
            .sort(['registros', 'CNAE'], descending=[True, False])
        )
        
        # Se temos dados CNAE, fazer JOIN para obter descrições
        if data_manager.df_cnae is not None:
            print("🔗 Fazendo JOIN com dados CNAE...")
            
            # JOIN com subclasses
            cnaes_com_desc = cnaes_df.join(
                data_manager.df_cnae,
                left_on='CNAE_STR',
                right_on='Codigo_Subclasse',
                how='left'
            )
            
            # Agrupar por CLASSE para organização hierárquica
            classes_dict = {}
            
            # Verificar quantas colunas o JOIN retornou
            colunas = cnaes_com_desc.columns
            print(f"🔍 Colunas após JOIN: {colunas}")
            
            for row in cnaes_com_desc.iter_rows():
                # Adaptar baseado no número de colunas retornadas
                if len(row) >= 7:
                    cnae, registros, cnae_str, codigo_classe, codigo_subclasse, nome_classe, nome_subclasse = row[:7]
                elif len(row) >= 6:
                    cnae, registros, cnae_str, codigo_classe, codigo_subclasse, nome_classe = row[:6]
                    nome_subclasse = None
                elif len(row) >= 3:
                    cnae, registros, cnae_str = row[:3]
                    codigo_classe = codigo_subclasse = nome_classe = nome_subclasse = None
                else:
                    continue
                
                if cnae is None or str(cnae).strip() == '':
                    continue
                
                # Se não tem descrição, usar código
                classe_nome = nome_classe if nome_classe else f"Classe {str(cnae)[:5]}"
                subclasse_nome = nome_subclasse if nome_subclasse else f"CNAE {cnae}"
                
                # Agrupar por classe
                if classe_nome not in classes_dict:
                    classes_dict[classe_nome] = {
                        'classe': classe_nome,
                        'codigo_classe': codigo_classe if codigo_classe else str(cnae)[:5],
                        'subclasses': [],
                        'total_registros': 0
                    }
                
                classes_dict[classe_nome]['subclasses'].append({
                    'cnae': str(cnae),
                    'nome': subclasse_nome,
                    'registros': registros
                })
                classes_dict[classe_nome]['total_registros'] += registros
            
            # Converter para lista e ordenar
            classes = list(classes_dict.values())
            classes.sort(key=lambda x: x['total_registros'], reverse=True)
            
            # Ordenar subclasses dentro de cada classe
            for classe in classes:
                classe['subclasses'].sort(key=lambda x: x['registros'], reverse=True)
            
            total_cnaes = sum(len(classe['subclasses']) for classe in classes)
            
            print(f"🏷️ CNAEs organizados para '{segmento}': {len(classes)} classes, {total_cnaes} CNAEs")
            
            return jsonify({
                'success': True,
                'segmento': segmento,
                'classes': classes,
                'total_classes': len(classes),
                'total_cnaes': total_cnaes
            })
        else:
            # Fallback: sem descrições, apenas códigos
            print("⚠️ Dados CNAE não disponíveis, retornando apenas códigos")
            cnaes = []
            for row in cnaes_df.iter_rows():
                cnae, registros, cnae_str = row
                if cnae is not None and str(cnae).strip() != '':
                    cnaes.append({
                        'cnae': str(cnae),
                        'nome': f"CNAE {cnae}",
                        'registros': registros
                    })
            
            return jsonify({
                'success': True,
                'segmento': segmento,
                'cnaes': cnaes,
                'total': len(cnaes)
            })
        
    except Exception as e:
        print(f"❌ Erro na API CNAEs por segmento: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/cnaes/todos', methods=['GET'])
@login_required
def api_todos_cnaes():
    """API para obter todos os CNAEs disponíveis"""
    try:
        if data_manager.df is None:
            return jsonify({'error': 'Dados não carregados'}), 400
        
        df = data_manager.df
        
        # Verificar se a coluna CNAE existe
        if 'CNAE' not in df.columns:
            return jsonify({'error': 'Coluna CNAE não encontrada'}), 400
        
        # Obter todos os CNAEs únicos com contagem
        cnaes_df = (
            df
            .group_by(['CNAE'])
            .agg([pl.len().alias('registros')])
            .with_columns([
                pl.col('CNAE').cast(pl.Utf8).str.zfill(7).alias('cnae_str')
            ])
            .sort(['registros'], descending=True)
        )
        
        if data_manager.df_cnae is not None:
            # JOIN com dados CNAE para obter descrições
            cnaes_com_desc = (
                cnaes_df
                .join(
                    data_manager.df_cnae,
                    left_on='cnae_str',
                    right_on='Codigo_Subclasse',
                    how='left'
                )
            )
            
            # Agrupar por CLASSE para organização hierárquica
            classes_dict = {}
            
            # Verificar quantas colunas o JOIN retornou
            colunas = cnaes_com_desc.columns
            print(f"🔍 Colunas após JOIN todos CNAEs: {colunas}")
            
            for row in cnaes_com_desc.iter_rows():
                # Adaptar baseado no número de colunas retornadas
                if len(row) >= 7:
                    cnae, registros, cnae_str, codigo_classe, codigo_subclasse, nome_classe, nome_subclasse = row[:7]
                elif len(row) >= 6:
                    cnae, registros, cnae_str, codigo_classe, codigo_subclasse, nome_classe = row[:6]
                    nome_subclasse = None
                elif len(row) >= 3:
                    cnae, registros, cnae_str = row[:3]
                    codigo_classe = codigo_subclasse = nome_classe = nome_subclasse = None
                else:
                    continue
                
                if cnae is None or str(cnae).strip() == '':
                    continue
                
                # Se não tem descrição, usar código
                classe_nome = nome_classe if nome_classe else f"Classe {str(cnae)[:5]}"
                subclasse_nome = nome_subclasse if nome_subclasse else f"CNAE {cnae}"
                
                # Agrupar por classe
                if classe_nome not in classes_dict:
                    classes_dict[classe_nome] = {
                        'classe': classe_nome,
                        'codigo_classe': codigo_classe if codigo_classe else str(cnae)[:5],
                        'subclasses': [],
                        'total_registros': 0
                    }
                
                classes_dict[classe_nome]['subclasses'].append({
                    'cnae': str(cnae),
                    'nome': subclasse_nome,
                    'registros': registros
                })
                classes_dict[classe_nome]['total_registros'] += registros
            
            # Converter para lista e ordenar
            classes = list(classes_dict.values())
            classes.sort(key=lambda x: x['total_registros'], reverse=True)
            
            # Ordenar subclasses dentro de cada classe
            for classe in classes:
                classe['subclasses'].sort(key=lambda x: x['registros'], reverse=True)
            
            total_cnaes = sum(len(classe['subclasses']) for classe in classes)
            
            print(f"🏷️ Todos os CNAEs carregados: {len(classes)} classes, {total_cnaes} CNAEs")
            
            return jsonify({
                'success': True,
                'classes': classes,
                'total_classes': len(classes),
                'total_cnaes': total_cnaes
            })
        else:
            # Fallback: sem descrições, apenas códigos
            print("⚠️ Dados CNAE não disponíveis, retornando apenas códigos")
            cnaes = []
            for row in cnaes_df.iter_rows():
                cnae, registros, cnae_str = row
                if cnae is not None and str(cnae).strip() != '':
                    cnaes.append({
                        'cnae': str(cnae),
                        'nome': f"CNAE {cnae}",
                        'registros': registros
                    })
            
            return jsonify({
                'success': True,
                'cnaes': cnaes,
                'total': len(cnaes)
            })
        
    except Exception as e:
        print(f"❌ Erro na API todos CNAEs: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/ranking', methods=['POST'])
@login_required
def api_ranking():
    try:
        if data_manager.df is None:
            return jsonify({'error': 'Dados não carregados'}), 400
        
        data = request.get_json() or {}
        filtros = data.get('filtros', {})
        
        df = data_manager.df
        # A coluna principal de empresa é 'NOME'
        coluna_empresa = 'NOME' if 'NOME' in df.columns else None
        
        if not coluna_empresa:
            return jsonify({'error': 'Coluna empresa não encontrada'}), 400
        
        # Aplicar filtros se fornecidos
        if filtros:
            df = aplicar_filtros_avancados(df, filtros)
        
        # Verificar quais colunas existem para agregar de forma segura
        colunas_agg = [pl.col('NOVOS').sum().alias('total_novos')]
        
        # Adicionar PENDENTES apenas se existir
        if 'PENDENTES' in df.columns:
            colunas_agg.append(pl.col('PENDENTES').sum().alias('total_pendentes'))
        elif 'PENDENTES BRUTO' in df.columns:
            colunas_agg.append(pl.col('PENDENTES BRUTO').sum().alias('total_pendentes'))
        else:
            # Se não há coluna de pendentes, usar 0
            colunas_agg.append(pl.lit(0).alias('total_pendentes'))
        
        # Ranking completo SEM LIMITE (todas as empresas) para distribuição
        ranking_completo = (
            df.group_by(coluna_empresa)
            .agg(colunas_agg)
            .sort('total_novos', descending=True)
        )
        
        # Ranking limitado para renderização na interface (evitar erro JavaScript)
        ranking_limitado = ranking_completo.head(100)  # Máximo 100 para renderização
        
        # Resultado do ranking (limitado para renderização)
        resultado = []
        volume_total_mensal = 0
        for i, row in enumerate(ranking_limitado.iter_rows()):
            empresa, novos, pendentes = row
            # Garantir que empresa seja string
            empresa_str = str(empresa) if empresa is not None else "Não informado"
            volume_mensal = novos if novos else 0
            volume_total_mensal += volume_mensal
            
            resultado.append({
                'posicao': i + 1,
                'nome': empresa_str,  # Mudado de 'empresa' para 'nome' para compatibilidade
                'empresa': empresa_str,  # Manter também para compatibilidade
                'processos': novos,
                'volume_mensal': volume_mensal,
                'pendentes': pendentes if pendentes else 0
            })
        
        # Dados completos para distribuição (TODAS as empresas)
        ranking_distribuicao = []
        for row in ranking_completo.iter_rows():
            empresa, novos, pendentes = row
            empresa_str = str(empresa) if empresa is not None else "Não informado"
            volume_mensal = novos if novos else 0
            
            ranking_distribuicao.append({
                'empresa': empresa_str,
                'processos': novos,
                'volume_mensal': volume_mensal,
                'pendentes': pendentes if pendentes else 0
            })
        
        # Calcular estatísticas gerais baseadas no ranking completo
        total_empresas = len(ranking_distribuicao)  # Total de empresas únicas no resultado
        volume_total_mensal_completo = sum(emp['volume_mensal'] for emp in ranking_distribuicao)
        volume_medio_mensal = volume_total_mensal_completo // total_empresas if total_empresas > 0 else 0
        
        estatisticas = {
            'total_empresas': total_empresas,  # Total real de empresas únicas
            'volume_total_mensal': volume_total_mensal_completo,  # Volume total real
            'volume_medio_mensal': volume_medio_mensal,
            'empresas_ranking': len(resultado)  # Apenas para ranking limitado
        }
        
        return jsonify({
            'success': True, 
            'ranking': resultado,
            'ranking_completo': ranking_distribuicao,  # Dados completos para distribuição
            'estatisticas': estatisticas  # Adicionar estatísticas na resposta
        })
    except Exception as e:
        print(f"❌ Erro na API ranking: {e}")  # Debug
        return jsonify({'error': str(e)}), 500

@app.route('/api/simulacao', methods=['POST'])
@login_required
def api_simulacao():
    """API para executar simulação financeira completa"""
    try:
        data = request.get_json()
        
        # Parâmetros da simulação
        empresas_selecionadas = data.get('empresas_selecionadas', [])
        volume_customizado = data.get('volume_customizado')
        preco = float(data.get('preco', 50.0))
        custo_base = int(data.get('custo_base', 50000))
        clientes = int(data.get('clientes', 3))
        reinvestimento = float(data.get('reinvestimento', 30.0)) / 100
        
        # Calcular volume total
        if volume_customizado:
            volume_total = volume_customizado
        elif empresas_selecionadas:
            if data_manager.df is None:
                return jsonify({'error': 'Dados não carregados'}), 400
            
            df = data_manager.df
            # A coluna principal de empresa é 'NOME'
            coluna_empresa = 'NOME' if 'NOME' in df.columns else None
            
            # Somar volume das empresas selecionadas
            empresas_df = (
                df.filter(pl.col(coluna_empresa).is_in(empresas_selecionadas))
                .group_by(coluna_empresa)
                .agg([pl.col('NOVOS').sum().alias('total_novos')])
            )
            
            volume_total = empresas_df.select(pl.col('total_novos').sum()).item() or 0
            volume_total = round(volume_total / 12)  # Converter para mensal
        else:
            return jsonify({'error': 'Volume não especificado'}), 400
        
        # Executar cálculos financeiros
        resultados = calcular_financas(volume_total, preco, custo_base, clientes, reinvestimento)
        
        # Calcular break-even
        break_even = encontrar_break_even(preco, custo_base, clientes)
        
        # Análise de sensibilidade
        sensibilidade = {
            'volume': [],
            'preco': []
        }
        
        # Sensibilidade ao volume (±50%)
        for fator in [0.5, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.5]:
            vol_teste = int(volume_total * fator)
            if vol_teste > 0:
                result = calcular_financas(vol_teste, preco, custo_base, clientes, reinvestimento)
                sensibilidade['volume'].append({
                    'volume': vol_teste,
                    'lucro_liquido': result['lucro_liquido']
                })
        
        # Sensibilidade ao preço (±50%)
        for fator in [0.5, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.5]:
            preco_teste = preco * fator
            result = calcular_financas(volume_total, preco_teste, custo_base, clientes, reinvestimento)
            sensibilidade['preco'].append({
                'preco': preco_teste,
                'lucro_liquido': result['lucro_liquido']
            })
        
        return jsonify({
            'success': True,
            'volume_simulado': volume_total,
            'resultados': resultados,
            'break_even': break_even,
            'sensibilidade': sensibilidade
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/relatorio-detalhado', methods=['POST'])
@login_required
def api_relatorio_detalhado():
    """API para gerar relatório detalhado com análises por porte, ramo, segmento e CNAE"""
    try:
        filtros = request.json.get('filtros', {})
        
        # Carregar dados
        df_empresas = aplicar_filtros_avancados(data_manager.df, filtros)
        
        if df_empresas.is_empty():
            return jsonify({
                'success': True,
                'porte': [],
                'ramo': [],
                'segmento': [],
                'cnae_classes': [],
                'cnae_subclasses': []
            })
        
        # Calcular dados empresariais
        empresas_df = (
            df_empresas
            .pipe(agrupar_por_empresa)
            .pipe(calcular_processos_mensais)
            .with_columns([
                pl.when(pl.col('volume_mensal') <= 10)
                .then(pl.lit('1. Micro (1-10 proc/mês)'))
                .when(pl.col('volume_mensal') <= 50)
                .then(pl.lit('2. Pequena (11-50 proc/mês)'))
                .when(pl.col('volume_mensal') <= 100)
                .then(pl.lit('3. Média (51-100 proc/mês)'))
                .when(pl.col('volume_mensal') <= 500)
                .then(pl.lit('4. Grande (101-500 proc/mês)'))
                .when(pl.col('volume_mensal') <= 1000)
                .then(pl.lit('4. Muito Grande (501-1000 proc/mês)'))
                .otherwise(pl.lit('5. Gigante (1000+ proc/mês)'))
                .alias('faixa_porte')
            ])
        )
        
        # === 1. ANÁLISE POR PORTE ===
        porte_analise = (
            empresas_df.group_by('faixa_porte')
            .agg([
                pl.len().alias('quantidade'),
                pl.col('volume_mensal').sum().alias('volume_total'),
                pl.col('volume_mensal').mean().alias('volume_medio')
            ])
            .sort('faixa_porte')
        )
        
        porte_resultado = []
        for row in porte_analise.iter_rows():
            faixa, quantidade, volume_total, volume_medio = row
            porte_resultado.append({
                'faixa': faixa,
                'quantidade': quantidade,
                'volume_total': int(volume_total) if volume_total else 0,
                'volume_medio': int(volume_medio) if volume_medio else 0
            })
        
        # === 2. ANÁLISE POR RAMO ===
        ramo_resultado = []
        if 'RAMO' in empresas_df.columns:
            ramo_analise = (
                empresas_df.group_by('RAMO')
                .agg([
                    pl.len().alias('quantidade'),
                    pl.col('volume_mensal').sum().alias('volume_total'),
                    pl.col('volume_mensal').mean().alias('volume_medio')
                ])
                .sort('quantidade', descending=True)
            )
            
            for row in ramo_analise.iter_rows():
                ramo, quantidade, volume_total, volume_medio = row
                ramo_resultado.append({
                    'ramo': ramo,
                    'quantidade': quantidade,
                    'volume_total': int(volume_total) if volume_total else 0,
                    'volume_medio': int(volume_medio) if volume_medio else 0
                })
        
        # === 3. ANÁLISE POR SEGMENTO ===
        segmento_resultado = []
        if 'SEGMENTO' in empresas_df.columns:
            segmento_analise = (
                empresas_df.group_by('SEGMENTO')
                .agg([
                    pl.len().alias('quantidade'),
                    pl.col('volume_mensal').sum().alias('volume_total'),
                    pl.col('volume_mensal').mean().alias('volume_medio')
                ])
                .sort('quantidade', descending=True)
            )
            
            for row in segmento_analise.iter_rows():
                segmento, quantidade, volume_total, volume_medio = row
                segmento_resultado.append({
                    'segmento': segmento,
                    'quantidade': quantidade,
                    'volume_total': int(volume_total) if volume_total else 0,
                    'volume_medio': int(volume_medio) if volume_medio else 0
                })
        
        # === 4. ANÁLISE POR CNAE (CLASSES E SUBCLASSES) ===
        cnae_classes_resultado = []
        cnae_subclasses_resultado = []
        
        if 'CNAE' in empresas_df.columns:
            # Carregar dados CNAE com informações de classe e subclasse
            try:
                df_cnae_info = pl.read_csv(data_manager.cnae_file)
                
                # Mapear CNAEs para suas classes e subclasses
                empresas_com_cnae = empresas_df.join(
                    df_cnae_info.select(['CNAE', 'CODIGO_CLASSE', 'CODIGO_SUBCLASSE', 'NOME_CLASSE', 'NOME_SUBCLASSE']),
                    on='CNAE',
                    how='left'
                )
                
                # Análise por Classes CNAE
                if 'NOME_CLASSE' in empresas_com_cnae.columns:
                    classe_analise = (
                        empresas_com_cnae.filter(pl.col('NOME_CLASSE').is_not_null())
                        .group_by('NOME_CLASSE')
                        .agg([
                            pl.len().alias('quantidade'),
                            pl.col('volume_mensal').sum().alias('volume_total'),
                            pl.col('volume_mensal').mean().alias('volume_medio'),
                            pl.col('CODIGO_CLASSE').first().alias('codigo_classe')
                        ])
                        .sort('quantidade', descending=True)
                    )
                    
                    for row in classe_analise.iter_rows():
                        nome_classe, quantidade, volume_total, volume_medio, codigo_classe = row
                        cnae_classes_resultado.append({
                            'classe': nome_classe,
                            'codigo_classe': codigo_classe,
                            'quantidade': quantidade,
                            'volume_total': int(volume_total) if volume_total else 0,
                            'volume_medio': int(volume_medio) if volume_medio else 0
                        })
                
                # Análise por Subclasses CNAE
                if 'NOME_SUBCLASSE' in empresas_com_cnae.columns:
                    subclasse_analise = (
                        empresas_com_cnae.filter(pl.col('NOME_SUBCLASSE').is_not_null())
                        .group_by(['NOME_SUBCLASSE', 'NOME_CLASSE'])
                        .agg([
                            pl.len().alias('quantidade'),
                            pl.col('volume_mensal').sum().alias('volume_total'),
                            pl.col('volume_mensal').mean().alias('volume_medio'),
                            pl.col('CODIGO_SUBCLASSE').first().alias('codigo_subclasse')
                        ])
                        .sort('quantidade', descending=True)
                        .limit(20)  # Limitar a 20 subclasses mais relevantes
                    )
                    
                    for row in subclasse_analise.iter_rows():
                        nome_subclasse, nome_classe, quantidade, volume_total, volume_medio, codigo_subclasse = row
                        cnae_subclasses_resultado.append({
                            'subclasse': nome_subclasse,
                            'classe_pai': nome_classe,
                            'codigo_subclasse': codigo_subclasse,
                            'quantidade': quantidade,
                            'volume_total': int(volume_total) if volume_total else 0,
                            'volume_medio': int(volume_medio) if volume_medio else 0
                        })
                        
            except Exception as e:
                print(f"⚠️ Erro ao carregar análise CNAE: {e}")
        
        return jsonify({
            'success': True,
            'porte': porte_resultado,
            'ramo': ramo_resultado,
            'segmento': segmento_resultado,
            'cnae_classes': cnae_classes_resultado,
            'cnae_subclasses': cnae_subclasses_resultado
        })
    except Exception as e:
        print(f"❌ Erro na API relatório detalhado: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/progress', methods=['GET'])
@login_required
def api_progress():
    """API para obter progresso do carregamento"""
    return jsonify(progress_data)

def update_progress(percent, status, details='', speed='', bytes=''):
    """Atualizar progresso global"""
    global progress_data
    progress_data.update({
        'percent': min(100, max(0, percent)),
        'status': status,
        'details': details,
        'speed': speed,
        'bytes': bytes,
        'active': True
    })
    print(f"📊 Progresso: {percent:.1f}% - {status}")



def agrupar_por_empresa(df: pl.DataFrame) -> pl.DataFrame:
    """
    Agrupa dados por empresa, priorizando CNPJ quando disponível
    Remove duplicatas de empresas que aparecem em múltiplos tribunais/graus
    """
    if df.is_empty():
        return df
    
    # Detectar se existe coluna de CNPJ
    colunas_cnpj = [col for col in df.columns if 'CNPJ' in col.upper()]
    
    if colunas_cnpj:
        # Usar CNPJ para agrupamento (método mais preciso)
        coluna_cnpj = colunas_cnpj[0]
        
        # Definir agregações básicas
        agregacoes = [
            pl.col('NOME').first().alias('NOME'),
            pl.col('NOVOS').sum().alias('NOVOS'),
            pl.col('TRIBUNAL').first().alias('TRIBUNAL'),
            pl.len().alias('REGISTROS_AGRUPADOS')
        ]
        
        # Adicionar outras colunas se existirem
        for col in df.columns:
            if col not in ['NOME', 'NOVOS', 'TRIBUNAL', coluna_cnpj]:
                if 'PENDENTES' in col or 'BAIXADOS' in col:
                    agregacoes.append(pl.col(col).sum().alias(col))
                else:
                    agregacoes.append(pl.col(col).first().alias(col))
        
        df_agrupado = df.group_by([coluna_cnpj]).agg(agregacoes)
        
        # Remover coluna CNPJ da visualização
        colunas_para_manter = [col for col in df_agrupado.columns if col != coluna_cnpj]
        df_agrupado = df_agrupado.select(colunas_para_manter)
        
    else:
        # Fallback: agrupar por nome da empresa
        colunas_agrupamento = ['NOME']
        if 'SEGMENTO' in df.columns:
            colunas_agrupamento.append('SEGMENTO')
        
        agregacoes = [
            pl.col('NOVOS').sum().alias('NOVOS'),
            pl.col('TRIBUNAL').first().alias('TRIBUNAL'),
            pl.len().alias('REGISTROS_AGRUPADOS')
        ]
        
        # Adicionar outras colunas
        for col in df.columns:
            if col not in ['NOME', 'NOVOS', 'TRIBUNAL'] + colunas_agrupamento:
                if 'PENDENTES' in col or 'BAIXADOS' in col:
                    agregacoes.append(pl.col(col).sum().alias(col))
                else:
                    agregacoes.append(pl.col(col).first().alias(col))
        
        df_agrupado = df.group_by(colunas_agrupamento).agg(agregacoes)
    
    return df_agrupado

def calcular_processos_mensais(df: pl.DataFrame) -> pl.DataFrame:
    """
    Calcula processos mensais baseado na metodologia CNJ oficial
    NOVOS: Processos iniciados nos 12 MESES ANTERIORES (período anual)
    PENDENTES: Snapshot do mês de referência
    """
    if df.is_empty():
        return df
    
    df_com_calculo = df.with_columns([
        # Método 1: NOVOS ÷ 12 (metodologia CNJ correta)
        pl.when(pl.col('NOVOS').is_not_null() & (pl.col('NOVOS') > 0))
        .then((pl.col('NOVOS').cast(pl.Float64) / 12).round())
        
        # Método 2: Estimativa por PENDENTES ÷ 10 (rotatividade)
        .when(pl.col('PENDENTES BRUTO').is_not_null() & (pl.col('PENDENTES BRUTO') > 0))
        .then((pl.col('PENDENTES BRUTO').cast(pl.Float64) / 10).round())
        
        # Método 3: Estimativa mínima
        .otherwise(25)
        .alias('volume_mensal')
    ]).with_columns([
        # Método usado para transparência
        pl.when(pl.col('NOVOS').is_not_null() & (pl.col('NOVOS') > 0))
        .then(pl.lit("NOVOS ÷ 12"))
        .when(pl.col('PENDENTES BRUTO').is_not_null() & (pl.col('PENDENTES BRUTO') > 0))
        .then(pl.lit("PENDENTES ÷ 10"))
        .otherwise(pl.lit("Estimativa mínima"))
        .alias('metodo_calculo')
    ])
    
    return df_com_calculo

def aplicar_filtros_avancados(df: pl.DataFrame, filtros: dict) -> pl.DataFrame:
    """Aplica filtros avançados baseados nos parâmetros (suporta seleção múltipla)"""
    if df.is_empty():
        return df
    
    df_filtrado = df
    
    # Filtro por tribunal (seleção múltipla)
    tribunais = filtros.get('tribunais', [])
    if tribunais and len(tribunais) > 0:
        # Se tribunais é uma lista, usar .is_in()
        if isinstance(tribunais, list):
            df_filtrado = df_filtrado.filter(pl.col('TRIBUNAL').is_in(tribunais))
        # Se for string única, usar == (compatibilidade)
        elif tribunais != 'Todos':
            df_filtrado = df_filtrado.filter(pl.col('TRIBUNAL') == tribunais)
    
    # Filtro por grau (seleção múltipla)
    graus = filtros.get('graus', [])
    if graus and len(graus) > 0 and 'GRAU' in df.columns:
        if isinstance(graus, list):
            df_filtrado = df_filtrado.filter(pl.col('GRAU').is_in(graus))
        elif graus != 'Todos':
            df_filtrado = df_filtrado.filter(pl.col('GRAU') == graus)
    
    # Filtro por segmento (seleção múltipla)
    segmentos = filtros.get('segmentos', [])
    if segmentos and len(segmentos) > 0 and 'SEGMENTO' in df.columns:
        if isinstance(segmentos, list):
            df_filtrado = df_filtrado.filter(pl.col('SEGMENTO').is_in(segmentos))
        elif segmentos != 'Todos':
            df_filtrado = df_filtrado.filter(pl.col('SEGMENTO') == segmentos)
    
    # Filtro por ramo (seleção múltipla)
    ramos = filtros.get('ramos', [])
    if ramos and len(ramos) > 0 and 'RAMO' in df.columns:
        if isinstance(ramos, list):
            df_filtrado = df_filtrado.filter(pl.col('RAMO').is_in(ramos))
        elif ramos != 'Todos':
            df_filtrado = df_filtrado.filter(pl.col('RAMO') == ramos)
    
    # Filtro por CNAE (seleção múltipla)
    cnaes = filtros.get('cnae', [])
    if cnaes and len(cnaes) > 0 and 'CNAE' in df.columns:
        if isinstance(cnaes, list):
            # Converter todos os CNAEs para string para comparação correta
            cnaes_str = [str(cnae) for cnae in cnaes if cnae and str(cnae).strip() != '']
            if cnaes_str:
                df_filtrado = df_filtrado.filter(pl.col('CNAE').cast(pl.Utf8).is_in(cnaes_str))
        elif cnaes != 'Todos' and str(cnaes).strip() != '':
            # Compatibilidade com seleção única
            df_filtrado = df_filtrado.filter(pl.col('CNAE').cast(pl.Utf8) == str(cnaes))
    
    # Filtros por Classe e Subclasse CNAE (requer JOIN com dados CNAE)
    classes_cnae = filtros.get('classes_cnae', [])
    subclasses_cnae = filtros.get('subclasses_cnae', [])
    
    if (classes_cnae and len(classes_cnae) > 0) or (subclasses_cnae and len(subclasses_cnae) > 0):
        if data_manager.df_cnae is not None and 'CNAE' in df_filtrado.columns:
            # JOIN com dados CNAE para aplicar filtros de classe/subclasse
            df_com_cnae = df_filtrado.join(
                data_manager.df_cnae,
                left_on=pl.col('CNAE').cast(pl.Utf8).str.zfill(7),
                right_on='Codigo_Subclasse',
                how='left'
            )
            
            # Aplicar filtro por classe CNAE
            if classes_cnae and len(classes_cnae) > 0:
                if isinstance(classes_cnae, list):
                    df_com_cnae = df_com_cnae.filter(pl.col('Nome_Classe').is_in(classes_cnae))
                else:
                    df_com_cnae = df_com_cnae.filter(pl.col('Nome_Classe') == classes_cnae)
            
            # Aplicar filtro por subclasse CNAE
            if subclasses_cnae and len(subclasses_cnae) > 0:
                if isinstance(subclasses_cnae, list):
                    df_com_cnae = df_com_cnae.filter(pl.col('Nome_Subclasse').is_in(subclasses_cnae))
                else:
                    df_com_cnae = df_com_cnae.filter(pl.col('Nome_Subclasse') == subclasses_cnae)
            
            # Manter apenas as colunas originais
            colunas_originais = [col for col in df_filtrado.columns if col in df_com_cnae.columns]
            df_filtrado = df_com_cnae.select(colunas_originais)
    
    # Nota: Filtros de volume são aplicados após calcular_processos_mensais()
    # pois a coluna volume_mensal ainda não existe neste ponto
    
    # Busca por nome da empresa
    if filtros.get('busca_empresa'):
        busca = filtros['busca_empresa'].lower()
        df_filtrado = df_filtrado.filter(
            pl.col('NOME').str.to_lowercase().str.contains(busca)
        )
    
    return df_filtrado

def aplicar_filtros_volume(df: pl.DataFrame, filtros: dict) -> pl.DataFrame:
    """Aplica filtros de volume após a coluna volume_mensal ser criada"""
    if df.is_empty():
        return df
    
    df_filtrado = df
    
    # Filtro por volume mínimo
    if filtros.get('volume_minimo'):
        df_filtrado = df_filtrado.filter(pl.col('volume_mensal') >= filtros['volume_minimo'])
    
    # Filtro por volume máximo
    if filtros.get('volume_maximo'):
        df_filtrado = df_filtrado.filter(pl.col('volume_mensal') <= filtros['volume_maximo'])
    
    return df_filtrado

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

def gerar_dados_simulados() -> pl.DataFrame:
    """Gera dados simulados para demonstração"""
    import random
    
    # Usar seed fixa para dados consistentes
    np.random.seed(42)
    random.seed(42)
    
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
        'NOME': empresas[:1000],
        'TRIBUNAL': np.random.choice(['TRT1', 'TRT2', 'TJSP', 'TRF1', 'TST', 'TJRJ', 'TJMG'], 1000),
        'GRAU': np.random.choice(['1º GRAU', '2º GRAU', 'INSTÂNCIA ÚNICA'], 1000),
        'RAMO': np.random.choice(ramos, 1000),
        'NOVOS': np.random.randint(100, 5000, 1000),
        'PENDENTES BRUTO': np.random.randint(500, 20000, 1000),
        'PENDENTES LÍQUIDO': np.random.randint(300, 15000, 1000),
        'SEGMENTO': np.random.choice(['ADMINISTRAÇÃO PÚBLICA', 'TELECOMUNICAÇÕES', 'BANCÁRIO', 'VAREJO', 'ENERGIA'], 1000),
        'ANO': [2025] * 1000,
        'MES': np.random.randint(1, 13, 1000)
    }
    
    return pl.DataFrame(dados_fake)



if __name__ == '__main__':
    print("🚀 Iniciando servidor Flask...")
    print("📍 URL: http://127.0.0.1:5000")
    print("👤 Login: admin / 123")
    print("🔄 Aguarde o carregamento dos dados...")
    
    # Para produção, usar configurações diferentes
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(debug=debug, host='0.0.0.0', port=port, use_reloader=False) 
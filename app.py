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

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'pdpj2024-simulador-secreto')

# Simulação de banco (em produção seria PostgreSQL)
users_db = {
    'admin': {
        'id': 1,
        'password_hash': generate_password_hash('pdpj2024'),
        'email': 'admin@simulador.com'
    }
}

class DataManager:
    def __init__(self):
        self.file_id = "1Ns07hTZaK4Ry6bFEHvLACZ5tHJ7b-C2E"
        self.cache_file = "dados_litigantes.parquet"
        self.df = None
    
    def download_data(self):
        try:
            print("📥 Baixando dados dos grandes litigantes...")
            
            # URLs com diferentes estratégias
            download_urls = [
                f"https://drive.google.com/uc?export=download&id={self.file_id}&confirm=t",
                f"https://drive.usercontent.google.com/download?id={self.file_id}&export=download&confirm=t",
                f"https://drive.google.com/uc?id={self.file_id}&export=download",
                f"https://docs.google.com/uc?export=download&id={self.file_id}"
            ]
            
            session = requests.Session()
            
            for i, url in enumerate(download_urls):
                try:
                    print(f"🔄 Tentativa {i+1}/4: {url[:50]}...")
                    
                    # Primeira requisição para obter token se necessário
                    response = session.get(url, stream=True, timeout=300)
                    
                    # Verificar se é uma página de confirmação de vírus
                    if 'virus scan warning' in response.text.lower() or 'download_warning' in response.text:
                        print("⚠️ Detectada página de confirmação de vírus, extraindo link direto...")
                        
                        # Procurar pelo link de confirmação
                        import re
                        confirm_pattern = r'href="(/uc\?export=download[^"]*)"'
                        match = re.search(confirm_pattern, response.text)
                        
                        if match:
                            direct_url = "https://drive.google.com" + match.group(1).replace('&amp;', '&')
                            print(f"🔗 Link direto encontrado: {direct_url[:60]}...")
                            response = session.get(direct_url, stream=True, timeout=300)
                    
                    # Verificar se a resposta parece ser binária (arquivo parquet)
                    content_type = response.headers.get('content-type', '').lower()
                    if 'text/html' in content_type and response.status_code == 200:
                        print("⚠️ Resposta em HTML detectada, tentando próxima URL...")
                        continue
                    
                    if response.status_code == 200:
                        print("💾 Salvando arquivo...")
                        total_size = 0
                        
                        with open(self.cache_file, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                                    total_size += len(chunk)
                                    
                                    # Mostrar progresso a cada 10MB
                                    if total_size % (10 * 1024 * 1024) == 0:
                                        print(f"📦 Baixados: {total_size / (1024*1024):.1f} MB")
                        
                        print(f"✅ Download concluído: {total_size / (1024*1024):.1f} MB")
                        
                        # Verificar integridade do arquivo
                        try:
                            print("🔍 Verificando integridade do arquivo...")
                            test_df = pl.scan_parquet(self.cache_file)
                            rows = test_df.select(pl.len()).collect().item()
                            print(f"✅ Arquivo válido com {rows:,} registros")
                            return True
                            
                        except Exception as e:
                            print(f"❌ Arquivo corrompido: {e}")
                            # Remover arquivo corrompido
                            if os.path.exists(self.cache_file):
                                os.remove(self.cache_file)
                            continue
                            
                except Exception as e:
                    print(f"❌ Erro na tentativa {i+1}: {e}")
                    continue
            
            print("❌ Todas as tentativas de download falharam")
            return False
            
        except Exception as e:
            print(f"❌ Erro geral no download: {e}")
            return False
    
    def load_data(self, limit=500000):
        try:
            # Tentar carregar arquivo local primeiro
            if os.path.exists(self.cache_file):
                print(f"📂 Carregando arquivo local: {self.cache_file}")
                try:
                    df_lazy = pl.scan_parquet(self.cache_file)
                    self.df = df_lazy.head(limit).collect()
                    print(f"✅ Dados carregados do arquivo local: {len(self.df):,} registros")
                    return self.df
                except Exception as e:
                    print(f"⚠️ Arquivo local corrompido: {e}")
                    os.remove(self.cache_file)
            
            # Se não existe arquivo local, tentar download
            print("🌐 Tentando download do Google Drive...")
            if not self.download_data():
                print("⚠️ Download falhou, gerando dados de teste...")
                return self._create_fallback_data(limit)
            
            # Carregar dados baixados
            df_lazy = pl.scan_parquet(self.cache_file)
            self.df = df_lazy.head(limit).collect()
            print(f"✅ Dados carregados: {len(self.df):,} registros")
            return self.df
            
        except Exception as e:
            print(f"❌ Erro ao carregar: {e}")
            print("🔄 Tentando dados de fallback...")
            return self._create_fallback_data(limit)
    
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
    return render_template('dashboard.html', username=session.get('username'))

@app.route('/api/carregar-dados', methods=['POST'])
@login_required
def api_carregar_dados():
    try:
        data = request.get_json()
        limit = data.get('limit', 500000)
        
        print(f"🔄 Solicitação de carregamento: {limit:,} registros")
        
        df = data_manager.load_data(limit=limit)
        if df is None:
            error_msg = 'Falha ao baixar ou carregar os dados do Google Drive. Verifique sua conexão de internet.'
            print(f"❌ {error_msg}")
            return jsonify({'error': error_msg}), 500
        
        total_registros = len(df)
        total_processos = df.select(pl.col('NOVOS').sum()).item() if 'NOVOS' in df.columns else 0
        
        coluna_empresa = None
        for col in ['NOME', 'EMPRESA', 'ÓRGÃO', 'ORGAO']:
            if col in df.columns:
                coluna_empresa = col
                break
        
        print(f"✅ Dados carregados com sucesso: {total_registros:,} registros")
        
        # Verificar se são dados de demonstração
        is_demo = total_registros <= 10000
        
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
        error_msg = f'Erro no carregamento: {str(e)}'
        print(f"❌ {error_msg}")
        return jsonify({'error': error_msg}), 500

@app.route('/api/ranking', methods=['POST'])
@login_required
def api_ranking():
    try:
        if data_manager.df is None:
            return jsonify({'error': 'Dados não carregados'}), 400
        
        df = data_manager.df
        coluna_empresa = None
        for col in ['NOME', 'EMPRESA', 'ÓRGÃO', 'ORGAO']:
            if col in df.columns:
                coluna_empresa = col
                break
        
        if not coluna_empresa:
            return jsonify({'error': 'Coluna empresa não encontrada'}), 400
        
        ranking = (
            df.group_by(coluna_empresa)
            .agg([pl.col('NOVOS').sum().alias('total_novos')])
            .sort('total_novos', descending=True)
            .head(20)
        )
        
        resultado = []
        for i, row in enumerate(ranking.iter_rows()):
            empresa, novos = row
            resultado.append({
                'posicao': i + 1,
                'empresa': empresa,
                'processos': novos
            })
        
        return jsonify({'success': True, 'ranking': resultado})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/simulacao', methods=['POST'])
@login_required
def api_simulacao():
    try:
        data = request.get_json()
        preco = float(data.get('preco', 50.0))
        conversao = float(data.get('conversao', 5.0)) / 100
        
        if data_manager.df is None:
            return jsonify({'error': 'Dados não carregados'}), 400
        
        df = data_manager.df
        coluna_empresa = None
        for col in ['NOME', 'EMPRESA', 'ÓRGÃO', 'ORGAO']:
            if col in df.columns:
                coluna_empresa = col
                break
        
        empresas = (
            df.group_by(coluna_empresa)
            .agg([pl.col('NOVOS').sum().alias('total_novos')])
            .sort('total_novos', descending=True)
            .head(10)
        )
        
        resultado = []
        for row in empresas.iter_rows():
            empresa, processos = row
            clientes = int(processos * conversao)
            receita_mensal = clientes * preco * 12
            
            resultado.append({
                'empresa': empresa,
                'processos': processos,
                'clientes_potenciais': clientes,
                'receita_mensal': receita_mensal
            })
        
        return jsonify({'success': True, 'simulacao': resultado})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 
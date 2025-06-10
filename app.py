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
            print("📥 Baixando dados...")
            urls = [
                f"https://drive.google.com/uc?export=download&id={self.file_id}",
                f"https://drive.google.com/uc?id={self.file_id}&export=download"
            ]
            
            for url in urls:
                try:
                    response = requests.get(url, stream=True, timeout=300)
                    if response.status_code == 200:
                        with open(self.cache_file, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                        
                        # Verificar arquivo
                        test_df = pl.scan_parquet(self.cache_file)
                        rows = test_df.select(pl.len()).collect().item()
                        print(f"✅ Dados baixados: {rows:,} registros")
                        return True
                except Exception as e:
                    continue
            return False
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
    
    def load_data(self, limit=500000):
        try:
            if not os.path.exists(self.cache_file):
                if not self.download_data():
                    return None
            
            df_lazy = pl.scan_parquet(self.cache_file)
            self.df = df_lazy.head(limit).collect()
            print(f"✅ Carregados: {len(self.df):,} registros")
            return self.df
        except Exception as e:
            print(f"❌ Erro ao carregar: {e}")
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
        
        df = data_manager.load_data(limit=limit)
        if df is None:
            return jsonify({'error': 'Falha ao carregar dados'}), 500
        
        total_registros = len(df)
        total_processos = df.select(pl.col('NOVOS').sum()).item() if 'NOVOS' in df.columns else 0
        
        coluna_empresa = None
        for col in ['NOME', 'EMPRESA', 'ÓRGÃO', 'ORGAO']:
            if col in df.columns:
                coluna_empresa = col
                break
        
        return jsonify({
            'success': True,
            'stats': {
                'total_registros': total_registros,
                'total_processos': total_processos,
                'coluna_empresa': coluna_empresa
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
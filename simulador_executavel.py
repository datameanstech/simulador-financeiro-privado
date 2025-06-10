#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 SIMULADOR FINANCEIRO - GRANDES LITIGANTES
Versão Executável para Não-Desenvolvedores

INSTRUÇÕES:
1. Baixe este arquivo
2. Clique duas vezes para executar  
3. Use a interface gráfica simples
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import os
import sys
import subprocess

def instalar_dependencias():
    """Instalar automaticamente as dependências"""
    try:
        import polars as pl
        import requests
        return True
    except ImportError:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'polars', 'requests'])
            return True
        except:
            return False

class SimuladorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎯 Simulador Financeiro - Grandes Litigantes")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        self.df = None
        self.arquivo_path = None
        self.processando = False
        
        self.criar_interface()
    
    def criar_interface(self):
        # Título
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)
        
        tk.Label(
            title_frame, 
            text="🎯 SIMULADOR FINANCEIRO - GRANDES LITIGANTES",
            font=('Arial', 14, 'bold'),
            fg='white',
            bg='#2c3e50'
        ).pack(expand=True)
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # PASSO 1: Dados
        frame1 = tk.LabelFrame(main_frame, text="📥 PASSO 1: Carregar Dados", font=('Arial', 11, 'bold'), bg='#f0f0f0')
        frame1.pack(fill='x', pady=(0, 10))
        
        btn_frame1 = tk.Frame(frame1, bg='#f0f0f0')
        btn_frame1.pack(fill='x', padx=10, pady=8)
        
        tk.Button(
            btn_frame1,
            text="🚀 BAIXAR DADOS AUTOMATICAMENTE",
            command=self.baixar_dados_automatico,
            bg='#27ae60', fg='white', font=('Arial', 10, 'bold'),
            height=2, cursor='hand2'
        ).pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        tk.Button(
            btn_frame1,
            text="📁 ESCOLHER ARQUIVO LOCAL",
            command=self.escolher_arquivo,
            bg='#3498db', fg='white', font=('Arial', 10, 'bold'),
            height=2, cursor='hand2'
        ).pack(side='right', fill='x', expand=True, padx=(5, 0))
        
        self.dados_status = tk.Label(frame1, text="Nenhum arquivo carregado", fg='gray', bg='#f0f0f0')
        self.dados_status.pack(pady=3)
        
        # PASSO 2: Configurações
        frame2 = tk.LabelFrame(main_frame, text="⚙️ PASSO 2: Configurar Simulação", font=('Arial', 11, 'bold'), bg='#f0f0f0')
        frame2.pack(fill='x', pady=(0, 10))
        
        config_frame = tk.Frame(frame2, bg='#f0f0f0')
        config_frame.pack(fill='x', padx=10, pady=8)
        
        # Configurações em 2 linhas
        row1 = tk.Frame(config_frame, bg='#f0f0f0')
        row1.pack(fill='x', pady=3)
        
        tk.Label(row1, text="💰 Preço por processo: R$", font=('Arial', 9), bg='#f0f0f0').pack(side='left')
        self.preco_var = tk.StringVar(value="50.00")
        tk.Entry(row1, textvariable=self.preco_var, width=8).pack(side='left', padx=(5, 15))
        
        tk.Label(row1, text="🏢 Custo mensal: R$", font=('Arial', 9), bg='#f0f0f0').pack(side='left')
        self.custo_var = tk.StringVar(value="10000")
        tk.Entry(row1, textvariable=self.custo_var, width=8).pack(side='left', padx=(5, 0))
        
        row2 = tk.Frame(config_frame, bg='#f0f0f0')
        row2.pack(fill='x', pady=3)
        
        tk.Label(row2, text="📊 Taxa conversão: ", font=('Arial', 9), bg='#f0f0f0').pack(side='left')
        self.conversao_var = tk.StringVar(value="5.0")
        tk.Entry(row2, textvariable=self.conversao_var, width=8).pack(side='left', padx=(5, 5))
        tk.Label(row2, text="%", bg='#f0f0f0').pack(side='left', padx=(0, 15))
        
        tk.Label(row2, text="📈 Registros: ", font=('Arial', 9), bg='#f0f0f0').pack(side='left')
        self.limite_var = tk.StringVar(value="500000")
        limite_combo = ttk.Combobox(row2, textvariable=self.limite_var, width=10, state='readonly')
        limite_combo['values'] = ('100000', '500000', '1000000', 'TODOS')
        limite_combo.pack(side='left', padx=(5, 0))
        
        # PASSO 3: Análises
        frame3 = tk.LabelFrame(main_frame, text="🔍 PASSO 3: Executar Análises", font=('Arial', 11, 'bold'), bg='#f0f0f0')
        frame3.pack(fill='x', pady=(0, 10))
        
        btn_frame3 = tk.Frame(frame3, bg='#f0f0f0')
        btn_frame3.pack(fill='x', padx=10, pady=8)
        
        tk.Button(btn_frame3, text="🏆 RANKING", command=lambda: self.executar_analise('ranking'),
                 bg='#e74c3c', fg='white', font=('Arial', 9, 'bold'), cursor='hand2'
                ).pack(side='left', fill='x', expand=True, padx=(0, 2))
        
        tk.Button(btn_frame3, text="💰 SIMULAÇÃO", command=lambda: self.executar_analise('simulacao'),
                 bg='#f39c12', fg='white', font=('Arial', 9, 'bold'), cursor='hand2'
                ).pack(side='left', fill='x', expand=True, padx=(2, 2))
        
        tk.Button(btn_frame3, text="⚖️ TRIBUNAIS", command=lambda: self.executar_analise('tribunais'),
                 bg='#9b59b6', fg='white', font=('Arial', 9, 'bold'), cursor='hand2'
                ).pack(side='left', fill='x', expand=True, padx=(2, 2))
        
        tk.Button(btn_frame3, text="📋 COMPLETO", command=lambda: self.executar_analise('completo'),
                 bg='#16a085', fg='white', font=('Arial', 9, 'bold'), cursor='hand2'
                ).pack(side='left', fill='x', expand=True, padx=(2, 0))
        
        # RESULTADOS
        frame4 = tk.LabelFrame(main_frame, text="📊 RESULTADOS", font=('Arial', 11, 'bold'), bg='#f0f0f0')
        frame4.pack(fill='both', expand=True)
        
        self.resultado_text = scrolledtext.ScrolledText(
            frame4, wrap=tk.WORD, font=('Consolas', 9), bg='white', fg='black'
        )
        self.resultado_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Texto inicial
        self.resultado_text.insert(tk.END, "🎯 BEM-VINDO AO SIMULADOR FINANCEIRO!\n\n")
        self.resultado_text.insert(tk.END, "COMO USAR:\n")
        self.resultado_text.insert(tk.END, "1️⃣ Carregue os dados (botão verde 'BAIXAR DADOS')\n")
        self.resultado_text.insert(tk.END, "2️⃣ Configure os valores se quiser (ou use os padrões)\n")
        self.resultado_text.insert(tk.END, "3️⃣ Clique em uma das análises\n")
        self.resultado_text.insert(tk.END, "4️⃣ Aguarde os resultados aparecerem aqui\n\n")
        self.resultado_text.insert(tk.END, "💡 DICA: Comece com 'RANKING' para ver as maiores empresas!\n")
        
        # Status bar
        self.status_label = tk.Label(self.root, text="Pronto para começar", relief=tk.SUNKEN, anchor=tk.W, bg='#ecf0f1')
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
    
    def atualizar_status(self, texto):
        self.status_label.config(text=texto)
        self.root.update()
    
    def log_resultado(self, texto):
        self.resultado_text.insert(tk.END, f"\n{texto}")
        self.resultado_text.see(tk.END)
        self.root.update()
    
    def baixar_dados_automatico(self):
        if self.processando:
            messagebox.showwarning("Atenção", "Já existe um processo em andamento!")
            return
        
        def baixar():
            self.processando = True
            try:
                self.atualizar_status("Baixando dados...")
                self.log_resultado("🚀 INICIANDO DOWNLOAD...")
                
                import polars as pl
                import requests
                
                file_id = "1Ns07hTZaK4Ry6bFEHvLACZ5tHJ7b-C2E"
                nome_arquivo = "grandes_litigantes_202504.parquet"
                
                self.log_resultado("📥 Conectando ao Google Drive...")
                
                urls = [
                    f"https://drive.google.com/uc?export=download&id={file_id}",
                    f"https://drive.google.com/uc?id={file_id}&export=download"
                ]
                
                for i, url in enumerate(urls):
                    try:
                        self.log_resultado(f"🔄 Tentativa {i+1}...")
                        
                        session = requests.Session()
                        response = session.get(url, stream=True, timeout=300)
                        
                        if response.status_code == 200:
                            self.log_resultado("💾 Salvando arquivo...")
                            
                            with open(nome_arquivo, 'wb') as f:
                                for chunk in response.iter_content(chunk_size=8192):
                                    if chunk:
                                        f.write(chunk)
                            
                            if os.path.exists(nome_arquivo) and os.path.getsize(nome_arquivo) > 1000000:
                                try:
                                    test_df = pl.scan_parquet(nome_arquivo)
                                    rows = test_df.select(pl.len()).collect().item()
                                    
                                    self.arquivo_path = nome_arquivo
                                    self.dados_status.config(text=f"✅ Arquivo: {rows:,} registros", fg='green')
                                    self.log_resultado(f"✅ SUCESSO! {rows:,} registros disponíveis")
                                    self.atualizar_status("Dados prontos")
                                    return
                                    
                                except Exception as e:
                                    self.log_resultado(f"⚠️ Arquivo corrompido: {e}")
                                    continue
                    
                    except Exception as e:
                        self.log_resultado(f"❌ Erro: {str(e)[:100]}")
                
                self.log_resultado("❌ Download falhou. Tente 'Escolher Arquivo' se já tem o arquivo.")
                messagebox.showerror("Erro", "Download falhou. Use 'Escolher Arquivo' se já tem o .parquet")
                
            except Exception as e:
                self.log_resultado(f"❌ ERRO: {str(e)}")
                messagebox.showerror("Erro", f"Erro: {str(e)}")
            
            finally:
                self.processando = False
                self.atualizar_status("Pronto")
        
        thread = threading.Thread(target=baixar)
        thread.daemon = True
        thread.start()
    
    def escolher_arquivo(self):
        file_path = filedialog.askopenfilename(
            title="Escolher arquivo .parquet",
            filetypes=[("Arquivos Parquet", "*.parquet"), ("Todos", "*.*")]
        )
        
        if file_path:
            try:
                import polars as pl
                test_df = pl.scan_parquet(file_path)
                rows = test_df.select(pl.len()).collect().item()
                
                self.arquivo_path = file_path
                self.dados_status.config(text=f"✅ Arquivo: {rows:,} registros", fg='green')
                self.log_resultado(f"✅ Arquivo carregado: {rows:,} registros")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Arquivo inválido: {str(e)}")
    
    def executar_analise(self, tipo):
        if not self.arquivo_path:
            messagebox.showwarning("Atenção", "Primeiro carregue os dados!")
            return
        
        if self.processando:
            messagebox.showwarning("Atenção", "Aguarde o processamento atual!")
            return
        
        def processar():
            self.processando = True
            try:
                import polars as pl
                
                preco = float(self.preco_var.get())
                custo = float(self.custo_var.get())
                conversao = float(self.conversao_var.get()) / 100
                limite = self.limite_var.get()
                
                self.atualizar_status(f"Processando {tipo}...")
                self.log_resultado(f"\n🔍 ANÁLISE: {tipo.upper()}")
                self.log_resultado("=" * 50)
                
                df_lazy = pl.scan_parquet(self.arquivo_path)
                
                if limite != 'TODOS':
                    n_limit = int(limite)
                    self.log_resultado(f"📊 Carregando {n_limit:,} registros...")
                    df = df_lazy.head(n_limit).collect()
                else:
                    self.log_resultado("📊 Carregando TODOS (pode demorar muito)...")
                    df = df_lazy.collect()
                
                self.log_resultado(f"✅ {len(df):,} registros carregados")
                
                # Análises
                if tipo == 'ranking':
                    self.analise_ranking(df)
                elif tipo == 'simulacao':
                    self.analise_simulacao(df, preco, custo, conversao)
                elif tipo == 'tribunais':
                    self.analise_tribunais(df)
                elif tipo == 'completo':
                    self.analise_completa(df, preco, custo, conversao)
                
                self.log_resultado("\n✅ ANÁLISE CONCLUÍDA!")
                
            except Exception as e:
                self.log_resultado(f"\n❌ ERRO: {str(e)}")
                messagebox.showerror("Erro", f"Erro: {str(e)}")
            
            finally:
                self.processando = False
                self.atualizar_status("Pronto")
        
        thread = threading.Thread(target=processar)
        thread.daemon = True
        thread.start()
    
    def analise_ranking(self, df):
        self.log_resultado("\n🏆 TOP 20 EMPRESAS:")
        
        coluna_empresa = None
        for col in ['NOME', 'EMPRESA', 'ÓRGÃO', 'ORGAO']:
            if col in df.columns:
                coluna_empresa = col
                break
        
        if not coluna_empresa:
            self.log_resultado("❌ Coluna empresa não encontrada")
            return
        
        empresas = (
            df.group_by(coluna_empresa)
            .agg([pl.col('NOVOS').sum().alias('total_novos')])
            .sort('total_novos', descending=True)
            .head(20)
        )
        
        for i, row in enumerate(empresas.iter_rows()):
            empresa, novos = row
            self.log_resultado(f"{i+1:2d}. {empresa[:40]:40} | {novos:8,}")
    
    def analise_simulacao(self, df, preco, custo, conversao):
        self.log_resultado(f"\n💰 SIMULAÇÃO (R$ {preco:.0f}/proc, {conversao*100:.1f}% conversão):")
        
        coluna_empresa = None
        for col in ['NOME', 'EMPRESA', 'ÓRGÃO', 'ORGAO']:
            if col in df.columns:
                coluna_empresa = col
                break
        
        if not coluna_empresa:
            return
        
        empresas = (
            df.group_by(coluna_empresa)
            .agg([pl.col('NOVOS').sum().alias('total_novos')])
            .sort('total_novos', descending=True)
            .head(10)
        )
        
        self.log_resultado(f"{'EMPRESA':<35} | {'PROCESSOS':<10} | {'RECEITA/MÊS':<12}")
        self.log_resultado("-" * 65)
        
        for row in empresas.iter_rows():
            empresa, processos = row
            clientes = int(processos * conversao)
            receita = clientes * preco * 12
            self.log_resultado(f"{empresa[:34]:<35} | {processos:<10,} | R$ {receita:<10,.0f}")
    
    def analise_tribunais(self, df):
        self.log_resultado(f"\n⚖️ PROCESSOS POR TRIBUNAL:")
        
        if 'TRIBUNAL' not in df.columns:
            self.log_resultado("❌ Coluna TRIBUNAL não encontrada")
            return
        
        tribunais = (
            df.group_by('TRIBUNAL')
            .agg([pl.col('NOVOS').sum().alias('total_novos')])
            .sort('total_novos', descending=True)
        )
        
        total = tribunais.select(pl.col('total_novos').sum()).item()
        
        for row in tribunais.head(10).iter_rows():
            tribunal, novos = row
            pct = (novos/total)*100
            self.log_resultado(f"{tribunal:<25} | {novos:>8,} ({pct:>5.1f}%)")
    
    def analise_completa(self, df, preco, custo, conversao):
        self.log_resultado(f"\n📋 RELATÓRIO EXECUTIVO:")
        
        total_registros = len(df)
        total_processos = df.select(pl.col('NOVOS').sum()).item()
        
        self.log_resultado(f"📊 Registros: {total_registros:,}")
        self.log_resultado(f"⚖️ Processos: {total_processos:,}")
        self.log_resultado(f"💰 Receita potencial: R$ {total_processos * preco:,.0f}")
        self.log_resultado(f"👥 Clientes potenciais: {int(total_processos * conversao):,}")
        
        self.analise_ranking(df)
        self.analise_simulacao(df, preco, custo, conversao)
        self.analise_tribunais(df)
    
    def executar(self):
        if not instalar_dependencias():
            messagebox.showerror("Erro", "Não foi possível instalar dependências")
            return
        
        self.root.mainloop()

if __name__ == "__main__":
    app = SimuladorGUI()
    app.executar() 
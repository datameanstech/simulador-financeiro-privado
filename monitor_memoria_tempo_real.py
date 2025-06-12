#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import psutil
import time
import json
from datetime import datetime
import threading
import sys
from pathlib import Path
import requests
import matplotlib.pyplot as plt
from collections import deque
import warnings
warnings.filterwarnings('ignore')

class MonitorMemoriaTempoReal:
    """Monitor de memória em tempo real para o Simulador Financeiro"""
    
    def __init__(self, pid=None, url_app="http://127.0.0.1:5000"):
        self.pid = pid
        self.url_app = url_app
        self.processo = None
        self.dados_memoria = deque(maxlen=300)  # Últimos 5 minutos (1 amostra/seg)
        self.dados_cpu = deque(maxlen=300)
        self.timestamps = deque(maxlen=300)
        self.monitorando = False
        self.alertas = []
        
        # Limites de alerta
        self.limite_memoria_mb = 1024  # 1GB
        self.limite_cpu_percent = 80
        
    def encontrar_processo_flask(self):
        """Encontra o processo do Flask automaticamente"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline']:
                    cmdline = ' '.join(proc.info['cmdline'])
                    if 'app.py' in cmdline or 'flask' in cmdline.lower():
                        print(f"🔍 Processo Flask encontrado: PID {proc.info['pid']}")
                        return proc.info['pid']
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        print("⚠️ Processo Flask não encontrado automaticamente")
        return None
    
    def inicializar_monitoramento(self):
        """Inicializa o monitoramento do processo"""
        if not self.pid:
            self.pid = self.encontrar_processo_flask()
        
        if not self.pid:
            print("❌ Não foi possível encontrar o processo para monitorar")
            return False
        
        try:
            self.processo = psutil.Process(self.pid)
            print(f"✅ Monitoramento iniciado para PID: {self.pid}")
            print(f"📱 Processo: {self.processo.name()}")
            return True
        except psutil.NoSuchProcess:
            print(f"❌ Processo {self.pid} não encontrado")
            return False
    
    def coletar_metricas(self):
        """Coleta métricas do processo"""
        try:
            # Memória
            memoria_info = self.processo.memory_info()
            memoria_mb = memoria_info.rss / (1024 * 1024)  # MB
            
            # CPU
            cpu_percent = self.processo.cpu_percent()
            
            # Timestamp
            timestamp = datetime.now()
            
            # Armazenar dados
            self.dados_memoria.append(memoria_mb)
            self.dados_cpu.append(cpu_percent)
            self.timestamps.append(timestamp)
            
            # Verificar alertas
            self._verificar_alertas(memoria_mb, cpu_percent)
            
            return {
                'timestamp': timestamp,
                'memoria_mb': memoria_mb,
                'cpu_percent': cpu_percent,
                'threads': self.processo.num_threads(),
                'conexoes': len(self.processo.connections()),
                'arquivos_abertos': len(self.processo.open_files())
            }
            
        except psutil.NoSuchProcess:
            print("❌ Processo não existe mais")
            self.monitorando = False
            return None
        except Exception as e:
            print(f"⚠️ Erro ao coletar métricas: {e}")
            return None
    
    def _verificar_alertas(self, memoria_mb, cpu_percent):
        """Verifica se há alertas a serem disparados"""
        agora = datetime.now()
        
        # Alerta de memória
        if memoria_mb > self.limite_memoria_mb:
            alerta = {
                'tipo': 'MEMORIA_ALTA',
                'timestamp': agora,
                'valor': memoria_mb,
                'limite': self.limite_memoria_mb,
                'mensagem': f"🚨 Uso de memória alto: {memoria_mb:.1f} MB (limite: {self.limite_memoria_mb} MB)"
            }
            self.alertas.append(alerta)
            print(alerta['mensagem'])
        
        # Alerta de CPU
        if cpu_percent > self.limite_cpu_percent:
            alerta = {
                'tipo': 'CPU_ALTA',
                'timestamp': agora,
                'valor': cpu_percent,
                'limite': self.limite_cpu_percent,
                'mensagem': f"🚨 Uso de CPU alto: {cpu_percent:.1f}% (limite: {self.limite_cpu_percent}%)"
            }
            self.alertas.append(alerta)
            print(alerta['mensagem'])
        
        # Alerta de crescimento rápido de memória
        if len(self.dados_memoria) >= 30:  # 30 segundos de dados
            memoria_inicial = self.dados_memoria[-30]
            crescimento = memoria_mb - memoria_inicial
            if crescimento > 100:  # Crescimento de 100MB em 30 segundos
                alerta = {
                    'tipo': 'CRESCIMENTO_RAPIDO',
                    'timestamp': agora,
                    'crescimento': crescimento,
                    'mensagem': f"⚠️ Crescimento rápido de memória: +{crescimento:.1f} MB em 30s"
                }
                self.alertas.append(alerta)
                print(alerta['mensagem'])
    
    def testar_endpoints(self):
        """Testa principais endpoints da aplicação"""
        endpoints = [
            '/api/filtros',
            '/api/cnaes/todos',
            '/api/ranking'
        ]
        
        resultados = {}
        
        for endpoint in endpoints:
            try:
                url = f"{self.url_app}{endpoint}"
                inicio = time.time()
                response = requests.get(url, timeout=10)
                fim = time.time()
                
                resultados[endpoint] = {
                    'status': response.status_code,
                    'tempo_resposta': fim - inicio,
                    'tamanho_mb': len(response.content) / (1024 * 1024)
                }
                
                if response.status_code != 200:
                    print(f"⚠️ Endpoint {endpoint}: Status {response.status_code}")
                
            except Exception as e:
                resultados[endpoint] = {
                    'erro': str(e)
                }
                print(f"❌ Erro ao testar {endpoint}: {e}")
        
        return resultados
    
    def gerar_grafico_tempo_real(self):
        """Gera gráfico atualizado em tempo real"""
        if len(self.dados_memoria) < 2:
            return
        
        try:
            plt.style.use('dark_background')
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
            
            # Converter timestamps para segundos relativos
            tempo_relativo = range(len(self.dados_memoria))
            
            # Gráfico de memória
            ax1.clear()
            ax1.plot(tempo_relativo, list(self.dados_memoria), color='#00ff41', linewidth=2)
            ax1.fill_between(tempo_relativo, list(self.dados_memoria), alpha=0.3, color='#00ff41')
            ax1.set_title('📈 Uso de Memória (Tempo Real)', fontsize=14, color='white')
            ax1.set_ylabel('Memória (MB)', color='white')
            ax1.grid(True, alpha=0.3)
            
            # Linha de limite
            ax1.axhline(y=self.limite_memoria_mb, color='red', linestyle='--', alpha=0.7, label=f'Limite: {self.limite_memoria_mb} MB')
            ax1.legend()
            
            # Gráfico de CPU
            ax2.clear()
            ax2.plot(tempo_relativo, list(self.dados_cpu), color='orange', linewidth=2)
            ax2.fill_between(tempo_relativo, list(self.dados_cpu), alpha=0.3, color='orange')
            ax2.set_title('📈 Uso de CPU (Tempo Real)', fontsize=14, color='white')
            ax2.set_ylabel('CPU (%)', color='white')
            ax2.set_xlabel('Tempo (segundos atrás)', color='white')
            ax2.grid(True, alpha=0.3)
            
            # Linha de limite
            ax2.axhline(y=self.limite_cpu_percent, color='red', linestyle='--', alpha=0.7, label=f'Limite: {self.limite_cpu_percent}%')
            ax2.legend()
            
            plt.tight_layout()
            plt.pause(0.1)  # Pausa para atualizar
            
        except Exception as e:
            print(f"⚠️ Erro ao gerar gráfico: {e}")
    
    def salvar_log(self, metricas):
        """Salva log das métricas"""
        log_file = f"monitor_memoria_{datetime.now().strftime('%Y%m%d')}.jsonl"
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                log_entry = {
                    'timestamp': metricas['timestamp'].isoformat(),
                    'memoria_mb': metricas['memoria_mb'],
                    'cpu_percent': metricas['cpu_percent'],
                    'threads': metricas['threads'],
                    'conexoes': metricas['conexoes'],
                    'arquivos_abertos': metricas['arquivos_abertos']
                }
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            print(f"⚠️ Erro ao salvar log: {e}")
    
    def executar_teste_stress(self):
        """Executa teste de stress nos endpoints"""
        print("\n🔥 INICIANDO TESTE DE STRESS")
        print("-" * 30)
        
        # Endpoints para testar
        endpoints_stress = [
            '/api/filtros',
            '/api/cnaes/todos',
            '/api/ranking'
        ]
        
        for endpoint in endpoints_stress:
            print(f"🔄 Testando {endpoint}...")
            
            # Fazer 10 requisições rápidas
            tempos = []
            for i in range(10):
                try:
                    inicio = time.time()
                    response = requests.get(f"{self.url_app}{endpoint}", timeout=5)
                    fim = time.time()
                    tempos.append(fim - inicio)
                    
                    if response.status_code != 200:
                        print(f"  ❌ Falha na requisição {i+1}: {response.status_code}")
                    
                    time.sleep(0.1)  # Pequena pausa
                    
                except Exception as e:
                    print(f"  ❌ Erro na requisição {i+1}: {e}")
            
            if tempos:
                print(f"  ⏱️ Tempo médio: {sum(tempos)/len(tempos):.3f}s")
                print(f"  📊 Min/Max: {min(tempos):.3f}s / {max(tempos):.3f}s")
    
    def monitorar(self, duracao_segundos=300, com_graficos=True, teste_stress=False):
        """Inicia o monitoramento"""
        if not self.inicializar_monitoramento():
            return False
        
        self.monitorando = True
        
        print(f"📊 Monitoramento iniciado por {duracao_segundos} segundos")
        print("📋 Pressione Ctrl+C para parar antecipadamente")
        
        if com_graficos:
            plt.ion()  # Modo interativo
            plt.show()
        
        inicio = time.time()
        
        try:
            while self.monitorando and (time.time() - inicio) < duracao_segundos:
                # Coletar métricas
                metricas = self.coletar_metricas()
                
                if metricas:
                    # Salvar log
                    self.salvar_log(metricas)
                    
                    # Imprimir status
                    if int(time.time() - inicio) % 10 == 0:  # A cada 10 segundos
                        print(f"📊 {metricas['timestamp'].strftime('%H:%M:%S')} | "
                              f"Mem: {metricas['memoria_mb']:.1f}MB | "
                              f"CPU: {metricas['cpu_percent']:.1f}% | "
                              f"Threads: {metricas['threads']}")
                    
                    # Atualizar gráfico
                    if com_graficos and int(time.time() - inicio) % 2 == 0:  # A cada 2 segundos
                        self.gerar_grafico_tempo_real()
                
                time.sleep(1)  # Coleta a cada segundo
                
        except KeyboardInterrupt:
            print("\n⏹️ Monitoramento interrompido pelo usuário")
        
        finally:
            self.monitorando = False
            if com_graficos:
                plt.ioff()
            
            # Teste de stress no final se solicitado
            if teste_stress:
                self.executar_teste_stress()
            
            self._gerar_relatorio_final()
        
        return True
    
    def _gerar_relatorio_final(self):
        """Gera relatório final do monitoramento"""
        print("\n" + "="*50)
        print("📋 RELATÓRIO FINAL DE MONITORAMENTO")
        print("="*50)
        
        if self.dados_memoria:
            memoria_max = max(self.dados_memoria)
            memoria_min = min(self.dados_memoria)
            memoria_media = sum(self.dados_memoria) / len(self.dados_memoria)
            
            print(f"📊 MEMÓRIA:")
            print(f"   • Máxima:    {memoria_max:.1f} MB")
            print(f"   • Mínima:    {memoria_min:.1f} MB")
            print(f"   • Média:     {memoria_media:.1f} MB")
            print(f"   • Variação:  {memoria_max - memoria_min:.1f} MB")
        
        if self.dados_cpu:
            cpu_max = max(self.dados_cpu)
            cpu_media = sum(self.dados_cpu) / len(self.dados_cpu)
            
            print(f"\n📊 CPU:")
            print(f"   • Máximo:    {cpu_max:.1f}%")
            print(f"   • Médio:     {cpu_media:.1f}%")
        
        if self.alertas:
            print(f"\n🚨 ALERTAS DISPARADOS: {len(self.alertas)}")
            tipos_alertas = {}
            for alerta in self.alertas:
                tipo = alerta['tipo']
                tipos_alertas[tipo] = tipos_alertas.get(tipo, 0) + 1
            
            for tipo, count in tipos_alertas.items():
                print(f"   • {tipo}: {count} vezes")
        
        print(f"\n✅ Relatório salvo em: monitor_memoria_{datetime.now().strftime('%Y%m%d')}.jsonl")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor de memória em tempo real para Simulador Financeiro')
    parser.add_argument('--pid', type=int, help='PID do processo Flask')
    parser.add_argument('--duracao', type=int, default=300, help='Duração em segundos (padrão: 300)')
    parser.add_argument('--sem-graficos', action='store_true', help='Executar sem gráficos')
    parser.add_argument('--teste-stress', action='store_true', help='Executar teste de stress no final')
    parser.add_argument('--url', default='http://127.0.0.1:5000', help='URL da aplicação')
    
    args = parser.parse_args()
    
    print("📊 MONITOR DE MEMÓRIA - SIMULADOR FINANCEIRO")
    print("=" * 50)
    
    monitor = MonitorMemoriaTempoReal(
        pid=args.pid,
        url_app=args.url
    )
    
    sucesso = monitor.monitorar(
        duracao_segundos=args.duracao,
        com_graficos=not args.sem_graficos,
        teste_stress=args.teste_stress
    )
    
    if sucesso:
        print("\n🎉 Monitoramento concluído com sucesso!")
    else:
        print("\n❌ Erro durante o monitoramento")
        sys.exit(1)

if __name__ == "__main__":
    main() 
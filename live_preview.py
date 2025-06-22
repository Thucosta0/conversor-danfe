"""
⚕️ Live Preview System - Hospital Albert Einstein
Sistema de monitoramento em tempo real para arquivos XML
ATIVO APENAS DURANTE DESENVOLVIMENTO (não funciona no .exe)
Autor: renamerPRO© System
"""

import os
import sys
import time
import threading

# Detectar se está em modo desenvolvimento
MODO_DESENVOLVIMENTO = not getattr(sys, 'frozen', False)

# Importar watchdog apenas se estiver em desenvolvimento
if MODO_DESENVOLVIMENTO:
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        WATCHDOG_DISPONIVEL = True
    except ImportError:
        print("⚠️ Watchdog não instalado - Live Preview desabilitado")
        WATCHDOG_DISPONIVEL = False
else:
    # Em modo executável, não importar watchdog
    WATCHDOG_DISPONIVEL = False
    Observer = None
    FileSystemEventHandler = None


class LivePreviewHandler(FileSystemEventHandler if WATCHDOG_DISPONIVEL else object):
    """Handler profissional para monitoramento de arquivos em tempo real"""
    
    def __init__(self, app_instance):
        super().__init__()
        self.app = app_instance
        self.debounce_timer = None
        self.debounce_delay = 1.0  # 1 segundo de delay para evitar múltiplas atualizações
        self.eventos_processados = 0
        
    def on_any_event(self, event):
        """Callback para qualquer evento no sistema de arquivos"""
        if event.is_directory:
            return
            
        # Filtrar apenas arquivos XML e PDF
        extensoes_validas = ['.xml', '.pdf']
        if not any(event.src_path.lower().endswith(ext) for ext in extensoes_validas):
            return
            
        # Implementar debounce para evitar múltiplas atualizações rápidas
        if self.debounce_timer:
            self.debounce_timer.cancel()
            
        self.debounce_timer = threading.Timer(
            self.debounce_delay, 
            self._processar_evento, 
            [event]
        )
        self.debounce_timer.start()
        
    def _processar_evento(self, event):
        """Processa o evento após o debounce"""
        try:
            self.eventos_processados += 1
            
            event_type = self._traduzir_evento(event.event_type)
            arquivo = os.path.basename(event.src_path)
            
            # Atualizar interface de forma thread-safe
            self.app.root.after(0, lambda: self._atualizar_interface(event, arquivo, event_type))
            
        except Exception as e:
            print(f"❌ Erro ao processar evento watchdog: {e}")
    
    def _traduzir_evento(self, event_type):
        """Traduz o tipo de evento para português"""
        traducoes = {
            'modified': 'modificado',
            'created': 'criado',
            'deleted': 'excluído',
            'moved': 'movido'
        }
        return traducoes.get(event_type, event_type)
    
    def _atualizar_interface(self, event, arquivo, event_type):
        """Atualiza a interface com as mudanças detectadas"""
        try:
            timestamp = time.strftime("%H:%M:%S")
            icone = self._obter_icone_evento(event.event_type)
            
            # Log do evento com formatação profissional
            log_msg = f"{icone} [{timestamp}] LIVE: {arquivo} - {event_type.upper()}"
            
            # Adicionar ao log principal se disponível
            if hasattr(self.app, 'adicionar_log'):
                self.app.adicionar_log(log_msg)
            
            # Re-escanear automaticamente na aba principal
            if self._deve_atualizar_aba_principal(event):
                self.app._atualizar_contagem_arquivos()
                
                # Auto-processar se configurado
                if (hasattr(self.app, 'auto_processar') and 
                    self.app.auto_processar.get() and 
                    event.event_type == 'created' and 
                    event.src_path.lower().endswith('.xml')):
                    
                    self.app._processar_arquivo_automatico(event.src_path)
            
            # Atualizar aba de renomeação se necessário
            if self._deve_atualizar_aba_renomear(event):
                self.app._atualizar_chaves_automatico()
                
                # Auto-renomear se configurado
                if (hasattr(self.app, 'auto_renomear') and 
                    self.app.auto_renomear.get() and 
                    event.event_type == 'created'):
                    
                    self.app._renomear_arquivo_automatico(event.src_path)
                    
        except Exception as e:
            print(f"❌ Erro ao atualizar interface: {e}")
    
    def _obter_icone_evento(self, event_type):
        """Retorna ícone baseado no tipo de evento"""
        icones = {
            'created': '🟢',
            'modified': '🟡',
            'deleted': '🔴',
            'moved': '🔵'
        }
        return icones.get(event_type, '⚪')
    
    def _deve_atualizar_aba_principal(self, event):
        """Verifica se deve atualizar a aba principal"""
        if not (hasattr(self.app, 'pasta_xml') and self.app.pasta_xml.get()):
            return False
        
        return event.src_path.startswith(self.app.pasta_xml.get())
    
    def _deve_atualizar_aba_renomear(self, event):
        """Verifica se deve atualizar a aba de renomeação"""
        if not (hasattr(self.app, 'entrada_pasta_renomear') and 
                self.app.entrada_pasta_renomear.get()):
            return False
        
        pasta_renomear = self.app.entrada_pasta_renomear.get()
        return event.src_path.startswith(pasta_renomear)


class LivePreviewManager:
    """Gerenciador principal do sistema de Live Preview"""
    
    def __init__(self, app_instance):
        self.app = app_instance
        self.observer = None
        self.handler = None
        self.pastas_monitoradas = set()
        self.ativo = False
        
    def iniciar_monitoramento(self, pasta):
        """Inicia o monitoramento de uma pasta"""
        if not WATCHDOG_DISPONIVEL:
            if hasattr(self.app, 'adicionar_log'):
                self.app.adicionar_log("⚠️ Live Preview disponível apenas em modo desenvolvimento")
            return False
            
        try:
            if not os.path.exists(pasta):
                raise FileNotFoundError(f"Pasta não existe: {pasta}")
            
            # Parar monitoramento anterior se existir
            self.parar_monitoramento()
            
            # Criar novo observer
            self.observer = Observer()
            self.handler = LivePreviewHandler(self.app)
            
            # Adicionar monitoramento recursivo
            self.observer.schedule(self.handler, pasta, recursive=True)
            
            # Iniciar observer
            self.observer.start()
            self.pastas_monitoradas.add(pasta)
            self.ativo = True
            
            # Log de início
            if hasattr(self.app, 'adicionar_log'):
                self.app.adicionar_log(f"🟢 LIVE PREVIEW ativado para: {os.path.basename(pasta)}")
            
            return True
            
        except Exception as e:
            if hasattr(self.app, 'adicionar_log'):
                self.app.adicionar_log(f"❌ Erro ao iniciar Live Preview: {str(e)}")
            return False
    
    def parar_monitoramento(self):
        """Para o monitoramento de arquivos"""
        try:
            if self.observer and self.observer.is_alive():
                self.observer.stop()
                self.observer.join()
                
            self.observer = None
            self.handler = None
            self.pastas_monitoradas.clear()
            self.ativo = False
            
            # Log de parada
            if hasattr(self.app, 'adicionar_log'):
                self.app.adicionar_log("🔴 LIVE PREVIEW desativado")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao parar Live Preview: {e}")
            return False
    
    def adicionar_pasta(self, pasta):
        """Adiciona uma nova pasta ao monitoramento"""
        if not self.observer:
            return self.iniciar_monitoramento(pasta)
        
        try:
            if pasta not in self.pastas_monitoradas:
                self.observer.schedule(self.handler, pasta, recursive=True)
                self.pastas_monitoradas.add(pasta)
                
                if hasattr(self.app, 'adicionar_log'):
                    self.app.adicionar_log(f"➕ Pasta adicionada ao Live Preview: {os.path.basename(pasta)}")
            
            return True
            
        except Exception as e:
            if hasattr(self.app, 'adicionar_log'):
                self.app.adicionar_log(f"❌ Erro ao adicionar pasta: {str(e)}")
            return False
    
    def obter_status(self):
        """Retorna o status atual do Live Preview"""
        if not WATCHDOG_DISPONIVEL:
            return "🔴 Disponível apenas em desenvolvimento"
            
        if not self.ativo:
            return "🔴 Inativo"
        
        total_pastas = len(self.pastas_monitoradas)
        total_eventos = self.handler.eventos_processados if self.handler else 0
        
        return f"🟢 Ativo - {total_pastas} pasta(s) - {total_eventos} eventos"
    
    def reiniciar(self):
        """Reinicia o sistema de monitoramento"""
        pastas_temp = list(self.pastas_monitoradas)
        self.parar_monitoramento()
        
        # Aguardar um momento
        time.sleep(0.5)
        
        # Reiniciar com as pastas anteriores
        if pastas_temp:
            self.iniciar_monitoramento(pastas_temp[0])
            for pasta in pastas_temp[1:]:
                self.adicionar_pasta(pasta)
    
    def __del__(self):
        """Destrutor para garantir limpeza"""
        self.parar_monitoramento()


def criar_live_preview(app_instance):
    """Factory function para criar instância do Live Preview"""
    if MODO_DESENVOLVIMENTO:
        return LivePreviewManager(app_instance)
    else:
        # Retornar versão "dummy" para modo executável
        return LivePreviewDummy(app_instance)


class LivePreviewDummy:
    """Versão dummy do Live Preview para modo executável"""
    
    def __init__(self, app_instance):
        self.app = app_instance
        self.ativo = False
    
    def iniciar_monitoramento(self, pasta):
        return False
    
    def parar_monitoramento(self):
        return True
    
    def adicionar_pasta(self, pasta):
        return False
    
    def obter_status(self):
        return "🔴 Disponível apenas durante desenvolvimento"
    
    def reiniciar(self):
        pass 
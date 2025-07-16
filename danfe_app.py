import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import threading
import webbrowser
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
from datetime import datetime


class DanfeAppMassa:
    def __init__(self):
        # Configuração de tema e cores Einstein
        ctk.set_appearance_mode("light")  # Tema claro para ambiente hospitalar
        ctk.set_default_color_theme("blue")
        
        # Paleta de cores Hospital Albert Einstein (suavizada)
        self.cores = {
            'azul_primary': '#003D7A',      # Azul Einstein principal
            'azul_secondary': '#0056B3',    # Azul secundário
            'azul_light': '#E3F2FD',       # Azul claro suavizado
            'azul_accent': '#1976D2',       # Azul accent mais suave
            'cinza_text': '#37474F',       # Cinza textos mais suave
            'cinza_light': '#F5F7FA',      # Cinza claro suavizado
            'cinza_medium': '#ECEFF1',     # Cinza médio para cards
            'verde_success': '#2E7D32',     # Verde mais suave
            'laranja_warning': '#F57C00',   # Laranja mais suave
            'vermelho_error': '#C62828',    # Vermelho mais discreto
            'branco_suave': '#FAFBFC'      # Branco suavizado
        }
        
        self.root = ctk.CTk()
        self.root.title("⚕️ renamerPRO©")
        self.root.geometry("1000x650")
        self.root.minsize(800, 600)
        self.root.resizable(True, True)
        self.root.configure(fg_color=self.cores['cinza_medium'])
        
        # Configurar ícone e título profissional
        try:
            self.root.iconbitmap(default="einstein_icon.ico")  # Caso tenha ícone
        except:
            pass
        
        # Configurar grid responsivo
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        self.pasta_xml = tk.StringVar()
        self.pasta_saida = tk.StringVar()
        self.status_texto = tk.StringVar(value="Sistema pronto para processamento")
        self.arquivos_xml = []
        self.processando = False
        self.chaves_xml = {}
        self.linhas_renomeacao = []
        self.vcredist_tentado = False
        
        self.criar_interface()

    def criar_botao_profissional(self, parent, text, command, width=200, height=45, 
                                cor_principal=None, cor_hover=None, icone=""):
        """Cria botões com design profissional Einstein"""
        if cor_principal is None:
            cor_principal = self.cores['azul_primary']
        if cor_hover is None:
            cor_hover = self.cores['azul_secondary']
            
        botao = ctk.CTkButton(
            parent,
            text=f"{icone} {text}",
            command=command,
            width=width,
            height=height,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=cor_principal,
            hover_color=cor_hover,
            corner_radius=8,
            border_width=2,
            border_color=cor_principal,
            text_color=self.cores['branco_suave']
        )
        return botao

    def criar_card_profissional(self, parent, titulo, subtitle=""):
        """Cria cards profissionais com header Einstein"""
        card = ctk.CTkFrame(
            parent,
            fg_color=self.cores['branco_suave'],
            corner_radius=12,
            border_width=1,
            border_color=self.cores['azul_light']
        )
        
        # Header do card
        header = ctk.CTkFrame(
            card,
            fg_color=self.cores['azul_primary'],
            corner_radius=10,
            height=35
        )
        header.pack(fill="x", padx=5, pady=(2, 0))
        header.pack_propagate(False)
        
        # Título
        titulo_label = ctk.CTkLabel(
            header,
            text=titulo,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.cores['branco_suave']
        )
        titulo_label.pack(pady=8)
        
        if subtitle:
            subtitle_label = ctk.CTkLabel(
                card,
                text=subtitle,
                font=ctk.CTkFont(size=12),
                text_color=self.cores['cinza_text']
            )
            subtitle_label.pack(pady=(8, 0))
        
        return card
        
    def criar_interface(self):
        # Frame principal responsivo
        main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=0, pady=0)
        main_container.grid_columnconfigure(0, weight=1)
        
        # Header compacto Einstein
        header_frame = ctk.CTkFrame(
            main_container,
            fg_color=self.cores['azul_primary'],
            corner_radius=12,
            height=30
        )
        header_frame.pack(fill="x", pady=0)
        header_frame.pack_propagate(False)
        
        # Título compacto
        titulo_principal = ctk.CTkLabel(
            header_frame,
            text="⚕️ renamerPRO©",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.cores['branco_suave']
        )
        titulo_principal.pack(pady=4)
        
        # TabView responsivo
        self.tabview = ctk.CTkTabview(
            main_container,
            corner_radius=12,
            fg_color=self.cores['branco_suave'],
            segmented_button_fg_color=self.cores['azul_light'],
            segmented_button_selected_color=self.cores['azul_primary'],
            segmented_button_selected_hover_color=self.cores['azul_secondary']
        )
        self.tabview.place(x=0, y=30, relwidth=1.0, relheight=0.96)
        

        
        # Abas
        self.tab_principal = self.tabview.add("🏥 Processamento em Massa")
        self.tab_renomear = self.tabview.add("📋 Renomeação Inteligente")
        
        self.criar_aba_principal()
        self.criar_aba_renomeacao()

    def criar_aba_principal(self):
        # Container principal scrollável
        container = ctk.CTkScrollableFrame(self.tab_principal, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=0, pady=0)
        container.grid_columnconfigure(0, weight=1)
        
        # Card de Configuração
        config_card = self.criar_card_profissional(
            container, 
            "⚙️ Configuração de Processamento",
            "Configure as pastas de origem e destino dos documentos"
        )
        config_card.pack(fill="x", pady=0, padx=0)
        
        # Grid responsivo para inputs
        input_frame = ctk.CTkFrame(config_card, fg_color="transparent")
        input_frame.pack(fill="x", padx=8, pady=3)
        input_frame.grid_columnconfigure(0, weight=1)
        
        # Pasta XML
        xml_label = ctk.CTkLabel(
            input_frame,
            text="📁 Pasta com Arquivos XML:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.cores['cinza_text'],
            anchor="w"
        )
        xml_label.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        xml_container = ctk.CTkFrame(input_frame, fg_color="transparent")
        xml_container.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        xml_container.grid_columnconfigure(0, weight=1)
        
        self.entrada_pasta_xml = ctk.CTkEntry(
            xml_container,
            textvariable=self.pasta_xml,
            placeholder_text="Selecione a pasta contendo os arquivos XML...",
            font=ctk.CTkFont(size=12),
            height=40,
            corner_radius=8,
            border_color=self.cores['azul_light']
        )
        self.entrada_pasta_xml.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        btn_xml = self.criar_botao_profissional(
            xml_container,
            "Selecionar",
            self.selecionar_pasta_xml,
            width=120,
            icone="📁"
        )
        btn_xml.grid(row=0, column=1)
        
        # Pasta Saída
        saida_label = ctk.CTkLabel(
            input_frame,
            text="💾 Pasta de Destino (Opcional):",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.cores['cinza_text'],
            anchor="w"
        )
        saida_label.grid(row=2, column=0, sticky="ew", pady=(0, 5))
        
        saida_container = ctk.CTkFrame(input_frame, fg_color="transparent")
        saida_container.grid(row=3, column=0, sticky="ew", pady=(0, 15))
        saida_container.grid_columnconfigure(0, weight=1)
        
        self.entrada_pasta_saida = ctk.CTkEntry(
            saida_container,
            textvariable=self.pasta_saida,
            placeholder_text="Deixe vazio para usar a mesma pasta dos XMLs...",
            font=ctk.CTkFont(size=12),
            height=40,
            corner_radius=8,
            border_color=self.cores['azul_light']
        )
        self.entrada_pasta_saida.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        btn_saida = self.criar_botao_profissional(
            saida_container,
            "Selecionar",
            self.selecionar_pasta_saida,
            width=120,
            icone="💾"
        )
        btn_saida.grid(row=0, column=1)
        
        # Info e Controles
        controle_card = self.criar_card_profissional(
            container,
            "📊 Controle de Processamento"
        )
        controle_card.pack(fill="x", pady=(2, 0), padx=0)
        
        # Status dos arquivos
        self.label_arquivos = ctk.CTkLabel(
            controle_card,
            text="📋 Aguardando seleção de pasta...",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.cores['cinza_text']
        )
        self.label_arquivos.pack(pady=3)
        
        # Botões de ação
        botoes_frame = ctk.CTkFrame(controle_card, fg_color="transparent")
        botoes_frame.pack(pady=(0, 3))
        
        self.btn_escanear = self.criar_botao_profissional(
            botoes_frame,
            "ESCANEAR PASTA",
            self.escanear_pasta,
            width=170,
            height=45,
            cor_principal=self.cores['laranja_warning'],
            cor_hover="#E5A500",
            icone="🔍"
        )
        self.btn_escanear.pack(side="left", padx=8)
        
        self.btn_processar = self.criar_botao_profissional(
            botoes_frame,
            "PROCESSAR DOCUMENTOS",
            self.processar_massa_thread,
            width=200,
            height=45,
            cor_principal=self.cores['verde_success'],
            cor_hover="#218838",
            icone="⚡"
        )
        self.btn_processar.pack(side="left", padx=8)
        self.btn_processar.configure(state="disabled")
        
        # Progresso
        progresso_frame = ctk.CTkFrame(controle_card, fg_color="transparent")
        progresso_frame.pack(fill="x", padx=12, pady=(0, 3))
        
        prog_label = ctk.CTkLabel(
            progresso_frame,
            text="📈 Progresso do Processamento:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.cores['cinza_text'],
            anchor="w"
        )
        prog_label.pack(fill="x", pady=(0, 6))
        
        self.progresso_geral = ctk.CTkProgressBar(
            progresso_frame,
            height=18,
            corner_radius=10,
            progress_color=self.cores['azul_primary']
        )
        self.progresso_geral.pack(fill="x", pady=(0, 6))
        self.progresso_geral.set(0)
        
        self.label_progresso = ctk.CTkLabel(
            progresso_frame,
            text="0 / 0 documentos processados",
            font=ctk.CTkFont(size=12),
            text_color=self.cores['cinza_text']
        )
        self.label_progresso.pack()
        
        # Log profissional
        log_card = self.criar_card_profissional(
            container,
            "📋 Log de Processamento",
            "Acompanhe em tempo real o processamento dos documentos"
        )
        log_card.pack(fill="both", expand=True, pady=(3, 0), padx=0)
        
        self.log_text = ctk.CTkTextbox(
            log_card,
            font=ctk.CTkFont(size=11, family="Consolas"),
            corner_radius=8,
            fg_color=self.cores['cinza_medium'],
            text_color=self.cores['cinza_text'],
            height=200
        )
        self.log_text.pack(fill="both", expand=True, padx=8, pady=8)
        
        # Status bar profissional
        status_frame = ctk.CTkFrame(
            container,
            fg_color=self.cores['azul_primary'],
            corner_radius=10,
            height=40
        )
        status_frame.pack(fill="x", pady=(2, 0))
        status_frame.pack_propagate(False)
        
        status_container = ctk.CTkFrame(status_frame, fg_color="transparent")
        status_container.pack(expand=True, fill="both")
        
        status_label = ctk.CTkLabel(
            status_container,
            text="💼 Status:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.cores['branco_suave']
        )
        status_label.pack(side="left", padx=(15, 5), pady=8)
        
        self.status_label = ctk.CTkLabel(
            status_container,
            textvariable=self.status_texto,
            font=ctk.CTkFont(size=12),
            text_color=self.cores['azul_light']
        )
        self.status_label.pack(side="left", padx=5, pady=8)
        
        self.carregar_log_inicial()

    def criar_aba_renomeacao(self):
        # Container principal scrollável
        container = ctk.CTkScrollableFrame(self.tab_renomear, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=0, pady=0)
        container.grid_columnconfigure(0, weight=1)
        
        # Header da aba
        header_card = self.criar_card_profissional(
            container,
            "📋 Renomeação Inteligente de XMLs e PDFs",
            "Sistema avançado para renomeação simultânea de XMLs e PDFs por chave de acesso"
        )
        header_card.pack(fill="x", pady=0, padx=5)
        
        # Configuração
        config_frame = ctk.CTkFrame(header_card, fg_color="transparent")
        config_frame.pack(fill="x", padx=12, pady=12)
        config_frame.grid_columnconfigure(0, weight=1)
        
        pasta_label = ctk.CTkLabel(
            config_frame,
            text="📁 Diretório de Documentos XML e PDF:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.cores['cinza_text'],
            anchor="w"
        )
        pasta_label.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        pasta_container = ctk.CTkFrame(config_frame, fg_color="transparent")
        pasta_container.grid(row=1, column=0, sticky="ew")
        pasta_container.grid_columnconfigure(0, weight=1)
        
        self.entrada_pasta_renomear = ctk.CTkEntry(
            pasta_container,
            placeholder_text="Selecione o diretório contendo os arquivos XML e PDF...",
            font=ctk.CTkFont(size=12),
            height=40,
            corner_radius=8,
            border_color=self.cores['azul_light']
        )
        self.entrada_pasta_renomear.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        btn_pasta_renomear = self.criar_botao_profissional(
            pasta_container,
            "Localizar",
            self.selecionar_pasta_renomear,
            width=120,
            icone="🔍"
        )
        btn_pasta_renomear.grid(row=0, column=1)
        
        # Controles avançados
        controles_card = self.criar_card_profissional(
            container,
            "🛠️ Controles de Operação"
        )
        controles_card.pack(fill="x", pady=(0, 10))
        
        # Botões organizados profissionalmente
        botoes_container = ctk.CTkFrame(controles_card, fg_color="transparent")
        botoes_container.pack(fill="x", padx=12, pady=12)
        
        # Linha principal de botões - Interface Simplificada
        linha_botoes = ctk.CTkFrame(botoes_container, fg_color="transparent")
        linha_botoes.pack(fill="x", pady=10)
        
        # Botões de configuração (esquerda)
        self.btn_lote_dados = self.criar_botao_profissional(
            linha_botoes,
            "LOTE DE DADOS",
            self.abrir_janela_lote,
            width=160,
            height=45,
            cor_principal="#6C757D",
            cor_hover="#5A6268",
            icone="📋"
        )
        self.btn_lote_dados.pack(side="left", padx=(0, 10))
        
        self.btn_adicionar_linha = self.criar_botao_profissional(
            linha_botoes,
            "NOVA LINHA",
            self.adicionar_linha_renomeacao,
            width=140,
            height=45,
            cor_principal=self.cores['azul_accent'],
            cor_hover="#0066CC",
            icone="➕"
        )
        self.btn_adicionar_linha.pack(side="left", padx=(0, 10))
        
        self.btn_limpar_dados = self.criar_botao_profissional(
            linha_botoes,
            "LIMPAR",
            self.limpar_dados_massa,
            width=110,
            height=45,
            cor_principal="#DC3545",
            cor_hover="#C82333",
            icone="🧹"
        )
        self.btn_limpar_dados.pack(side="left", padx=(0, 10))
        
        # Novo botão para relatório Excel
        self.btn_relatorio_excel = self.criar_botao_profissional(
            linha_botoes,
            "RELATÓRIO EXCEL",
            self.gerar_relatorio_excel,
            width=180,
            height=45,
            cor_principal="#28A745",
            cor_hover="#218838",
            icone="📊"
        )
        self.btn_relatorio_excel.pack(side="left", padx=(0, 20))
        
        # Botão principal (direita) - Destaque especial
        self.btn_processar_completo = self.criar_botao_profissional(
            linha_botoes,
            "EXECUTAR TUDO",
            self.processar_completo_thread,
            width=220,
            height=50,
            cor_principal="#FF6B35",  # Laranja vibrante
            cor_hover="#E55A2B",
            icone="🚀"
        )
        self.btn_processar_completo.pack(side="right", padx=(10, 0))
        
        # Tabela profissional
        tabela_card = self.criar_card_profissional(
            container,
            "📊 Tabela de Mapeamento",
            "Configure a correspondência entre chaves de acesso e nomes de arquivo"
        )
        tabela_card.pack(fill="x", pady=(0, 10))
        
        # Cabeçalho da tabela
        header_tabela = ctk.CTkFrame(
            tabela_card,
            fg_color=self.cores['azul_light'],
            corner_radius=8
        )
        header_tabela.pack(fill="x", padx=12, pady=(12, 5))
        
        # Grid responsivo para cabeçalhos
        header_tabela.grid_columnconfigure(0, weight=2)  # Chave
        header_tabela.grid_columnconfigure(1, weight=2)  # Nome
        header_tabela.grid_columnconfigure(2, weight=1)  # Status
        header_tabela.grid_columnconfigure(3, weight=0)  # Ações
        
        ctk.CTkLabel(
            header_tabela,
            text="🔑 Chave de Acesso",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.cores['azul_primary']
        ).grid(row=0, column=0, padx=15, pady=12, sticky="w")
        
        ctk.CTkLabel(
            header_tabela,
            text="📄 Nome do Arquivo",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.cores['azul_primary']
        ).grid(row=0, column=1, padx=15, pady=12, sticky="w")
        
        ctk.CTkLabel(
            header_tabela,
            text="📊 Status",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.cores['azul_primary']
        ).grid(row=0, column=2, padx=15, pady=12, sticky="w")
        
        ctk.CTkLabel(
            header_tabela,
            text="🛠️ Ações",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.cores['azul_primary']
        ).grid(row=0, column=3, padx=15, pady=12, sticky="w")
        
        # Área scrollável responsiva
        self.scroll_frame = ctk.CTkScrollableFrame(
            tabela_card,
            fg_color=self.cores['cinza_medium'],
            corner_radius=8,
            height=180
        )
        self.scroll_frame.pack(fill="x", padx=12, pady=(0, 12))
        
        # Configurar responsividade do scroll
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        
        self.linhas_renomeacao = []
        
        # Log profissional da renomeação
        log_renomear_card = self.criar_card_profissional(
            container,
            "📋 Log de Renomeação",
            "Acompanhe o processo de validação e renomeação dos arquivos"
        )
        log_renomear_card.pack(fill="x", pady=(0, 10))
        
        self.log_renomeacao = ctk.CTkTextbox(
            log_renomear_card,
            font=ctk.CTkFont(size=11, family="Consolas"),
            height=150,
            corner_radius=8,
            fg_color=self.cores['cinza_medium'],
            text_color=self.cores['cinza_text']
        )
        self.log_renomeacao.pack(fill="both", expand=True, padx=12, pady=12)
        
        # Log inicial
        self.log_renomeacao.insert("0.0", """⚕️ Hospital Israelita Albert Einstein - Sistema de Renomeação
📋 Renomeação Inteligente de XMLs e PDFs
💡 Selecione o diretório e escaneie as chaves para começar.
🔗 XMLs e PDFs serão renomeados juntos automaticamente.
🆕 NOVO: Dados de rastro (lote, validade, fabricação) incluídos na DANFE!""")

    def adicionar_linha_renomeacao(self):
        # Container responsivo para linha
        linha_frame = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=self.cores['branco_suave'],
            corner_radius=8,
            border_width=1,
            border_color=self.cores['azul_light']
        )
        linha_frame.pack(fill="x", padx=5, pady=3)
        
        # Grid responsivo
        linha_frame.grid_columnconfigure(0, weight=2)  # Chave
        linha_frame.grid_columnconfigure(1, weight=2)  # Nome
        linha_frame.grid_columnconfigure(2, weight=1)  # Status
        linha_frame.grid_columnconfigure(3, weight=0)  # Botão
        
        # Entry para chave
        entry_chave = ctk.CTkEntry(
            linha_frame,
            placeholder_text="Chave de acesso (44 dígitos)...",
            font=ctk.CTkFont(size=11),
            height=35,
            corner_radius=6,
            border_color=self.cores['azul_light']
        )
        entry_chave.grid(row=0, column=0, padx=(10, 5), pady=8, sticky="ew")
        
        # Entry para nome
        entry_nome = ctk.CTkEntry(
            linha_frame,
            placeholder_text="Nome do arquivo (sem extensão)...",
            font=ctk.CTkFont(size=11),
            height=35,
            corner_radius=6,
            border_color=self.cores['azul_light']
        )
        entry_nome.grid(row=0, column=1, padx=5, pady=8, sticky="ew")
        
        # Status
        label_status = ctk.CTkLabel(
            linha_frame,
            text="⏳ Aguardando",
            font=ctk.CTkFont(size=11),
            text_color=self.cores['cinza_text']
        )
        label_status.grid(row=0, column=2, padx=5, pady=8, sticky="w")
        
        # Botão remover
        btn_remover = ctk.CTkButton(
            linha_frame,
            text="🗑️",
            command=lambda: self.remover_linha_renomeacao(linha_frame),
            width=35,
            height=35,
            font=ctk.CTkFont(size=10),
            fg_color=self.cores['vermelho_error'],
            hover_color="#C82333",
            corner_radius=6
        )
        btn_remover.grid(row=0, column=3, padx=(5, 10), pady=8)
        
        self.linhas_renomeacao.append({
            'frame': linha_frame,
            'chave': entry_chave,
            'nome': entry_nome,
            'status': label_status
        })

    def remover_linha_renomeacao(self, linha_frame):
        # Encontrar e remover a linha
        for i, linha in enumerate(self.linhas_renomeacao):
            if linha['frame'] == linha_frame:
                linha_frame.destroy()
                self.linhas_renomeacao.pop(i)
                break
                
    def selecionar_pasta_renomear(self):
        pasta = filedialog.askdirectory(title="Selecione a pasta com XMLs para renomear")
        if pasta:
            self.entrada_pasta_renomear.delete(0, 'end')
            self.entrada_pasta_renomear.insert(0, pasta)
            
    def escanear_chaves_xml(self):
        """Função de escaneamento executada em thread"""
        self.executar_thread_segura(self.escanear_chaves_xml_completo)
        
    def extrair_chave_xml(self, caminho_arquivo):
        try:
            tree = ET.parse(caminho_arquivo)
            root = tree.getroot()
            
            # Buscar chave de acesso em diferentes locais possíveis
            namespaces = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
            
            # Tentar encontrar a chave
            chave_elem = root.find('.//nfe:chNFe', namespaces)
            if chave_elem is not None:
                return chave_elem.text
                
            # Tentar sem namespace
            chave_elem = root.find('.//chNFe')
            if chave_elem is not None:
                return chave_elem.text
                
            # Buscar no atributo Id
            id_elem = root.find('.//*[@Id]')
            if id_elem is not None:
                id_value = id_elem.get('Id')
                if id_value and len(id_value) >= 44:
                    return id_value[-44:]  # Pegar os últimos 44 caracteres
                    
            return None
            
        except Exception:
            return None
            
    def validar_e_renomear_thread(self):
        """Função de validação e renomeação executada em thread"""
        self.executar_thread_segura(self.validar_e_renomear_completo)

    def processar_completo_thread(self):
        """Função que executa TUDO: escaneamento + validação + renomeação"""
        self.executar_thread_segura(self.processar_tudo_completo)

    def processar_tudo_completo(self):
        """Função completa que faz escaneamento, validação e renomeação em sequência"""
        pasta = self.entrada_pasta_renomear.get()
        if not pasta:
            def mostrar_erro():
                messagebox.showerror("Erro", "Selecione a pasta com arquivos XML primeiro!")
            
            self.root.after(0, mostrar_erro)
            return
            
        if not self.linhas_renomeacao:
            def mostrar_erro_dados():
                messagebox.showerror("Erro", "Adicione dados para renomeação!\n\nUse 'LOTE DE DADOS' ou 'NOVA LINHA' para adicionar registros primeiro.")
            
            self.root.after(0, mostrar_erro_dados)
            return

        # Log inicial
        def log_inicial():
            self.log_renomeacao.insert("end", f"\n🚀 INICIANDO PROCESSAMENTO COMPLETO...\n")
            self.log_renomeacao.insert("end", f"📁 Pasta: {pasta}\n")
            self.log_renomeacao.insert("end", f"📋 Registros para processar: {len(self.linhas_renomeacao)}\n\n")
            self.log_renomeacao.see("end")
        
        self.root.after(0, log_inicial)

        try:
            # ETAPA 1: Escaneamento das chaves
            def log_etapa1():
                self.log_renomeacao.insert("end", "🔍 ETAPA 1/3: ESCANEANDO CHAVES DE ACESSO...\n")
                self.log_renomeacao.see("end")
            
            self.root.after(0, log_etapa1)
            
            self.chaves_xml = {}
            arquivos_processados = 0
            
            arquivos_xml = self.escanear_xmls_pasta(pasta)
            
            if not arquivos_xml:
                def mostrar_erro_xml():
                    self.log_renomeacao.insert("end", "❌ Nenhum arquivo XML encontrado na pasta!\n")
                    self.log_renomeacao.see("end")
                    messagebox.showerror("Erro", "Nenhum arquivo XML encontrado na pasta selecionada!")
                
                self.root.after(0, mostrar_erro_xml)
                return
            
            # Processar arquivos XML e PDFs
            self.associacoes_pdf = self.associar_xml_pdf(pasta)
            
            for chave, dados in self.associacoes_pdf.items():
                self.chaves_xml[chave] = dados['xml']
                arquivos_processados += 1

            def log_resultado_escaneamento():
                self.log_renomeacao.insert("end", f"✅ Escaneamento concluído: {arquivos_processados} chaves encontradas\n\n")
                self.log_renomeacao.see("end")
            
            self.root.after(0, log_resultado_escaneamento)

            if arquivos_processados == 0:
                def mostrar_erro_chaves():
                    self.log_renomeacao.insert("end", "❌ Nenhuma chave de acesso encontrada nos XMLs!\n")
                    self.log_renomeacao.see("end")
                    messagebox.showerror("Erro", "Nenhuma chave de acesso foi encontrada nos arquivos XML!")
                
                self.root.after(0, mostrar_erro_chaves)
                return

            # ETAPA 2 e 3: Validação e Renomeação
            def log_etapa2():
                self.log_renomeacao.insert("end", "✅ ETAPA 2/3: VALIDANDO E RENOMEANDO ARQUIVOS...\n")
                self.log_renomeacao.see("end")
            
            self.root.after(0, log_etapa2)
            
            sucessos = 0
            erros = 0
            
            for linha in self.linhas_renomeacao:
                chave_original = linha['chave'].get().strip()
                nome_final = linha['nome'].get().strip()
                
                if not chave_original or not nome_final:
                    continue
                    
                chave = chave_original.strip()
                
                # Validar chave
                if not self.validar_chave_nfe(chave):
                    def atualizar_status():
                        linha['status'].configure(text="❌ Chave")
                    
                    self.root.after(0, atualizar_status)
                    erros += 1
                    continue
                    
                # Verificar se chave existe
                if chave not in self.chaves_xml:
                    def atualizar_status():
                        linha['status'].configure(text="❌ N/Existe")
                    
                    self.root.after(0, atualizar_status)
                    erros += 1
                    continue
                    
                # Renomear XML e PDF
                try:
                    resultado_renomeacao = self.renomear_xml_e_pdf(chave, nome_final)
                    
                    if resultado_renomeacao['sucesso']:
                        def atualizar_status():
                            linha['status'].configure(text="✅ OK")
                        
                        self.root.after(0, atualizar_status)
                        sucessos += 1
                    else:
                        def atualizar_status():
                            linha['status'].configure(text="❌ Erro")
                        
                        self.root.after(0, atualizar_status)
                        erros += 1
                        
                except Exception as e:
                    def atualizar_status():
                        linha['status'].configure(text="❌ Erro")
                    
                    self.root.after(0, atualizar_status)
                    erros += 1

            # ETAPA 3: Finalização
            def log_finalizacao():
                self.log_renomeacao.insert("end", f"\n🎉 ETAPA 3/3: PROCESSAMENTO DE XMLs E PDFs FINALIZADO!\n")
                self.log_renomeacao.insert("end", f"✅ Conjuntos XMLs+PDFs renomeados: {sucessos}\n")
                self.log_renomeacao.insert("end", f"❌ Erros encontrados: {erros}\n")
                self.log_renomeacao.insert("end", f"📊 Total processado: {sucessos + erros}\n")
                self.log_renomeacao.insert("end", f"🎯 Taxa de sucesso: {(sucessos/(sucessos+erros)*100):.1f}%\n" if (sucessos + erros) > 0 else "")
                self.log_renomeacao.see("end")
                
                # Mostrar resultado final
                if sucessos > 0:
                    messagebox.showinfo("🎉 Processamento Completo!", f"Processamento de XMLs e PDFs finalizado!\n\n✅ {sucessos} conjunto(s) de arquivos renomeados\n❌ {erros} erros\n\nXMLs e PDFs foram processados juntos automaticamente!\nTodos os arquivos com chaves válidas foram renomeados.")
                else:
                    messagebox.showwarning("⚠️ Processamento Concluído", f"Processamento finalizado com problemas.\n\n❌ {erros} erros encontrados\n✅ {sucessos} sucessos\n\nVerifique os dados e tente novamente.")
            
            self.root.after(0, log_finalizacao)

        except Exception as e:
            def mostrar_erro_geral():
                error_msg = f"❌ ERRO DURANTE PROCESSAMENTO: {str(e)}\n"
                self.log_renomeacao.insert("end", error_msg)
                self.log_renomeacao.see("end")
                messagebox.showerror("Erro Crítico", f"Erro durante o processamento completo:\n\n{str(e)}\n\nTente novamente ou use as funções individuais.")
            
            self.root.after(0, mostrar_erro_geral)
        
    def validar_e_renomear_completo(self):
        pasta = self.entrada_pasta_renomear.get()
        if not pasta:
            messagebox.showerror("Erro", "Selecione a pasta primeiro!")
            return
            
        if not self.chaves_xml:
            messagebox.showerror("Erro", "Execute o escaneamento de chaves primeiro!\n\nClique em 'ESCANEAR CHAVES' antes de validar.")
            return
            
        if not self.linhas_renomeacao:
            messagebox.showerror("Erro", "Adicione dados para renomeação!\n\nUse 'LOTE DE DADOS' ou 'NOVA LINHA' para adicionar registros.")
            return
            
        sucessos = 0
        erros = 0
        
        # Buffer para logs - OTIMIZAÇÃO
        log_buffer = ["\n🚀 INICIANDO VALIDAÇÃO E RENOMEAÇÃO DE XMLs E PDFs...\n\n"]
        
        for linha in self.linhas_renomeacao:
            chave_original = linha['chave'].get().strip()
            nome_final = linha['nome'].get().strip()
            
            if not chave_original or not nome_final:
                continue
                
            chave = chave_original.strip()
            
            # Validar chave (usando função auxiliar - elimina duplicação)
            if not self.validar_chave_nfe(chave):
                def atualizar_status():
                    linha['status'].configure(text="❌ Chave")
                
                self.root.after(0, atualizar_status)
                log_buffer.append(f"❌ Chave inválida: {chave}\n")
                erros += 1
                continue
                
            # Verificar se chave existe
            if chave not in self.chaves_xml:
                def atualizar_status():
                    linha['status'].configure(text="❌ N/Existe")
                
                self.root.after(0, atualizar_status)
                log_buffer.append(f"❌ Chave não encontrada nos XMLs: {chave}\n")
                erros += 1
                continue
                
                        # Renomear XML e PDF
            try:
                resultado_renomeacao = self.renomear_xml_e_pdf(chave, nome_final)
                
                if resultado_renomeacao['sucesso']:
                    def atualizar_status():
                        linha['status'].configure(text="✅ OK")
                    
                    self.root.after(0, atualizar_status)
                    log_buffer.append(resultado_renomeacao['log'])
                    sucessos += 1
                else:
                    def atualizar_status():
                        linha['status'].configure(text="❌ Erro")
            
                    self.root.after(0, atualizar_status)  
                    log_buffer.append(resultado_renomeacao['log'])
                    erros += 1
            
            except Exception as e:
                def atualizar_status():
                    linha['status'].configure(text="❌ Erro")
                
                self.root.after(0, atualizar_status)
                log_buffer.append(f"❌ Erro inesperado: {str(e)}\n")
                erros += 1
                
        # Adicionar logs finais
        log_buffer.extend([
            f"\n🎉 VALIDAÇÃO E RENOMEAÇÃO DE XMLs E PDFs CONCLUÍDA!\n",
            f"✅ Sucessos: {sucessos}\n",
            f"❌ Erros: {erros}\n",
            f"📊 Total processado: {sucessos + erros}\n"
        ])
        
        # OTIMIZAÇÃO: Uma única atualização da interface
        def atualizar_interface_final():
            for log in log_buffer:
                self.log_renomeacao.insert("end", log)
            self.log_renomeacao.see("end")
            
            # Mostrar resultado
            if sucessos > 0:
                messagebox.showinfo("Concluído!", f"🎉 Renomeação de XMLs e PDFs Finalizada!\n\n✅ {sucessos} conjunto(s) de arquivos renomeados\n❌ {erros} erros encontrados\n\nXMLs e PDFs foram renomeados juntos!\nConfira o log para detalhes.")
            else:
                messagebox.showwarning("Atenção", f"Nenhum arquivo foi renomeado.\n\n❌ {erros} erros encontrados\n\nVerifique os dados e tente novamente.")
            
        self.root.after(0, atualizar_interface_final)
    
    def limpar_dados_massa(self):
        resposta = messagebox.askyesno(
            "Confirmar Limpeza", 
            "🧹 Tem certeza que deseja limpar TODOS os dados da tabela?\n\nEsta ação não pode ser desfeita!"
        )
        
        if resposta:
            # Limpar todas as linhas existentes
            for linha in self.linhas_renomeacao:
                linha['frame'].destroy()
            self.linhas_renomeacao.clear()
            
            # Log
            self.log_renomeacao.insert("end", f"\n🧹 DADOS LIMPOS:\n")
            self.log_renomeacao.insert("end", f"✅ Tabela limpa com sucesso\n")
            self.log_renomeacao.insert("end", f"📝 Tabela pronta para novos dados\n")
            self.log_renomeacao.see("end")
            
            messagebox.showinfo("Limpeza Concluída!", "✅ Todos os dados foram removidos da tabela!")
    
    def gerar_relatorio_excel(self):
        """Gera um relatório completo em Excel com todos os dados da tabela de mapeamento"""
        try:
            if not self.linhas_renomeacao:
                messagebox.showwarning("Aviso", "⚠️ Nenhum dado para gerar relatório!\n\nAdicione dados na tabela primeiro usando 'LOTE DE DADOS' ou 'NOVA LINHA'.")
                return
            
            # Coletar dados da tabela
            dados_relatorio = []
            for i, linha in enumerate(self.linhas_renomeacao, 1):
                chave = linha['chave'].get().strip()
                nome = linha['nome'].get().strip()
                status = linha['status'].cget("text")
                
                # Criar registro do relatório
                registro = {
                    'Linha': i,
                    'Chave de Acesso': chave,
                    'Nome do Arquivo': nome,
                    'Status': status,
                    'Chave Válida': '✅ Sim' if self.validar_chave_nfe(chave) else '❌ Não',
                    'Preenchido': '✅ Completo' if (chave and nome) else '⚠️ Incompleto',
                    'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Adicionar informações extras se disponível
                if hasattr(self, 'chaves_xml') and chave in self.chaves_xml:
                    registro['XML Encontrado'] = '✅ Sim'
                    registro['Caminho XML'] = self.chaves_xml[chave]
                else:
                    registro['XML Encontrado'] = '❌ Não'
                    registro['Caminho XML'] = ''
                
                # Verificar PDF associado
                if hasattr(self, 'associacoes_pdf') and chave in self.associacoes_pdf:
                    pdf_path = self.associacoes_pdf[chave]['pdf']
                    registro['PDF Encontrado'] = '✅ Sim' if pdf_path else '❌ Não'
                    registro['Caminho PDF'] = pdf_path or ''
                else:
                    registro['PDF Encontrado'] = '❌ Não'
                    registro['Caminho PDF'] = ''
                
                dados_relatorio.append(registro)
            
            # Solicitar local para salvar
            pasta_renomear = self.entrada_pasta_renomear.get()
            pasta_inicial = pasta_renomear if pasta_renomear else os.path.expanduser("~")
            
            nome_arquivo = f"Relatorio_Renomeacao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            arquivo_excel = filedialog.asksaveasfilename(
                title="Salvar Relatório de Renomeação",
                initialdir=pasta_inicial,
                defaultextension=".xlsx",
                filetypes=[
                    ("Excel files", "*.xlsx"),
                    ("All files", "*.*")
                ],
                initialfile=nome_arquivo
            )
            
            if not arquivo_excel:
                return
            
            # Criar DataFrame
            df = pd.DataFrame(dados_relatorio)
            
            # Criar Excel com formatação
            with pd.ExcelWriter(arquivo_excel, engine='openpyxl') as writer:
                # Escrever dados principais
                df.to_excel(writer, sheet_name='Relatório Renomeação', index=False)
                
                # Obter workbook e worksheet para formatação
                workbook = writer.book
                worksheet = writer.sheets['Relatório Renomeação']
                
                # Ajustar largura das colunas
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
                
                # Criar planilha de resumo
                resumo_data = []
                total_registros = len(dados_relatorio)
                chaves_validas = sum(1 for r in dados_relatorio if r['Chave Válida'] == '✅ Sim')
                registros_completos = sum(1 for r in dados_relatorio if r['Preenchido'] == '✅ Completo')
                xmls_encontrados = sum(1 for r in dados_relatorio if r['XML Encontrado'] == '✅ Sim')
                pdfs_encontrados = sum(1 for r in dados_relatorio if r['PDF Encontrado'] == '✅ Sim')
                
                # Status dos registros
                status_ok = sum(1 for r in dados_relatorio if '✅' in r['Status'])
                status_erro = sum(1 for r in dados_relatorio if '❌' in r['Status'])
                status_aguardando = sum(1 for r in dados_relatorio if '⏳' in r['Status'])
                
                resumo_data = [
                    ['📊 RESUMO DO RELATÓRIO DE RENOMEAÇÃO', ''],
                    ['Data/Hora Geração:', datetime.now().strftime("%d/%m/%Y %H:%M:%S")],
                    ['Pasta de Trabalho:', pasta_renomear or 'Não selecionada'],
                    ['', ''],
                    ['📋 ESTATÍSTICAS GERAIS', ''],
                    ['Total de Registros:', total_registros],
                    ['Registros Completos:', f"{registros_completos} ({registros_completos/total_registros*100:.1f}%)" if total_registros > 0 else '0'],
                    ['Chaves Válidas:', f"{chaves_validas} ({chaves_validas/total_registros*100:.1f}%)" if total_registros > 0 else '0'],
                    ['', ''],
                    ['📄 ARQUIVOS ENCONTRADOS', ''],
                    ['XMLs Encontrados:', f"{xmls_encontrados} ({xmls_encontrados/total_registros*100:.1f}%)" if total_registros > 0 else '0'],
                    ['PDFs Encontrados:', f"{pdfs_encontrados} ({pdfs_encontrados/total_registros*100:.1f}%)" if total_registros > 0 else '0'],
                    ['', ''],
                    ['🎯 STATUS DOS REGISTROS', ''],
                    ['Processados com Sucesso:', status_ok],
                    ['Erros Encontrados:', status_erro],
                    ['Aguardando Processamento:', status_aguardando],
                    ['', ''],
                    ['💡 OBSERVAÇÕES', ''],
                    ['• Chaves devem ter exatamente 44 dígitos numéricos', ''],
                    ['• XMLs e PDFs são renomeados em conjunto', ''],
                    ['• Status mostra resultado do último processamento', ''],
                    ['• Relatório gerado automaticamente pelo renamerPRO©', '']
                ]
                
                # Criar DataFrame do resumo
                df_resumo = pd.DataFrame(resumo_data)
                df_resumo.columns = ['Parâmetro', 'Valor']
                df_resumo.to_excel(writer, sheet_name='Resumo', index=False)
                
                # Ajustar largura das colunas do resumo
                resumo_ws = writer.sheets['Resumo']
                resumo_ws.column_dimensions['A'].width = 40
                resumo_ws.column_dimensions['B'].width = 30
            
            # Log de sucesso
            self.log_renomeacao.insert("end", f"\n📊 RELATÓRIO EXCEL GERADO:\n")
            self.log_renomeacao.insert("end", f"✅ Arquivo: {os.path.basename(arquivo_excel)}\n")
            self.log_renomeacao.insert("end", f"📁 Local: {os.path.dirname(arquivo_excel)}\n")
            self.log_renomeacao.insert("end", f"📋 Registros: {len(dados_relatorio)}\n")
            self.log_renomeacao.insert("end", f"📊 Planilhas: Relatório + Resumo\n")
            self.log_renomeacao.see("end")
            
            # Perguntar se deseja abrir o arquivo
            resposta = messagebox.askyesno(
                "Relatório Gerado!", 
                f"📊 Relatório Excel criado com sucesso!\n\n"
                f"📁 Arquivo: {os.path.basename(arquivo_excel)}\n"
                f"📋 {len(dados_relatorio)} registros exportados\n"
                f"📊 2 planilhas: Dados + Resumo\n\n"
                f"Deseja abrir o arquivo agora?"
            )
            
            if resposta:
                try:
                    os.startfile(arquivo_excel)
                except:
                    webbrowser.open(arquivo_excel)
            
        except ImportError:
            messagebox.showerror(
                "Erro - Biblioteca Necessária", 
                "❌ Biblioteca pandas não encontrada!\n\n"
                "Para usar esta funcionalidade, instale:\n"
                "pip install pandas openpyxl\n\n"
                "Ou execute o arquivo requirements.txt"
            )
        except Exception as e:
            error_msg = f"❌ Erro ao gerar relatório: {str(e)}\n"
            self.log_renomeacao.insert("end", error_msg)
            self.log_renomeacao.see("end")
            messagebox.showerror("Erro", f"Erro ao gerar relatório Excel:\n\n{str(e)}")

    # ============= FUNÇÕES AUXILIARES (ELIMINAM DUPLICAÇÕES) =============
    
    def escanear_xmls_pasta(self, pasta):
        """Função auxiliar para escanear XMLs de uma pasta (elimina duplicação)"""
        arquivos_xml = []
        try:
            for arquivo in os.listdir(pasta):
                if arquivo.lower().endswith('.xml'):
                    caminho_completo = os.path.join(pasta, arquivo)
                    arquivos_xml.append(caminho_completo)
        except Exception as e:
            print(f"Erro ao escanear pasta: {e}")
        return arquivos_xml

    def escanear_arquivos_pasta(self, pasta):
        """Função para escanear XMLs e PDFs de uma pasta"""
        arquivos = {'xml': [], 'pdf': []}
        try:
            for arquivo in os.listdir(pasta):
                caminho_completo = os.path.join(pasta, arquivo)
                if arquivo.lower().endswith('.xml'):
                    arquivos['xml'].append(caminho_completo)
                elif arquivo.lower().endswith('.pdf'):
                    arquivos['pdf'].append(caminho_completo)
        except Exception as e:
            print(f"Erro ao escanear pasta: {e}")
        return arquivos

    def associar_xml_pdf(self, pasta):
        """Associa XMLs com seus PDFs correspondentes por nome similar"""
        arquivos = self.escanear_arquivos_pasta(pasta)
        associacoes = {}
        
        for xml_path in arquivos['xml']:
            xml_nome = os.path.splitext(os.path.basename(xml_path))[0]
            chave = self.extrair_chave_xml(xml_path)
            
            if chave:
                # Buscar PDF correspondente
                pdf_correspondente = None
                
                # Tentativa 1: PDF com mesmo nome do XML
                pdf_mesmo_nome = os.path.join(pasta, f"{xml_nome}.pdf")
                if os.path.exists(pdf_mesmo_nome):
                    pdf_correspondente = pdf_mesmo_nome
                else:
                    # Tentativa 2: PDF com sufixo _DANFE (apenas para compatibilidade)
                    pdf_danfe = os.path.join(pasta, f"{xml_nome}_DANFE.pdf")
                    if os.path.exists(pdf_danfe):
                        pdf_correspondente = pdf_danfe
                    else:
                        # Tentativa 3: PDF com a chave no nome
                        for pdf_path in arquivos['pdf']:
                            pdf_nome = os.path.basename(pdf_path)
                            if chave in pdf_nome or xml_nome.lower() in pdf_nome.lower():
                                pdf_correspondente = pdf_path
                                break
                
                associacoes[chave] = {
                    'xml': xml_path,
                    'pdf': pdf_correspondente
                }
        
        return associacoes

    def gerar_pdf_personalizado(self, arquivo_xml, nome_final):
        """Gera PDF com nome personalizado (sem sufixo _DANFE)"""
        try:
            # Verificações pré-processamento
            if not hasattr(self, '_php_validado'):
                self._validar_ambiente_php()
            
            # Usar PHP para gerar DANFE com nome personalizado
            script_dir = os.path.dirname(os.path.abspath(__file__))
            php_full_path = os.path.join(script_dir, "php", "php.exe")
            script_php_full = os.path.join(script_dir, "gerador_danfe.php")
            
            # Comando com nome personalizado
            cmd = [php_full_path, script_php_full, arquivo_xml, nome_final]
            
            # Executar PHP
            php_dir = os.path.join(script_dir, "php")
            resultado = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=60,
                creationflags=subprocess.CREATE_NO_WINDOW,
                cwd=php_dir
            )
            
            # Verificar resultado
            if resultado.returncode == 0 and "SUCCESS:" in resultado.stdout:
                arquivo_pdf = resultado.stdout.strip().replace("SUCCESS:", "")
                return arquivo_pdf if os.path.exists(arquivo_pdf) else None
            else:
                return None
                
        except Exception as e:
            print(f"Erro ao gerar PDF personalizado: {e}")
            return None

    def renomear_xml_e_pdf(self, chave, nome_final):
        """Renomeia XML e gera/renomeia PDF com o novo nome (SEM sufixo _DANFE)"""
        try:
            resultado = {'sucesso': False, 'log': ''}
            
            if chave not in self.chaves_xml:
                resultado['log'] = f"❌ Chave não encontrada: {chave}\n"
                return resultado
            
            # Obter informações do XML
            xml_original = self.chaves_xml[chave]
            pasta_arquivo = os.path.dirname(xml_original)
            novo_xml = os.path.join(pasta_arquivo, f"{nome_final}.xml")
            novo_pdf = os.path.join(pasta_arquivo, f"{nome_final}.pdf")
            
            # Verificar se arquivos já existem
            if os.path.exists(novo_xml):
                resultado['log'] = f"❌ XML já existe: {nome_final}.xml\n"
                return resultado
            
            if os.path.exists(novo_pdf):
                resultado['log'] = f"❌ PDF já existe: {nome_final}.pdf\n"
                return resultado
            
            # Executar renomeação e geração
            arquivos_processados = []
            
            # 1. Renomear XML
            os.rename(xml_original, novo_xml)
            arquivos_processados.append(f"📄 XML: {os.path.basename(xml_original)} → {nome_final}.xml")
            self.chaves_xml[chave] = novo_xml
            
            # 2. Gerar PDF com nome personalizado (SEM sufixo _DANFE)
            try:
                pdf_gerado = self.gerar_pdf_personalizado(novo_xml, nome_final)
                
                if pdf_gerado and os.path.exists(pdf_gerado):
                    arquivos_processados.append(f"📄 PDF: Gerado como {nome_final}.pdf")
                    
                    # Atualizar associações se existirem
                    if hasattr(self, 'associacoes_pdf') and chave in self.associacoes_pdf:
                        # Remover PDF antigo se existir
                        pdf_antigo = self.associacoes_pdf[chave]['pdf']
                        if pdf_antigo and os.path.exists(pdf_antigo) and pdf_antigo != pdf_gerado:
                            try:
                                os.remove(pdf_antigo)
                            except:
                                pass
                        
                        self.associacoes_pdf[chave]['pdf'] = pdf_gerado
                else:
                    # Se falhou ao gerar PDF, ainda assim é sucesso parcial
                    arquivos_processados.append(f"⚠️ PDF: Erro ao gerar (XML renomeado com sucesso)")
                    
            except Exception as e:
                # Se PDF falhar, manter o XML renomeado
                arquivos_processados.append(f"⚠️ PDF: Erro ao gerar - {str(e)} (XML renomeado com sucesso)")
            
            # Sucesso (mesmo se PDF falhou)
            resultado['sucesso'] = True
            resultado['log'] = f"✅ {' + '.join(arquivos_processados)}\n"
            return resultado
            
        except Exception as e:
            # Tentar reverter XML se algo deu errado
            try:
                if 'novo_xml' in locals() and os.path.exists(novo_xml):
                    os.rename(novo_xml, xml_original)
                    self.chaves_xml[chave] = xml_original
            except:
                pass
            
            resultado['log'] = f"❌ Erro ao processar arquivos: {str(e)}\n"
            return resultado

    def validar_chave_nfe(self, chave):
        """Função auxiliar para validar chave NFe (elimina duplicação)"""
        chave = str(chave).strip()
        return len(chave) == 44 and chave.isdigit()

    def executar_thread_segura(self, target_func):
        """Função auxiliar para threading (elimina duplicação)"""
        thread = threading.Thread(target=target_func)
        thread.daemon = True
        thread.start()

    def processar_xmls_paralelo(self, arquivos_xml, pasta_saida, callback_sucesso=None, callback_erro=None):
        """Função auxiliar para processamento paralelo OTIMIZADA (elimina duplicação)"""
        sucessos = 0
        erros = 0
        inicio = time.time()
        
        # Buffer para logs - OTIMIZAÇÃO CRÍTICA
        log_buffer = []
        buffer_size = 10  # Atualizar interface a cada 10 arquivos
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self.processar_xml_individual_otimizado, arquivo, pasta_saida): arquivo 
                for arquivo in arquivos_xml
            }
            
            for future in as_completed(futures):
                arquivo = futures[future]
                nome_arquivo = os.path.basename(arquivo)
                
                try:
                    resultado = future.result()
                    if resultado:
                        sucessos += 1
                        log_buffer.append(f"✅ {nome_arquivo}")
                    else:
                        erros += 1
                        log_buffer.append(f"❌ {nome_arquivo}")
                except Exception as e:
                    erros += 1
                    log_buffer.append(f"❌ {nome_arquivo} - ERRO: {str(e)}")
                
                # OTIMIZAÇÃO: Atualizar interface em lotes
                if len(log_buffer) >= buffer_size:
                    self.atualizar_interface_lote(log_buffer, sucessos + erros, len(arquivos_xml))
                    log_buffer.clear()
        
        # Processar logs restantes
        if log_buffer:
            self.atualizar_interface_lote(log_buffer, sucessos + erros, len(arquivos_xml))
        
        tempo_total = time.time() - inicio
        return sucessos, erros, tempo_total

    def atualizar_interface_lote(self, logs, processados, total):
        """NOVA FUNÇÃO: Atualiza interface em lotes para melhor performance"""
        def atualizar():
            # Adicionar todos os logs de uma vez
            for log in logs:
                self.adicionar_log(log)
            
            # Atualizar progresso
            if hasattr(self, 'progresso_geral'):
                self.progresso_geral.set(processados / total)
                self.label_progresso.configure(text=f"{processados} / {total} arquivos processados")
        
        self.root.after(0, atualizar)

    def processar_xml_individual_otimizado(self, arquivo_xml, pasta_saida):
        """Versão OTIMIZADA sem logs excessivos"""
        try:
            # Verificações pré-processamento (fazer uma única vez)
            if not hasattr(self, '_php_validado'):
                self._validar_ambiente_php()
            
            # Usar PHP para gerar DANFE
            script_dir = os.path.dirname(os.path.abspath(__file__))
            php_full_path = os.path.join(script_dir, "php", "php.exe")
            script_php_full = os.path.join(script_dir, "gerador_danfe.php")
            
            cmd = [php_full_path, script_php_full, arquivo_xml]
            
            # Executar PHP otimizado
            php_dir = os.path.join(script_dir, "php")
            resultado = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=60,  # Reduzido de 120 para 60 segundos
                creationflags=subprocess.CREATE_NO_WINDOW,
                cwd=php_dir
            )
            
            # Verificar resultado
            if resultado.returncode == 0 and "SUCCESS:" in resultado.stdout:
                arquivo_pdf = resultado.stdout.strip().replace("SUCCESS:", "")
                
                if os.path.exists(arquivo_pdf):
                    # Mover PDF se necessário
                    if pasta_saida != os.path.dirname(arquivo_xml):
                        nome_pdf = os.path.basename(arquivo_pdf)
                        novo_caminho = os.path.join(pasta_saida, nome_pdf)
                        
                        if os.path.exists(novo_caminho):
                            os.remove(novo_caminho)
                        
                        os.rename(arquivo_pdf, novo_caminho)
                    
                    return True
            
            return False
                
        except subprocess.TimeoutExpired:
            return False
        except Exception:
            return False

    def _validar_ambiente_php(self):
        """NOVA FUNÇÃO: Valida ambiente PHP uma única vez"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        php_full_path = os.path.join(script_dir, "php", "php.exe")
        script_php_full = os.path.join(script_dir, "gerador_danfe.php")
        
        if not os.path.exists(php_full_path):
            raise Exception(f"PHP não encontrado: {php_full_path}")
        
        if not os.path.exists(script_php_full):
            raise Exception(f"Script PHP não encontrado: {script_php_full}")
        
        self._php_validado = True

    def mostrar_conclusao_processamento(self, sucessos, erros, tempo_total, pasta_saida):
        """Função auxiliar para mostrar conclusão (elimina duplicação)"""
        if sucessos > 0:
            resposta = messagebox.askyesno(
                "Processamento Concluído!", 
                f"✅ {sucessos} DANFEs geradas\n❌ {erros} erros\n\nDeseja abrir a pasta com os PDFs?"
            )
            
            if resposta:
                try:
                    os.startfile(pasta_saida)
                except:
                    webbrowser.open(pasta_saida)

    # ============= FUNÇÕES ORIGINAIS (REFATORADAS) =============

    def carregar_log_inicial(self):
        log_inicial = """⚕️ renamerPRO©
        
🔹 Sistema inicializado com sucesso
🔹 Aguardando configuração de pastas...
🔹 NOVO: Dados de rastro incluídos automaticamente na DANFE
🔹 Campos de rastro: nLote, qLote, dFab, dVal
🔹 Você é responsável pelos seus atos

   1. Inicie o processamento em massa"""

        self.log_text.delete("0.0", "end")
        self.log_text.insert("0.0", log_inicial)
        
    def selecionar_pasta_xml(self):
        pasta = filedialog.askdirectory(title="Selecione a pasta com os XMLs")
        if pasta:
            self.pasta_xml.set(pasta)
            self.status_texto.set(f"Pasta XML selecionada: {os.path.basename(pasta)}")
            self.btn_escanear.configure(state="normal")
            

            
    def selecionar_pasta_saida(self):
        pasta = filedialog.askdirectory(title="Selecione a pasta para salvar os PDFs")
        if pasta:
            self.pasta_saida.set(pasta)
            
    def escanear_pasta(self):
        if not self.pasta_xml.get():
            messagebox.showerror("Erro", "Selecione a pasta com XMLs primeiro!")
            return
            
        pasta = self.pasta_xml.get()
        
        # Usar função auxiliar (elimina duplicação)
        self.arquivos_xml = self.escanear_xmls_pasta(pasta)
                
        total = len(self.arquivos_xml)
        
        if total == 0:
            self.label_arquivos.configure(text="❌ Nenhum arquivo XML encontrado na pasta!")
            self.btn_processar.configure(state="disabled")
            messagebox.showwarning("Aviso", "Nenhum arquivo XML encontrado na pasta selecionada!")
        else:
            self.label_arquivos.configure(text=f"✅ {total} arquivo(s) XML encontrado(s)")
            self.btn_processar.configure(state="normal")
            
            self.adicionar_log(f"\n🔍 ESCANEAMENTO CONCLUÍDO:")
            self.adicionar_log(f"📁 Pasta: {pasta}")
            self.adicionar_log(f"📊 Total de XMLs: {total}")
            
            self.adicionar_log(f"\n📄 Arquivos encontrados:")
            for i, arquivo in enumerate(self.arquivos_xml[:5]):
                nome = os.path.basename(arquivo)
                self.adicionar_log(f"  {i+1}. {nome}")
            
            if total > 5:
                self.adicionar_log(f"  ... e mais {total-5} arquivo(s)")
                
            self.adicionar_log(f"\n✅ Pronto para processar! Clique em 'PROCESSAR TODOS'")
            
    def adicionar_log(self, texto):
        self.log_text.insert("end", texto + "\n")
        self.log_text.see("end")
        
    def processar_massa_thread(self):
        if self.processando:
            return
            
        # Usar função auxiliar (elimina duplicação)
        self.executar_thread_segura(self.processar_massa)
        
    def processar_massa(self):
        if not self.arquivos_xml:
            messagebox.showerror("Erro", "Escaneie a pasta primeiro!")
            return
            
        self.processando = True
        total = len(self.arquivos_xml)
        sucessos = 0
        erros = 0
        
        pasta_saida = self.pasta_saida.get() or self.pasta_xml.get()
        
        self.root.after(0, lambda: self.btn_processar.configure(state="disabled", text="🔄 Processando..."))
        self.root.after(0, lambda: self.btn_escanear.configure(state="disabled"))
        self.root.after(0, lambda: self.status_texto.set("Processando XMLs em massa..."))
        
        self.root.after(0, lambda: self.adicionar_log(f"\n🚀 INICIANDO PROCESSAMENTO EM MASSA:"))
        self.root.after(0, lambda: self.adicionar_log(f"📊 Total: {total} arquivos"))
        self.root.after(0, lambda: self.adicionar_log(f"📤 Pasta saída: {pasta_saida}"))
        self.root.after(0, lambda: self.adicionar_log(f"⚡ Processamento paralelo ativado (5 simultâneos)\n"))
        
        inicio = time.time()
        
        # OTIMIZADO: Processar sem callbacks excessivos
        sucessos, erros, tempo_total = self.processar_xmls_paralelo(
            self.arquivos_xml, pasta_saida
        )
        
        self.root.after(0, lambda: self.adicionar_log(f"\n🎉 PROCESSAMENTO CONCLUÍDO!"))
        self.root.after(0, lambda: self.adicionar_log(f"✅ Sucessos: {sucessos}"))
        self.root.after(0, lambda: self.adicionar_log(f"❌ Erros: {erros}"))
        self.root.after(0, lambda: self.adicionar_log(f"⏱️ Tempo total: {tempo_total:.1f} segundos"))
        self.root.after(0, lambda: self.adicionar_log(f"⚡ Média: {tempo_total/total:.1f}s por arquivo"))
        
        self.root.after(0, lambda: self.btn_processar.configure(state="normal", text="🎯 PROCESSAR TODOS"))
        self.root.after(0, lambda: self.btn_escanear.configure(state="normal"))
        self.root.after(0, lambda: self.status_texto.set(f"✅ Concluído: {sucessos} sucessos, {erros} erros"))
        
        # Usar função auxiliar (elimina duplicação)
        self.mostrar_conclusao_processamento(sucessos, erros, tempo_total, pasta_saida)
        
        self.processando = False
    

        
    
    def instalar_vcredist(self):
        """Instala Visual C++ Redistributable 2015-2022 automaticamente"""
        try:
            import urllib.request
            
            # URL do Visual C++ Redistributable x64 2015-2022
            url = "https://aka.ms/vs/17/release/vc_redist.x64.exe"
            arquivo_installer = "vc_redist.x64.exe"
            
            self.adicionar_log("📥 Baixando Visual C++ Redistributable...")
            
            # Baixar o installer
            urllib.request.urlretrieve(url, arquivo_installer)
            
            self.adicionar_log("⚙️ Instalando Visual C++ Redistributable...")
            
            # Executar instalação silenciosa
            resultado = subprocess.run(
                [arquivo_installer, "/quiet", "/norestart"],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos
            )
            
            # Limpar arquivo temporário
            if os.path.exists(arquivo_installer):
                os.remove(arquivo_installer)
            
            if resultado.returncode == 0:
                self.adicionar_log("✅ Visual C++ Redistributable instalado com sucesso!")
                return True
            else:
                self.adicionar_log(f"❌ Erro na instalação (código: {resultado.returncode})")
                return False
                
        except Exception as e:
            self.adicionar_log(f"❌ Erro ao instalar dependências: {str(e)}")
            return False

    def processar_xml_individual(self, arquivo_xml, pasta_saida):
        try:
            # Verificar se arquivo XML existe
            if not os.path.exists(arquivo_xml):
                self.adicionar_log(f"❌ Arquivo não encontrado: {arquivo_xml}")
                return False
            
            # Verificar se pasta de saída existe
            if not os.path.exists(pasta_saida):
                try:
                    os.makedirs(pasta_saida, exist_ok=True)
                except Exception as e:
                    self.adicionar_log(f"❌ Erro ao criar pasta: {pasta_saida} - {str(e)}")
                    return False
            
            # Usar PHP para gerar DANFE
            # Obter o diretório do script atual
            script_dir = os.path.dirname(os.path.abspath(__file__))
            php_full_path = os.path.join(script_dir, "php", "php.exe")
            script_php_full = os.path.join(script_dir, "gerador_danfe.php")
            
            # Verificar se arquivos existem
            if not os.path.exists(php_full_path):
                self.adicionar_log(f"❌ PHP não encontrado: {php_full_path}")
                return False
            
            if not os.path.exists(script_php_full):
                self.adicionar_log(f"❌ Script PHP não encontrado: {script_php_full}")
                return False
            
            # Comando para executar PHP (usar caminhos absolutos)
            cmd = [php_full_path, script_php_full, arquivo_xml]
            
                        # Executar PHP com melhor tratamento de erro
            try:
                # Executar do diretório php para carregar extensões
                php_dir = os.path.join(script_dir, "php")
                resultado = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=120,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    cwd=php_dir  # Executar do diretório php para carregar extensões
                )
            except FileNotFoundError:
                self.adicionar_log(f"❌ PHP executável não encontrado: {php_full_path}")
                return False
            except Exception as e:
                self.adicionar_log(f"❌ Erro ao executar PHP: {str(e)}")
                return False
            
            # Verificar se é erro de DLL faltando (Visual C++ Redistributable)
            if resultado.returncode == 3221225781:  # 0xC0000135 - DLL_NOT_FOUND
                # Tentar instalar apenas uma vez
                if not self.vcredist_tentado:
                    self.adicionar_log(f"❌ PHP precisa do Visual C++ Redistributable 2015-2022")
                    self.adicionar_log(f"🔧 Instalando dependências automaticamente...")
                    
                    if self.instalar_vcredist():
                        self.adicionar_log(f"🔄 Reinicie o aplicativo para usar o PHP corrigido")
                    
                    self.vcredist_tentado = True
                
                self.adicionar_log(f"❌ {os.path.basename(arquivo_xml)} - Dependência Visual C++ necessária")
                return False
            
            # Verificar resultado
            if resultado.returncode == 0 and "SUCCESS:" in resultado.stdout:
                arquivo_pdf = resultado.stdout.strip().replace("SUCCESS:", "")
                
                # Verificar se PDF foi criado
                if not os.path.exists(arquivo_pdf):
                    self.adicionar_log(f"❌ PDF não foi criado: {arquivo_pdf}")
                    return False
                
                # Mover PDF para pasta de saída se necessário
                if pasta_saida != os.path.dirname(arquivo_xml):
                    nome_pdf = os.path.basename(arquivo_pdf)
                    novo_caminho = os.path.join(pasta_saida, nome_pdf)
                    
                    try:
                        # Se arquivo já existe na pasta de destino, removê-lo
                        if os.path.exists(novo_caminho):
                            os.remove(novo_caminho)
                        
                        os.rename(arquivo_pdf, novo_caminho)
                        nome_pdf = os.path.basename(novo_caminho)
                    except Exception as e:
                        self.adicionar_log(f"❌ Erro ao mover PDF: {str(e)}")
                        return False
                else:
                    nome_pdf = os.path.basename(arquivo_pdf)
                
                self.adicionar_log(f"✅ {nome_pdf}")
                return True
            else:
                # Log do erro detalhado
                error_msg = resultado.stderr.strip() if resultado.stderr else "Erro desconhecido"
                stdout_msg = resultado.stdout.strip() if resultado.stdout else ""
                
                if "ERROR:" in stdout_msg:
                    error_msg = stdout_msg.replace("ERROR:", "").strip()
                
                # Se não há saída, pode ser problema com dependências
                if not stdout_msg and not error_msg:
                    if resultado.returncode == 3221225781:
                        error_msg = "Dependência Visual C++ necessária"
                    else:
                        error_msg = f"PHP erro código {resultado.returncode}"
                
                self.adicionar_log(f"❌ {os.path.basename(arquivo_xml)} - {error_msg}")
                return False
                
        except subprocess.TimeoutExpired:
            self.adicionar_log(f"❌ Timeout ao processar: {os.path.basename(arquivo_xml)}")
            return False
        except Exception as e:
            self.adicionar_log(f"❌ Erro inesperado: {str(e)}")
            return False
            
    def abrir_janela_lote(self):
        # Criar janela popup
        self.janela_lote = ctk.CTkToplevel(self.root)
        self.janela_lote.title("📋 Adicionar Lote de Dados")
        self.janela_lote.geometry("1200x900")
        self.janela_lote.minsize(1000, 600)
        self.janela_lote.transient(self.root)
        self.janela_lote.grab_set()
        
        # Instrução compacta
        instrucao = ctk.CTkLabel(
            self.janela_lote,
            text="Preencha os campos abaixo. Use uma linha por registro:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        instrucao.pack(pady=15)
        
        # Frame principal
        main_frame = ctk.CTkFrame(self.janela_lote)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Frame das colunas
        colunas_frame = ctk.CTkFrame(main_frame)
        colunas_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Coluna esquerda - Chaves
        frame_chaves = ctk.CTkFrame(colunas_frame)
        frame_chaves.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=10)
        
        ctk.CTkLabel(
            frame_chaves,
            text="🔑 Chave Acesso NF",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))
        
        ctk.CTkLabel(
            frame_chaves,
            text="(44 dígitos numéricos)",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack(pady=(0, 10))
        
        self.textbox_chaves = ctk.CTkTextbox(
            frame_chaves,
            font=ctk.CTkFont(size=11),
            height=500
        )
        self.textbox_chaves.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Coluna direita - Nomes
        frame_nomes = ctk.CTkFrame(colunas_frame)
        frame_nomes.pack(side="right", fill="both", expand=True, padx=(5, 10), pady=10)
        
        ctk.CTkLabel(
            frame_nomes,
            text="📄 Nome Arq. NF",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))
        
        ctk.CTkLabel(
            frame_nomes,
            text="(Nome desejado para o arquivo)",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack(pady=(0, 10))
        
        self.textbox_nomes = ctk.CTkTextbox(
            frame_nomes,
            font=ctk.CTkFont(size=11),
            height=500
        )
        self.textbox_nomes.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Botões
        botoes_frame = ctk.CTkFrame(main_frame)
        botoes_frame.pack(fill="x", padx=10, pady=10)
        
        btn_limpar = ctk.CTkButton(
            botoes_frame,
            text="🧹 Limpar",
            command=self.limpar_lote,
            width=140,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#808080",
            hover_color="#696969"
        )
        btn_limpar.pack(side="left", padx=(20, 15), pady=15)
        
        btn_processar = ctk.CTkButton(
            botoes_frame,
            text="✅ Processar Lote",
            command=self.processar_lote_dados,
            width=170,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2E8B57",
            hover_color="#228B22"
        )
        btn_processar.pack(side="right", padx=(15, 15), pady=15)
        
        btn_cancelar = ctk.CTkButton(
            botoes_frame,
            text="❌ Cancelar",
            command=self.fechar_janela_lote,
            width=140,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#DC143C",
            hover_color="#B22222"
        )
        btn_cancelar.pack(side="right", padx=15, pady=15)
    
    def limpar_lote(self):
        self.textbox_chaves.delete("0.0", "end")
        self.textbox_nomes.delete("0.0", "end")
        self.textbox_chaves.focus()
    
    def fechar_janela_lote(self):
        self.janela_lote.destroy()
    
    def processar_lote_dados(self):
        try:
            # Obter textos das textboxes
            texto_chaves = self.textbox_chaves.get("0.0", "end").strip()
            texto_nomes = self.textbox_nomes.get("0.0", "end").strip()
            
            if not texto_chaves or not texto_nomes:
                messagebox.showwarning("Aviso", "Preencha ambos os campos!")
                return
            
            # Dividir em linhas
            linhas_chaves = [linha.strip() for linha in texto_chaves.split('\n') if linha.strip()]
            linhas_nomes = [linha.strip() for linha in texto_nomes.split('\n') if linha.strip()]
            
            # Validar quantidade de linhas
            if len(linhas_chaves) != len(linhas_nomes):
                messagebox.showerror("Erro", f"Quantidade de linhas diferente!\n\nChaves: {len(linhas_chaves)} linhas\nNomes: {len(linhas_nomes)} linhas\n\nCada chave deve ter um nome correspondente.")
                return
            
            # Validar chaves (usando função auxiliar - elimina duplicação)
            chaves_validas = []
            for i, chave_original in enumerate(linhas_chaves):
                chave = chave_original.strip()
                if not self.validar_chave_nfe(chave):
                    messagebox.showerror("Erro", f"Chave inválida na linha {i+1}:\n{chave_original}\n\nChaves devem ter exatamente 44 dígitos numéricos.")
                    return
                chaves_validas.append(chave)
            
            # Limpar tabela atual
            for linha in self.linhas_renomeacao:
                linha['frame'].destroy()
            self.linhas_renomeacao.clear()
            
            # Adicionar dados processados
            for chave, nome in zip(chaves_validas, linhas_nomes):
                self.adicionar_linha_renomeacao()
                ultima_linha = self.linhas_renomeacao[-1]
                
                # Preencher campos
                ultima_linha['chave'].delete(0, 'end')
                ultima_linha['chave'].insert(0, chave)
                ultima_linha['nome'].delete(0, 'end')
                ultima_linha['nome'].insert(0, nome)
            
            # Log
            total_processado = len(chaves_validas)
            self.log_renomeacao.insert("end", f"\n📋 LOTE DE DADOS PROCESSADO:\n")
            self.log_renomeacao.insert("end", f"✅ {total_processado} registros adicionados\n")
            self.log_renomeacao.insert("end", "🔍 Iniciando escaneamento automático...\n")
            self.log_renomeacao.see("end")
            
            # Fechar janela
            self.janela_lote.destroy()
            
            # Mudar para a aba de renomeação
            self.tabview.set("📋 Renomeação Inteligente")
            
            # Executar escaneamento automático das chaves
            self.executar_thread_segura(self.escanear_chaves_automatico)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar lote: {str(e)}")

    def escanear_chaves_automatico(self):
        """Função para escanear chaves automaticamente após processar lote"""
        pasta = self.entrada_pasta_renomear.get()
        
        # Se não há pasta selecionada, solicitar seleção
        if not pasta:
            def solicitar_pasta():
                messagebox.showinfo("Pasta Necessária", "Selecione a pasta com os arquivos XML para continuar o escaneamento.")
                self.selecionar_pasta_renomear()
                
                # Verificar se pasta foi selecionada
                pasta_selecionada = self.entrada_pasta_renomear.get()
                if pasta_selecionada:
                    # Executar escaneamento em thread
                    self.executar_thread_segura(self.escanear_chaves_xml_completo)
            
            self.root.after(0, solicitar_pasta)
            return
        
        # Executar escaneamento completo
        self.escanear_chaves_xml_completo()

    def escanear_chaves_xml_completo(self):
        """Função completa de escaneamento com melhor feedback para XMLs e PDFs"""
        pasta = self.entrada_pasta_renomear.get()
        if not pasta:
            def mostrar_erro():
                messagebox.showerror("Erro", "Selecione a pasta com XMLs primeiro!")
            
            self.root.after(0, mostrar_erro)
            return
            
        self.chaves_xml = {}
        self.associacoes_pdf = {}
        arquivos_processados = 0
        pdfs_encontrados = 0
        
        # Log inicial
        def log_inicial():
            self.log_renomeacao.insert("end", "\n🔍 ESCANEANDO XMLs E PDFs...\n")
            self.log_renomeacao.see("end")
        
        self.root.after(0, log_inicial)
        
        # Escanear arquivos XML e PDF
        arquivos = self.escanear_arquivos_pasta(pasta)
        
        if not arquivos['xml']:
            def mostrar_erro_xml():
                self.log_renomeacao.insert("end", "❌ Nenhum arquivo XML encontrado na pasta!\n")
                self.log_renomeacao.see("end")
                messagebox.showerror("Erro", "Nenhum arquivo XML encontrado na pasta selecionada!")
            
            self.root.after(0, mostrar_erro_xml)
            return
        
        try:
            log_buffer = []
            log_buffer.append(f"📁 Encontrados: {len(arquivos['xml'])} XMLs, {len(arquivos['pdf'])} PDFs\n\n")
            
            # Associar XMLs com PDFs
            self.associacoes_pdf = self.associar_xml_pdf(pasta)
            
            for chave, dados in self.associacoes_pdf.items():
                xml_path = dados['xml']
                pdf_path = dados['pdf']
                nome_xml = os.path.basename(xml_path)
                
                self.chaves_xml[chave] = xml_path
                arquivos_processados += 1
                
                if pdf_path:
                    nome_pdf = os.path.basename(pdf_path)
                    log_buffer.append(f"✅ {nome_xml} + {nome_pdf}: {chave}\n")
                    pdfs_encontrados += 1
                else:
                    log_buffer.append(f"⚠️ {nome_xml} (sem PDF): {chave}\n")
            
            # Log final
            log_buffer.extend([
                f"\n📊 ESCANEAMENTO CONCLUÍDO:\n",
                f"✅ {arquivos_processados} chaves mapeadas\n",
                f"📄 {pdfs_encontrados} PDFs associados aos XMLs\n",
                f"🎯 Pronto para renomeação de XMLs e PDFs!\n"
            ])
            
            # Atualizar interface
            def atualizar_interface():
                for log in log_buffer:
                    self.log_renomeacao.insert("end", log)
                self.log_renomeacao.see("end")
                
                # Mostrar mensagem de sucesso
                if arquivos_processados > 0:
                    pdf_msg = f"\n📄 {pdfs_encontrados} PDFs serão renomeados junto" if pdfs_encontrados > 0 else "\n⚠️ Nenhum PDF associado encontrado"
                    messagebox.showinfo("Sucesso!", f"✅ Escaneamento concluído!\n\n🔑 {arquivos_processados} chaves encontradas{pdf_msg}\n\nAgora use 'VALIDAR E RENOMEAR' para processar tudo!")
                else:
                    messagebox.showwarning("Aviso", "Nenhuma chave de acesso foi encontrada nos arquivos XML!")
            
            self.root.after(0, atualizar_interface)
            
        except Exception as e:
            def mostrar_erro_escaneamento():
                error_msg = f"❌ Erro ao escanear: {str(e)}\n"
                self.log_renomeacao.insert("end", error_msg)
                self.log_renomeacao.see("end")
                messagebox.showerror("Erro", f"Erro durante o escaneamento: {str(e)}")
            
            self.root.after(0, mostrar_erro_escaneamento)

    def executar(self):
        # Configurar controles de janela
        self.root.protocol("WM_DELETE_WINDOW", self.fechar_aplicacao)
        
        # Configurar título
        self.root.title("⚕️ renamerPRO©")
        
        print("🖥️ Aplicação iniciada")
        

        
        self.root.mainloop()
    
    def fechar_aplicacao(self):
        """Fecha a aplicação com cleanup adequado"""
        try:
            # Fechar aplicação
            self.root.quit()
            print("👋 Aplicação fechada com sucesso")
            
        except Exception as e:
            print(f"❌ Erro ao fechar aplicação: {e}")
            self.root.quit()



if __name__ == "__main__":
    app = DanfeAppMassa()
    app.executar()
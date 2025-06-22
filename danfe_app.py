import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import sys
import threading
import webbrowser
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed


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
        self.root.title("⚕️ renamerPRO© - Hospital Israelita Albert Einstein")
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
        
        # Detectar se está executando como executável empacotado
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.getcwd()
        
        self.php_path = os.path.join(base_path, "php-8.4.8-nts-Win32-vs17-x64", "php.exe")
        
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
            text="⚕️ renamerPRO© - Hospital Albert Einstein",
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
            "📋 Renomeação Inteligente por Chave de Acesso",
            "Sistema avançado para renomeação e processamento de documentos fiscais"
        )
        header_card.pack(fill="x", pady=0, padx=5)
        
        # Configuração
        config_frame = ctk.CTkFrame(header_card, fg_color="transparent")
        config_frame.pack(fill="x", padx=12, pady=12)
        config_frame.grid_columnconfigure(0, weight=1)
        
        pasta_label = ctk.CTkLabel(
            config_frame,
            text="📁 Diretório de Documentos XML:",
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
            placeholder_text="Selecione o diretório contendo os arquivos XML...",
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
        
        # Primeira linha de botões
        linha1 = ctk.CTkFrame(botoes_container, fg_color="transparent")
        linha1.pack(fill="x", pady=(0, 8))
        
        self.btn_escanear_chaves = self.criar_botao_profissional(
            linha1,
            "ESCANEAR CHAVES",
            self.escanear_chaves_xml,
            width=150,
            height=40,
            cor_principal=self.cores['laranja_warning'],
            cor_hover="#E5A500",
            icone="🔍"
        )
        self.btn_escanear_chaves.pack(side="left", padx=(0, 8))
        
        self.btn_adicionar_linha = self.criar_botao_profissional(
            linha1,
            "NOVA LINHA",
            self.adicionar_linha_renomeacao,
            width=130,
            height=40,
            cor_principal=self.cores['azul_accent'],
            cor_hover="#0066CC",
            icone="➕"
        )
        self.btn_adicionar_linha.pack(side="left", padx=8)
        
        self.btn_lote_dados = self.criar_botao_profissional(
            linha1,
            "LOTE DE DADOS",
            self.abrir_janela_lote,
            width=150,
            height=40,
            cor_principal="#6C757D",
            cor_hover="#5A6268",
            icone="📋"
        )
        self.btn_lote_dados.pack(side="left", padx=8)
        
        self.btn_limpar_dados = self.criar_botao_profissional(
            linha1,
            "LIMPAR",
            self.limpar_dados_massa,
            width=100,
            height=40,
            cor_principal="#6C757D",
            cor_hover="#5A6268",
            icone="🧹"
        )
        self.btn_limpar_dados.pack(side="left", padx=8)
        
        # Segunda linha de botões (ações principais)
        linha2 = ctk.CTkFrame(botoes_container, fg_color="transparent")
        linha2.pack(fill="x")
        
        self.btn_validar_renomear = self.criar_botao_profissional(
            linha2,
            "VALIDAR E RENOMEAR",
            self.validar_e_renomear_thread,
            width=180,
            height=40,
            cor_principal=self.cores['verde_success'],
            cor_hover="#218838",
            icone="✅"
        )
        self.btn_validar_renomear.pack(side="right", padx=(8, 0))
        
        self.btn_processar_selecionados = self.criar_botao_profissional(
            linha2,
            "PROCESSAR TODOS",
            self.processar_selecionados_thread,
            width=180,
            height=40,
            cor_principal=self.cores['azul_primary'],
            cor_hover=self.cores['azul_secondary'],
            icone="⚡"
        )
        self.btn_processar_selecionados.pack(side="right", padx=8)
        
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
📋 Aguardando configuração de diretório...
💡 Selecione o diretório e escaneie as chaves para começar.""")

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
        pasta = self.entrada_pasta_renomear.get()
        if not pasta:
            messagebox.showerror("Erro", "Selecione a pasta com XMLs primeiro!")
            return
            
        self.chaves_xml = {}
        arquivos_processados = 0
        
        self.log_renomeacao.delete("0.0", "end")
        self.log_renomeacao.insert("0.0", "🔍 Escaneando chaves de acesso...\n\n")
        
        # Usar função auxiliar (elimina duplicação)
        arquivos_xml = self.escanear_xmls_pasta(pasta)
        
        try:
            for arquivo in arquivos_xml:
                nome_arquivo = os.path.basename(arquivo)
                chave = self.extrair_chave_xml(arquivo)
                
                if chave:
                    self.chaves_xml[chave] = arquivo
                    arquivos_processados += 1
                    self.log_renomeacao.insert("end", f"✅ {nome_arquivo}: {chave}\n")
                else:
                    self.log_renomeacao.insert("end", f"❌ {nome_arquivo}: Chave não encontrada\n")
                        
            self.log_renomeacao.insert("end", f"\n📊 Total: {arquivos_processados} chaves mapeadas\n")
            self.log_renomeacao.insert("end", "✅ Escaneamento concluído! Agora preencha as chaves desejadas.\n")
            
        except Exception as e:
            self.log_renomeacao.insert("end", f"❌ Erro ao escanear: {str(e)}\n")
            
        self.log_renomeacao.see("end")
        
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
        # Usar função auxiliar (elimina duplicação)
        self.executar_thread_segura(self.validar_e_renomear)
        
    def validar_e_renomear(self):
        pasta = self.entrada_pasta_renomear.get()
        if not pasta:
            messagebox.showerror("Erro", "Selecione a pasta primeiro!")
            return
            
        if not self.chaves_xml:
            messagebox.showerror("Erro", "Escaneie as chaves primeiro!")
            return
            
        sucessos = 0
        erros = 0
        
        self.root.after(0, lambda: self.log_renomeacao.insert("end", "\n🚀 INICIANDO VALIDAÇÃO E RENOMEAÇÃO...\n\n"))
        
        for linha in self.linhas_renomeacao:
            chave_original = linha['chave'].get().strip()
            nome_final = linha['nome'].get().strip()
            
            if not chave_original or not nome_final:
                continue
                
            chave = chave_original.strip()
            
            # Validar chave (usando função auxiliar - elimina duplicação)
            if not self.validar_chave_nfe(chave):
                self.root.after(0, lambda l=linha: l['status'].configure(text="❌ Chave"))
                self.root.after(0, lambda c=chave: self.log_renomeacao.insert("end", f"❌ Chave inválida: {c}\n"))
                erros += 1
                continue
                
            # Verificar se chave existe
            if chave not in self.chaves_xml:
                self.root.after(0, lambda l=linha: l['status'].configure(text="❌ N/Existe"))
                self.root.after(0, lambda c=chave: self.log_renomeacao.insert("end", f"❌ Chave não encontrada: {c}\n"))
                erros += 1
                continue
                
            # Renomear arquivo
            try:
                arquivo_original = self.chaves_xml[chave]
                pasta_arquivo = os.path.dirname(arquivo_original)
                novo_nome = os.path.join(pasta_arquivo, f"{nome_final}.xml")
                
                if os.path.exists(novo_nome):
                    self.root.after(0, lambda l=linha: l['status'].configure(text="❌ Existe"))
                    self.root.after(0, lambda n=nome_final: self.log_renomeacao.insert("end", f"❌ Arquivo já existe: {n}.xml\n"))
                    erros += 1
                    continue
                    
                os.rename(arquivo_original, novo_nome)
                self.root.after(0, lambda l=linha: l['status'].configure(text="✅ OK"))
                self.root.after(0, lambda o=os.path.basename(arquivo_original), n=nome_final: 
                              self.log_renomeacao.insert("end", f"✅ {o} → {n}.xml\n"))
                sucessos += 1
                
                # Atualizar o dicionário
                self.chaves_xml[chave] = novo_nome
                
            except Exception as e:
                self.root.after(0, lambda l=linha: l['status'].configure(text="❌ Erro"))
                self.root.after(0, lambda e=str(e): self.log_renomeacao.insert("end", f"❌ Erro: {e}\n"))
                erros += 1
                
        self.root.after(0, lambda: self.log_renomeacao.insert("end", f"\n🎉 RENOMEAÇÃO CONCLUÍDA!\n"))
        self.root.after(0, lambda: self.log_renomeacao.insert("end", f"✅ Sucessos: {sucessos}\n"))
        self.root.after(0, lambda: self.log_renomeacao.insert("end", f"❌ Erros: {erros}\n"))
        self.root.after(0, lambda: self.log_renomeacao.see("end"))
        
        if sucessos > 0:
            messagebox.showinfo("Concluído!", f"Renomeação finalizada!\n\n✅ {sucessos} arquivos renomeados\n❌ {erros} erros")
    
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
    
    def processar_selecionados_thread(self):
        if self.processando:
            return
        
        # Usar função auxiliar (elimina duplicação)
        self.executar_thread_segura(self.processar_selecionados)
    
    def processar_selecionados(self):
        pasta_xml = self.entrada_pasta_renomear.get()
        
        if not pasta_xml:
            messagebox.showerror("Erro", "Selecione a pasta com XMLs primeiro!")
            return
        
        # Escanear TODOS os XMLs da pasta (usando função auxiliar - elimina duplicação)
        todos_xmls = self.escanear_xmls_pasta(pasta_xml)
        
        if not todos_xmls:
            messagebox.showerror("Erro", "Nenhum arquivo XML encontrado na pasta!")
            return
        
        # Determinar pasta de saída
        pasta_saida = self.entrada_pasta_renomear.get()  # Usar a mesma pasta por padrão
        
        self.processando = True
        total = len(todos_xmls)
        sucessos = 0
        erros = 0
        
        self.root.after(0, lambda: self.btn_processar_selecionados.configure(state="disabled", text="🔄 Processando..."))
        self.root.after(0, lambda: self.btn_validar_renomear.configure(state="disabled"))
        
        self.root.after(0, lambda: self.log_renomeacao.insert("end", f"\n🚀 PROCESSANDO TODOS OS XMLs DA PASTA:\n"))
        self.root.after(0, lambda: self.log_renomeacao.insert("end", f"📊 Total: {total} arquivos\n"))
        self.root.after(0, lambda: self.log_renomeacao.insert("end", f"📤 Pasta saída: {pasta_saida}\n\n"))
        
        inicio = time.time()
        
        # Processar com função auxiliar (elimina duplicação)
        def callback_sucesso(nome):
            self.log_renomeacao.insert("end", f"✅ {nome}\n")
            
        def callback_erro(nome):
            self.log_renomeacao.insert("end", f"❌ {nome}\n")
            
        sucessos, erros, tempo_total = self.processar_xmls_paralelo(
            todos_xmls, pasta_saida, callback_sucesso, callback_erro
        )
        
        self.root.after(0, lambda: self.log_renomeacao.insert("end", f"\n🎉 PROCESSAMENTO CONCLUÍDO!\n"))
        self.root.after(0, lambda: self.log_renomeacao.insert("end", f"✅ PDFs criados: {sucessos}\n"))
        self.root.after(0, lambda: self.log_renomeacao.insert("end", f"❌ Erros: {erros}\n"))
        self.root.after(0, lambda: self.log_renomeacao.insert("end", f"⏱️ Tempo total: {tempo_total:.1f} segundos\n"))
        
        self.root.after(0, lambda: self.btn_processar_selecionados.configure(state="normal", text="🎯 PROCESSAR TODOS XMLs"))
        self.root.after(0, lambda: self.btn_validar_renomear.configure(state="normal"))
        self.root.after(0, lambda: self.log_renomeacao.see("end"))
        
        # Usar função auxiliar (elimina duplicação)
        self.mostrar_conclusao_processamento(sucessos, erros, tempo_total, pasta_saida)
        
        self.processando = False
        
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
        """Função auxiliar para processamento paralelo (elimina duplicação)"""
        sucessos = 0
        erros = 0
        inicio = time.time()
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self.processar_xml_individual, arquivo, pasta_saida): arquivo 
                for arquivo in arquivos_xml
            }
            
            for future in as_completed(futures):
                arquivo = futures[future]
                nome_arquivo = os.path.basename(arquivo)
                
                try:
                    resultado = future.result()
                    if resultado:
                        sucessos += 1
                        if callback_sucesso:
                            self.root.after(0, lambda n=nome_arquivo: callback_sucesso(n))
                    else:
                        erros += 1
                        if callback_erro:
                            self.root.after(0, lambda n=nome_arquivo: callback_erro(n))
                except Exception as e:
                    erros += 1
                    if callback_erro:
                        self.root.after(0, lambda n=nome_arquivo, e=str(e): callback_erro(f"{n} - ERRO: {e}"))
        
        tempo_total = time.time() - inicio
        return sucessos, erros, tempo_total

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
        log_inicial = """⚕️ Hospital Israelita Albert Einstein - renamerPRO©
        
🔹 Sistema inicializado com sucesso
🔹 Aguardando configuração de pastas...
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
        
        # Processar com função auxiliar (elimina duplicação)
        def callback_sucesso(nome):
            nonlocal sucessos
            sucessos += 1
            self.adicionar_log(f"✅ {nome}")
            self.progresso_geral.set(sucessos / total)
            self.label_progresso.configure(text=f"{sucessos} / {total} arquivos processados")
            
        def callback_erro(nome):
            nonlocal erros
            erros += 1
            self.adicionar_log(f"❌ {nome}")
            processados = sucessos + erros
            self.progresso_geral.set(processados / total)
            self.label_progresso.configure(text=f"{processados} / {total} arquivos processados")
            
        sucessos, erros, tempo_total = self.processar_xmls_paralelo(
            self.arquivos_xml, pasta_saida, callback_sucesso, callback_erro
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
    

        
    def processar_xml_individual(self, arquivo_xml, pasta_saida):
        try:
            # Detectar se está executando como executável empacotado
            if getattr(sys, 'frozen', False):
                # Executável empacotado - arquivos estão em _MEIPASS
                base_path = sys._MEIPASS
            else:
                # Script Python normal
                base_path = os.getcwd()
            
            script_php = os.path.join(base_path, "gerador_danfe.php")
            cmd = [self.php_path, script_php, arquivo_xml]
            
            # Executar PHP sem abrir janela CMD (silencioso)
            resultado = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                cwd=base_path,
                creationflags=subprocess.CREATE_NO_WINDOW  # Não abrir janela CMD
            )
            
            if resultado.returncode == 0 and "SUCCESS:" in resultado.stdout:
                arquivo_pdf = resultado.stdout.strip().replace("SUCCESS:", "")
                
                if pasta_saida != os.path.dirname(arquivo_xml):
                    nome_pdf = os.path.basename(arquivo_pdf)
                    novo_caminho = os.path.join(pasta_saida, nome_pdf)
                    
                    if os.path.exists(arquivo_pdf):
                        os.rename(arquivo_pdf, novo_caminho)
                
                return True
            else:
                return False
                
        except Exception:
            return False
            
    def abrir_janela_lote(self):
        # Criar janela popup
        self.janela_lote = ctk.CTkToplevel(self.root)
        self.janela_lote.title("📋 Adicionar Lote de Dados")
        self.janela_lote.geometry("1200x900")
        self.janela_lote.minsize(1000, 600)
        self.janela_lote.transient(self.root)
        self.janela_lote.grab_set()
        
        # Título
        titulo = ctk.CTkLabel(
            self.janela_lote,
            text="📋 Adicionar Lote de Dados",
            font=ctk.CTkFont(size=26, weight="bold")
        )
        titulo.pack(pady=25)
        
        # Instrução
        instrucao = ctk.CTkLabel(
            self.janela_lote,
            text="Preencha os campos abaixo. Use uma linha por registro:",
            font=ctk.CTkFont(size=14)
        )
        instrucao.pack(pady=(0, 20))
        
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
            self.log_renomeacao.insert("end", "💡 Clique em 'ESCANEAR CHAVES' para validar\n")
            self.log_renomeacao.see("end")
            
            # Fechar janela
            self.janela_lote.destroy()
            
            messagebox.showinfo("Sucesso!", f"✅ {total_processado} registros adicionados com sucesso!\n\nAgora escaneie as chaves para validar.")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar lote: {str(e)}")


    def executar(self):
        # Configurar controles de janela
        self.root.protocol("WM_DELETE_WINDOW", self.fechar_aplicacao)
        
        # Configurar título
        self.root.title("⚕️ renamerPRO© - Hospital Israelita Albert Einstein")
        
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


"""
===============================================================================
📋 DOCUMENTAÇÃO - SISTEMA LIVE PREVIEW
Hospital Israelita Albert Einstein - renamerPRO©
===============================================================================

🔴 LIVE PREVIEW SYSTEM - MONITORAMENTO EM TEMPO REAL
----------------------------------------------------

O Sistema Live Preview utiliza a biblioteca 'watchdog' para monitorar mudanças
em tempo real nos arquivos XML e PDF, proporcionando uma experiência dinâmica
e profissional ao usuário.

📁 ARQUIVOS DO SISTEMA:
-----------------------
• live_preview.py          - Módulo principal do watchdog
• danfe_app.py             - Aplicação principal com integração
• exemplo_live_preview.py  - Exemplo standalone para testes
• requirements.txt         - Dependências (inclui watchdog>=3.0.0)

🚀 FUNCIONALIDADES PRINCIPAIS:
------------------------------

1. 🔍 MONITORAMENTO AUTOMÁTICO:
   • Detecta arquivos criados, modificados, excluídos e movidos
   • Filtra apenas arquivos .xml e .pdf
   • Debounce de 1 segundo para evitar spam de eventos
   • Monitoramento recursivo de subpastas

2. 📊 INTERFACE INTEGRADA:
   • Checkbox "🔴 Ativar Live Preview" na aba principal
   • Status em tempo real com contadores de pastas e eventos
   • Logs coloridos com timestamp no formato [HH:MM:SS]
   • Auto-ativação quando seleciona pasta XML

3. ⚡ PROCESSAMENTO AUTOMÁTICO:
   • Checkbox "⚡ Auto-processar novos XMLs"
   • Processa automaticamente novos arquivos XML detectados
   • Atualiza contagem de arquivos em tempo real
   • Re-escaneia chaves da aba de renomeação automaticamente

4. 🛠️ GERENCIAMENTO PROFISSIONAL:
   • Cleanup automático ao fechar aplicação
   • Múltiplas pastas monitoradas simultaneamente
   • Tratamento robusto de erros e exceções
   • Threads separadas para não bloquear interface

🎯 COMO USAR O LIVE PREVIEW:
---------------------------

1. INSTALAÇÃO:
   pip install -r requirements.txt

2. ATIVAÇÃO NA APLICAÇÃO:
   • Abra o renamerPRO©
   • Selecione uma pasta XML
   • Marque "🔴 Ativar Live Preview"
   • Opcionalmente marque "⚡ Auto-processar novos XMLs"

3. FUNCIONAMENTO:
   • Adicione/modifique/remova arquivos XML na pasta monitorada
   • Observe os logs em tempo real na interface
   • Arquivos novos são processados automaticamente (se habilitado)
   • Contagem de arquivos é atualizada instantaneamente

4. TESTE ISOLADO:
   python exemplo_live_preview.py

📋 LOGS DO LIVE PREVIEW:
-----------------------

Formato dos logs: [ÍCONE] [TIMESTAMP] LIVE: arquivo.xml - AÇÃO

Ícones por tipo de evento:
🟢 - Arquivo criado
🟡 - Arquivo modificado  
🔴 - Arquivo excluído
🔵 - Arquivo movido
⚪ - Outros eventos

Exemplo de logs:
[14:25:30] 🟢 LIVE: nota_fiscal_001.xml - CRIADO
[14:25:31] ⚡ AUTO-PROCESSANDO: nota_fiscal_001.xml
[14:25:32] ✅ AUTO-SUCESSO: nota_fiscal_001.xml

🔧 CONFIGURAÇÕES TÉCNICAS:
-------------------------

• Debounce Timer: 1.0 segundo (evita múltiplas atualizações)
• Max Workers: 5 threads paralelas para processamento
• Monitoring: Recursivo (inclui subpastas)
• File Types: .xml, .pdf
• Thread Safety: Interface atualizada via root.after()

⚙️ CLASSES PRINCIPAIS:
---------------------

1. LivePreviewHandler(FileSystemEventHandler):
   • Handler principal para eventos do watchdog
   • Processa eventos com debounce
   • Atualiza interface de forma thread-safe

2. LivePreviewManager:
   • Gerenciador principal do sistema
   • Controla Observer do watchdog
   • Mantém estado de pastas monitoradas

3. Integração na DanfeAppMassa:
   • self.live_preview: instância do LivePreviewManager
   • self.live_preview_ativo: BooleanVar para controle
   • self.auto_processar: BooleanVar para processamento automático

🐛 TROUBLESHOOTING:
------------------

1. ERRO: "Pasta não existe"
   → Verifique se o caminho da pasta está correto

2. ERRO: "Falha ao ativar Live Preview" 
   → Verifique permissões da pasta
   → Tente reiniciar a aplicação

3. PERFORMANCE: Muitos eventos
   → Live Preview usa debounce de 1s
   → Eventos são processados em batch

4. MEMÓRIA: Uso excessivo
   → Live Preview limpa automaticamente
   → Observer é finalizado corretamente

📊 STATUS DO SISTEMA:
--------------------

Status possíveis:
🔴 Inativo                    - Live Preview desabilitado
🟢 Ativo - X pasta(s) - Y eventos - Funcionando normalmente

🏥 BOAS PRÁTICAS:
-----------------

1. PERFORMANCE:
   • Monitore apenas pastas necessárias
   • Use auto-processamento com moderação
   • Feche aplicação adequadamente para cleanup

2. SEGURANÇA:
   • Não monitore pastas do sistema
   • Verifique permissões antes de ativar
   • Mantenha backups dos arquivos importantes

3. PRODUÇÃO:
   • Teste em ambiente controlado primeiro
   • Configure logs adequadamente
   • Monitore uso de recursos

💡 DICAS AVANÇADAS:
------------------

• Para múltiplas pastas: Use live_preview.adicionar_pasta(nova_pasta)
• Para reiniciar: Use live_preview.reiniciar() 
• Para status: Use live_preview.obter_status()
• Para parar: Use live_preview.parar_monitoramento()

🎉 BENEFÍCIOS DO LIVE PREVIEW:
-----------------------------

✅ Experiência de usuário dinâmica e moderna
✅ Processamento automático de novos arquivos  
✅ Feedback visual imediato das mudanças
✅ Redução de cliques e operações manuais
✅ Monitoramento profissional de arquivos
✅ Integração transparente com workflow existente

===============================================================================
🏥 Hospital Israelita Albert Einstein - Departamento de TI
📧 Sistema desenvolvido com as melhores práticas médicas e tecnológicas
⚕️ "Excelência em Tecnologia da Informação Hospitalar"
===============================================================================
""" 

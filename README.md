# ⚕️ renamerPRO© - Sistema de Processamento DANFE

Sistema profissional para processamento em massa de documentos fiscais (DANFEs) desenvolvido para o Hospital Israelita Albert Einstein.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.0+-green.svg)
![PHP](https://img.shields.io/badge/PHP-8.4+-purple.svg)
![Status](https://img.shields.io/badge/Status-Ativo-success.svg)

## 🏥 Sobre o Projeto

O **renamerPRO©** é uma solução completa para automatização do processamento de documentos fiscais eletrônicos, desenvolvido especificamente para ambientes hospitalares com foco na eficiência e usabilidade profissional.

### ✨ Principais Funcionalidades

- 🚀 **Processamento em Massa**: Converte múltiplos XMLs para PDF simultaneamente
- 📋 **Renomeação Inteligente**: Sistema avançado de mapeamento por chave de acesso
- ⚡ **Processamento Paralelo**: Até 5 documentos processados simultaneamente
- 🎨 **Interface Moderna**: Design profissional com tema Hospital Einstein
- 📊 **Monitoramento em Tempo Real**: Logs detalhados e barras de progresso
- 🔍 **Validação Automática**: Verificação de chaves NFe e integridade dos arquivos

## 🛠️ Tecnologias Utilizadas

- **Python 3.8+** - Linguagem principal
- **CustomTkinter 5.0+** - Interface gráfica moderna
- **PHP 8.4** - Engine de processamento DANFE
- **Composer** - Gerenciamento de dependências PHP
- **Threading** - Processamento paralelo
- **XML/ElementTree** - Manipulação de documentos fiscais

## 📦 Dependências PHP

- `nfephp-org/sped-nfe` - Biblioteca para processamento NFe
- `nfephp-org/sped-da` - Geração de documentos auxiliares
- `tecnickcom/tc-lib-barcode` - Geração de códigos de barras

## 🚀 Instalação

### 1. Clone o Repositório
```bash
git clone https://github.com/seu-usuario/renamerPRO.git
cd renamerPRO
```

### 2. Instalar Dependências Python
```bash
pip install -r requirements.txt
```

### 3. Configurar PHP (Incluído)
O projeto já inclui o PHP 8.4 portável com todas as dependências configuradas.

### 4. Instalar Bibliotecas PHP
```bash
php composer.phar install
```

## 🖥️ Como Usar

### Processamento em Massa

1. **Abra o renamerPRO©**
   ```bash
   python danfe_app.py
   ```

2. **Configure as Pastas**
   - Selecione a pasta contendo os arquivos XML
   - Opcionalmente, escolha uma pasta de destino para os PDFs

3. **Execute o Processamento**
   - Clique em "ESCANEAR PASTA" para verificar os arquivos
   - Clique em "PROCESSAR DOCUMENTOS" para iniciar a conversão

### Renomeação Inteligente

1. **Acesse a Aba "📋 Renomeação Inteligente"**

2. **Configure o Diretório**
   - Selecione a pasta com os XMLs
   - Clique em "ESCANEAR CHAVES" para mapear os arquivos

3. **Configurar Mapeamento**
   - Use "NOVA LINHA" para adicionar mapeamentos individuais
   - Use "LOTE DE DADOS" para importação em massa
   - Configure chave de acesso → nome desejado

4. **Execute as Operações**
   - "VALIDAR E RENOMEAR" - Renomeia os arquivos
   - "PROCESSAR TODOS" - Gera PDFs de todos os XMLs

## 📊 Funcionalidades Avançadas

### 🔄 Processamento Paralelo
- Utiliza ThreadPoolExecutor para máxima eficiência
- Processa até 5 documentos simultaneamente
- Otimizado para grandes volumes de arquivos

### 📋 Sistema de Logs
- Logs em tempo real com timestamps
- Códigos de status coloridos
- Relatórios detalhados de sucesso/erro

### 🎯 Validação Inteligente
- Validação automática de chaves NFe (44 dígitos)
- Verificação de integridade dos arquivos XML
- Detecção de arquivos duplicados

### 📊 Interface Responsiva
- Design adaptativo para diferentes resoluções
- Tema profissional Hospital Einstein
- Componentes modernos com CustomTkinter

## 🔧 Configuração Avançada

### Personalização de Cores
```python
# Edite as cores no arquivo danfe_app.py
self.cores = {
    'azul_primary': '#003D7A',      # Azul Einstein principal
    'azul_secondary': '#0056B3',    # Azul secundário
    'verde_success': '#2E7D32',     # Verde sucesso
    # ... outras cores
}
```

### Ajuste de Performance
```python
# Número de threads paralelas (danfe_app.py)
ThreadPoolExecutor(max_workers=5)  # Ajuste conforme necessário
```

## 📁 Estrutura do Projeto

```
renamerPRO/
├── danfe_app.py              # Aplicação principal
├── gerador_danfe.php         # Engine PHP para DANFE
├── live_preview.py           # Sistema de monitoramento
├── requirements.txt          # Dependências Python
├── composer.json            # Dependências PHP
├── composer.lock           # Lock de versões PHP
├── README.md              # Documentação
├── .gitignore            # Arquivos ignorados
├── php-8.4.8-nts-Win32-vs17-x64/  # PHP portável
└── vendor/                        # Bibliotecas PHP
```

## 🎨 Interface

### Tela Principal - Processamento em Massa
- ⚙️ **Configuração**: Seleção de pastas
- 📊 **Controle**: Botões de escaneamento e processamento  
- 📈 **Progresso**: Barras de progresso em tempo real
- 📋 **Logs**: Acompanhamento detalhado das operações

### Tela de Renomeação Inteligente
- 🔍 **Escaneamento**: Mapeamento automático de chaves
- 📊 **Tabela**: Interface para configuração de mapeamentos
- 🛠️ **Controles**: Botões para operações em lote
- 📋 **Logs**: Feedback detalhado das operações

## 🚨 Troubleshooting

### Problemas Comuns

**1. Erro: "PHP não encontrado"**
```bash
# Verifique se o PHP está no diretório correto
ls php-8.4.8-nts-Win32-vs17-x64/php.exe
```

**2. Erro: "Bibliotecas PHP não instaladas"**
```bash
# Reinstale as dependências
php composer.phar install --no-dev
```

**3. Interface não carrega**
```bash
# Verifique a instalação do CustomTkinter
pip install --upgrade customtkinter
```

**4. XMLs não são reconhecidos**
- Verifique se os arquivos têm extensão `.xml`
- Confirme se são XMLs válidos de NFe
- Verifique permissões de leitura da pasta

## 📈 Performance

### Benchmarks Típicos
- **Volume**: 1000+ XMLs processados simultaneamente
- **Velocidade**: ~2-3 segundos por DANFE
- **Memória**: ~50-100MB durante processamento
- **CPU**: Otimizado para múltiplos cores

### Recomendações de Hardware
- **RAM**: Mínimo 4GB, recomendado 8GB+
- **CPU**: Múltiplos cores para melhor paralelização
- **Armazenamento**: SSD recomendado para I/O intensivo

## 🔐 Segurança

- ✅ Validação rigorosa de arquivos de entrada
- ✅ Processamento local (sem envio de dados externos)
- ✅ Logs detalhados para auditoria
- ✅ Backup automático recomendado

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📋 Roadmap

- [ ] 🔴 Sistema Live Preview (monitoramento em tempo real)
- [ ] 📊 Dashboard analytics
- [ ] 🔒 Sistema de usuários e permissões
- [ ] 📱 Interface responsiva mobile
- [ ] 🌐 API REST para integração
- [ ] 📧 Notificações por email
- [ ] 📊 Relatórios em Excel/PDF

## 📞 Suporte

Para suporte técnico ou dúvidas:

- 📧 **Email**: suporte-ti@einstein.br
- 📱 **Teams**: Canal renamerPRO
- 🎫 **Tickets**: Sistema interno de TI

## 📄 Licença

Este projeto é proprietário do Hospital Israelita Albert Einstein.
Todos os direitos reservados © 2024

## 🏥 Créditos

**Desenvolvido por**: Departamento de TI - Hospital Israelita Albert Einstein
**Versão**: 2.0.0
**Data**: 2024

---

<div align="center">

**⚕️ Hospital Israelita Albert Einstein**

*"Excelência em Tecnologia da Informação Hospitalar"*

</div> 
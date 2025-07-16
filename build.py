#!/usr/bin/env python3
"""
Script de build para renamerPRO© Hospital Einstein
Empacota Python + PHP + dependências em um único executável
"""

import os
import shutil
import subprocess
import sys

def instalar_pyinstaller():
    """Instala PyInstaller se não estiver instalado"""
    try:
        import PyInstaller
        print("✅ PyInstaller já instalado")
    except ImportError:
        print("📦 Instalando PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def preparar_build():
    """Prepara ambiente para build"""
    print("🔧 Preparando ambiente de build...")
    
    # Criar diretório de build se não existir
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    print("✅ Ambiente preparado")

def criar_spec_file():
    """Cria arquivo .spec personalizado para o build"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['danfe_app.py'],
    pathex=[],
    binaries=[
        # Incluir todo o diretório PHP
        ('php/*', 'php/'),
        ('vendor/*', 'vendor/'),
    ],
    datas=[
        # Arquivos de dados necessários
        ('gerador_danfe.php', '.'),
        ('composer.json', '.'),
        ('requirements.txt', '.'),
        ('README.md', '.'),
    ],
    hiddenimports=[
        'customtkinter',
        'tkinter',
        'subprocess',
        'threading',
        'xml.etree.ElementTree',
        'concurrent.futures',
        'webbrowser',
        'time',
        'os',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='renamerPRO',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Interface gráfica, sem console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='einstein_icon.ico' if os.path.exists('einstein_icon.ico') else None,
)
'''
    
    with open('renamerPRO.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content.strip())
    
    print("✅ Arquivo .spec criado")

def executar_build():
    """Executa o build do executável"""
    print("🚀 Iniciando build do executável...")
    
    cmd = [
        "pyinstaller",
        "--clean",
        "--noconfirm",
        "renamerPRO.spec"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ Build concluído com sucesso!")
        
        # Verificar se executável foi criado
        exe_path = "dist/renamerPRO_Einstein.exe"
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"📁 Executável criado: {exe_path}")
            print(f"📊 Tamanho: {size_mb:.1f} MB")
        else:
            print("❌ Executável não foi encontrado")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro no build: {e}")
        return False
    
    return True

def criar_instalador():
    """Cria script de instalação/distribuição"""
    
    install_script = '''
@echo off
echo ===============================================
echo  renamerPRO© - Hospital Israelita Albert Einstein
echo  Sistema de Processamento de DANFEs
echo ===============================================
echo.

echo 📦 Verificando arquivos...
if not exist "renamerPRO_Einstein.exe" (
    echo ❌ Arquivo principal não encontrado!
    pause
    exit /b 1
)

echo ✅ Todos os arquivos encontrados
echo.
echo 🚀 Iniciando renamerPRO©...
echo.

start "" "renamerPRO_Einstein.exe"

echo ✅ Sistema iniciado com sucesso!
echo.
echo 💡 Dica: Crie um atalho na área de trabalho para acesso rápido
pause
'''
    
    with open('dist/Iniciar_renamerPRO.bat', 'w', encoding='utf-8') as f:
        f.write(install_script.strip())
    
    print("✅ Script de inicialização criado")

def main():
    """Função principal do build"""
    print("🏥 renamerPRO© Hospital Einstein - Build System")
    print("=" * 50)
    
    # Verificar se estamos no diretório correto
    if not os.path.exists('danfe_app.py'):
        print("❌ Execute este script no diretório do projeto!")
        return
    
    # Verificar dependências
    if not os.path.exists('php/php.exe'):
        print("❌ Diretório PHP não encontrado!")
        return
    
    if not os.path.exists('vendor'):
        print("❌ Dependências PHP não instaladas! Execute: composer install")
        return
    
    try:
        # Etapas do build
        instalar_pyinstaller()
        preparar_build()
        criar_spec_file()
        
        if executar_build():
            criar_instalador()
            
            print("\n🎉 BUILD CONCLUÍDO COM SUCESSO!")
            print("=" * 50)
            print("📁 Arquivos gerados em: dist/")
            print("🚀 Executável: dist/renamerPRO_Einstein.exe")
            print("▶️  Iniciar: dist/Iniciar_renamerPRO.bat")
            print("\n💡 O executável é portável e pode ser distribuído!")
        else:
            print("\n❌ Build falhou!")
            
    except Exception as e:
        print(f"\n❌ Erro durante o build: {e}")

if __name__ == "__main__":
    main() 
# -*- mode: python ; coding: utf-8 -*-
# macOS PyInstaller spec file
# 使用方式：pyinstaller Jar_Tools_mac.spec

block_cipher = None

a = Analysis(
    ['jar_tools_mac.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['requests', 'zipfile', 'shutil'],
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
    name='Jar_Tools',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,   # macOS 注意：保持 False
    target_arch=None,       # None = 当前架构；'x86_64' 或 'arm64' 可指定
    codesign_identity=None,
    entitlements_file=None,
)

# 可选：生成 .app bundle（双击运行）
app = BUNDLE(
    exe,
    name='Jar_Tools.app',
    icon=None,              # 可替换为 .icns 图标路径
    bundle_identifier='com.finereport.jartools',
    info_plist={
        'NSHighResolutionCapable': True,
        'CFBundleShortVersionString': '1.0.0',
    },
)

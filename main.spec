# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('src/config.json', '.'),
    ('src/cve_info/csv_data/keywords.csv', 'cve_info/csv_data'),
    ('src/news_info/csv_data/news_url.csv', 'news_info/csv_data'),
    ('src/news_info/csv_data/news_word.csv', 'news_info/csv_data'),
    ('src/news_info/csv_data/sent_articles.csv', 'news_info/csv_data')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from PyInstaller.utils.hooks import copy_metadata


project_root = Path.cwd()
site_packages = project_root / "runtime" / ".venv" / "Lib" / "site-packages"
streamlit_package = site_packages / "streamlit"

datas = copy_metadata("streamlit")
datas += [
    (str(streamlit_package / "static"), "streamlit/static"),
    (str(project_root / "runtime" / "__init__.py"), "runtime"),
    (str(project_root / "runtime" / "app"), "runtime/app"),
    (str(project_root / "runtime" / "assets"), "runtime/assets"),
    (str(project_root / "runtime" / "automations"), "runtime/automations"),
    (str(project_root / "runtime" / "core"), "runtime/core"),
    (str(project_root / ".streamlit"), ".streamlit"),
]

binaries = []

hiddenimports = [
    "streamlit.web.cli",
    "streamlit.runtime",
    "streamlit.config",
    "streamlit.delta_generator",
    "streamlit.components.v1",
    "streamlit.runtime.scriptrunner.magic",
    "streamlit.runtime.scriptrunner.magic_funcs",
    "streamlit.runtime.scriptrunner.script_runner",
    "streamlit.runtime.scriptrunner.script_cache",
    "streamlit.runtime.scriptrunner.exec_code",
    "watchdog.observers.winapi",
]

excludes = [
    "matplotlib",
    "pytest",
    "notebook",
    "jupyter",
    "IPython",
    "pywebview",
    "pythonnet",
    "clr_loader",
    "git",
    "gitdb",
]


a = Analysis(
    [str(project_root / "launcher.py")],
    pathex=[str(project_root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=1,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="DataPlatform",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    onefile=True,
)

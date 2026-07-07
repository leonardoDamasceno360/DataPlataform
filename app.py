"""
Arquivo wrapper para Streamlit Cloud deployment.
Executa a aplicação principal localizada em runtime/app/main.py
"""
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Importar e executar a aplicação principal
from runtime.app.main import *  # noqa: F401, F403

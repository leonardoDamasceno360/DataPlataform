import argparse
import logging
import os
import socket
import subprocess
import sys
import time
import webbrowser

from pathlib import Path
from urllib.request import urlopen


APP_NAME = "Data Platform"
APP_SLUG = "DataPlatform"

HOST = "127.0.0.1"

STARTUP_TIMEOUT = 90


# =========================================================
# PATHS
# =========================================================
def get_project_root():

    if getattr(sys, "frozen", False):

        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parent


PROJECT_ROOT = get_project_root()


def resource_path(*parts):

    if getattr(sys, "frozen", False):

        base_path = Path(sys._MEIPASS)

    else:

        base_path = PROJECT_ROOT

    return base_path.joinpath(*parts)


# =========================================================
# APP HOME
# =========================================================
def get_default_app_home():

    local_app_data = os.getenv("LOCALAPPDATA")

    if local_app_data:

        return Path(local_app_data) / APP_SLUG

    return Path.home() / f".{APP_SLUG.lower()}"


APP_HOME = Path(
    os.getenv(
        "DATA_PLATFORM_HOME",
        get_default_app_home()
    )
)

LOG_DIR = APP_HOME / "logs"

DATA_DIR = APP_HOME / "data"

LOG_DIR.mkdir(
    parents=True,
    exist_ok=True
)

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# =========================================================
# LOGGING
# =========================================================
def configure_logging():

    log_file = LOG_DIR / "launcher.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(
                log_file,
                encoding="utf-8"
            )
        ],
        force=True,
    )

    return logging.getLogger(APP_SLUG)


LOGGER = configure_logging()


# =========================================================
# RUNTIME
# =========================================================
RUNTIME_VENV_PYTHON = (
    PROJECT_ROOT
    / "runtime"
    / ".venv"
    / "Scripts"
    / "python.exe"
)

REQUIREMENTS_FILE = (
    PROJECT_ROOT
    / "requirements.txt"
)

MAIN_APP = resource_path(
    "runtime",
    "app",
    "main.py"
)


# =========================================================
# PYTHON
# =========================================================
def resolve_python_executable():

    candidates = [

        RUNTIME_VENV_PYTHON,

        Path(sys.executable)
    ]

    for candidate in candidates:

        if candidate.exists():

            return str(candidate)

    raise FileNotFoundError(
        "Nenhum interpretador Python valido encontrado."
    )


def ensure_runtime_dependencies(
    python_executable
):

    if getattr(sys, "frozen", False):

        return

    check_result = subprocess.run(
        [
            python_executable,
            "-c",
            "import streamlit",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    if check_result.returncode == 0:

        return

    LOGGER.info(
        "Instalando dependencias..."
    )

    subprocess.run(
        [
            python_executable,
            "-m",
            "pip",
            "install",
            "-r",
            str(REQUIREMENTS_FILE),
        ],
        cwd=PROJECT_ROOT,
        check=True,
    )


# =========================================================
# PORT
# =========================================================
def find_free_port():

    with socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    ) as sock:

        sock.bind((HOST, 0))

        sock.listen(1)

        return sock.getsockname()[1]


# =========================================================
# WAIT SERVER
# =========================================================
def wait_for_server(
    url,
    timeout=STARTUP_TIMEOUT
):

    deadline = time.time() + timeout

    while time.time() < deadline:

        try:

            with urlopen(
                url,
                timeout=2
            ) as response:

                if response.status == 200:

                    return True

        except Exception:

            time.sleep(1)

    return False


# =========================================================
# ENV
# =========================================================
def build_streamlit_env():

    env = os.environ.copy()

    env["DATA_PLATFORM_HOME"] = str(APP_HOME)

    env["DATA_PLATFORM_LOG_DIR"] = str(LOG_DIR)

    env["DATA_PLATFORM_OUTPUT_DIR"] = str(
        DATA_DIR / "outputs"
    )

    env["DATA_PLATFORM_HISTORY_DIR"] = str(
        DATA_DIR / "history"
    )

    env["STREAMLIT_GLOBAL_DEVELOPMENT_MODE"] = "false"

    return env


# =========================================================
# STREAMLIT PROCESS
# =========================================================
def start_streamlit_process(port):

    app_home = str(APP_HOME)

    env = build_streamlit_env()

    if getattr(sys, "frozen", False):

        command = [

            sys.executable,

            "--streamlit-child",

            "--port",
            str(port),

            "--app-home",
            app_home,
        ]

    else:

        python_executable = resolve_python_executable()

        ensure_runtime_dependencies(
            python_executable
        )

        command = [

            python_executable,

            str(Path(__file__).resolve()),

            "--streamlit-child",

            "--port",
            str(port),

            "--app-home",
            app_home,
        ]

    LOGGER.info(
        "Iniciando Streamlit na porta %s",
        port,
    )

    print("PROJECT_ROOT:", PROJECT_ROOT)

    print("COMMAND:", command)

    return subprocess.Popen(
        command,
        cwd=PROJECT_ROOT,
        env=env,
    )


# =========================================================
# STREAMLIT CHILD
# =========================================================
def run_streamlit_child(
    port,
    app_home
):

    os.environ["DATA_PLATFORM_HOME"] = app_home

    from streamlit.web import cli as stcli

    sys.argv = [

        "streamlit",

        "run",

        str(MAIN_APP),

        "--server.port",
        str(port),

        "--server.address",
        HOST,

        "--server.headless=true",

        "--browser.gatherUsageStats=false",

        "--theme.base=light",

        "--theme.primaryColor=#1F5AA6",
    ]

    LOGGER.info(
        "Executando Streamlit: %s",
        MAIN_APP,
    )

    stcli.main()


# =========================================================
# BROWSER
# =========================================================
def open_in_browser(url):

    LOGGER.info(
        "Abrindo navegador: %s",
        url,
    )

    webbrowser.open_new(url)


# =========================================================
# SHUTDOWN
# =========================================================
def shutdown_process(process):

    if (
        process is None
        or process.poll() is not None
    ):
        return

    LOGGER.info(
        "Encerrando Streamlit."
    )

    process.terminate()

    try:

        process.wait(timeout=5)

    except subprocess.TimeoutExpired:

        process.kill()

        process.wait(timeout=5)


# =========================================================
# MAIN LAUNCHER
# =========================================================
def run_launcher():

    port = find_free_port()

    app_url = f"http://{HOST}:{port}"

    process = start_streamlit_process(port)

    try:

        if not wait_for_server(app_url):

            raise RuntimeError(
                "O servidor Streamlit nao respondeu."
            )

        open_in_browser(app_url)

        process.wait()

    finally:

        shutdown_process(process)


# =========================================================
# ARGS
# =========================================================
def parse_args():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--streamlit-child",
        action="store_true",
        help=argparse.SUPPRESS,
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8501,
        help=argparse.SUPPRESS,
    )

    parser.add_argument(
        "--app-home",
        default=str(APP_HOME),
        help=argparse.SUPPRESS,
    )

    return parser.parse_args()


# =========================================================
# MAIN
# =========================================================
def main():

    args = parse_args()

    if args.streamlit_child:

        run_streamlit_child(
            args.port,
            args.app_home,
        )

        return

    LOGGER.info(
        "Launcher iniciado."
    )

    run_launcher()


if __name__ == "__main__":

    main()
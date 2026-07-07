![1779113993762](image/README/1779113993762.png)![1779113995289](image/README/1779113995289.png)![1779113997624](image/README/1779113997624.png)# Data Platform

Enterprise Streamlit application for HR and operations data processing.

## Run locally

```powershell
.\runtime\.venv\Scripts\python.exe -m streamlit run runtime\app\main.py --server.address 127.0.0.1 --server.port 8501
```

## Dependencies

- `requirements.txt`: dependency set for Streamlit Community Cloud.
- `requirements-desktop.txt`: full dependency set for local desktop/EXE usage.

To refresh the local desktop environment with all packages:

```powershell
.\runtime\.venv\Scripts\python.exe -m pip install -r requirements-desktop.txt
```

## Streamlit Community Cloud

- Repository entrypoint: `app.py`
- Main application module: `runtime/app/main.py`
- Community Cloud always runs from the repository root.
- Files written to disk in cloud are temporary and may disappear after reboot or redeploy.

## Run desktop launcher

```powershell
.\runtime\.venv\Scripts\python.exe launcher.py
```

## Build the executable

```powershell
powershell -ExecutionPolicy Bypass -File .\build.ps1
```

The final executable is generated at:

```text
dist\DataPlatform.exe
```

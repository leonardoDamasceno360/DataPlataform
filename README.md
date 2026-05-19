![1779113993762](image/README/1779113993762.png)![1779113995289](image/README/1779113995289.png)![1779113997624](image/README/1779113997624.png)# Data Platform

Enterprise Streamlit application for HR and operations data processing.

## Run locally

```powershell
.\runtime\.venv\Scripts\python.exe -m streamlit run runtime\app\main.py --server.address 127.0.0.1 --server.port 8501
```

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
dist\DataPlatform\DataPlatform.exe
```

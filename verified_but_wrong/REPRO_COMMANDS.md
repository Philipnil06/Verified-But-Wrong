# Reproduction Commands

```powershell
py run_all_repro.py
py -m compileall .
py -c "import app; print('app import ok')"
py -m streamlit run app.py
```

No API calls are made by `run_all_repro.py`.

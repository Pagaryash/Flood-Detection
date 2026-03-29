#!/usr/bin/env python3
import os, sys, time
from datetime import datetime
import subprocess

base = os.path.dirname(os.path.abspath(__file__))
nb_path = os.path.join(base, "notebooks", "01_fetch_S1_Mumbai.ipynb")

# Sequentially run cells 1–3 via papermill
print("🚀 Running flood pipeline at", datetime.utcnow().isoformat())
cmd = [
    sys.executable, "-m", "papermill",
    nb_path,
    os.path.join(base, "notebooks", "runs", f"run_{datetime.utcnow().strftime('%Y%m%d_%H%M')}.ipynb")
]
os.makedirs(os.path.join(base, "notebooks", "runs"), exist_ok=True)
subprocess.run(cmd, check=False)
print("✅ Pipeline finished.")

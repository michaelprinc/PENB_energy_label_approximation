"""
Hlavní entrypoint aplikace
Spustí Streamlit GUI

Použití:
    python main.py
    
    nebo přímo:
    streamlit run app_gui/gui_main.py
"""
import sys
import os
import subprocess

# Přidej current directory do PYTHONPATH
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

if __name__ == "__main__":
    # Cesta k GUI modulu
    gui_path = os.path.join(project_dir, "app_gui", "gui_main.py")
    
    # Spusť Streamlit jako subprocess s nastaveným PYTHONPATH
    env = os.environ.copy()
    env['PYTHONPATH'] = project_dir
    
    # Spusť Streamlit
    try:
        subprocess.run([
            sys.executable,
            "-m", "streamlit",
            "run",
            gui_path,
            "--server.port=8501"
        ], env=env, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Chyba při spuštění Streamlit: {e}")
        print("\nZkuste spustit přímo:")
        print(f"  streamlit run {gui_path}")
        sys.exit(1)
    except FileNotFoundError:
        print("Streamlit není nainstalován!")
        print("Nainstalujte závislosti: pip install -r requirements.txt")
        sys.exit(1)

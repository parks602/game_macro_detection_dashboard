# main.py
import subprocess
from utils.utils import configure_streamlit

if __name__ == "__main__":
    configure_streamlit()

    subprocess.run(["streamlit", "run", "ui/main_ui.py"])

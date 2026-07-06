from pathlib import Path
import runpy


INNER_APP = Path(__file__).resolve().parent / "dashboard_streamlit_v2" / "app.py"

runpy.run_path(str(INNER_APP), run_name="__main__")
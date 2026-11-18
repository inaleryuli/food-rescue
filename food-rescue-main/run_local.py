"""Launch the app from any directory; use --cli for a dependency-free demo."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

if __name__ == "__main__":
    if "--cli" in sys.argv:
        from src.app import main
        main([arg for arg in sys.argv[1:] if arg != "--cli"])
    else:
        try:
            import streamlit
        except ImportError:
            raise SystemExit("Install dependencies with: python -m pip install -r requirements.txt\nOr run the offline CLI: python run_local.py --cli")
        raise SystemExit(subprocess.call(
            [sys.executable, "-m", "streamlit", "run", str(ROOT / "streamlit_app.py"),
             "--browser.gatherUsageStats=false", *sys.argv[1:]], cwd=ROOT,
        ))

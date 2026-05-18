"""
Hugging Face Spaces entrypoint.

HF Spaces (Gradio SDK) runs `app.py` at the repo root and serves the
module-level `demo` Blocks. Keeping the `__main__` guard lets it also run
locally with `python app.py` (equivalent to `python -m dashboard.app.main`).
"""

from dashboard.app.main import build_app

demo = build_app()

if __name__ == "__main__":
    demo.launch()

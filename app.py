"""
Hugging Face Spaces entrypoint.

HF Spaces (Gradio SDK) runs `app.py` at the repo root and serves the
module-level `demo` Blocks. Keeping the `__main__` guard lets it also run
locally with `python app.py` (equivalent to `python -m dashboard.app.main`).
"""

import os

# Disable Gradio's experimental SSR mode. It causes noisy asyncio
# "Invalid file descriptor" finalizer tracebacks (and occasional flaky
# rendering) on HF Spaces. Set BEFORE importing gradio so it's the default
# regardless of whether Spaces calls .launch() itself or runs this file.
os.environ.setdefault("GRADIO_SSR_MODE", "False")

from dashboard.app.main import build_app

demo = build_app()

if __name__ == "__main__":
    demo.launch(ssr_mode=False)

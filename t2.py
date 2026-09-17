"""相容入口；正式範例位於 examples/02_browser_sessions/open_blogger_admin.py。"""

from pathlib import Path
import runpy

globals().update(runpy.run_path(
    str(Path(__file__).resolve().parent / "examples/02_browser_sessions/open_blogger_admin.py"),
    run_name=__name__,
))

"""相容入口；正式範例位於 examples/01_basics/open_page.py。"""

from pathlib import Path
import runpy

globals().update(runpy.run_path(
    str(Path(__file__).resolve().parent / "examples/01_basics/open_page.py"),
    run_name=__name__,
))

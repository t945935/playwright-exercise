"""相容入口；正式範例位於 examples/05_visuals/website_screenshots.py。"""

from pathlib import Path
import runpy

globals().update(runpy.run_path(
    str(Path(__file__).resolve().parent / "examples/05_visuals/website_screenshots.py"),
    run_name=__name__,
))

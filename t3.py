"""相容入口；正式範例位於 examples/06_publishing/publish_blogger_post.py。"""

from pathlib import Path
import runpy

globals().update(runpy.run_path(
    str(Path(__file__).resolve().parent / "examples/06_publishing/publish_blogger_post.py"),
    run_name=__name__,
))

"""相容入口；正式範例位於 examples/06_publishing/create_play_book.py。"""

from pathlib import Path
import runpy

globals().update(runpy.run_path(
    str(Path(__file__).resolve().parent / "examples/06_publishing/create_play_book.py"),
    run_name=__name__,
))

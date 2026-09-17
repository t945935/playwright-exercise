"""相容入口；正式範例位於 examples/04_tracking/tsmc_price_tracker.py。"""

from pathlib import Path
import runpy

globals().update(runpy.run_path(
    str(Path(__file__).resolve().parent / "examples/04_tracking/tsmc_price_tracker.py"),
    run_name=__name__,
))

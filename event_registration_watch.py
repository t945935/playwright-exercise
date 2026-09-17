"""相容入口；正式範例位於 examples/04_tracking/event_registration_watch.py。"""

from pathlib import Path
import runpy

globals().update(runpy.run_path(
    str(Path(__file__).resolve().parent / "examples/04_tracking/event_registration_watch.py"),
    run_name=__name__,
))

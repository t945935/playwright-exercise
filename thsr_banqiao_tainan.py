"""相容入口；正式範例位於 examples/03_data_queries/thsr_banqiao_tainan.py。"""

from pathlib import Path
import runpy

globals().update(runpy.run_path(
    str(Path(__file__).resolve().parent / "examples/03_data_queries/thsr_banqiao_tainan.py"),
    run_name=__name__,
))

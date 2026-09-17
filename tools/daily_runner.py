"""依序執行唯讀範例並保存每支程式的輸出摘要。"""

import argparse
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
JOBS = [
    ("ai-news", ROOT / "examples/03_data_queries/ai_news_today.py"),
    ("book-radar", ROOT / "examples/04_tracking/happyebook_new_books.py"),
    ("tsmc", ROOT / "examples/04_tracking/tsmc_price_tracker.py"),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="只列印命令，不連線或執行")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs/scheduler")
    parser.add_argument("--timeout", type=int, default=180, help="每支程式最長秒數")
    args = parser.parse_args()
    if args.timeout < 1:
        parser.error("timeout 必須大於 0")
    python = Path(sys.executable)
    commands = [[str(python), str(script)] for _, script in JOBS]
    for name, command in zip((name for name, _ in JOBS), commands):
        print(f"{name}: {' '.join(command)}")
    if args.dry_run:
        print("dry-run：未連線、未執行、未寫入摘要。")
        return 0

    args.output_dir.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc)
    results = []
    for name, command in zip((name for name, _ in JOBS), commands):
        print(f"\n=== {name} ===", flush=True)
        try:
            completed = subprocess.run(
                command, cwd=ROOT, capture_output=True, text=True,
                timeout=args.timeout, check=False,
            )
            result = {
                "name": name, "command": command, "returncode": completed.returncode,
                "stdout": completed.stdout, "stderr": completed.stderr,
            }
        except subprocess.TimeoutExpired as error:
            result = {"name": name, "command": command, "returncode": 124,
                      "stdout": error.stdout or "", "stderr": f"逾時：{args.timeout} 秒"}
        results.append(result)
        print(result["stdout"].rstrip())
        if result["stderr"]:
            print(result["stderr"].rstrip(), file=sys.stderr)
        print(f"退出碼：{result['returncode']}", flush=True)

    finished = datetime.now(timezone.utc)
    log = args.output_dir / f"run_{finished:%Y%m%d_%H%M%S}.log"
    lines = [f"開始：{started.isoformat()}", f"結束：{finished.isoformat()}"]
    for result in results:
        lines.extend([f"\n[{result['name']}] exit={result['returncode']}", result["stdout"], result["stderr"]])
    log.write_text("\n".join(lines), encoding="utf-8")
    failed = [result["name"] for result in results if result["returncode"] != 0]
    print(f"\n摘要：{log.resolve()}")
    if failed:
        print("失敗：" + ", ".join(failed), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Command-line entry point for one development task."""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Sequence

from .agent import run_compile_loop


_LOCAL_ENV_KEYS = {"DMXAPI_API_KEY", "DMXAPI_BASE_URL", "MODEL_A", "MODEL_B"}


def load_local_env(path: Path) -> None:
    if not path.is_file():
        return
    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8-sig").splitlines(), start=1
    ):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(f"invalid .env line {line_number}")
        name, value = line.split("=", 1)
        name = name.strip()
        if name in _LOCAL_ENV_KEYS:
            os.environ.setdefault(name, value.strip().strip('"').strip("'"))


def _default_output_dir(root: Path, model: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_model = re.sub(r"[^A-Za-z0-9_.-]+", "_", model)
    return root / "experiments" / "raw" / "development" / f"{timestamp}_{safe_model}"


def main(argv: Sequence[str] | None = None) -> int:
    root = Path(__file__).resolve().parents[2]
    load_local_env(root / ".env")

    parser = argparse.ArgumentParser(description="Run one ST generation and compile loop")
    parser.add_argument(
        "--task",
        type=Path,
        default=root / "tests" / "fixtures" / "motor_start_stop_fixture.json",
    )
    parser.add_argument("--model", default=os.environ.get("MODEL_A"))
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--max-repairs", type=int, default=2)
    parser.add_argument("--model-timeout", type=float, default=120.0)
    args = parser.parse_args(argv)

    if not args.model:
        parser.error("set MODEL_A in .env or pass --model")

    payload = json.loads(args.task.read_text(encoding="utf-8-sig"))
    task = payload.get("task", payload)
    output_dir = args.output_dir or _default_output_dir(root, args.model)
    result = run_compile_loop(
        task=task,
        model=args.model,
        template_project=root / "codesys" / "template" / "测试工程.project",
        output_dir=output_dir,
        max_repairs=args.max_repairs,
        model_timeout_seconds=args.model_timeout,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"Artifacts: {output_dir.resolve()}")
    return 0 if result["final_status"] == "compile_success" else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Command-line entry point for the Codex CLI baseline."""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Sequence

from .cli import load_local_env, load_shared_tests
from .codex_cli_baseline import run_codex_cli_baseline


def main(argv: Sequence[str] | None = None) -> int:
    root = Path(__file__).resolve().parents[2]
    load_local_env(root / ".env")
    parser = argparse.ArgumentParser(description="Run the Codex CLI baseline")
    parser.add_argument(
        "--task",
        type=Path,
        default=root / "tests" / "fixtures" / "motor_start_stop_fixture.json",
    )
    parser.add_argument("--tests", type=Path)
    parser.add_argument("--model", default=os.environ.get("MODEL_A"))
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--max-repairs", type=int, default=2)
    parser.add_argument("--model-timeout", type=float, default=300.0)
    args = parser.parse_args(argv)
    if not args.model:
        parser.error("set MODEL_A in .env or pass --model")

    payload = json.loads(args.task.read_text(encoding="utf-8-sig"))
    task = payload.get("task", payload)
    tests = load_shared_tests(root, payload, task, args.tests)
    if args.output_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_model = re.sub(r"[^A-Za-z0-9_.-]+", "_", args.model)
        output_dir = (
            root
            / "experiments"
            / "raw"
            / "development"
            / f"{timestamp}_{task.get('id', 'task')}_{safe_model}_codex_cli"
        )
    else:
        output_dir = args.output_dir
    result = run_codex_cli_baseline(
        task=task,
        tests=tests,
        model=args.model,
        template_project=root / "codesys" / "template" / "测试工程.project",
        output_dir=output_dir,
        max_repairs=args.max_repairs,
        model_timeout_seconds=args.model_timeout,
    )
    print(json.dumps(result, ensure_ascii=True, indent=2))
    print(f"Artifacts: {output_dir.resolve()}")
    return 0 if result["final_status"] in {"compile_success", "success"} else 1


if __name__ == "__main__":
    raise SystemExit(main())

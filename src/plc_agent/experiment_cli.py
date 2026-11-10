"""Run the frozen four-condition pre-run or formal experiment."""

from __future__ import annotations

import argparse
import json
import re
import secrets
from datetime import datetime
from pathlib import Path
from typing import Any, Sequence

from .agent import run_compile_loop
from .cli import load_local_env
from .codex_cli_baseline import run_codex_cli_baseline


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value)


def _task_paths(root: Path, phase: str, config: dict[str, Any]) -> list[Path]:
    if phase == "pre_run":
        paths = []
        for task_id in config["pre_run_tasks"]:
            matches = list((root / "data" / "tasks").glob(f"*/{task_id}.json"))
            if len(matches) != 1:
                raise ValueError(f"expected one task file for {task_id}")
            paths.append(matches[0])
        return paths
    return sorted((root / "data" / "tasks" / "public").glob("*.json")) + sorted(
        (root / "data" / "tasks" / "custom").glob("*.json")
    )


def run_experiment(
    *,
    root: Path,
    config: dict[str, Any],
    phase: str,
    output_dir: Path,
    resume: bool = False,
    retry_statuses: set[str] | None = None,
) -> list[dict[str, Any]]:
    expected_config = {**config, "phase": phase}
    if resume:
        if _read_json(output_dir / "run_config.json") != expected_config:
            raise ValueError("resume config does not match the saved run config")
        rows = _read_json(output_dir / "manifest.json")["runs"]
    else:
        output_dir.mkdir(parents=True, exist_ok=False)
        _write_json(output_dir / "run_config.json", expected_config)
        rows = []
    retry_statuses = retry_statuses or set()
    row_indexes = {
        (row["task_id"], row["framework"], row["model"]): index
        for index, row in enumerate(rows)
    }
    template = root / "codesys" / "template" / "测试工程.project"
    task_paths = _task_paths(root, phase, config)
    total_conditions = (
        len(task_paths) * len(config["frameworks"]) * len(config["models"])
    )
    condition_number = 0

    for task_path in task_paths:
        task = _read_json(task_path)
        kind = task_path.parent.name
        tests = _read_json(
            root / "data" / "test_cases" / kind / f"{task['id']}.json"
        )
        for framework in config["frameworks"]:
            for model in config["models"]:
                condition_number += 1
                key = (task["id"], framework, model)
                previous_index = row_indexes.get(key)
                previous = rows[previous_index] if previous_index is not None else None
                if previous and previous["final_status"] not in retry_statuses:
                    continue
                prefix = f"[{condition_number:03d}/{total_conditions:03d}]"
                action = "重跑" if previous else "开始"
                print(
                    f"{prefix} {action} task={task['id']} "
                    f"framework={framework} model={model}",
                    flush=True,
                )
                base_name = f"{framework}__{_safe_name(model)}"
                condition_dir = output_dir / task["id"] / base_name
                if previous:
                    retry_index = 1
                    while (output_dir / task["id"] / f"{base_name}__retry_{retry_index:02d}").exists():
                        retry_index += 1
                    condition_dir = (
                        output_dir
                        / task["id"]
                        / f"{base_name}__retry_{retry_index:02d}"
                    )
                result: dict[str, Any] | None = None
                try:
                    if framework == "custom":
                        result = run_compile_loop(
                            task=task,
                            tests=tests,
                            model=model,
                            template_project=template,
                            output_dir=condition_dir,
                            max_repairs=config["max_repairs"],
                            model_timeout_seconds=config["model_timeout_seconds"],
                            reasoning_effort=config.get("reasoning_effort"),
                            enable_candidate_precheck=config.get(
                                "enable_candidate_precheck", False
                            ),
                            regenerate_on_repeated_error=config.get(
                                "regenerate_on_repeated_error", False
                            ),
                        )
                    elif framework == "codex_cli":
                        result = run_codex_cli_baseline(
                            task=task,
                            tests=tests,
                            model=model,
                            template_project=template,
                            output_dir=condition_dir,
                            max_repairs=config["max_repairs"],
                            model_timeout_seconds=config["model_timeout_seconds"],
                        )
                    else:
                        raise ValueError(f"unsupported framework: {framework}")
                    row = {
                        "task_id": task["id"],
                        "framework": framework,
                        "model": model,
                        "final_status": result["final_status"],
                        "test_passed": result.get("test_passed", 0),
                        "test_total": result.get("test_total", 0),
                        "artifact_directory": str(
                            condition_dir.relative_to(output_dir)
                        ),
                    }
                except Exception as exc:
                    condition_dir.mkdir(parents=True, exist_ok=True)
                    error = {"type": type(exc).__name__, "message": str(exc)}
                    _write_json(condition_dir / "runner_error.json", error)
                    row = {
                        "task_id": task["id"],
                        "framework": framework,
                        "model": model,
                        "final_status": "runner_error",
                        "test_passed": 0,
                        "test_total": len(tests["tests"]),
                        "artifact_directory": str(
                            condition_dir.relative_to(output_dir)
                        ),
                        "failure_reason": error,
                    }
                if previous is not None and previous_index is not None:
                    row["supersedes_artifact_directory"] = previous[
                        "artifact_directory"
                    ]
                    row["retry_reason"] = "infrastructure_failure"
                    rows[previous_index] = row
                else:
                    row_indexes[key] = len(rows)
                    rows.append(row)
                _write_json(output_dir / "manifest.json", {"runs": rows})
                if result is None:
                    compile_text = "首次编译=未知 最终编译=未知 候选=0 修复=0 耗时=0.0s"
                else:
                    first_compile = "通过" if result.get("first_compile_pass") else "失败"
                    final_compile = "通过" if result.get("final_compile_pass") else "失败"
                    compile_text = (
                        f"首次编译={first_compile} 最终编译={final_compile} "
                        f"候选={result.get('attempts', 0)} "
                        f"修复={result.get('repairs', 0)} "
                        f"耗时={float(result.get('duration_seconds', 0.0)):.1f}s"
                    )
                print(
                    f"{prefix} 完成 status={row['final_status']} {compile_text} "
                    f"测试={row.get('test_passed', 0)}/{len(tests['tests'])} "
                    f"证据={row['artifact_directory']}",
                    flush=True,
                )
    return rows


def main(argv: Sequence[str] | None = None) -> int:
    root = Path(__file__).resolve().parents[2]
    load_local_env(root / ".env")
    parser = argparse.ArgumentParser(description="Run the four-condition experiment")
    parser.add_argument("--phase", choices=("pre_run", "formal"), default="pre_run")
    parser.add_argument(
        "--config", type=Path, default=root / "config" / "experiment.json"
    )
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--resume", type=Path)
    parser.add_argument(
        "--retry-status",
        action="append",
        default=[],
        choices=("model_error", "timeout", "runner_error"),
    )
    args = parser.parse_args(argv)
    if args.resume and args.output_dir:
        parser.error("--resume and --output-dir cannot be used together")

    config = _read_json(args.config)
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + secrets.token_hex(3)
    output_dir = args.resume or args.output_dir or (
        root / "experiments" / "raw" / args.phase / run_id
    )
    rows = run_experiment(
        root=root,
        config=config,
        phase=args.phase,
        output_dir=output_dir,
        resume=args.resume is not None,
        retry_statuses=set(args.retry_status),
    )
    print(f"Artifacts: {output_dir.resolve()}")
    return 0 if all(row["final_status"] != "runner_error" for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Single-task generate, compile, and repair loop."""

from __future__ import annotations

import json
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable

from .candidate import StCandidate
from .codesys_runner import CompileResult, compile_project
from .model_client import ChatCompletion, chat_completion


ChatFunction = Callable[..., ChatCompletion]
CompileFunction = Callable[..., CompileResult]


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _render_prompt(path: Path, replacements: dict[str, str]) -> str:
    prompt = path.read_text(encoding="utf-8")
    for name, value in replacements.items():
        prompt = prompt.replace("{" + name + "}", value)
    return prompt


def _compile_errors(result: CompileResult) -> list[dict[str, Any]]:
    return [asdict(message) for message in result.errors]


def run_compile_loop(
    *,
    task: dict[str, Any],
    model: str,
    template_project: str | Path,
    output_dir: str | Path,
    max_repairs: int = 2,
    model_timeout_seconds: float = 120.0,
    reasoning_effort: str | None = None,
    chat_function: ChatFunction = chat_completion,
    compile_function: CompileFunction = compile_project,
) -> dict[str, Any]:
    """Run one task and preserve every model and compiler artifact."""

    if max_repairs < 0:
        raise ValueError("max_repairs must not be negative")
    if model_timeout_seconds <= 0:
        raise ValueError("model_timeout_seconds must be positive")

    run_dir = Path(output_dir).resolve()
    run_dir.mkdir(parents=True, exist_ok=False)
    root = Path(__file__).resolve().parents[2]
    task_json = json.dumps(task, ensure_ascii=False, indent=2)
    _write_json(run_dir / "task.json", task)
    _write_json(
        run_dir / "run_config.json",
        {
            "model": model,
            "max_repairs": max_repairs,
            "model_timeout_seconds": model_timeout_seconds,
            "reasoning_effort": reasoning_effort,
            "template_project": str(Path(template_project).resolve()),
        },
    )

    generate_template = root / "prompts" / "generate_st.txt"
    repair_template = root / "prompts" / "repair_st.txt"
    prompt = _render_prompt(generate_template, {"task_json": task_json})
    previous_output = ""
    errors: list[dict[str, Any]] = []
    api_models: list[str] = []
    usage_by_attempt: list[dict[str, Any]] = []
    started = time.monotonic()

    for attempt_index in range(max_repairs + 1):
        attempt_dir = run_dir / f"attempt_{attempt_index:02d}"
        attempt_dir.mkdir()
        (attempt_dir / "prompt.txt").write_text(prompt, encoding="utf-8")

        try:
            completion = chat_function(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "Return machine-readable CODESYS Structured Text only.",
                    },
                    {"role": "user", "content": prompt},
                ],
                timeout_seconds=model_timeout_seconds,
                reasoning_effort=reasoning_effort,
            )
        except Exception as exc:
            error = {"type": type(exc).__name__, "message": str(exc)}
            _write_json(attempt_dir / "model_error.json", error)
            final = {
                "task_id": task.get("id"),
                "model": model,
                "final_status": "model_error",
                "attempts": attempt_index + 1,
                "repairs": attempt_index,
                "first_compile_pass": False,
                "final_compile_pass": False,
                "duration_seconds": round(time.monotonic() - started, 3),
                "failure_reason": error,
            }
            _write_json(run_dir / "final_result.json", final)
            return final
        previous_output = completion.content
        if completion.model:
            api_models.append(completion.model)
        usage_by_attempt.append(completion.usage)
        (attempt_dir / "model_output.txt").write_text(
            previous_output,
            encoding="utf-8",
        )
        _write_json(attempt_dir / "model_response.json", completion.raw_response)

        try:
            candidate = StCandidate.from_model_text(previous_output)
        except ValueError as exc:
            errors = [{"kind": "parse_error", "text": str(exc)}]
            _write_json(attempt_dir / "parse_errors.json", errors)
        else:
            _write_json(attempt_dir / "candidate.json", candidate.to_dict())
            declaration_path = attempt_dir / "declaration.st"
            implementation_path = attempt_dir / "implementation.st"
            declaration_path.write_text(candidate.declaration + "\n", encoding="utf-8")
            implementation_path.write_text(candidate.implementation + "\n", encoding="utf-8")

            compile_result = compile_function(
                template_project=template_project,
                declaration_path=declaration_path,
                implementation_path=implementation_path,
                output_dir=attempt_dir / "compile",
                pou_name=candidate.pou_name,
                pou_type=candidate.pou_type,
            )
            errors = _compile_errors(compile_result)
            if compile_result.success:
                final = {
                    "task_id": task.get("id"),
                    "model": model,
                    "final_status": "compile_success",
                    "attempts": attempt_index + 1,
                    "repairs": attempt_index,
                    "first_compile_pass": attempt_index == 0,
                    "final_compile_pass": True,
                    "api_models": api_models,
                    "usage_by_attempt": usage_by_attempt,
                    "duration_seconds": round(time.monotonic() - started, 3),
                }
                _write_json(run_dir / "final_result.json", final)
                return final

        if attempt_index < max_repairs:
            prompt = _render_prompt(
                repair_template,
                {
                    "task_json": task_json,
                    "previous_output": previous_output,
                    "errors_json": json.dumps(errors, ensure_ascii=False, indent=2),
                },
            )

    final = {
        "task_id": task.get("id"),
        "model": model,
        "final_status": "compile_failure",
        "attempts": max_repairs + 1,
        "repairs": max_repairs,
        "first_compile_pass": False,
        "final_compile_pass": False,
        "api_models": api_models,
        "usage_by_attempt": usage_by_attempt,
        "duration_seconds": round(time.monotonic() - started, 3),
        "failure_reason": errors,
    }
    _write_json(run_dir / "final_result.json", final)
    return final

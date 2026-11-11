"""Single-task generate, compile, and repair loop."""

from __future__ import annotations

import json
import hashlib
import time
from dataclasses import asdict
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

from .candidate import StCandidate
from .codesys_runner import (
    CompileResult,
    TestExecutionResult,
    compile_project,
    execute_tests,
)
from .model_client import ChatCompletion, chat_completion
from .precheck import validate_candidate


ChatFunction = Callable[..., ChatCompletion]
CompileFunction = Callable[..., CompileResult]
TestFunction = Callable[..., TestExecutionResult]


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


@lru_cache(maxsize=None)
def _read_prompt(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _render_prompt(path: Path, replacements: dict[str, str]) -> str:
    prompt = _read_prompt(path)
    for name, value in replacements.items():
        prompt = prompt.replace("{" + name + "}", value)
    return prompt


def _compile_errors(result: CompileResult) -> list[dict[str, Any]]:
    return [asdict(message) for message in result.errors]


def _error_signature(errors: list[dict[str, Any]]) -> str:
    normalized = [
        {
            key: str(error.get(key, "")).strip().lower()
            for key in ("kind", "number", "text", "object_name", "variable")
            if error.get(key) not in (None, "")
        }
        for error in errors
    ]
    if not any(normalized):
        return ""
    payload = json.dumps(normalized, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]


def run_compile_loop(
    *,
    task: dict[str, Any],
    model: str,
    template_project: str | Path,
    output_dir: str | Path,
    max_repairs: int = 2,
    model_timeout_seconds: float = 120.0,
    reasoning_effort: str | None = None,
    tests: dict[str, Any] | None = None,
    enable_candidate_precheck: bool = False,
    regenerate_on_repeated_error: bool = False,
    combine_compile_and_test: bool = False,
    chat_function: ChatFunction = chat_completion,
    compile_function: CompileFunction = compile_project,
    test_function: TestFunction = execute_tests,
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
            "automatic_tests": tests is not None,
            "enable_candidate_precheck": enable_candidate_precheck,
            "regenerate_on_repeated_error": regenerate_on_repeated_error,
            "combine_compile_and_test": combine_compile_and_test,
        },
    )

    generate_template = root / "prompts" / "generate_st.txt"
    repair_template = root / "prompts" / "repair_st.txt"
    prompt = _render_prompt(generate_template, {"task_json": task_json})
    previous_output = ""
    errors: list[dict[str, Any]] = []
    api_models: list[str] = []
    usage_by_attempt: list[dict[str, Any]] = []
    attempts_detail: list[dict[str, Any]] = []
    previous_error_signature = ""
    stage = "generate"
    started = time.monotonic()
    compile_context = {
        "custom_types": task.get("custom_types", []),
        "inout_bindings": task.get("compile_context", {}).get(
            "inout_bindings", []
        ),
    }
    if not compile_context["custom_types"] and not compile_context["inout_bindings"]:
        compile_context = None

    for attempt_index in range(max_repairs + 1):
        attempt_dir = run_dir / f"attempt_{attempt_index:02d}"
        attempt_dir.mkdir()
        (attempt_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
        attempt_detail: dict[str, Any] = {
            "attempt": attempt_index,
            "stage": stage,
            "compiled": False,
            "compile_passed": False,
        }
        compile_success = False
        test_result: TestExecutionResult | None = None

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
            attempt_detail["errors"] = [error]
            attempts_detail.append(attempt_detail)
            _write_json(attempt_dir / "attempt_result.json", attempt_detail)
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
                "attempts_detail": attempts_detail,
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
            precheck_errors = (
                validate_candidate(task, candidate)
                if enable_candidate_precheck
                else []
            )
            if precheck_errors:
                errors = precheck_errors
                _write_json(attempt_dir / "precheck_errors.json", errors)
            else:
                declaration_path = attempt_dir / "declaration.st"
                implementation_path = attempt_dir / "implementation.st"
                declaration_path.write_text(
                    candidate.declaration + "\n", encoding="utf-8"
                )
                implementation_path.write_text(
                    candidate.implementation + "\n", encoding="utf-8"
                )

                if combine_compile_and_test and tests is not None:
                    test_result = test_function(
                        template_project=template_project,
                        declaration_path=declaration_path,
                        implementation_path=implementation_path,
                        task=task,
                        tests=tests,
                        output_dir=attempt_dir / "combined_execution",
                        compile_context=compile_context,
                    )
                    compile_success = test_result.compile_success
                    errors = [asdict(message) for message in test_result.errors]
                else:
                    compile_result = compile_function(
                        template_project=template_project,
                        declaration_path=declaration_path,
                        implementation_path=implementation_path,
                        output_dir=attempt_dir / "compile",
                        pou_name=candidate.pou_name,
                        pou_type=candidate.pou_type,
                        compile_context=compile_context,
                    )
                    compile_success = compile_result.success
                    errors = _compile_errors(compile_result)
                attempt_detail["compiled"] = True
                attempt_detail["compile_passed"] = compile_success
            if not precheck_errors and compile_success:
                attempt_detail["errors"] = []
                attempts_detail.append(attempt_detail)
                _write_json(attempt_dir / "attempt_result.json", attempt_detail)
                if tests is not None and test_result is None:
                    test_result = test_function(
                        template_project=template_project,
                        declaration_path=declaration_path,
                        implementation_path=implementation_path,
                        task=task,
                        tests=tests,
                        output_dir=run_dir / "test_execution",
                        compile_context=compile_context,
                    )
                final = {
                    "task_id": task.get("id"),
                    "model": model,
                    "final_status": (
                        "success"
                        if test_result is not None and test_result.success
                        else "test_failure"
                        if test_result is not None
                        else "compile_success"
                    ),
                    "attempts": attempt_index + 1,
                    "repairs": attempt_index,
                    "first_compile_pass": attempt_index == 0,
                    "final_compile_pass": True,
                    "api_models": api_models,
                    "usage_by_attempt": usage_by_attempt,
                    "duration_seconds": round(time.monotonic() - started, 3),
                    "attempts_detail": attempts_detail,
                }
                if test_result is not None:
                    final.update(
                        {
                            "test_passed": test_result.test_passed,
                            "test_total": test_result.test_total,
                            "test_results_file": str(
                                test_result.result_path.relative_to(run_dir)
                            ),
                        }
                    )
                    if not test_result.success:
                        final["failure_reason"] = "shared_tests_failed"
                _write_json(run_dir / "final_result.json", final)
                return final

        signature = _error_signature(errors)
        attempt_detail["errors"] = errors
        attempt_detail["error_signature"] = signature
        attempts_detail.append(attempt_detail)
        _write_json(attempt_dir / "attempt_result.json", attempt_detail)

        if attempt_index < max_repairs:
            repeated = bool(signature and signature == previous_error_signature)
            if regenerate_on_repeated_error and repeated:
                prompt = _render_prompt(generate_template, {"task_json": task_json})
                prompt += (
                    "\n\nThe previous two candidates produced the same error signature. "
                    "Create an independent solution from scratch; do not copy the previous candidate."
                )
                stage = "regenerate"
            else:
                prompt = _render_prompt(
                    repair_template,
                    {
                        "task_json": task_json,
                        "previous_output": previous_output,
                        "errors_json": json.dumps(
                            errors, ensure_ascii=False, indent=2
                        ),
                    },
                )
                stage = "repair"
            previous_error_signature = signature

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
        "attempts_detail": attempts_detail,
    }
    _write_json(run_dir / "final_result.json", final)
    return final

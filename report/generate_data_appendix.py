"""Generate the report appendix for custom-task provenance, LTL, and tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "report" / "generated_data_appendix.tex"

SOURCE_LABELS = {
    "self_conceived": "自主构思",
    "experience_based": "经验改编",
    "synthetic": "规则合成",
}

def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def tex(value: Any) -> str:
    text = str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in text)


def code(value: Any) -> str:
    return r"{\ttfamily " + tex(value) + "}"


def format_value(value: Any) -> str:
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if value is None:
        return "null"
    if isinstance(value, dict):
        return ", ".join(f"{key}={format_value(item)}" for key, item in value.items())
    if isinstance(value, list):
        return "[" + ", ".join(format_value(item) for item in value) + "]"
    return str(value)


def join_text(values: list[Any] | None) -> str:
    if not values:
        return "无"
    return "；".join(str(value) for value in values)


def task_paths(kind: str) -> list[Path]:
    return sorted((ROOT / "data" / "tasks" / kind).glob("*.json"))


def append_table_header(lines: list[str], columns: str, headers: list[str]) -> None:
    lines.append(r"\begin{longtable}{" + columns + "}")
    lines.append(r"\toprule")
    lines.append(" & ".join(headers) + r"\\")
    lines.append(r"\midrule")
    lines.append(r"\endfirsthead")
    lines.append(r"\toprule")
    lines.append(" & ".join(headers) + r"\\")
    lines.append(r"\midrule")
    lines.append(r"\endhead")


def generate_custom_records(lines: list[str]) -> None:
    lines.extend(
        [
            r"\section{自建题构建与审核记录}",
            "10道自建题均按来源记录、PLC合理性和多样性三方面审核。"
            "其中自主构思2道、经验改编6道、规则合成2道；难度分布为easy 3道、"
            "medium 4道、hard 3道。自建题没有直接复制网络题目，因此没有外部链接；"
            "规则合成题在构建过程中明确记录了规则组合和人工修改。",
        ]
    )
    for path in task_paths("custom"):
        task = read_json(path)
        provenance = task.get("provenance", {})
        lines.append(
            r"\subsection{" + code(task["id"]) + " " + tex(task["title"]) + "}"
        )
        append_table_header(lines, r"L{3.0cm}L{10.3cm}", ["项目", "记录内容"])
        rows = (
            ("难度", task.get("difficulty", "")),
            ("来源类型", SOURCE_LABELS.get(provenance.get("source_type"), provenance.get("source_type", ""))),
            ("来源说明", task.get("source_reference", "")),
            ("构建或改编过程", join_text(provenance.get("creation_process"))),
            ("人工修改", join_text(provenance.get("human_modifications"))),
            ("审核过程", join_text(provenance.get("review_process"))),
            ("PLC场景合理性", task.get("plc_rationale", "")),
            ("多样性标签", "、".join(task.get("diversity_tags", []))),
        )
        for name, value in rows:
            lines.append(f"{tex(name)} & {tex(value)}" + r"\\")
        lines.extend([r"\bottomrule", r"\end{longtable}"])


def generate_ltl(lines: list[str]) -> None:
    lines.extend(
        [
            r"\section{逐题LTL规约}",
            "本附录列出30道题的全部LTL性质。公式中的$G$表示始终成立，$X$表示一次PLC扫描后的状态。"
            "这些性质用于需求整理、测试覆盖检查和模型上下文，尚未接入形式化验证工具。",
        ]
    )
    for kind in ("public", "custom"):
        for task_path in task_paths(kind):
            task = read_json(task_path)
            spec_path = ROOT / "data" / "specs" / kind / task_path.name
            spec = read_json(spec_path)
            lines.append(
                r"\subsection{" + code(task["id"]) + " " + tex(task["title"]) + "}"
            )
            lines.append(
                r"\noindent\textbf{状态语义：}" + tex(spec.get("state_semantics", ""))
            )
            propositions = spec.get("propositions", {})
            if propositions:
                append_table_header(lines, r"L{3.3cm}L{10.0cm}", ["命题", "含义"])
                for name, meaning in propositions.items():
                    lines.append(code(name) + " & " + tex(meaning) + r"\\")
                lines.extend([r"\bottomrule", r"\end{longtable}"])
            append_table_header(
                lines, r"L{2.3cm}L{1.7cm}L{4.1cm}L{5.2cm}", ["性质编号", "类型", "说明", "LTL公式"]
            )
            for prop in spec.get("properties", []):
                lines.append(
                    " & ".join(
                        [
                            code(prop.get("id", "")),
                            tex(prop.get("type", "")),
                            tex(prop.get("description", "")),
                            code(prop.get("ltl", "")),
                        ]
                    )
                    + r"\\"
                )
            lines.extend([r"\bottomrule", r"\end{longtable}"])


def generate_tests(lines: list[str]) -> None:
    lines.extend(
        [
            r"\section{逐题测试用例}",
            "测试用例按课程模板列出名称、所属题目、初始状态、输入步骤、等待时间、预期输出和覆盖内容。",
        ]
    )
    for kind in ("public", "custom"):
        for task_path in task_paths(kind):
            task = read_json(task_path)
            tests_path = ROOT / "data" / "test_cases" / kind / task_path.name
            document = read_json(tests_path)
            lines.append(
                r"\subsection{" + code(task["id"]) + " " + tex(task["title"]) + "}"
            )
            for test in document.get("tests", []):
                lines.append(
                    r"\subsubsection{" + code(test.get("id", "")) + " " + tex(test.get("name", "")) + "}"
                )
                initial = format_value(test.get("initial_state", {})) or "冷复位后的默认状态"
                coverage = "、".join(test.get("coverage", [])) or "主要功能"
                lines.append(r"\noindent\textbf{初始状态：}" + tex(initial) + r"\\")
                lines.append(r"\textbf{覆盖内容：}" + tex(coverage))
                append_table_header(
                    lines,
                    r"L{1.0cm}L{4.7cm}L{1.4cm}L{4.0cm}L{2.1cm}",
                    ["周期", "输入", "等待/ms", "预期输出", "检查内容"],
                )
                for step in test.get("steps", []):
                    wait_ms = step.get("advance_ms", 50)
                    lines.append(
                        " & ".join(
                            [
                                tex(step.get("cycle", "")),
                                tex(format_value(step.get("inputs", {}))),
                                tex(wait_ms),
                                tex(format_value(step.get("expected_outputs", {}))),
                                tex(step.get("check", "")),
                            ]
                        )
                        + r"\\"
                    )
                lines.extend([r"\bottomrule", r"\end{longtable}"])

def main() -> int:
    lines = [
        "% Generated from the frozen task, specification, and test JSON files.",
        r"\begingroup",
        r"\small",
    ]
    generate_custom_records(lines)
    generate_ltl(lines)
    generate_tests(lines)
    lines.append(r"\endgroup")
    OUTPUT.write_text("\n\n".join(lines) + "\n", encoding="utf-8")
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# encoding: utf-8
"""Compile one CODESYS project and save structured compiler messages.

This script runs inside CODESYS Scripting (IronPython 2.7), not CPython.
The project and result paths are read from ``PLC_AGENT_PROJECT_PATH`` and
``PLC_AGENT_RESULT_PATH``. Command-line arguments remain available as a
fallback for interactive debugging.
"""

from __future__ import print_function

import io
import json
import os
import sys
import traceback


def to_text(value):
    if value is None:
        return None
    try:
        return unicode(value)
    except NameError:
        return str(value)


def severity_name(severity):
    if severity == Severity.FatalError:
        return "fatal_error"
    if severity == Severity.Error:
        return "error"
    if severity == Severity.Warning:
        return "warning"
    if severity == Severity.Information:
        return "information"
    if severity == Severity.Text:
        return "text"
    return to_text(severity)


def collect_messages():
    records = []
    for category in system.get_message_categories(True):
        try:
            category_name = to_text(system.get_message_category_description(category))
        except Exception:
            category_name = to_text(category)

        for message in system.get_message_objects(category):
            obj = message.object
            try:
                object_name = to_text(obj.get_name()) if obj is not None else None
            except Exception:
                object_name = None

            records.append({
                "category": category_name,
                "severity": severity_name(message.severity),
                "number": to_text(message.number),
                "text": to_text(message.text),
                "object": object_name,
                "position": to_text(message.position_text),
            })
    return records


def write_result(path, result):
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent)
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    with io.open(path, "w", encoding="utf-8") as output_file:
        output_file.write(payload)


def read_optional_text(path_variable):
    path = os.environ.get(path_variable)
    if not path:
        return None
    with io.open(path, "r", encoding="utf-8") as input_file:
        return input_file.read()


def reference_function_block(project, pou_name):
    matches = project.find_ignore_transient_objects("PLC_PRG", recursive=True)
    if len(matches) != 1:
        raise RuntimeError(
            "Expected one PROGRAM named PLC_PRG, found {0}".format(len(matches))
        )

    program = matches[0]
    program.textual_declaration.replace(
        "PROGRAM PLC_PRG\n"
        "VAR\n"
        "    candidateInstance : {0};\n"
        "END_VAR\n".format(pou_name)
    )
    program.textual_implementation.replace("candidateInstance();\n")


def replace_pou_text(project, application):
    declaration = read_optional_text("PLC_AGENT_DECLARATION_PATH")
    implementation = read_optional_text("PLC_AGENT_IMPLEMENTATION_PATH")
    if declaration is None and implementation is None:
        return None
    if declaration is None or implementation is None:
        raise ValueError(
            "PLC_AGENT_DECLARATION_PATH and PLC_AGENT_IMPLEMENTATION_PATH "
            "must be set together"
        )

    pou_name = os.environ.get("PLC_AGENT_POU_NAME", "PLC_PRG")
    pou_type = os.environ.get("PLC_AGENT_POU_TYPE", "PROGRAM").upper()
    matches = project.find_ignore_transient_objects(pou_name, recursive=True)
    if len(matches) == 0 and pou_type == "FUNCTION_BLOCK":
        pou = application.create_function_block(name=pou_name)
    elif len(matches) == 1:
        pou = matches[0]
    else:
        raise RuntimeError(
            "Expected one POU named {0}, found {1}".format(pou_name, len(matches))
        )

    pou.textual_declaration.replace(declaration)
    pou.textual_implementation.replace(implementation)
    if pou_type == "FUNCTION_BLOCK":
        reference_function_block(project, pou_name)
    return pou_name


def main():
    project_arg = os.environ.get("PLC_AGENT_PROJECT_PATH")
    result_arg = os.environ.get("PLC_AGENT_RESULT_PATH")
    if not project_arg or not result_arg:
        if len(sys.argv) < 3:
            raise ValueError(
                "Set PLC_AGENT_PROJECT_PATH and PLC_AGENT_RESULT_PATH, "
                "or pass both paths through --scriptargs. sys.argv={0}".format(sys.argv)
            )
        project_arg = sys.argv[-2]
        result_arg = sys.argv[-1]

    project_path = os.path.abspath(project_arg)
    result_path = os.path.abspath(result_arg)
    project = None

    result = {
        "project_path": project_path,
        "success": False,
        "messages": [],
        "exception": None,
        "replaced_pou": None,
    }

    try:
        if projects.primary is not None:
            projects.primary.close()

        project = projects.open(project_path, primary=True)
        application = project.active_application
        if application is None:
            raise RuntimeError("The project has no active application")

        result["replaced_pou"] = replace_pou_text(project, application)
        application.rebuild()
        result["messages"] = collect_messages()
        result["success"] = not any(
            message["severity"] in ("fatal_error", "error")
            for message in result["messages"]
        )
    except Exception:
        result["exception"] = traceback.format_exc()
        try:
            result["messages"] = collect_messages()
        except Exception:
            pass
    finally:
        if project is not None:
            project.close()
        write_result(result_path, result)

    print("CODESYS_COMPILE_RESULT={0}".format(result_path))
    print("CODESYS_COMPILE_SUCCESS={0}".format(result["success"]))
    system.exit(0 if result["success"] else 2)


main()

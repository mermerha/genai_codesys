# encoding: utf-8
"""Compile a candidate, execute shared tests in Simulation, and save JSON.

This script runs inside CODESYS Scripting (IronPython 2.7).
"""

from __future__ import print_function

import io
import json
import os
import re
import traceback


def text(value):
    try:
        return unicode(value)
    except NameError:
        return str(value)


def read_json(variable):
    with io.open(os.environ[variable], "r", encoding="utf-8") as source:
        return json.loads(source.read())


def read_text(variable):
    with io.open(os.environ[variable], "r", encoding="utf-8") as source:
        return source.read()


def write_json(path, payload):
    with io.open(path, "w", encoding="utf-8") as target:
        target.write(json.dumps(payload, ensure_ascii=False, indent=2))


def severity_name(severity):
    if severity == Severity.FatalError:
        return "fatal_error"
    if severity == Severity.Error:
        return "error"
    if severity == Severity.Warning:
        return "warning"
    if severity == Severity.Information:
        return "information"
    return text(severity)


def collect_messages():
    records = []
    for category in system.get_message_categories(True):
        for message in system.get_message_objects(category):
            obj = message.object
            try:
                object_name = text(obj.get_name()) if obj is not None else None
            except Exception:
                object_name = None
            records.append({
                "severity": severity_name(message.severity),
                "number": text(message.number),
                "text": text(message.text),
                "object": object_name,
                "position": text(message.position_text),
            })
    return records


def create_custom_types(project, application, context):
    for custom_type in context.get("custom_types", []):
        matches = project.find_ignore_transient_objects(
            custom_type["name"], recursive=True
        )
        dut = matches[0] if matches else application.create_dut(
            name=custom_type["name"]
        )
        lines = ["TYPE {0} :".format(custom_type["name"]), "STRUCT"]
        for field in custom_type.get("fields", []):
            lines.append("    {0} : {1};".format(
                field["name"], field["data_type"]
            ))
        lines.extend(["END_STRUCT", "END_TYPE"])
        dut.textual_declaration.replace("\n".join(lines) + "\n")


def binding_map(context):
    return dict(
        (item["parameter"], item)
        for item in context.get("inout_bindings", [])
    )


def replace_candidate(project, application, request, context):
    task = request["task"]
    pou_name = task["pou_name"]
    matches = project.find_ignore_transient_objects(pou_name, recursive=True)
    if len(matches) == 0:
        pou = application.create_function_block(name=pou_name)
    elif len(matches) == 1:
        pou = matches[0]
    else:
        raise RuntimeError("Expected at most one candidate POU")
    pou.textual_declaration.replace(read_text("PLC_AGENT_DECLARATION_PATH"))
    pou.textual_implementation.replace(read_text("PLC_AGENT_IMPLEMENTATION_PATH"))

    bindings = binding_map(context)
    declaration = [
        "PROGRAM PLC_PRG",
        "VAR",
        "    candidateInstance : {0};".format(pou_name),
    ]
    arguments = []
    for item in task["interface"]:
        direction = item["direction"].lower()
        name = item["name"]
        data_type = item["data_type"]
        if direction == "input":
            declaration.append("    test_{0} : {1};".format(name, data_type))
            arguments.append("{0} := test_{0}".format(name))
        elif direction == "output":
            declaration.append("    actual_{0} : {1};".format(name, data_type))
            arguments.append("{0} => actual_{0}".format(name))
        elif direction == "inout":
            binding = bindings.get(name)
            if binding is None:
                raise ValueError("Missing inout binding for {0}".format(name))
            declaration.append("    {0} : {1};".format(
                binding["variable"], binding["data_type"]
            ))
            arguments.append("{0} := {1}".format(name, binding["variable"]))
        else:
            raise ValueError("Unsupported interface direction {0}".format(direction))
    declaration.append("END_VAR")

    programs = project.find_ignore_transient_objects("PLC_PRG", recursive=True)
    if len(programs) != 1:
        raise RuntimeError("Expected one PLC_PRG")
    programs[0].textual_declaration.replace("\n".join(declaration) + "\n")
    programs[0].textual_implementation.replace(
        "candidateInstance({0});\n".format(", ".join(arguments))
    )


def find_device(project):
    devices = []
    for obj in project.get_children(recursive=True):
        if hasattr(obj, "set_simulation_mode"):
            devices.append(obj)
    if len(devices) != 1:
        raise RuntimeError(
            "Expected one programmable device, found {0}".format(len(devices))
        )
    return devices[0]


def array_lower_bound(data_type):
    match = re.match(r"^ARRAY\[\s*(-?\d+)\.\.", data_type, re.IGNORECASE)
    return int(match.group(1)) if match else 1


def interface_map(task):
    return dict((item["name"], item) for item in task["interface"])


def root_expression(name, item, bindings):
    direction = item["direction"].lower()
    if direction == "input":
        return "PLC_PRG.test_{0}".format(name)
    if direction == "output":
        return "PLC_PRG.actual_{0}".format(name)
    if direction == "inout":
        return "PLC_PRG.{0}".format(bindings[name]["variable"])
    raise ValueError("Unsupported interface direction")


def flatten_value(expression, value, data_type):
    if isinstance(value, list):
        lower = array_lower_bound(data_type)
        flattened = []
        for offset, item in enumerate(value):
            flattened.extend(flatten_value(
                "{0}[{1}]".format(expression, lower + offset), item, ""
            ))
        return flattened
    if isinstance(value, dict):
        flattened = []
        for name, item in value.items():
            flattened.extend(flatten_value(
                "{0}.{1}".format(expression, name), item, ""
            ))
        return flattened
    return [(expression, value)]


def prepared_literal(value):
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (int, float)):
        return text(value)
    value_text = text(value)
    if re.match(r"^(?:[A-Za-z]+#|16#)", value_text):
        return value_text
    return "'{0}'".format(value_text.replace("'", "''"))


def parse_numeric(value):
    cleaned = text(value).strip()
    if "#" in cleaned:
        parts = cleaned.split("#")
        if len(parts) >= 2 and parts[-2] == "16":
            return int(parts[-1], 16)
        cleaned = parts[-1]
    return float(cleaned) if "." in cleaned else int(cleaned)


def parse_duration(value):
    cleaned = text(value).strip().upper()
    if "#" not in cleaned:
        raise ValueError("not an IEC duration")
    body = cleaned.split("#", 1)[1]
    units = {
        "D": 86400000000000,
        "H": 3600000000000,
        "M": 60000000000,
        "S": 1000000000,
        "MS": 1000000,
        "US": 1000,
        "NS": 1,
    }
    total = 0.0
    position = 0
    for match in re.finditer(r"(\d+(?:\.\d+)?)(MS|US|NS|D|H|M|S)", body):
        if match.start() != position:
            raise ValueError("invalid IEC duration")
        total += float(match.group(1)) * units[match.group(2)]
        position = match.end()
    if position != len(body):
        raise ValueError("invalid IEC duration")
    return int(round(total))


def values_equal(actual, expected):
    actual_text = text(actual).strip()
    if isinstance(expected, bool):
        return actual_text.upper() == ("TRUE" if expected else "FALSE")
    if isinstance(expected, (int, float)):
        try:
            actual_number = parse_numeric(actual_text)
        except Exception:
            return False
        if isinstance(expected, float):
            return abs(float(actual_number) - expected) <= 0.0001
        return actual_number == expected
    expected_text = text(expected).strip()
    if re.match(r"^(?:T|TIME|LT|LTIME)#", expected_text, re.IGNORECASE):
        try:
            return parse_duration(actual_text) == parse_duration(expected_text)
        except Exception:
            return False
    if re.match(r"^(?:[A-Za-z]+#)?16#", expected_text, re.IGNORECASE):
        try:
            return parse_numeric(actual_text) == parse_numeric(expected_text)
        except Exception:
            return False
    return actual_text.strip("'\"").upper() == expected_text.strip("'\"").upper()


def prepare_values(online_application, values):
    for expression, value in values:
        online_application.set_prepared_value(
            expression, prepared_literal(value)
        )
    online_application.write_prepared_values()


def run_tests(online_application, request, context):
    task = request["task"]
    test_document = request["tests"]
    settle_ms = int(request.get("settle_ms", 50))
    interfaces = interface_map(task)
    bindings = binding_map(context)
    results = []

    for test_case in test_document["tests"]:
        if online_application.application_state == ApplicationState.run:
            online_application.stop()
        online_application.reset(ResetOption.Cold)

        initial_writes = []
        initial_checks = []
        for name, value in test_case.get("initial_state", {}).items():
            item = interfaces.get(name)
            if item is None:
                raise ValueError(
                    "Test {0} refers to non-interface initial state {1}".format(
                        test_case["id"], name
                    )
                )
            flattened = flatten_value(
                root_expression(name, item, bindings), value, item["data_type"]
            )
            if item["direction"].lower() == "output":
                initial_checks.extend(flattened)
            else:
                initial_writes.extend(flattened)
        if initial_writes:
            prepare_values(online_application, initial_writes)

        online_application.start()
        if initial_checks:
            system.delay(settle_ms)
            actual = online_application.read_values(
                [item[0] for item in initial_checks]
            )
            for index, expected_item in enumerate(initial_checks):
                if not values_equal(actual[index], expected_item[1]):
                    raise ValueError(
                        "Initial output mismatch in {0}: {1}".format(
                            test_case["id"], expected_item[0]
                        )
                    )

        step_results = []
        test_passed = True
        failed_step = None
        for step in test_case["steps"]:
            writes = []
            for name, value in step.get("inputs", {}).items():
                item = interfaces[name]
                if item["direction"].lower() == "output":
                    raise ValueError("Cannot write output {0}".format(name))
                writes.extend(flatten_value(
                    root_expression(name, item, bindings),
                    value,
                    item["data_type"],
                ))
            if writes:
                prepare_values(online_application, writes)

            delay_ms = int(step.get("advance_ms", 0))
            system.delay(delay_ms if delay_ms > 0 else settle_ms)

            expected_values = []
            for name, value in step.get("expected_outputs", {}).items():
                item = interfaces[name]
                expected_values.extend(flatten_value(
                    root_expression(name, item, bindings),
                    value,
                    item["data_type"],
                ))
            expressions = [item[0] for item in expected_values]
            actual_values = online_application.read_values(expressions)
            differences = []
            actual_record = {}
            for index, expected_item in enumerate(expected_values):
                expression, expected = expected_item
                actual_value = text(actual_values[index])
                actual_record[expression] = actual_value
                if not values_equal(actual_value, expected):
                    differences.append({
                        "expression": expression,
                        "expected": expected,
                        "actual": actual_value,
                    })
            step_passed = len(differences) == 0
            if not step_passed and failed_step is None:
                failed_step = step["cycle"]
            test_passed = test_passed and step_passed
            step_results.append({
                "cycle": step["cycle"],
                "passed": step_passed,
                "actual_outputs": actual_record,
                "differences": differences,
            })

        results.append({
            "test_id": test_case["id"],
            "passed": test_passed,
            "failed_step": failed_step,
            "steps": step_results,
        })
    return results


def main():
    result_path = os.environ["PLC_AGENT_RESULT_PATH"]
    project_path = os.environ["PLC_AGENT_PROJECT_PATH"]
    request = read_json("PLC_AGENT_TEST_REQUEST_PATH")
    context = read_json("PLC_AGENT_COMPILE_CONTEXT_PATH")
    project = None
    payload = {
        "success": False,
        "compile_success": False,
        "compile_messages": [],
        "test_passed": 0,
        "test_total": len(request["tests"].get("tests", [])),
        "tests": [],
        "exception": None,
    }
    exit_code = 2
    try:
        if projects.primary is not None:
            projects.primary.close()
        project = projects.open(project_path, primary=True)
        application = project.active_application
        create_custom_types(project, application, context)
        replace_candidate(project, application, request, context)
        application.rebuild()
        payload["compile_messages"] = collect_messages()
        payload["compile_success"] = not any(
            item["severity"] in ("error", "fatal_error")
            for item in payload["compile_messages"]
        )
        if not payload["compile_success"]:
            raise RuntimeError("Candidate or test wrapper did not compile")

        project.save()
        find_device(project).set_simulation_mode(True)
        online_application = online.create_online_application(application)
        try:
            online_application.login(OnlineChangeOption.Never, True)
            payload["tests"] = run_tests(
                online_application, request, context
            )
            payload["test_passed"] = sum(
                1 for item in payload["tests"] if item["passed"]
            )
            payload["success"] = (
                payload["test_passed"] == payload["test_total"]
            )
            exit_code = 0 if payload["success"] else 3
        finally:
            try:
                online_application.stop()
                online_application.logout()
            except Exception:
                pass
            dispose = getattr(online_application, "Dispose", None)
            if dispose is not None:
                dispose()
    except Exception:
        payload["exception"] = traceback.format_exc()
    finally:
        if project is not None:
            project.close()
        write_json(result_path, payload)
    system.exit(exit_code)


main()

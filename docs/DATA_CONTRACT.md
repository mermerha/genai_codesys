# 数据接口草案

版本：0.5
状态：单 POU 模型输出、题库、工具无关 LTL、共享测试标准和自动执行语义已冻结。

目标是让题库、LTL、测试、Agent 和实验分析能够独立开发，通过文件接口集成。

## 标识规则

- 公共题：`public_01` 至 `public_20`。
- 自建题：`custom_01` 起。
- 测试用例：`<task_id>_tc01` 起。
- 规约：`<task_id>_p01` 起。
- ID 一旦进入正式实验不得复用或静默修改。

## 题目记录

正式数据每题一个 JSON，最低字段：

```json
{
  "id": "public_01",
  "title": "Automated Filling Line Control",
  "difficulty": "easy",
  "source_type": "provided",
  "source_reference": "大作业题库",
  "requirements": "自然语言需求",
  "pou_name": "FB_Example",
  "pou_type": "FUNCTION_BLOCK",
  "interface": [],
  "custom_types": [],
  "review": {
    "status": "pending",
    "reviewer": null,
    "notes": []
  }
}
```

自建题还需记录：

```json
{
  "provenance": {
    "source_type": "self_conceived | experience_based | synthetic | public_web",
    "source_url": null,
    "creation_process": [],
    "human_modifications": [],
    "review_process": []
  },
  "plc_rationale": "实际 PLC 场景合理性说明",
  "diversity_tags": ["任务类型", "控制特征", "难度"]
}
```

`public_web` 必须填写原始链接；`synthetic` 必须说明合成过程。所有自建题都必须说明人工修改、审核过程和 PLC 合理性。

`pou_name` 是该题要求模型使用的固定 IEC 标识符；同一道题在全部实验设置下保持一致。

需要 DUT 或 `VAR_IN_OUT` 的题目可增加：

```json
{
  "custom_types": [
    {
      "name": "ST_Example",
      "kind": "STRUCT",
      "fields": [{"name": "value", "data_type": "DINT"}]
    }
  ],
  "compile_context": {
    "inout_bindings": [
      {
        "parameter": "items",
        "variable": "candidateItems",
        "data_type": "ARRAY[1..10] OF ST_Example"
      }
    ]
  }
}
```

`custom_types` 在临时 CODESYS 工程中创建 DUT；`inout_bindings` 只提供使候选进入真实调用链所需的固定测试变量，不改变题目正式接口。

## LTL 规约记录

```json
{
  "task_id": "public_01",
  "state_semantics": "待统一定义",
  "propositions": {},
  "assumptions": [],
  "properties": [
    {
      "id": "public_01_p01",
      "type": "safety",
      "description": "自然语言说明",
      "ltl": "工具无关的 ASCII 表达式",
      "tool_expression": null
    }
  ],
  "review": {
    "status": "pending",
    "reviewer": null,
    "notes": []
  }
}
```

`tool_expression` 只有在确定 PLCVerif 或其他工具的实际语法后填写，不能凭空假设。

当前 LTL 使用工具无关的 ASCII 写法：`G` 表示始终，`F` 表示最终，`X` 表示下一次扫描后的状态，`GF` 表示反复发生，`!`、`&&`、`||`、`->` 分别表示非、与、或、蕴含。比较、计时完成和状态关系先定义成命题，再在公式中引用；正式接入验证工具时再转换到具体语法。

## 测试用例记录

这里定义的是所有实验设置共享的“测试标准”，只保存输入、预期输出和覆盖内容，不保存任何一次运行的实际输出或通过状态。

```json
{
  "id": "public_01_tc01",
  "task_id": "public_01",
  "name": "正常启动并保持运行",
  "initial_state": {},
  "steps": [
    {
      "cycle": 0,
      "inputs": {},
      "expected_outputs": {},
      "check": "检查内容"
    }
  ],
  "coverage": ["initialization", "normal_flow"],
  "review": {
    "status": "pending",
    "reviewer": null,
    "notes": []
  }
}
```

正式实验的实际输出不能回写或覆盖标准测试定义。每次运行的 `test_results.json` 另行保存测试 ID、逐步骤实际输出、失败差异和通过状态，保证四种设置共享同一个测试标准。

为减少文件数量，正式测试按任务保存为 `data/test_cases/public/<task_id>.json` 或 `data/test_cases/custom/<task_id>.json`，顶层格式为 `{"task_id": "...", "tests": [...]}`。步骤可包含可选字段 `advance_ms`，表示执行该次扫描前经过的时间，缺省为 0；`expected_outputs` 只列出该步骤需要检查的输出。

`tests/fixtures/` 中允许使用一个顶层对象包装 `task`、`spec` 和 `tests`，以便单文件完成集成测试；正式题库分别存放在 `data/tasks/public/`、`data/tasks/custom/`、`data/specs/` 和 `data/test_cases/`。

每个测试用例执行前对 CODESYS Simulation 做冷复位。`initial_state` 只能引用题目公开接口：输入和 `inout` 值在启动前写入，输出值在启动后的初始化扫描中检查；禁止引用候选内部变量。需要特定内部状态时，必须通过前置测试步骤和公开输入到达。

步骤中的 `inputs` 允许只列出本步骤改变的公开输入，未列出的输入保持上一测试步骤的值。`advance_ms` 表示写入本步骤输入后等待的真实时间；定时边界必须留出足够扫描和脚本通信裕量，不能使用 1 ms 等脆弱边界判断。

## Agent 候选输出（首版已冻结）

首版模型必须只返回以下四个字符串字段：

```json
{
  "pou_name": "FB_Example",
  "pou_type": "FUNCTION_BLOCK",
  "declaration": "...",
  "implementation": "..."
}
```

- `pou_name` 必须是 IEC 标识符。
- `pou_type` 首版只支持 `PROGRAM` 和 `FUNCTION_BLOCK`；`PROGRAM` 固定使用模板中的 `PLC_PRG`。
- `declaration` 包含完整 POU 头和变量声明；`implementation` 只包含 ST 实现体。
- 不接受解释文字或额外 JSON 字段；允许整个 JSON 外包一层 Markdown 代码围栏。
- 编译 `FUNCTION_BLOCK` 时，harness 会在临时工程的 `PLC_PRG` 中自动实例化并调用候选对象，确保其真正进入 CODESYS 编译链。
- 需要 DUT、GVL 或多个 POU 的题目在扩展接口前不得进入首版正式实验。

## 单次实验结果

最低字段：

```json
{
  "run_id": "唯一运行标识",
  "task_id": "public_01",
  "framework": "baseline_or_custom",
  "model": "准确模型标识",
  "config_id": "冻结配置标识",
  "attempts": [],
  "first_compile_pass": false,
  "final_compile_pass": false,
  "test_passed": 0,
  "test_total": 0,
  "test_results_file": "相对于 artifact_directory 的逐用例结果文件",
  "final_status": "success_or_failure_or_timeout",
  "duration_seconds": 0,
  "usage": {},
  "failure_reason": null,
  "artifact_directory": "相对路径"
}
```

每个 `attempt` 应保存提示词、原始响应、解析后的候选代码、编译消息、耗时和终止判断。原始响应不能只保留经过清洗的版本。

`test_results_file` 指向逐用例测试结果。该文件至少为每个测试用例保存：测试 ID、各步骤实际输出、通过/不通过、失败步骤和差异说明。汇总字段 `test_passed` 与 `test_total` 必须由该文件计算，不得手工填写后失去追溯。

## 指标定义

- 首次编译通过率：第一次生成后即编译通过的任务数 / 该实验设置的任务总数。
- 修复 `n` 次累计编译通过率：在首次生成及最多 `n` 次修复内编译通过的任务数 / 任务总数。
- 测试用例通过率：通过的测试用例数 / 实际执行的测试用例总数。
- 整体任务通过率：全部规定测试用例均通过的任务数 / 任务总数。
- 平均修复次数：按任务记录的实际修复轮次平均值；失败任务同样保留实际轮次。
- 时间与资源：至少记录单任务总耗时和可获得的模型 Token 用量；费用只有在模型价格和计算口径冻结后汇总。

## 原始实验目录与不可覆盖规则

建议结构：

```text
experiments/raw/<run_id>/<task_id>/<framework>__<model>/
├── run_config.json
├── attempt_00/
├── attempt_01/
├── test_results.json
└── final_result.json
```

- `run_id` 使用本地时间 `YYYYMMDD_HHMMSS` 加短随机后缀，完整时间与时区另写入元数据。
- 创建运行目录时若目标已存在，应立即报错，不允许覆盖。
- 开发和实验配置模板统一放在 `config/`；`run_config.json` 保存本次正式运行实际使用的完整配置快照。正式结果以运行目录中的快照为准。
- 汇总程序只读取原始目录生成 `experiments/processed/`，不得反向修改原始结果。

## 正式实验前仍需确定

- 正式实验参数、超时、模型版本和基线 Agent。
- 不同模型 API 返回的 Token、费用和模型版本字段映射。

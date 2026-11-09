# 数据接口草案

版本：0.3
状态：单 POU 模型输出接口已冻结；正式题库、LTL 和测试接口仍为草案。

目标是让题库、LTL、测试、Agent 和实验分析能够独立开发，通过文件接口集成。

## 标识规则

- 公共题：`public_01` 至 `public_20`。
- 自建题：`custom_01` 起。
- 测试用例：`<task_id>_tc01` 起。
- 规约：`<task_id>_p01` 起。
- ID 一旦进入正式实验不得复用或静默修改。

## 题目记录

正式数据建议每题一个 JSON，最低字段：

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

自建题还需记录：生成提示或原始链接、人工修改、PLC 场景合理性、多样性标签和审核过程。

`pou_name` 是该题要求模型使用的固定 IEC 标识符；同一道题在全部实验设置下保持一致。

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

`tests/fixtures/` 中允许使用一个顶层对象包装 `task`、`spec` 和 `tests`，以便单文件完成集成测试；正式题库分别存放在 `data/tasks/public/`、`data/tasks/custom/`、`data/specs/` 和 `data/test_cases/`。

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

## 冻结前必须解决的问题

- 公共题 JSON 中英文文本的处理方式。
- 一个文件一题还是单一数组文件。
- POU、DUT、GVL 等多对象任务的表示方式。
- LTL 扫描周期语义。
- 测试步骤中时间、定时器和模拟量的表示方式。
- CODESYS 错误消息的结构化字段。
- 不同模型 API 返回的 Token、费用和模型版本字段映射。

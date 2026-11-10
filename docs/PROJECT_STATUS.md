# 项目状态

最后更新：2026-11-10

## 当前阶段

题库、工具无关 LTL 和共享测试标准已经重新冻结。自研 harness 的生成、CODESYS 编译、错误反馈、修复和自动功能测试闭环可用；模型 A 为 `deepseek-v4.1-flash-1017`，模型 B 暂定为 `qwen3-coder-flash`，使用默认推理配置，不传 `reasoning_effort`。

现成 Agent 基线已由 `smolagents CodeAgent` 更换为 `Codex CLI 0.167.0-alpha.3.2`，并与自研 harness 共用 CODESYS Simulation 自动测试执行器。四种设置的 12 次小规模预跑和 30 道题、四种设置共 120 次正式运行均已完成；正式清单无缺失、无重复、无未处理的运行器错误。

正式批次运行到 59 条时发现连续 DMXAPI SSL 断连；确认 15 条为基础设施失败后，在同一批次中完成续跑。有效结果保持不变，故障项写入独立 retry 目录并保留旧证据。

## 已完成

- 已核对中文版作业要求、20 道公共题、测试模板和 DMXAPI 说明。
- 已建立项目规则、要求清单、流程、决策记录和数据接口。
- 已实现纯 Python 调用 CODESYS、结构化错误提取和真实 `FUNCTION_BLOCK` 主程序引用链。
- 已实现 DMXAPI 客户端、严格候选解析和单题生成—编译—修复循环。
- 已支持通过 `compile_context` 创建 DUT 和绑定数组 `VAR_IN_OUT`；正确与错误候选均经过真实 CODESYS 编译验证。
- `public_18` 已统一适配为容量 10 的 DINT FIFO，并记录原始接口、适配原因和公平性说明。
- 20 道公共题、20 份 LTL 和 61 个测试用例已冻结，共 92 条性质和 201 个测试步骤。
- 已建立 10 道自建题、10 份 LTL 和 30 个测试用例，共 42 条性质和 79 个测试步骤。
- 自建题难度分布为 easy 3、medium 4、hard 3；来源分布为自主构思 2、经验改编 6、规则合成 2。每题均包含来源、创建或改编过程、人工修改、审核过程、PLC 合理性和多样性标签。
- 全部 30 道题的 JSON、ID、命题引用、接口字段和冻结状态校验通过。
- Codex CLI 基线每题最多生成 3 个候选；外部循环只反馈上一候选和 CODESYS 编译错误，测试用例不向 Agent 开放；模型轨迹、候选、编译和测试证据均会保存。
- 固定联调题真实验证：模型 A 首次编译通过；模型 B 修复一次候选格式后编译通过。
- 自动测试执行器已接入两种 Agent：每个测试前冷复位，只读写公开接口，并保存逐步骤实际输出与差异。
- 原先依赖候选内部状态或非默认输出状态的测试已改为通过公开输入建立状态；脆弱的 1 ms 定时边界已改为带扫描裕量的检查。
- Python 测试共 16 项：12 项通过，4 项真实 CODESYS 集成测试按默认配置跳过。
- 真实自动测试验证：正确电机候选 2/2、`public_03` 3/3、FIFO 3/3、定时看门狗 3/3 通过；错误电机候选 0/2 且失败步骤和差异记录正确；完整自研 harness 2/2 通过。
- `config/experiment.json` 已冻结模型、修复次数、超时、测试方式和 easy/medium/hard 预跑题；批量入口会依次执行四种设置并持续写入清单。
- Codex CLI 模型 B 固定联调样例首次编译通过，共享测试 2/2 通过；此前未完成的 smolagents 预跑已停止，不计入实验结果。
- 新预跑批次 12/12 完成：`public_03` 四组均为 3/3；`public_09` 的自研 deepseek、自研 qwen、Codex deepseek、Codex qwen 分别为 2/3、2/3、2/3、1/3；`public_19` 两个 deepseek 设置均为 4/4，两个 qwen 设置均为 0/4。
- 正式实验支持在冻结配置不变的前提下续跑；只重跑有明确 SSL、连接重试或 CODESYS 执行器故障证据的条件，模型质量、编译失败和功能测试失败不重跑。
- 正式实验 120/120 完成；最终状态为成功 43、功能测试失败 52、编译失败 25，无 `runner_error`。
- 已生成逐任务 CSV/JSON、四种设置汇总 CSV/JSON 和报告用 Markdown 分析；测试通过率统一以每组固定的 92 个计划测试用例为分母。
- 模型预验证与困难题对比已完成，模型 B 暂定为 `qwen3-coder-flash`；这些结果仅用于选型，不计入正式实验。

## 数据集规模

| 数据 | 题目 | LTL 性质 | 测试用例 | 测试步骤 |
|---|---:|---:|---:|---:|
| 公共题 | 20 | 92 | 62 | 263 |
| 自建题 | 10 | 42 | 30 | 81 |
| 合计 | 30 | 134 | 92 | 344 |

冻结只表示题面、规约和测试标准已经确定；LTL 尚未接入具体形式化验证工具，自动测试只完成环境验证，尚未执行四种设置的正式实验。

## 保留证据

- 原始材料说明：[`SOURCE_MATERIALS.md`](SOURCE_MATERIALS.md)。
- 作业验收清单：[`REQUIREMENTS.md`](REQUIREMENTS.md)。
- 数据接口：[`DATA_CONTRACT.md`](DATA_CONTRACT.md)。
- 固定联调样例：`tests/fixtures/motor_start_stop_fixture.json`。
- 纯 Python 正确/错误编译：`experiments/raw/environment_validation/20261105_104535_python_valid/`、`20261105_104535_python_invalid/`。
- 功能块正确/错误编译：`experiments/raw/environment_validation/20261105_192949_function_block_valid/`、`20261105_192949_function_block_invalid/`。
- DUT 与数组 `VAR_IN_OUT` 正确/错误编译：`experiments/raw/environment_validation/20261109_172822_special_interface_valid/`、`20261109_172822_special_interface_invalid/`。
- 固定 DINT FIFO 正确/错误编译：`experiments/raw/environment_validation/20261109_173225_fifo_interface_valid/`、`20261109_173225_fifo_interface_invalid/`。
- Codex CLI 模型 B 联调：`experiments/raw/development/20261109_232345_fixture_motor_start_stop_qwen3-coder-flash_codex_cli/`。
- Codex CLI 替换后的完整预跑：`experiments/raw/pre_run/20261109_232534_341da0/`。
- 正式实验批次：`experiments/raw/formal/20261109_234635_2ba96d/`。
- 正式逐任务汇总：`experiments/processed/formal_runs.csv`、`formal_runs.json`。
- 四种设置汇总：`experiments/processed/formal_summary.csv`、`formal_summary.json`。
- 报告用分析表：`experiments/analysis/formal_analysis.md`。
- 自动测试正确/错误样例：`experiments/raw/environment_validation/20261109_184703_auto_test_valid/`、`20261109_184738_auto_test_wrong/`。
- 公共标量题、FIFO 和定时题：`experiments/raw/environment_validation/20261109_185616_public_03_auto_test/`、`20261109_185719_public_18_auto_test/`、`20261109_185944_custom_09_auto_test/`。
- 完整 harness 自动测试：`experiments/raw/environment_validation/20261109_190157_harness_auto_test/`。
- 模型选型原始记录保存在 `experiments/raw/development/`，不计入正式实验结果。

正式证据只使用模型原始响应、提示词、候选 ST、配置和编译 JSON；可重新生成的工程文件和缓存由 Git 忽略。

## 当前缺口

- 实验报告、PPT、演示录屏和最终提交检查尚未完成。

## 接下来

1. 根据正式汇总和案例候选编写实验报告。
2. 完成 PPT、演示录屏和最终提交检查。

## 更新规则

- 未实际验证的内容标为待办，不写成已完成。
- 只有阶段成果、阻塞或下一步实质变化时更新本文件。
- 报告数字必须追溯到保留的原始记录或汇总结果。

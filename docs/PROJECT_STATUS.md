# 项目状态

最后更新：2026-11-05

## 当前阶段

项目治理和目录整理已完成初版。真实 `FUNCTION_BLOCK` 创建、引用、自动编译与结构化错误提取已经通过验证；单 POU 模型输出接口已冻结。模型 A 已完成一次真实生成—编译闭环，模型 B 的服务路由连续两次超时。

完整要求见 [`REQUIREMENTS.md`](REQUIREMENTS.md)，完整阶段流程见 [`WORKFLOW.md`](WORKFLOW.md)。本文件只记录当前事实、阻塞和近期行动。

## 最近完成

- 已核对最新版中文作业要求、20 道公共题、测试模板和 DMXAPI 说明。
- 已建立 `AGENTS.md`、README、要求清单、流程、决策记录和数据接口草案。
- 已建立 `tests/fixtures/motor_start_stop_fixture.json` 作为非正式题库的联调样例。
- 已明确同一道题在四种实验设置下使用相同测试和判定标准。
- 已简化项目目录：配置统一到 `config/`，分析归入 `experiments/analysis/`，PPT 和演示材料归入 `report/`。
- 已确认原始材料保持在 `genai/` 和 `大作业题库json/`，并修正文档指引。
- 已盘点 Python 3.12.4、CODESYS V3.5 SP22 Patch 4、CODESYS Scripting 4.2.0.0、Control Win x64 和 Gateway。
- 已创建固定模板工程 `codesys/template/测试工程.project`。
- 已实现 `codesys/scripts/compile_project.py` 和 `src/plc_agent/codesys_runner.py`，能够由 CPython 直接替换 `PLC_PRG`、无界面编译并输出结构化 JSON。
- 正确 ST 已验证为 0 错误、0 警告；故意缺少分号的错误 ST 已提取错误号、对象、位置和错误文本。
- 已将完整项目迁移到纯英文根路径 `G:\Genai_codesys`，项目内部相对结构保持不变；迁移后正确和错误两个 CODESYS 样例均复验通过。
- 纯 Python 正确/错误集成测试均已通过；项目不再使用或保留 `run_compile.ps1`。
- 已验证脚本可在模板应用中创建 `MotorControl` 功能块，并由 `PLC_PRG` 自动实例化和调用，保证候选代码真正进入编译链。
- 功能块正确样例编译为 0 错误；包含未定义标识符的错误样例返回错误号、对象、位置和文本。
- `docs/DATA_CONTRACT.md` 0.2 已冻结首版单 POU 四字段模型输出接口。
- 已实现无额外 SDK 的 DMXAPI 客户端、严格候选解析和单题生成—编译—修复闭环；10 项 Python 测试通过，2 项真实 CODESYS 测试按默认设置跳过。
- Git 仓库已建立，`main` 跟踪 GitHub `origin/main`。
- DMXAPI 模型列表已确认 `deepseek-v4.1-flash-1017` 和 `doubao-seed-2-1-pro-260628` 均为该密钥可见的准确 ID。
- 模型 A `deepseek-v4.1-flash-1017` 已真实生成 `MotorStartStop` 功能块并首次编译通过：0 错误、0 警告、无修复，总耗时 33.234 秒；API 实际返回模型标识 `DeepSeek-V4.1-Flash-261017`，总 Token 1340。
- 模型 A 候选经人工快速复核，满足停止/急停优先、启动置位和松开启动后保持三项样题行为。
- 模型 B `doubao-seed-2-1-pro-260628` 在相同任务上分别于 120 秒和 300 秒达到读取超时，均未收到模型输出、未进入 CODESYS。

## 当前证据

- 原始材料及 SHA-256：[`SOURCE_MATERIALS.md`](SOURCE_MATERIALS.md)。
- 老师要求验收清单：[`REQUIREMENTS.md`](REQUIREMENTS.md)。
- 当前数据接口草案：[`DATA_CONTRACT.md`](DATA_CONTRACT.md)。
- 固定联调样例：`tests/fixtures/motor_start_stop_fixture.json`。
- 正确 ST 编译结果：`experiments/raw/environment_validation/20261104_175110_715_valid/compile_result.json`。
- 错误 ST 编译结果：`experiments/raw/environment_validation/20261104_175146_857_invalid/compile_result.json`。
- 固化启动脚本复验结果：`experiments/raw/environment_validation/20261104_175316_987_launcher_valid/compile_result.json`。
- 迁移后正确 ST 编译结果：`experiments/raw/environment_validation/20261105_102148_979_post_move_valid/compile_result.json`。
- 迁移后错误 ST 编译结果：`experiments/raw/environment_validation/20261105_102309_067_post_move_invalid/compile_result.json`。
- 纯 Python 正确 ST 编译结果：`experiments/raw/environment_validation/20261105_104535_python_valid/compile_result.json`。
- 纯 Python 错误 ST 编译结果：`experiments/raw/environment_validation/20261105_104535_python_invalid/compile_result.json`。
- 功能块正确样例：`experiments/raw/environment_validation/20261105_192949_function_block_valid/compile_result.json`。
- 功能块错误样例：`experiments/raw/environment_validation/20261105_192949_function_block_invalid/compile_result.json`。
- 模型 A 真实闭环：`experiments/raw/development/20261105_195953_deepseek-v4.1-flash-1017/`。
- 模型 B 120 秒超时：`experiments/raw/development/20261105_200039_doubao-seed-2-1-pro-260628/`。
- 模型 B 300 秒超时：`experiments/raw/development/20261105_200337_doubao-seed-2-1-pro-260628/`。

## 当前阻塞

- 模型 B 路由连续两次超时，需决定更换模型或联系 DMXAPI/助教排查。
- 现成 Agent 基线和正式实验参数尚未确定。
- 团队名单、技术负责人和正式实验机尚未记录。

## 接下来四步

1. 决定模型 B 是更换为其他可用模型，还是先联系服务方排查当前路由。
2. 确认现成 Agent 基线候选。
3. 转换 20 道公共题，并由人工复核题意和接口。
4. 分工设计、复核并冻结 LTL 与测试标准。

## 更新规则

- “已完成”必须有文件、日志或运行结果支持。
- 只有阶段性成果、阻塞或下一步发生实质变化时更新本文件。
- 不在这里复制完整要求清单或长期流程。

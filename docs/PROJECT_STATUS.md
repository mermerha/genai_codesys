# 项目状态

最后更新：2026-11-05

## 当前阶段

项目治理和目录整理已完成初版。纯 Python CODESYS 自动编译与结构化错误提取已经通过最小验证，当前进入“最小接口冻结、模型 API 验证和单题生成—编译—修复闭环”。

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

## 当前阻塞

- 尚未完成一次真实 DMXAPI 模型调用。
- 模型 A、模型 B、现成 Agent 基线和正式实验参数尚未确定。
- 团队名单、技术负责人和正式实验机尚未记录。
- 当前项目目录尚未检测到 Git 仓库。

## 接下来四步

1. 用固定联调样例验证并冻结最小数据接口。
2. 完成一次真实 DMXAPI 模型调用，但不保存真实密钥。
3. 实现单题生成—编译—修复闭环。
4. 确认两个模型和基线 Agent 候选。

## 更新规则

- “已完成”必须有文件、日志或运行结果支持。
- 只有阶段性成果、阻塞或下一步发生实质变化时更新本文件。
- 不在这里复制完整要求清单或长期流程。

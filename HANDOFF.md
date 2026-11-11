# 项目交接说明

本文面向第一次接触项目的同学，说明项目做了什么、各目录负责什么、如何运行代码，以及实验结果保存在哪里。所有命令默认在项目根目录 `G:\Genai_codesys` 下执行。

## 1. 项目概况

本项目实现了一个面向 CODESYS 的 Structured Text（ST）代码生成 Agent。输入是 PLC 自然语言需求，系统会调用模型生成 ST 候选代码，进行接口预检，交给 CODESYS 编译，根据编译错误修复代码，并在 CODESYS Simulation 中自动执行固定测试用例。

实验包含：

- 20 道老师提供的公共题；
- 10 道自建 PLC 题；
- 自研 harness 和 Codex CLI 两种框架；
- `deepseek-v4.1-flash-1017` 和 `qwen3-coder-flash` 两个模型；
- 共 30 × 2 × 2 = 120 个正式实验条件。

当前最终正式实验已经完成 120/120。项目保留了初始完整实验和最终正式实验，用于报告中的前后对比；中间版本和预测试原始记录已经清理。

需要区分两个状态：代码和正式实验已经完成，但最终提交物还没有完成。目前仍需补成员信息、重新生成两个 PDF、制作 PPT 和录屏。

## 2. 接手后先看什么

建议按下面的顺序阅读：

1. `README.md`：项目入口和最常用命令。
2. `docs/PROJECT_STATUS.md`：当前进度、保留证据和剩余工作。
3. 本文：目录结构和完整运行流程。
4. `docs/REQUIREMENTS.md`：课程作业的硬性要求。
5. `docs/DATA_CONTRACT.md`：题目、LTL、测试和结果的 JSON 格式。
6. `docs/DECISIONS.md`：模型、基线 Agent 和架构选择的原因。

## 3. 工作目录结构

```text
G:\Genai_codesys\
├── README.md                     项目入口
├── HANDOFF.md                    本交接文档
├── AGENTS.md                     项目开发和修改规则
├── .env                          本机 API 配置，不得提交
├── genai\                        老师原始 PDF、DOCX 和说明，只读保留
├── 大作业题库json\               老师提供的原始公共题，只读保留
├── data\                         已转换并冻结的实验数据
│   ├── tasks\public\             20 道公共题
│   ├── tasks\custom\             10 道自建题及来源、审核记录
│   ├── specs\                    30 道题的工具无关 LTL
│   └── test_cases\               30 道题共享的自动测试定义
├── prompts\                      自研 harness 和 Codex CLI 的提示词、输出 Schema
├── src\plc_agent\                Python 主程序
│   ├── cli.py                    自研 harness 单题入口
│   ├── experiment_cli.py         四种设置的批量实验入口
│   ├── codex_baseline_cli.py     Codex CLI 单题入口
│   ├── agent.py                  生成、预检、编译、修复和测试闭环
│   ├── codesys_runner.py         Python 到 CODESYS 的边界
│   ├── model_client.py           DMXAPI 客户端
│   └── precheck.py               候选接口预检
├── codesys\
│   ├── template\测试工程.project 固定 CODESYS 模板工程
│   └── scripts\                  CODESYS 内部编译和测试脚本
├── config\
│   ├── experiment_v4.json        最终 120 轮实验配置
│   └── experiment*.json          历史配置，只用于理解迭代过程
├── tests\                         Python 单元测试和固定联调样例
├── experiments\
│   ├── raw\formal\               保留的初始、最终原始实验记录
│   ├── processed\                逐题结果和汇总 CSV、JSON
│   └── analysis\                 汇总、比较和制图脚本
├── report\
│   ├── report.tex                主报告 LaTeX 源码
│   ├── data_appendix.tex         数据附录入口
│   ├── generated_data_appendix.tex 自动生成的逐题附录内容
│   ├── generate_data_appendix.py 附录生成脚本
│   ├── figures\                  报告图表
│   └── pptcourse\                课程课件参考材料
└── other\                        报告写作底稿和指南
```

`genai/` 和 `大作业题库json/` 是老师原始材料，不要覆盖、移动或改写。正式题目、LTL 和测试统一修改 `data/` 下的转换版本。

## 4. 当前保留的正式数据

原始实验只保留两批：

```text
experiments/raw/formal/20261109_234635_2ba96d/       初始完整实验，120 条
experiments/raw/formal/20261111_102220_v4_formal/    最终正式实验，120 条
```

最终正式批次包含 `manifest.json`、`run_config.json` 和 30 道题的四种设置记录。当前 `manifest.json` 中共有 120 条运行记录。

报告直接使用的汇总文件位于：

```text
experiments/processed/formal_runs.csv
experiments/processed/formal_runs.json
experiments/processed/formal_summary.csv
experiments/processed/formal_summary.json
experiments/processed/initial_runs.csv
experiments/processed/initial_runs.json
experiments/processed/initial_summary.csv
experiments/processed/initial_summary.json
experiments/processed/initial_final_comparison.csv
experiments/processed/initial_final_comparison.json
```

不要手工修改汇总数字。汇总应从 `experiments/raw/` 重新生成。

## 5. 运行环境

当前完成实验的机器使用：

- Windows；
- Python 3.12.4：`D:\python\python.exe`；
- CODESYS V3.5 SP22 Patch 4；
- CODESYS 可执行文件：`F:\genai\CODESYS\Common\CODESYS.exe`；
- Codex CLI 0.167.0-alpha.3.2；
- DMXAPI 的 OpenAI 兼容接口；
- NumPy 2.4.0、Matplotlib 3.10.8，用于报告图表。

核心 harness 主要使用 Python 标准库。只有重新生成图表时需要 NumPy 和 Matplotlib。

`src/plc_agent/codesys_runner.py` 当前将 CODESYS 路径和 Profile 默认设置为：

```text
F:\genai\CODESYS\Common\CODESYS.exe
CODESYS V3.5 SP22 Patch 4
```

如果换电脑，需要先修改该文件中的 `DEFAULT_CODESYS_EXE` 和 `DEFAULT_PROFILE`，或保证新环境使用相同路径与 Profile。现有命令行入口没有单独暴露这两个参数。

更换 CODESYS 路径、Profile 或版本属于实验环境变化。若重新进行正式实验，应建立新批次并在报告中记录环境变化，不能将新结果混入现有正式批次。

## 6. 配置模型 API

项目根目录使用 `.env` 保存本机配置。该文件包含真实密钥，已经被 Git 忽略，不得提交、截图或写入报告。

新环境可以按下面的格式创建 `.env`：

```dotenv
DMXAPI_API_KEY=填写真实密钥
DMXAPI_BASE_URL=https://www.dmxapi.cn/v1
MODEL_A=deepseek-v4.1-flash-1017
MODEL_B=qwen3-coder-flash
```

当前代码使用默认推理配置，不需要设置或传入 `reasoning_effort=none`。

三个 Python 入口都会根据源码位置定位项目根目录，并自动读取根目录的 `.env`。因此即使从其他目录启动模块，也会读取本项目的 `.env`；仍建议始终在项目根目录执行命令，避免相对任务路径解析错误。

## 7. 无外部费用的本地检查

先确认 Python、Codex CLI、CODESYS 和模板工程存在：

```powershell
& 'D:\python\python.exe' --version
codex --version
Test-Path 'F:\genai\CODESYS\Common\CODESYS.exe'
Test-Path 'codesys\template\测试工程.project'
```

运行 Python 单元测试：

```powershell
& 'D:\python\python.exe' -m unittest discover -s tests -v
```

当前验证结果为 23 项测试，其中 19 项通过，4 项真实 CODESYS 集成测试按默认设置跳过。这个命令不会调用模型，也不会启动 CODESYS。

如果确实要运行真实 CODESYS 集成测试，可临时设置环境变量后执行测试：

```powershell
$env:RUN_CODESYS_INTEGRATION = '1'
& 'D:\python\python.exe' -m unittest tests.test_codesys_integration -v
Remove-Item Env:RUN_CODESYS_INTEGRATION
```

该命令会启动真实 CODESYS，不应在 CODESYS 被其他任务占用时运行。

## 8. 运行单题自研 harness

固定联调题同时包含题目和测试，适合检查完整闭环：

```powershell
& 'D:\python\python.exe' -m src.plc_agent `
  --task tests\fixtures\motor_start_stop_fixture.json `
  --model deepseek-v4.1-flash-1017 `
  --max-repairs 2 `
  --candidate-precheck
```

该命令会调用模型并启动 CODESYS。未指定 `--output-dir` 时，结果写入：

```text
experiments/raw/development/<时间>_<模型>/
```

运行正式题时，需要同时提供对应的测试文件。例如：

```powershell
& 'D:\python\python.exe' -m src.plc_agent `
  --task data\tasks\public\public_03.json `
  --tests data\test_cases\public\public_03.json `
  --model deepseek-v4.1-flash-1017 `
  --max-repairs 2 `
  --candidate-precheck
```

## 9. 运行单题 Codex CLI 基线

```powershell
& 'D:\python\python.exe' -m src.plc_agent.codex_baseline_cli `
  --task tests\fixtures\motor_start_stop_fixture.json `
  --model qwen3-coder-flash `
  --max-repairs 2 `
  --model-timeout 300
```

Codex CLI 只负责生成结构化候选，CODESYS 编译、错误反馈和自动测试仍由项目外部循环完成。项目会自动查找系统中的 `codex` 命令或 Codex 桌面端自带的可执行文件。

上面的 fixture 自带测试定义，因此不需要额外传 `--tests`。项目会在启动 Codex CLI 时自动写入 DMXAPI provider 配置，并从 `.env` 读取 `DMXAPI_API_KEY` 和 `DMXAPI_BASE_URL`，不依赖用户的 Codex 全局模型配置。

运行正式题时需要明确传入共享测试文件：

```powershell
& 'D:\python\python.exe' -m src.plc_agent.codex_baseline_cli `
  --task data\tasks\public\public_03.json `
  --tests data\test_cases\public\public_03.json `
  --model qwen3-coder-flash `
  --max-repairs 2 `
  --model-timeout 300
```

默认输出目录为：

```text
experiments/raw/development/<时间>_<题目>_<模型>_codex_cli/
```

## 10. 运行四种设置的预测试

最终配置文件是 `config/experiment_v4.json`。它的预测试只运行 `public_03`，共 1 道题 × 2 个框架 × 2 个模型 = 4 个条件：

```powershell
& 'D:\python\python.exe' -m src.plc_agent.experiment_cli `
  --phase pre_run `
  --config config\experiment_v4.json
```

默认输出到：

```text
experiments/raw/pre_run/<时间>_<随机后缀>/
```

这一步仍会调用模型和 CODESYS。只有在更换电脑、模型、CODESYS 环境或关键代码后才需要重新预测试。

## 11. 运行120个正式实验条件

正式运行命令为：

```powershell
& 'D:\python\python.exe' -m src.plc_agent.experiment_cli `
  --phase formal `
  --config config\experiment_v4.json
```

正式阶段没有设置 `formal_tasks`，因此会自动读取 20 道公共题和 10 道自建题，并运行四种框架—模型组合，共 120 个条件。

任务发现规则是按文件名排序读取 `data/tasks/public/*.json`，再读取 `data/tasks/custom/*.json`。正式运行前应确认这两个目录仍然恰好包含 20 和 10 个 JSON；误放额外 JSON 会改变实验集合。

默认输出到：

```text
experiments/raw/formal/<时间>_<随机后缀>/
```

批量入口会逐条件更新 `manifest.json`，因此中途停止后可以续跑。不要为了检查命令而启动正式实验；它会产生 API 费用，并长时间占用 CODESYS。

最终批次的平均单条件耗时约 114.59 秒。120 个条件串行执行的量级约为 3.8 小时，实际时间会受到模型服务和 CODESYS 状态影响。运行期间应让本项目独占 CODESYS，并预留数百 MiB 临时工程空间。API 费用取决于供应商计费，当前项目没有完整可靠的费用口径，启动前应自行确认余额。

### 断点续跑

```powershell
& 'D:\python\python.exe' -m src.plc_agent.experiment_cli `
  --phase formal `
  --config config\experiment_v4.json `
  --resume experiments\raw\formal\<批次目录名>
```

配置必须与批次中的 `run_config.json` 完全一致，否则程序会拒绝续跑。

续跑适用于刚刚中断的新批次，应继续使用启动该批次时未修改的同一配置文件。当前两个已完成批次不需要续跑，也不要为了测试命令对它们执行 `--resume`。项目没有提供自动从 `run_config.json` 反向生成配置模板的功能。

只应重跑具有明确基础设施故障证据的条件。例如只重跑 `runner_error`：

```powershell
& 'D:\python\python.exe' -m src.plc_agent.experiment_cli `
  --phase formal `
  --config config\experiment_v4.json `
  --resume experiments\raw\formal\<批次目录名> `
  --retry-status runner_error
```

模型生成错误、编译失败和功能测试失败属于实验结果，不应为了提高成功率而随意重跑。

重跑不会覆盖旧条件目录。程序会建立 `__retry_01` 等新目录，在 `manifest.json` 中用新记录替代当前有效记录，并保存 `supersedes_artifact_directory` 和 `retry_reason` 指向旧证据。

## 12. 单次运行会保存什么

每个题目—框架—模型条件有独立目录，主要内容包括：

```text
<task_id>/<framework>__<model>/
├── task.json                  本次实际题目和 Spec 上下文
├── run_config.json            框架、模型、超时和修复设置
├── attempt_00/                第一次候选
│   ├── prompt.txt             实际提示词
│   ├── model_response.json    或模型输出、Codex CLI 轨迹
│   ├── candidate.json
│   ├── declaration.st
│   ├── implementation.st
│   ├── attempt_result.json
│   └── combined_execution/    合并编译和测试记录
└── final_result.json          单条件最终状态
```

不同框架的细节文件名略有区别，但都需要保留原始模型输出、候选代码、编译或测试结果和最终状态。CODESYS 生成的 `candidate.project`、`*.bootinfo`、`*.compileinfo`、`*.precompilecache` 和 `*.opt` 可以在实验结束后清理，它们不属于最终统计证据。

## 13. 重新生成正式汇总

从最终正式批次生成逐题结果、四种设置汇总和 Markdown 分析：

```powershell
& 'D:\python\python.exe' experiments\analysis\summarize_formal.py `
  --batch experiments\raw\formal\20261111_102220_v4_formal
```

该脚本要求批次包含 120 个唯一条件且没有 `runner_error`，输出：

```text
experiments/processed/formal_runs.csv
experiments/processed/formal_runs.json
experiments/processed/formal_summary.csv
experiments/processed/formal_summary.json
experiments/analysis/formal_analysis.md
```

重新生成初始—最终对比：

```powershell
& 'D:\python\python.exe' experiments\analysis\compare_initial_final.py
```

重新生成报告图表：

```powershell
& 'D:\python\python.exe' experiments\analysis\generate_report_figures.py
```

图表输出到 `report/figures/`。

`compare_initial_final.py` 固定读取当前 `initial_runs.json` 和 `formal_runs.json`，并固定统计现有两个原始批次的 CODESYS 启动记录；`generate_report_figures.py` 也固定读取当前 processed 文件。若以后建立新正式批次，需要先明确修改这些输入指向，不能直接假设脚本会自动选择最新批次。

## 14. 重新生成报告和数据附录

当前工作区保留了 LaTeX 源码，但根目录下的 `report/report.pdf` 和 `report/data_appendix.pdf` 尚未重新生成。

编译需要可用的 TeX Live、XeLaTeX、`latexmk`、CTeX 中文支持和报告引用的中文字体。当前机器可以调用 `latexmk`，下列命令曾用于本项目的 XeLaTeX 构建；换电脑后应先确认这些依赖。

先生成逐题数据附录内容：

```powershell
& 'D:\python\python.exe' report\generate_data_appendix.py
```

然后从 `report` 目录编译：

```powershell
Push-Location report
latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=out report.tex
latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=out data_appendix.tex
Copy-Item -LiteralPath 'out\report.pdf' -Destination 'report.pdf' -Force
Copy-Item -LiteralPath 'out\data_appendix.pdf' -Destination 'data_appendix.pdf' -Force
Pop-Location
```

`report/out/` 是可重新生成的编译目录。最终提交时保留 `report.tex`、附录源文件和根部两个最终 PDF 即可。

## 15. 常见问题

### 提示 `DMXAPI_API_KEY is not set`

检查根目录 `.env` 是否存在，并确认键名为 `DMXAPI_API_KEY`。不要把密钥写进代码或提交到 Git。

### 提示找不到 CODESYS

检查 `F:\genai\CODESYS\Common\CODESYS.exe` 是否存在，并核对 `codesys_runner.py` 中的默认路径和 Profile。

### CODESYS 超时或没有生成结果文件

先确认没有其他 CODESYS 进程占用模板或 Simulation。查看本次运行目录中的 `process_result.json`、`test_process_result.json` 或 `runner_error.json`，不要只根据终端最后一行判断模型质量。

### 提示找不到 Codex CLI

先运行：

```powershell
codex --version
```

如果命令不存在，需要安装或修复 Codex CLI。当前验证版本为 `codex-cli 0.167.0-alpha.3.2`。

### 提示输出目录已经存在

运行目录采用不可覆盖规则。换一个新的 `--output-dir`，或者使用批量入口的 `--resume` 续跑原批次，不要直接覆盖旧记录。

### 正式汇总报缺少120条记录

检查批次根目录的 `manifest.json`。正式汇总只接受 120 个唯一题目—框架—模型条件，并拒绝仍含 `runner_error` 的批次。

## 16. 修改项目时的边界

- 同一道题的四种设置必须使用相同题目、LTL、测试用例和判定标准。
- 测试用例不能放进模型提示词，也不能在运行后回写标准测试定义。
- 正式实验开始后，题目、提示词、模型、参数和测试集必须冻结。
- 修改正式配置或关键执行逻辑后，需要建立新批次，不能覆盖旧结果。
- 原始模型响应、候选 ST、配置、编译结果、测试结果和最终状态属于实验依据。
- `genai/`、`大作业题库json/` 和 `.env` 不得改写或提交。
- Git 提交由项目负责人手动执行。

## 17. 复现边界

当前项目没有为最终正式实验单独记录 Git commit 或 tag，原始批次保存了实际实验配置，但不能单靠配置快照完全恢复当时的全部源码。这是现有复现记录的一个局限。

接手人应保留当前代码、初始和最终两个原始批次、processed 汇总以及本交接文档。后续若重新进行正式实验，应在运行前记录 Git commit、配置快照、模型标识、CODESYS 版本和数据集版本。

## 18. 当前下一步

代码和最终正式实验已经完成。接手后主要工作是：

1. 补全报告封面的成员、学号、指导教师和分工；
2. 重新编译主报告和数据附录 PDF；
3. 根据报告制作 PPT 和演示录屏；
4. 核对最终提交包中是否包含源码、题库、LTL、测试用例、正式结果、报告和运行说明。


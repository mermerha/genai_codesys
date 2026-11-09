# 面向 CODESYS 的 ST 代码生成 Agent

本项目是生成式人工智能课程大作业，目标是实现一个轻量级 PLC 编程 Agent：根据自然语言需求生成 Structured Text（ST）代码，调用 CODESYS 编译，并利用编译错误和测试反馈自动修复代码。

项目使用老师提供的 20 道公共题和不少于 10 道自建题，在“现成 Agent / 自研 Agent × 模型 A / 模型 B”四种设置下进行公平实验，最低完成 120 次正式任务运行。所有设置使用相同题目、测试用例和判定标准。

最终交付包括 Agent 源码、题库、LTL 规约、测试用例与实际结果、原始实验记录、汇总分析、实验报告、运行说明和项目汇报材料。测试用例设计和实际测试结果属于基础要求；测试自动执行器、PLCVerif 和多平台接入属于加分项。

## 当前状态与下一步

项目规则、要求清单、流程和联调样例已经建立；纯 Python CODESYS 调用、真实 `FUNCTION_BLOCK` 创建、无界面编译与结构化错误提取已经通过正确/错误样例验证。模型客户端和单题生成—编译—修复闭环已实现。模型 A `deepseek-v4.1-flash-1017` 已在简单、中等和困难公共题上完成编译预验证；当前模型 B 候选 `qwen3.8-flash` 通过简单题，但在中等题上于 300 秒超时，尚未冻结。

当前主线：

1. 用少量不同难度题预验证并冻结模型 B。
2. 确认现成 Agent 基线候选。
3. 将老师提供的 20 道公共题转换为冻结接口。
4. 设计、复核并冻结公共题的 LTL 与测试标准。

最新进度、阻塞项和证据以 [`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md) 为准。

## 核心闭环

```text
读取题目
→ 调用模型生成结构化 ST
→ 写入 CODESYS 模板工程
→ 编译并提取错误
→ 根据错误修复
→ 成功或达到终止条件
→ 使用固定测试用例测试
→ 保存全过程
```

首版只实现单 Agent 闭环，不提前增加多 Agent 或其他加分功能。

## 已验证命令

在项目根目录运行 Python 单元测试：

```powershell
D:\python\python.exe -m unittest discover -s tests -v
```

在本机 `.env` 已配置且 CODESYS 未被其他进程占用时，运行固定联调题的真实闭环：

```powershell
D:\python\python.exe -m src.plc_agent --max-repairs 2
```

## 文档导航

第一次进入项目只需阅读本文件和 [`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md)。其他文档按任务读取：

| 需要了解的内容 | 文档 |
|---|---|
| 老师要求与最终验收 | [`docs/REQUIREMENTS.md`](docs/REQUIREMENTS.md) |
| 项目完整阶段流程 | [`docs/WORKFLOW.md`](docs/WORKFLOW.md) |
| 已有架构和实验决定 | [`docs/DECISIONS.md`](docs/DECISIONS.md) |
| 题目、LTL、测试和结果格式 | [`docs/DATA_CONTRACT.md`](docs/DATA_CONTRACT.md) |
| 老师原始材料及哈希 | [`docs/SOURCE_MATERIALS.md`](docs/SOURCE_MATERIALS.md) |
| Codex 长期工作规则 | [`AGENTS.md`](AGENTS.md) |

新建或切换 Codex 项目时，应将本目录设为主要工作目录，使项目级 `AGENTS.md` 生效。

## 目录结构

```text
Genai_codesys/
├── AGENTS.md                  # Codex 长期规则
├── README.md                  # 项目入口
├── .env.example               # 环境变量示例，不含真实密钥
├── genai/                     # 老师提供的 PDF、DOCX 和 API 说明，保持原位
├── 大作业题库json/            # 老师提供的公共题 JSON，保持原位
├── config/                    # 开发与实验配置模板
├── data/
│   ├── tasks/
│   │   ├── public/            # 转换后的 20 道公共题
│   │   └── custom/            # 不少于 10 道自建题及来源记录
│   ├── specs/                 # LTL 规约
│   └── test_cases/            # 各实验设置共享的测试标准
├── src/plc_agent/             # 自研 Agent harness
├── codesys/
│   ├── template/              # 固定 CODESYS 模板工程
│   └── scripts/               # 写入、编译和错误提取脚本
├── prompts/                   # 生成和修复提示词
├── tests/fixtures/            # Python 测试和固定联调样例
├── experiments/
│   ├── raw/                   # 原始、不可覆盖的逐次运行记录
│   ├── processed/             # 汇总结果
│   └── analysis/              # 统计脚本、表格和图表
├── report/                    # 报告、PPT、演示和最终提交材料
└── docs/                      # 要求、状态、流程、决策和接口
```

`genai/` 和 `大作业题库json/` 是现有原始材料位置，只读保留，不再移动。转换后的数据进入 `data/`。

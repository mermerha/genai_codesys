# 原始材料清单

本文件只用于定位老师提供的输入。原始文件不应被项目脚本覆盖或移动。

| 文件 | 用途 | SHA-256 |
|---|---|---|
| `genai/Final project_CHINESE.pdf` | 中文作业要求 | `4170E534133A941BA4D4DAE9DD915972552DEE183967E21B1691BF244B00322C` |
| `genai/Final project_CHINESE.docx` | 中文要求 Word 版本 | `A7F7D75A3B7057D2F847754FF8C1E7C6C8516269094BD2491B8D9C886669BE79` |
| `genai/Final project_ENGLISH.docx` | 英文要求 Word 版本 | `EF34F149D4153BB2AEF180F4EF3C183028BC78616AD9013E36F1DCA6731181F3` |
| `genai/大作业题库.pdf` | 20 道公共题可读版 | `2C69CE26107E158AEA4A9F1BD2EFAD272B994A9D5207F5E2B20500FDEF6E2100` |
| `大作业题库json/大作业题库.json` | 公共题机器可读数据 | `05170AE18C1EC7C316D8334A84B6ECD48DE322C8236735D519B50F72F2D8D362` |
| `genai/大报告测试用例模板与示例.docx` | 测试要求、模板和示例 | `1F6FD4DE9077C2AE920DB56B3CA7901140162A6F638926459B131D5E29EC37FA` |
| `genai/DMXAPI_API调用说明.md` | 模型接口说明 | `3142E7693E41D46261153010404CB755B323FEF793A0B4AF065C87EE0E08C402` |

## 使用原则

- 转换或清洗后的公共题放入 `data/tasks/public/`。
- 自建题及生成、来源和审核记录放入 `data/tasks/custom/`。
- 报告引用要求时，以最新版中文 PDF 和测试模板为准。
- `genai/` 和 `大作业题库json/` 保持现有位置，不再移动或重命名。
- 原始材料发生更新时，先记录修改时间和差异，再更新要求与状态，不直接覆盖项目结论。
- 重新计算哈希发现变化时，把旧哈希和新哈希连同日期写入决策或状态记录；不要静默替换本表。

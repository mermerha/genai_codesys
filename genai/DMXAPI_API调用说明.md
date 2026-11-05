# DMXAPI API 调用说明

本文以兼容 OpenAI 格式的文本对话接口为例，介绍 DMXAPI 的基本配置和调用方法。

> **相关模型及价格可在此查询：[https://www.dmxapi.cn/rmb](https://www.dmxapi.cn/rmb)。** 调用时，请复制页面中的准确模型名称，填写到 `model` 参数中。

## 1. 调用前准备

1. 找助教获取本组的API key
2. 在 [模型及价格页面](https://www.dmxapi.cn/rmb) 选择需要使用的模型。
3. 确认所选模型支持的接口格式和参数。

## 2. 接口配置

| 配置项 | 填写内容 |
| --- | --- |
| Base URL | `https://www.dmxapi.cn/v1` |
| API Key | 调用者自己的 DMXAPI Key |
| Model | 从模型页面复制的准确模型名称 |
| 请求方式 | `POST` |
| 文本对话完整请求地址 | `https://www.dmxapi.cn/v1/chat/completions` |
| 请求体格式 | JSON |

使用 OpenAI Python SDK 时，`base_url` 填写到 `/v1` 即可；直接发送 HTTP 请求时，使用包含 `/chat/completions` 的完整请求地址。

## 3. Python 调用示例

### 安装依赖

```bash
pip install openai
```

### 发送请求

运行前，请替换示例中的 API Key 和模型名称。

```python
from openai import OpenAI

client = OpenAI(
    api_key="替换为你自己的 DMXAPI Key",
    base_url="https://www.dmxapi.cn/v1",
)

response = client.chat.completions.create(
    model="替换为模型页面中的准确模型名称",
    messages=[
        {"role": "user", "content": "你好，请介绍一下你自己。"}
    ],
    stream=False,
)

print(response.choices[0].message.content)
```

示例中的 Key 和模型名称均为占位文本，替换后再运行。实际项目建议通过环境变量或服务端配置读取 Key，避免将真实 Key 提交到代码仓库或暴露在前端代码中。

## 4. 通过 HTTP 直接调用

### 请求地址

```text
POST https://www.dmxapi.cn/v1/chat/completions
```

### 请求头

```http
Authorization: Bearer 你自己的DMXAPI_Key
Content-Type: application/json
```

`Bearer` 与 API Key 之间保留一个空格。

### 请求体

```json
{
  "model": "替换为模型页面中的准确模型名称",
  "messages": [
    {
      "role": "user",
      "content": "你好，请介绍一下你自己。"
    }
  ],
  "stream": false
}
```

### 参数说明

| 参数 | 说明 |
| --- | --- |
| `model` | 本次调用的模型名称，具体名称请在模型页面查询 |
| `messages` | 对话消息列表，可按顺序传入历史消息和当前问题 |
| `messages[].role` | 消息角色；示例中的 `user` 表示用户消息 |
| `messages[].content` | 发送给模型的文本内容 |
| `stream` | 是否使用流式输出；本示例设为 `false`，一次返回完整结果 |

非流式文本回复通常从返回结果的 `choices[0].message.content` 中读取。

## 5. 模型选择与使用说明

- **相关模型及价格查询地址：[https://www.dmxapi.cn/rmb](https://www.dmxapi.cn/rmb)。**
- 调用时请使用页面中的准确模型名称，不要自行修改模型标识。
- 不同模型支持的接口和参数可能不同。更换模型时，请检查其接口兼容性。
- 本文示例适用于支持相应 Chat Completions 格式的文本对话模型；图片、视频、语音等模型请按对应文档调用。
- 本文仅提供配置与调用示例，未使用真实 API Key 发起请求。

## 6. 相关链接

- [DMXAPI 官网](https://www.dmxapi.cn)
- [模型及价格查询](https://www.dmxapi.cn/rmb)
- [DMXAPI 开发者文档](https://doc.dmxapi.cn/)
- [文本对话非流式调用文档](https://doc.dmxapi.cn/openai-chat.html)

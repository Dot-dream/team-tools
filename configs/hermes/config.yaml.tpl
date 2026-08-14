# Hermes 配置模板 —— 拷回 ~/.hermes/config.yaml 后填 key
custom_providers:
- name: my-provider
  base_url: https://api.deepseek.com
  api_key: <YOUR_DEEPSEEK_API_KEY>
  api_mode: codex_responses
  models:
    deepseek-v4-pro:
      context_length: 1000000
      name: DeepSeek V4 Pro
    deepseek-v4-flash:
      context_length: 1000000
      name: DeepSeek V4 Flash
  model: deepseek-v4-pro
- name: work
  base_url: https://api.deepseek.com
  api_key: <YOUR_DEEPSEEK_API_KEY>
  api_mode: chat_completions
  models:
    deepseek-v4-pro:
      context_length: 1000000
      name: DeepSeek V4 Pro
    deepseek-v4-flash:
      context_length: 1000000
      name: DeepSeek V4 Flash
  model: deepseek-v4-pro
- name: xiaomi
  base_url: https://api.xiaomimimo.com/v1
  api_key: <YOUR_XIAOMI_MIMO_API_KEY>
  api_mode: chat_completions
  models:
    mimo-v2.5-pro:
      name: MiMo v2.5 Pro
    mimo-v2.5:
      name: MiMo v2.5
  model: mimo-v2.5-pro
model:
  default: deepseek-v4-pro
  provider: work
mcp_servers:
  hermes-docs-cn:
    enabled: true
    url: https://mcp.hermesagent.org.cn/v1
  aixprobe:
    enabled: true
    url: http://192.168.137.217:8080/
  mcp_servers:
    enabled: true
  codegraph mcp_servers:
    enabled: true

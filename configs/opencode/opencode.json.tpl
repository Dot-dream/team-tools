{
  "$schema": "https://opencode.ai/config.json",
  "shell": "C:\\Program Files\\PowerShell\\7\\pwsh.exe",
  "mcp": {
    "aixprobe": { "type": "remote", "url": "http://192.168.137.217:8080/", "enabled": true },
    "codegraph": { "type": "local", "command": ["codegraph", "serve", "--mcp"], "enabled": true },
    "hermes-docs-cn": { "type": "remote", "url": "https://mcp.hermesagent.org.cn/v1", "enabled": true },
    "jlink": { "type": "local", "command": ["python", "-m", "jlink_mcp"], "enabled": true },
    "moba-agent-bridge": { "type": "local", "command": ["python", "<YOUR_REPO_DIR>\\moba-agent-bridge\\server.py"], "enabled": true }
  },
  "provider": {
    "deepseek": {
      "models": { "deepseek-v4-pro": { "name": "deepseek-v4-pro" } },
      "npm": "@ai-sdk/openai-compatible",
      "options": {
        "apiKey": "<YOUR_DEEPSEEK_API_KEY>",
        "baseURL": "https://api.deepseek.com/v1",
        "setCacheKey": true
      }
    },
    "glm": {
      "models": { "glm-5.1": { "name": "GLM-5.1" } },
      "name": "Zhipu GLM",
      "npm": "@ai-sdk/openai-compatible",
      "options": {
        "apiKey": "<YOUR_GLM_API_KEY>",
        "baseURL": "https://open.bigmodel.cn/api/coding/paas/v4",
        "setCacheKey": true
      }
    },
    "my-proxie": {
      "models": {
        "deepseek-v4-flash": { "name": "DeepSeek V4 Flash" },
        "deepseek-v4-pro": { "name": "DeepSeek V4 Pro[1M]" }
      },
      "npm": "@ai-sdk/openai-compatible",
      "options": {
        "apiKey": "<YOUR_DEEPSEEK_API_KEY>",
        "baseURL": "https://api.deepseek.com/v1",
        "setCacheKey": true
      }
    }
  }
}

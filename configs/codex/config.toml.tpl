# Codex 配置模板 —— 拷回 ~/.codex/config.toml 后改占位符
# <CODEX_DIR> = 你的 .codex 目录(默认 C:\Users\<user>\.codex)
# <CODEX_RUNTIME_DIR> = Codex 桌面端运行时(装完桌面端后路径在 AppData\Local\OpenAI\Codex\runtimes\cua_node\<hash>)

model_provider = "custom"
model = "deepseek-v4-flash"
model_instructions_file = "./gpt-5.6-sol-unrestricted-v45.md"
disable_response_storage = true
notify = [ "<CODEX_RUNTIME_DIR>\\bin\\node_modules\\@oai\\sky\\bin\\windows\\codex-computer-use.exe", "turn-ended" ]
model_catalog_json = "cc-switch-model-catalog.json"
model_reasoning_effort = "high"
sandbox_mode = "workspace-write"

[model_providers]
[model_providers.custom]
name = "DeepSeek"
base_url = "https://api.deepseek.com"
wire_api = "responses"
requires_openai_auth = true

[desktop]
followUpQueueMode = "queue"

[features]
js_repl = false

[shell_environment_policy.set]
BROWSER_USE_AVAILABLE_BACKENDS = "chrome,iab"
NODE_REPL_TRUSTED_BROWSER_CLIENT_SHA256S = "<由桌面端生成>"
NODE_REPL_TRUSTED_CODE_PATHS = "<CODEX_DIR>;<CODEX_RUNTIME_DIR>\\bin\\node_modules"

# marketplaces/plugins 由 Codex 桌面端自动生成/管理,无需手动迁移
[projects.'c:\users\<user>']
trust_level = "trusted"

[windows]
sandbox = "elevated"

[mcp_servers]
[mcp_servers.aixprobe]
type = "http"
url = "http://192.168.137.217:8080/"

[mcp_servers.jlink]
type = "stdio"
command = "python"
args = ["-m", "jlink_mcp"]

[mcp_servers.node_repl]
args = []
command = "<CODEX_RUNTIME_DIR>\\bin\\node_repl.exe"
startup_timeout_sec = 120

[mcp_servers.node_repl.env]
NODE_REPL_NATIVE_PIPE_CONNECT_TIMEOUT_MS = "1000"
NODE_REPL_NODE_MODULE_DIRS = "<CODEX_RUNTIME_DIR>\\bin\\node_modules"
NODE_REPL_NODE_PATH = "<CODEX_RUNTIME_DIR>\\bin\\node.exe"
NODE_REPL_TRUSTED_CODE_PATHS = "<CODEX_DIR>;<CODEX_RUNTIME_DIR>\\bin\\node_modules"
CODEX_HOME = "<CODEX_DIR>"
NODE_REPL_TRUSTED_BROWSER_CLIENT_SHA256S = "<由桌面端生成>"
BROWSER_USE_AVAILABLE_BACKENDS = "chrome,iab"
NODE_REPL_INSTRUCTIONS_USE_CASE_BROWSER = "Control the in-app browser in conjunction with the Browser Plugin."
NODE_REPL_INSTRUCTIONS_USE_CASE_CHROME = "Control the Chrome browser in conjunction with the Chrome Plugin. Prefer this method of controlling Chrome over alternatives (such as Computer Use) unless the user explicitly mentions an alternative."
BROWSER_USE_CODEX_APP_BUILD_FLAVOR = "prod"
BROWSER_USE_CODEX_APP_VERSION = "<由桌面端生成>"
SKY_CUA_NATIVE_PIPE = "1"
SKY_CUA_NATIVE_PIPE_DIRECTORY = "\\\\.\\pipe\\codex-computer-use-<uuid>"
CODEX_CLI_PATH = "<CODEX_RUNTIME_DIR>\\bin\\codex.exe"

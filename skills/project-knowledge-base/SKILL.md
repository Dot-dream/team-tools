---
name: project-knowledge-base
description: 将一个代码项目打造成结构化的 Obsidian 项目知识库，并在 git 仓库中初始化 CLAUDE.md。流程：codegraph 扫描索引 → /init → 按子系统并行深度分析 → 搭建标准分层 Obsidian 知识库（含 Mermaid 图表、Canvas 可视化、术语表、走读教程）→ 质量审核。使用时机：用户想把某个代码库做成可持续维护的项目知识库、或为团队新成员建立可复现的入门文档、或需要"从代码到文档"的一站式产出。触发词：搭建知识库、构建项目知识库、codegraph 扫描、obsidian 知识库、给项目做文档。
---

# Project Knowledge Base Builder

把任意代码项目转换成结构化的 Obsidian 项目知识库 + CLAUDE.md。本 skill 编码了一套**验证过的配方**（流程），可在不同项目上复现约 95% 的效果。产出内容是项目专属的，但流程、结构、质量门是通用的。

## 总体流程（6 个阶段）

```
P1 收集参数 → P2 代码索引 → P3 生成 CLAUDE.md → P4 并行深度分析 → P5 搭建知识库 → P6 图表优化 → P7 质量审核
```

以下所有路径均为 skill 所在目录的相对路径（`~/.claude/skills/project-knowledge-base/`）。

---

## P1 收集参数

开工前先向用户确认，并写入一个本地 `params` 备忘（记录在会话中即可）：

1. **项目根目录**（绝对路径）
2. **内容语言**：默认中文（本 skill 模板均为中文）
3. **是否已有 Obsidian vault**：项目内 `obsidian/` 目录？还是新建？
4. **项目类型 / 子系统划分**：如果用户能说清楚模块划分就直接用；否则留待 P4 探测
5. **质量门深度**：默认轻量校验；mermaid 渲染与否按第 6 项的工具决策执行
6. **工具可用性决策（一次性询问，记住选择贯穿整个会话）**：开工前检测 **codegraph** 与 **mermaid-cli** 是否可用，各用一次 AskUserQuestion 询问"安装 or 降级"（已装的无需询问）：
   - **codegraph 缺失** → 询问：推荐"安装"（调用关系分析是质量核心，agent 依赖它查 callers/callees）；备选"降级"（纯文件解析 + 静态符号索引）。
   - **mermaid-cli 缺失** → 询问：推荐"降级"（`validate-kb.js` 已覆盖主要 Mermaid 语法坑）；备选"安装"（启用全量渲染验证，首次下载 chromium 较大）。
   - **铁律**：无论用户选哪条路，**安装失败都必须自动降级并明确告知**，绝不允许阻塞整个知识库流程。
   - 记录两个选择（如 `params.codegraph = install|degrade`、`params.mermaid = install|degrade`），P2/P7 按此执行。

> 若项目已有 `CLAUDE.md` 或 `obsidian/` 知识库，先告知用户是**重建**还是**增强**，避免覆盖已有成果。

## P2 代码索引（codegraph）

按 P1 的决策执行（`params.codegraph`）：

1. **检查**：`claude mcp list` 看 MCP 是否连接，或 `codegraph --version` 确认二进制可用。
2. **安装路径**（`params.codegraph = install` 且未装）：
   - 先尝试安装 codegraph 二进制（按其官方文档安装，如 `github.com/colbymchenry/codegraph` 提供的安装脚本/包管理器），然后 `codegraph install -y` 注册 MCP 服务。
   - 用 `codegraph --version` 验证；**任一步失败 → 自动降级（见降级路径）并明确告知用户本次使用降级模式**。
3. **索引**（安装路径成功或已有）：在项目根目录运行 `codegraph init`（或 `codegraph index` 重建）。
   - 创建 `.codegraph/`，产出符号/调用关系数据。
   - 项目很大时放后台运行，期间并行做 P3。
   - 完成后 `codegraph status` 记录文件数/节点数/边数（写进首页，作为"基于扫描"的佐证）。
4. **降级路径**（`params.codegraph = degrade`，或安装失败）：跳过索引。P4 的分析 agent 直接用文件读取 + Grep/Glob；知识库中「代码符号索引」用静态文件清单替代；首页不写"基于扫描"。**降级时必须向用户说明**，避免其误以为分析含调用关系。

## P3 生成 CLAUDE.md

用 Claude Code 内置 `/init` skill 生成，或按本 skill 的 `references/claude-md-sections.md` 结构手写。核心必须覆盖：

- **构建命令**（来自工程文件/README/批处理，不要编造）
- **关键编译宏/开关表**（尤其多工程 + 条件编译的项目）
- **架构大图**（跨多文件才能理解的：分层、模块调用、数据流、分区/变体）
- **开发注意事项**（已知坑、代码复用方式、独立子仓库等）

## P4 并行深度分析（核心阶段）

这是决定知识库质量的关键。原则：**探测 → 定义分析面 → 每个分析面一个并行 agent → 输出结构化笔记素材**。

### 4.1 探测项目结构
先自己快速读：README、工程文件、顶层目录树、入口文件（`main`/入口点）。确定项目类型（嵌入式/Web/后端…）和模块边界。

### 4.2 定义分析面
把项目切成 **3~5 个分析面**，每面一个 agent。切分维度参考：
- 按架构分层（应用层 / 协议栈 / 驱动层 / 引导程序）
- 按子系统（通信 / 诊断 / 网络管理 / 应用逻辑 / 存储）
- 按源码目录（每个顶层源码目录一面）

> 不要写死"CAN/Dcm/NM"这类专属名，而是按实际探测到的结构动态定义。

### 4.3 每个分析 agent 的任务模板
给每个 agent 的 prompt 必须包含：
1. 项目根路径 + 要分析的具体目录/模块
2. 使用 codegraph CLI（若可用）辅助查调用关系（`explore/query/node/callers`）
3. **必须阅读 .c/.h 源文件**，引用真实文件路径与函数名，禁止臆测
4. 输出结构化 Markdown 笔记素材，包含：
   - 模块职责表（模块 / 路径 / 职责 / 主要接口）
   - 数据流 / 状态机 / 时序（文字描述，后续转 Mermaid）
   - 关键函数清单
   - 配置项与宏
   - 与其它模块的调用关系
   - **发现的坑、遗留问题、`#if 0` 死代码、未接线逻辑**（这是最值钱的信息）

### 4.4 并行执行
用一次消息并发启动全部 agent（`Agent` 工具），后台运行。期间自己同步收集工程级信息（构建宏、子仓库、git 历史、README），避免与 agent 重复。

## P5 搭建 Obsidian 知识库

在项目内建 `obsidian/` vault，按 `references/kb-structure.md` 的标准结构创建。要点：

1. **目录分层编号**：`00-首页`、`01-项目概览`、`02-任务调度` … `08-索引`（见 kb-structure.md）
2. **首页 MOC**（`00-首页.md`）：项目定位 + Mermaid mindmap 导航 + 知识地图（wikilink 列表）+ 关键宏表，用 `templates/home-moc.md`
3. **先写不依赖 agent 结果的基础笔记**（项目简介、工程结构、构建配置），agent 完成后再落子系统笔记
4. **每条笔记规范**（见 kb-structure.md）：
   - frontmatter（title/tags/created）
   - `[[wikilink]]` 关联（首页导航的链接都要能解析）
   - 引用代码用 `文件路径:行号`
5. **必须包含的可复用笔记**（提升完整度）：
   - 术语表（`07-开发指南/术语表.md`）
   - 端到端走读教程（配时序图）——**主题必须自适应项目类型**，选择该项目**最有代表性的数据链路**，不要固定写诊断场景：
     - 协议栈/诊断项目 → "一条诊断请求如何走通全链路"
     - 灯控类项目 → "一条 CAN 报文如何点亮灯效" / "灯效数据链路"
     - 驱动类项目 → "外设初始化全链路"
     - 无明确数据链路的项目 → "从 main() 到首次业务输出的启动链路"
   - 代码符号索引（codegraph 查询结果或静态文件清单）

## P6 图表化优化

把文字内容升级为可视化（用户的核心诉求是"便于看代码和调用链"）。见 `references/mermaid-guide.md`：

1. **Mermaid 四类图表**按内容选择：
   - `mindmap` → 首页导航、架构概览
   - `flowchart` → 分层图、数据流、收发路径、启动流程
   - `stateDiagram-v2` → 状态机（调度、会话、NM、CanTp）
   - `sequenceDiagram` → 时序/调用顺序（诊断请求、刷写流程）
2. **必须新建**：
   - `架构全景.md`：mindmap + 分层 flowchart + 模块调用关系 graph + 数据流总览
   - `调用关系总览.md`：关键调用链（初始化/诊断/收发/跳转）的 graph 图
   - `架构关系.canvas`：分层 Canvas（用 `references/canvas-layout.md` 模板，按调用层次分带 + 颜色区分层次）
3. 给已有笔记逐个补图（数据流、状态机、时序替换纯文字段落）。

## P7 质量审核（质量门）

运行 `scripts/validate-kb.js`（无依赖，必跑）：

```bash
node ~/.claude/skills/project-knowledge-base/scripts/validate-kb.js <vault路径>
```

检查项：frontmatter 完整、wikilink 全部解析、Canvas JSON 有效、Mermaid 结构基本平衡。

**全量渲染验证**（按 P1 决策 `params.mermaid`）：

```bash
node ~/.claude/skills/project-knowledge-base/scripts/render-mermaid.js <vault路径>
```

- `params.mermaid = install`：直接运行渲染脚本——`npx @mermaid-js/mermaid-cli` 首次运行会**自动下载**（含 chromium，较大）。若下载/渲染失败 → 跳过渲染、明确告知用户用 `validate-kb.js` 兜底，**不阻塞交付**。
- `params.mermaid = degrade`：跳过渲染，仅跑 `validate-kb.js` 的结构检查兜底，并向用户说明本次未做渲染验证。
- 渲染发现失败的图表**必须修复**（见 mermaid-guide.md 的已知坑）后重跑，直至全部通过或明确告知用户遗留项。

**内容准确性审核**（人 + 机器）：
- 关键数字/宏/地址与源码核对（抽查即可）
- 已标注的"已知问题/坑"是否与代码一致
- 图表里的函数名与 `代码符号索引` 一致

## 交付清单

结束时向用户汇报：
1. CLAUDE.md 已生成（位置）
2. 知识库笔记数、Mermaid 图表数、渲染通过率、wikilink 解析率
3. 质量门的通过项
4. 已标注的已知问题/坑（来自 P4 agent 发现）

## 参考文件

- `references/kb-structure.md` — 知识库目录结构与笔记规范
- `references/mermaid-guide.md` — Mermaid 四类图表语法 + 已知坑（必读）
- `references/quality-gates.md` — 验收清单详情
- `references/canvas-layout.md` — 分层 Canvas JSON 模板
- `references/claude-md-sections.md` — CLAUDE.md 章节要点
- `templates/module-note.md` — 模块笔记模板
- `templates/home-moc.md` — 首页 MOC 模板
- `scripts/validate-kb.js` — 轻量校验（必跑）
- `scripts/render-mermaid.js` — 可选渲染验证

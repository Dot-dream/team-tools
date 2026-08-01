# knowledge-bases/ — 项目知识库

存放各**项目知识库**（Obsidian vault）或知识库模板/索引，统一管理团队的项目文档资产。

> 知识库本身由 `../skills/project-knowledge-base/` 技能自动生成。此目录用于**归档/共享**各项目已生成的知识库。

## 目录约定

```
knowledge-bases/
├── README.md                 # 本文
├── _template/                # 知识库结构模板（vault 骨架，供参考）
└── <project-name>/           # 每个项目一个子目录
    ├── README.md             # 该项目知识库说明（指向/说明 vault 位置）
    └── obsidian/             # 可选：直接归档该项目的 vault
```

## 两种管理方式（按需选）

### 方式 A：直接归档 vault（简单直接）
把项目的 `obsidian/` 整个拷进 `<project-name>/obsidian/`。适合知识库已定型、需要长期保存的项目。缺点是 vault 会随代码一起维护两份，需注意同步。

### 方式 B：只存说明 + 链接（推荐）
在 `<project-name>/README.md` 里写清楚：
- 该项目知识库在源码仓库里的位置（如 `xxx/obsidian/`）
- 如何生成/更新（用 `project-knowledge-base` skill）
- 关键入口笔记（`00-首页.md`）

源码仓库本身是知识库的"源头"，本目录只是索引。

## 知识库结构参考

标准 vault 结构见 `../skills/project-knowledge-base/references/kb-structure.md`：

```
00-首页.md                  # MOC 知识地图
01-项目概览/                # 简介/硬件/结构/构建/架构全景
02-任务调度/
03~06-*模块/                # 按项目子系统分层
07-开发指南/                # 配置速查/术语表/使用说明
08-索引/                    # 符号索引/调用关系总览
架构关系.canvas             # 分层可视化
Templates/                  # 笔记模板
```

## 如何为项目生成知识库

1. 在目标项目目录运行 Claude Code，说："用 project-knowledge-base 给 <项目> 搭建知识库"
2. 完成后把 vault 归档到这里（方式 A）或登记链接（方式 B）

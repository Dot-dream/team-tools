# 分层 Canvas 模板（调用层次布局）

> Obsidian Canvas（`.canvas`，JSON）用于可视化模块关系。**按调用层次分带布局**，而不是随意摆放。
> 文件放 vault 根目录：`架构关系.canvas`。

## 布局原则

1. **横向分带 = 架构层次**（自上而下 = 高层调低层）：
   - 概览/入口层 → 应用/调度层 → 核心协议/子系统层 → 驱动层 → 引导分区 → 参考/索引
2. **颜色区分层次**（Obsidian 预设 1~6）：
   - 1=红（BOOT 分区） 2=橙（应用/调度） 3=黄（概览/入口） 4=绿（驱动/SDK） 5=蓝（核心子系统） 6=紫（参考/索引）
3. **文本节点做层标签**（`type":"text"`，放每层左侧）
4. **边带 label** 标注调用关系（如 `Can_MainFunction`、`TP→Dcm`）
5. 每行 Y 坐标约差 230，节点宽 200 高 100

## 模板骨架

```json
{
  "nodes": [
    {"id": "t0", "type": "text", "text": "① 概览 / 入口层", "x": -1280, "y": -500, "width": 150, "height": 40},
    {"id": "home", "type": "file", "file": "00-首页.md", "x": -1080, "y": -500, "width": 200, "height": 100, "color": "3"},

    {"id": "t1", "type": "text", "text": "② 应用 / 调度层", "x": -1280, "y": -270, "width": 150, "height": 40},
    {"id": "n-app", "type": "file", "file": "05-网络管理与应用层/应用层逻辑.md", "x": -1080, "y": -270, "width": 200, "height": 100, "color": "2"},

    {"id": "t2", "type": "text", "text": "③ 核心子系统层", "x": -1280, "y": -40, "width": 150, "height": 40},
    {"id": "n-sub", "type": "file", "file": "03-.../模块.md", "x": -1080, "y": -40, "width": 200, "height": 100, "color": "5"},

    {"id": "t3", "type": "text", "text": "④ 驱动层", "x": -1280, "y": 190, "width": 150, "height": 40},
    {"id": "n-drv", "type": "file", "file": "06-.../驱动.md", "x": -1080, "y": 190, "width": 200, "height": 100, "color": "4"},

    {"id": "t4", "type": "text", "text": "⑤ 引导分区", "x": -1280, "y": 440, "width": 150, "height": 40},
    {"id": "n-boot", "type": "file", "file": "06-.../Bootloader.md", "x": -1080, "y": 440, "width": 200, "height": 100, "color": "1"},

    {"id": "t5", "type": "text", "text": "⑥ 参考 / 索引", "x": 580, "y": -100, "width": 150, "height": 40},
    {"id": "n-call", "type": "file", "file": "08-索引/调用关系总览.md", "x": 640, "y": -40, "width": 200, "height": 100, "color": "6"}
  ],
  "edges": [
    {"id": "e1", "fromNode": "home", "fromSide": "right", "toNode": "n-app", "toSide": "left", "label": "入口"},
    {"id": "e2", "fromNode": "n-app", "fromSide": "bottom", "toNode": "n-sub", "toSide": "top", "label": "调用"},
    {"id": "e3", "fromNode": "n-sub", "fromSide": "bottom", "toNode": "n-drv", "toSide": "top", "label": "依赖"},
    {"id": "e4", "fromNode": "n-drv", "fromSide": "bottom", "toNode": "n-boot", "toSide": "top", "label": "跳转"},
    {"id": "e5", "fromNode": "n-sub", "fromSide": "right", "toNode": "n-call", "toSide": "left", "label": "调用链"}
  ]
}
```

## 生成步骤

1. 按实际笔记文件填 `file` 字段（相对 vault 根路径）
2. 每层一个 `color`，层标签 `text` 节点放层左侧（x=-1280 或比最左节点再左 200）
3. 边 `label` 填真实调用关系；层级之间的边尽量垂直（`bottom→top`）
4. 写完用 `validate-kb.js` 校验（会自动检查 Canvas JSON、边端点、节点文件存在性）

## 校验

`validate-kb.js` 会检查：
- Canvas JSON 可解析
- 所有边端点引用存在的节点 id
- 所有 file 节点路径存在
- 所有 file 节点已着色（鼓励分层颜色）


# classic 架构文档

> **版本**: 1.0.0  
> **更新日期**: 2025-12-07  
> **模块类型**: python

---

## 1. 概述

<!-- HUMAN:overview -->
classic 模块负责 [TODO: 描述模块的核心职责和业务价值]。

**设计背景**：[TODO: 为什么需要这个模块？它解决了什么问题？]

**核心能力**：
- [TODO: 能力 1]
- [TODO: 能力 2]
<!-- /HUMAN:overview -->

---

## 2. 模块结构

<!-- AUTO:structure -->
```
classic/
├── evaluation.py
└── minimax.py
```
<!-- /AUTO:structure -->

---

## 3. 层级职责

<!-- AUTO:responsibilities -->
| 文件 | 层级 | 职责 |
|------|------|------|
| `evaluation.py` | [TODO] | [TODO: 描述职责] |
| `minimax.py` | [TODO] | [TODO: 描述职责] |
<!-- /AUTO:responsibilities -->

<!-- HUMAN:responsibilities_notes -->
**职责说明**：

[TODO: 补充各文件的详细职责描述，说明每个文件在整体架构中的角色]
<!-- /HUMAN:responsibilities_notes -->

---

## 4. 依赖关系

<!-- AUTO:dependencies -->
**架构图**：

![依赖关系图](images/classic_dependency_graph.png)

> 生成命令: `python3 -m scripts.module_inspector <module> --graph --files`

**依赖模块说明**：

| 依赖模块 | 依赖类型 | 业务逻辑 |
|----------|----------|----------|
| (无内部依赖) | - | - |
<!-- /AUTO:dependencies -->

<!-- HUMAN:dependency_notes -->
**依赖设计原则**：[TODO: 描述依赖的设计原则，如 "入口层 → 业务层 → 工具层"]

**补充说明**：

[TODO: 补充自动生成内容未能涵盖的依赖说明，如设计决策、历史原因等]
<!-- /HUMAN:dependency_notes -->

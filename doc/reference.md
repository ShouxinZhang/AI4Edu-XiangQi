
## 5. 核心接口

<!-- AUTO:exports -->
**导出的 API**：

- `test_ws`
- `run_server`
- `print_board`
- `test_moves`
- `HistoryStorage`
- `HistoryManager`
- `MCTS`
- `XiangqiGame`
- `get_latest_checkpoint`
- `save_checkpoint`
- `load_checkpoint`
- `BroadcastClient`
- `XiangqiDataset`
- `GameLogger`
- `Coach`
<!-- /AUTO:exports -->

<!-- HUMAN:api_details -->
**接口说明**：

| API | 模块 | 用途 |
|-----|------|------|
| `XiangqiGame` | game.py | 象棋规则引擎，管理棋盘状态和走法验证 |
| `XiangqiNet` | rl.models.xiangqi_net | ResNet神经网络，输出策略和价值估计 |
| `MCTS` | rl.algorithms.mcts | 蒙特卡洛树搜索，结合神经网络进行决策 |
| `Coach` | rl.training.coach | 训练管理器，执行自我对弈和模型优化 |
| `RLEvaluator` | rl.evaluation.evaluator | 自动化基准测试工具，负责评估模型强度 |
| `MinimaxSolver` | classic.minimax | 通用 Alpha-Beta 剪枝求解器 |

```python
# 使用示例
from game import XiangqiGame
from rl.models.xiangqi_net import XiangqiNet
from rl.algorithms.mcts import MCTS

game = XiangqiGame()
net = XiangqiNet()
mcts = MCTS(game, net, {'num_mcts_sims': 50, 'cpuct': 1.0})

# 获取当前棋盘的最佳走法概率分布
board = game.get_canonical_board()
pi = mcts.get_action_prob(board, temp=0)
best_action = max(range(len(pi)), key=lambda i: pi[i])
```
<!-- /HUMAN:api_details -->

---

## 6. 数据模型

<!-- HUMAN:data_models -->
**核心数据结构**：

```python
# 棋盘表示 (10x9 numpy数组)
# 正数=红方, 负数=黑方
# 1=帅/将, 2=仕, 3=象, 4=马, 5=车, 6=炮, 7=兵/卒
board = np.array([
    [5, 4, 3, 2, 1, 2, 3, 4, 5],  # 红方底线
    ...
    [-5,-4,-3,-2,-1,-2,-3,-4,-5]  # 黑方底线
])

# 走法编码
# action = start_pos * 90 + end_pos
# start_pos = y * 9 + x
```
<!-- /HUMAN:data_models -->

---

## 7. 扩展指南

<!-- HUMAN:extension -->
### 如何添加新功能

1. **增强神经网络**：修改 `model.py` 中的 `XiangqiNet` 类
2. **调整MCTS参数**：在 `train.py` 或 `server.py` 中修改 `args` 字典
3. **添加新的训练策略**：扩展 `Coach` 类的 `learn()` 方法

### 注意事项

- 修改棋盘表示后需同步更新 `game.py` 和前端的转换逻辑
- 训练时建议先用少量模拟次数验证流程正确性
- 神经网络结构变化后需重新训练
<!-- /HUMAN:extension -->

---

## 8. 代码质量

<!-- AUTO:quality -->

**行数统计**：

- `mcp_server.py`: 796 行 (接近阈值)
- ⚠️ `semver.js`: 1643 行 (超出 843 行)
- ⚠️ `full-versions.js`: 1683 行 (超出 883 行)
- ⚠️ `full-chromium-versions.js`: 2629 行 (超出 1829 行)
- `refresh-runtime.js`: 663 行 (接近阈值)
- ⚠️ `index.js`: 1737 行 (超出 937 行)
- ⚠️ `parse.js`: 1114 行 (超出 314 行)
- ⚠️ `parse.js`: 1085 行 (超出 285 行)
- `_tsserver.js`: 659 行 (接近阈值)
- ⚠️ `_tsc.js`: 132810 行 (超出 132010 行)
- ⚠️ `typescript.js`: 199120 行 (超出 198320 行)
- ⚠️ `react-dom-client.production.js`: 16049 行 (超出 15249 行)
- ⚠️ `react-dom-server.bun.development.js`: 9605 行 (超出 8805 行)
- ⚠️ `react-dom-server.browser.development.js`: 10601 行 (超出 9801 行)
- ⚠️ `react-dom-server.browser.production.js`: 7410 行 (超出 6610 行)
- ⚠️ `react-dom-server.bun.production.js`: 6745 行 (超出 5945 行)
- ⚠️ `react-dom-server.edge.development.js`: 10620 行 (超出 9820 行)
- ⚠️ `react-dom-profiling.profiling.js`: 18068 行 (超出 17268 行)
- ⚠️ `react-dom-server-legacy.node.production.js`: 6692 行 (超出 5892 行)
- ⚠️ `react-dom-client.development.js`: 28121 行 (超出 27321 行)
- ⚠️ `react-dom-server.node.production.js`: 7707 行 (超出 6907 行)
- ⚠️ `react-dom-server.edge.production.js`: 7512 行 (超出 6712 行)
- ⚠️ `react-dom-server.node.development.js`: 10802 行 (超出 10002 行)
- ⚠️ `react-dom-server-legacy.browser.development.js`: 9877 行 (超出 9077 行)
- ⚠️ `react-dom-profiling.development.js`: 28503 行 (超出 27703 行)
- ⚠️ `react-dom-server-legacy.browser.production.js`: 6603 行 (超出 5803 行)
- ⚠️ `react-dom-server-legacy.node.development.js`: 9877 行 (超出 9077 行)
- ⚠️ `source-map-consumer.js`: 1188 行 (超出 388 行)
- ⚠️ `parseAst.js`: 2318 行 (超出 1518 行)
- ⚠️ `rollup.js`: 23869 行 (超出 23069 行)
- ⚠️ `index.js`: 9003 行 (超出 8203 行)
- ⚠️ `node-entry.js`: 23947 行 (超出 23147 行)
- ⚠️ `parseAst.js`: 2086 行 (超出 1286 行)
- ⚠️ `watch.js`: 9297 行 (超出 8497 行)
- ⚠️ `helpers-generated.js`: 1442 行 (超出 642 行)
- `printer.js`: 780 行 (接近阈值)
- `typescript.js`: 725 行 (接近阈值)
- `flow.js`: 658 行 (接近阈值)
- ⚠️ `index.js`: 1251 行 (超出 451 行)
- ⚠️ `core.js`: 1726 行 (超出 926 行)
- ⚠️ `lowercase.js`: 2896 行 (超出 2096 行)
- ⚠️ `index.js`: 2797 行 (超出 1997 行)
- ⚠️ `index.js`: 14662 行 (超出 13862 行)
- ⚠️ `index.js`: 1043 行 (超出 243 行)
- ⚠️ `import-meta-resolve.js`: 1042 行 (超出 242 行)
- ⚠️ `lucide-react.js`: 25489 行 (超出 24689 行)
- ⚠️ `dynamicIconImports.js`: 1913 行 (超出 1113 行)
- ⚠️ `lucide-react.js`: 1667 行 (超出 867 行)
- ⚠️ `index.js`: 1663 行 (超出 863 行)
- ⚠️ `lucide-react.js`: 25485 行 (超出 24685 行)
- ⚠️ `index.js`: 1335 行 (超出 535 行)
- ⚠️ `module-runner.js`: 1311 行 (超出 511 行)
- ⚠️ `cli.js`: 949 行 (超出 149 行)
- ⚠️ `dep-D4NMHUTW.js`: 49531 行 (超出 48731 行)
- ⚠️ `dep-DWMUTS1A.js`: 7113 行 (超出 6313 行)
- ⚠️ `dep-C9BXG1mU.js`: 822 行 (超出 22 行)
- ⚠️ `dep-CvfTChi5.js`: 8218 行 (超出 7418 行)
- ⚠️ `lucide-react.js`: 28817 行 (超出 28017 行)
- ⚠️ `react-dom_client.js`: 20215 行 (超出 19415 行)
- ⚠️ `chunk-IGD3ZNHK.js`: 1033 行 (超出 233 行)
- ⚠️ `main.js`: 2242 行 (超出 1442 行)
- ⚠️ `react.development.js`: 1284 行 (超出 484 行)
- ⚠️ `react.react-server.development.js`: 848 行 (超出 48 行)

<!-- /AUTO:quality -->

---

## 9. 已知限制

<!-- HUMAN:limitations -->
**当前已知限制：**

1. **训练时间**：需要数小时GPU训练才能达到初级水平
2. **规则完整性**：尚未实现"将帅对面"规则检测
3. **和棋检测**：暂不支持重复局面和长将自动和棋
4. **性能优化**：MCTS可进一步并行化以提升速度

**待改进项：**

- 添加棋谱导入/导出功能
- 支持悔棋历史记录持久化
- 实现分布式训练支持
<!-- /HUMAN:limitations -->


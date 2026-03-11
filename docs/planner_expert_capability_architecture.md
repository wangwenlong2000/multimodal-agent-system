# Planner 读取专家能力摘要，Expert 读取工具白名单（v6）

## 核心分层

- Planner：只做“任务级规划”
  - 识别应该调用哪些专家
  - 给每个专家生成子任务卡片
  - 不决定具体工具顺序
- Expert：做“工具级决策”
  - 只看到自己的工具白名单
  - 自主决定先调用哪个工具、是否继续、何时结束

## 为什么这样设计

这样可以避免 Planner 直接看到全量 MCP 工具而变得越来越重；后续新增工具时，只要：

1. 更新工具插件与 MCP server
2. 把工具加入对应专家的 `tools.yaml`
3. 更新 `configs/expert_registry.yaml` 中该专家的能力摘要

Planner 就能通过专家能力摘要识别“哪个专家新增了什么能力”，而不需要知道工具的具体参数与 schema。

## 新增工具时的更新路径

- 工具层：`plugins/tools/...`
- 专家白名单：`plugins/experts/<expert>/tools.yaml`
- 专家能力摘要：`configs/expert_registry.yaml`

## 关键文件

- `configs/expert_registry.yaml`：Planner 读的专家能力注册表
- `core/expert_registry.py`：能力注册表读取与摘要接口
- `graph/nodes/planner.py`：使用专家能力摘要生成任务卡片
- `core/expert_agent.py`：专家自主工具调用循环
- `plugins/experts/*/tools.yaml`：专家工具白名单

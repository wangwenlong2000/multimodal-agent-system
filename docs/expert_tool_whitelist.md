# 专家工具白名单与自主工具调用说明（v5）

第五版开始，每个专家不再由程序写死工具调用顺序，而是进入“受限白名单下的自主工具调用循环”。

## 核心原则

- 每个专家只能看到自己的 `tools.yaml` 中声明的工具。
- 模型每一轮只能在这些白名单工具中二选一：
  - 调用某个工具
  - 结束并产出最终结果
- 即使模型输出了不在白名单中的工具，`tool_resolver` 也会拒绝执行。

## 运行流程

1. `handler.py` 创建 `ExpertToolAgent`
2. `ExpertToolAgent` 读取本专家的 `tools.yaml`
3. 通过 `tool_resolver.get_tools_schema()` 构造工具白名单 schema
4. 把白名单 schema 注入 Qwen 提示词
5. Qwen 返回 JSON：
   - `{"action":"call_tool","tool_name":"...","tool_args":{...}}`
   - 或 `{"action":"finish"}`
6. 运行时执行业务工具，并把结果回灌给专家
7. 达到停止条件后，专家输出结构化结果

## 重要文件

- `core/expert_agent.py`：专家自主工具调用循环
- `core/tool_resolver.py`：工具白名单与权限检查
- `plugins/experts/*/tools.yaml`：每个专家自己的工具白名单
- `plugins/experts/*/handler.py`：专家入口，现在统一委托给 `ExpertToolAgent`

## 当前能力边界

- 当前版本是“JSON 决策循环”，不是原生 function-calling SDK 绑定。
- 但已经具备专家自主选工具、工具白名单约束、工具结果回灌的完整机制。
- 后续如需升级为原生 tool calling，只需要替换 `ExpertToolAgent` 的动作决策层。

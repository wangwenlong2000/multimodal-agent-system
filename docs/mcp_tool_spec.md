# MCP Tool Specification (v4)

第四版开始，工具调用链优先通过真正的 MCP client 走 stdio 连接到 MCP server。

## 设计原则

1. `plugins/tools/**/tool.yaml` 里的 `source: mcp` 表示该工具优先通过 MCP 调用。
2. `configs/mcp_servers.yaml` 定义 MCP server 的启动命令。
3. `core/mcp_client.py` 负责通过 Python MCP SDK 建立 stdio 会话并调用工具。
4. `core/tool_resolver.py` 负责路由：
   - 优先走 MCP
   - MCP 失败时可按配置回退到本地 `adapter.py`

## 当前 transport

- `stdio`

## 当前 server 映射

- `general_server`
- `trajectory_server`
- `netflow_server`
- `streetview_server`

## 当前回退策略

`configs/mcp_servers.yaml` 中：

```yaml
fallback_to_local_adapter: true
```

表示当 MCP server 未安装、未启动或调用失败时，仍可退回本地占位实现，保证系统整体可跑通。

## 说明

这是一版“真实 MCP client 接入 + 本地 fallback 并存”的工程折中方案，适合当前项目处于算法工具逐步补全的阶段。

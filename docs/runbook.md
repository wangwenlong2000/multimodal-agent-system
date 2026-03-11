# Runbook

## 运行主系统

```bash
python app/main.py --query "分析目标对象在夜间的轨迹、网络流量与街景情况" --dump-state
```

## 启动 MCP 示例服务（可选）

```bash
python mcp/servers/general_server.py
python mcp/servers/trajectory_server.py
python mcp/servers/netflow_server.py
python mcp/servers/streetview_server.py
```

## 切换模型提供方

修改 `configs/active_model_provider.yaml`：

```yaml
active_provider: local_vllm
active_model: qwen2.5-14b-instruct
role_models:
  planner: qwen2.5-14b-instruct
  expert: qwen2.5-14b-instruct
  response: qwen2.5-14b-instruct
```

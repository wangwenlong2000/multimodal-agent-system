# Directory Guide (v5)

本文说明项目中每个主要目录和文件夹的职责，便于你自己维护和后续交接。

## 根目录

- `app/`
  - 应用入口层。
  - `main.py` 是 CLI 启动入口。
  - `bootstrap.py` 负责初始化系统上下文、配置、插件、模型、MCP client、案例仓库等。

- `graph/`
  - LangGraph 编排层。
  - 负责定义状态、节点、图结构与执行顺序。
  - `state.py` 定义整条图上的共享状态结构。
  - `graph_builder.py` 把各节点串成完整流程。

- `graph/nodes/`
  - 每个 LangGraph 节点单独一个文件。
  - `preprocess_query.py`：预处理用户问题。
  - `planner.py`：调用 Qwen API 做结构化规划。
  - `route_experts.py`：选择专家并探测 MCP server 可用性。
  - `execute_experts.py`：并行执行专家插件。
  - `align_results.py`：调用通用工具做结果对齐。
  - `fuse_results.py`：调用融合插件合并结果。
  - `generate_response.py`：调用 Qwen API 生成最终回答。
  - `write_case.py`：把成功结果写入案例仓库。

- `core/`
  - 系统核心基础设施层。
  - `config_loader.py`：加载 YAML 配置。
  - `plugin_loader.py`：扫描并发现插件。
  - `prompt_loader.py`：读取 prompt 模板。
  - `expert_agent.py`：第五版新增，负责专家在白名单工具内自主决策调用工具。
  - `model_resolver.py`：统一模型 provider 出口。
  - `mcp_client.py`：第四版新增，真正的 MCP stdio client。
  - `tool_resolver.py`：统一工具调用入口，优先走 MCP，失败时按配置回退本地 adapter。
  - `fusion_resolver.py`：加载融合插件。
  - `case_manager.py`：案例仓库写入、索引、去重。
  - `schema_validator.py`：预留给后续严格 schema 校验。
  - `evidence_merger.py`：证据合并辅助逻辑。

- `plugins/`
  - 所有可插拔模块都放在这里。

### `plugins/experts/`

每个专家一个独立目录。

- `trajectory_expert/`：时空轨迹专家
- `netflow_expert/`：网络流量专家
- `streetview_expert/`：街景视觉专家

每个专家目录里通常有：
- `plugin.yaml`：插件元信息
- `prompt.system.md`：系统提示词
- `prompt.user.md`：用户提示模板
- `schema.input.json`：输入结构定义
- `schema.output.json`：输出结构定义
- `tools.yaml`：该专家可用工具声明
- `handler.py`：专家执行入口

### `plugins/tools/`

工具插件目录，按领域拆分。

- `general/`：通用工具
  - `align_time/`
  - `align_location/`
  - `entity_mapping/`
  - `fuse_evidence/`

- `trajectory/`：轨迹工具
  - `load_trajectory/`
  - `stay_points/`
  - `map_match/`

- `netflow/`：流量工具
  - `load_netflow/`
  - `flow_aggregate/`
  - `anomaly_detect/`

- `streetview/`：街景工具
  - `load_streetview/`
  - `scene_classify/`
  - `object_detect/`

每个工具目录通常有：
- `tool.yaml`：工具元信息（名称、来源、所属 MCP server）
- `adapter.py`：本地 fallback 实现

### `plugins/models/`

模型 provider 插件目录。

- `qwen_api/`：当前主 provider，使用 Qwen API
- `local_vllm/`：预留给未来本地模型部署

每个 provider 目录通常有：
- `provider.yaml`：provider 元信息
- `models.yaml`：支持的模型与用途
- `client.py`：实际客户端实现

### `plugins/fusion/`

融合策略插件目录。

- `simple_fusion/`：简单融合策略
- `cross_modal_anomaly/`：跨模态异常融合策略

### `plugins/cases/`

案例仓库相关目录。

- `repository/`：案例库读写、索引、去重逻辑
- `classic_cases/`：人工维护的经典案例
- `generated_cases/`：系统运行后自动沉淀的案例

- `mcp/`
  - MCP 相关目录。
  - `servers/`：各领域 MCP server 入口脚本。
  - `registry/`：工具注册表。

- `configs/`
  - 系统配置目录。
  - `system.yaml`：系统级配置。
  - `active_plugins.yaml`：启用哪些插件。
  - `active_model_provider.yaml`：当前模型 provider 与角色模型映射。
  - `case_policy.yaml`：案例写回策略。
  - `mcp_servers.yaml`：第四版新增，MCP server 的 stdio 启动配置。
  - `logging.yaml`：日志配置。

- `data/`
  - 样例数据、mock 数据、映射表、缓存等。

- `tests/`
  - 测试目录。
  - `unit/`：单元测试
  - `integration/`：集成测试
  - `regression/`：回归测试（后续可扩）

- `docs/`
  - 项目文档目录。
  - 包括架构说明、目录指南、MCP 说明、模型 provider 说明、安装/运行文档等。

- `scripts/`
  - 常用辅助脚本。
  - 如创建 conda 环境、启动演示、启动 MCP server 等。

## 第四版最重要的变化

第四版之前，工具虽然声明成了 `source: mcp`，但实际上主要还是通过本地 `adapter.py` 在跑。

第四版开始：

1. 真正增加了 `core/mcp_client.py`
2. 真正通过 MCP Python SDK 的 stdio client 调 MCP server
3. `tool_resolver.py` 改成了“优先 MCP，失败时 fallback 本地 adapter”的模式
4. `route_experts.py` 会在执行前探测各 MCP server 的可用工具列表

这样整套系统的工具调用已经进入“真实 MCP 接入”阶段，而不是单纯占位结构。

## 第五版最重要的变化

第五版开始，专家插件不再由程序固定写死工具调用顺序。

现在每个专家会：

1. 读取自己的 `tools.yaml` 白名单
2. 只把这些白名单工具注入给 Qwen
3. 通过 `core/expert_agent.py` 进入多轮决策循环
4. 每一轮由 Qwen 决定：继续调用白名单内的哪个工具，还是结束
5. `tool_resolver.py` 在运行时再次校验白名单，防止越权调用

所以第五版的能力边界是：

- Planner 仍负责选择专家
- 但每个专家内部已经升级为“受限工具集下的自主工具调用智能体”
- 工具调用仍然优先走 MCP，失败时才 fallback 到本地 adapter


## v6 新增

- `configs/expert_registry.yaml`：Planner 使用的专家能力注册表。
- `core/expert_registry.py`：把能力注册表转换成 Planner 可用摘要。
- `docs/planner_expert_capability_architecture.md`：说明“Planner 看能力，Expert 看工具”的新分层。


## v8 新增

- `data/samples/netflow/sample_packets.csv`：网络流量单场景真实样例 CSV。
- `plugins/tools/netflow/common.py`：netflow 工具共用逻辑。
- `configs/active_plugins_multiscene_example.yaml`：后续切回多场景的示例配置。
- `docs/single_scenario_netflow_mode.md`：说明单场景优先、多场景框架保留的运行方式。

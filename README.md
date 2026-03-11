# Multimodal Agent System (v8)

这是一套基于 **LangGraph + MCP + Qwen API** 的多场景智能体系统仓库。

## v8 的定位

这一版采用：

- **单场景 netflow 优先跑通**
- **多场景框架继续保留**

也就是说：
- 当前默认只启用 `netflow_expert`
- 但仓库里仍保留 `trajectory_expert` 和 `streetview_expert`
- Planner / preprocess / expert registry / MCP / fusion 的多场景结构都还在
- 后续只需要重新启用插件配置，就可以逐步恢复多场景

## 当前默认运行链路

```text
query
  -> preprocess_query
  -> planner
  -> execute_experts (netflow_expert)
  -> align_results
  -> fuse_results
  -> generate_response
```

## 当前做实的最小工具链

- `load_netflow`：从 CSV 读取真实样例数据
- `flow_aggregate`：五元组聚合
- `anomaly_detect`：规则式异常检测

## 当前默认数据

```text
data/samples/netflow/sample_packets.csv
```

## 快速开始

```bash
conda env create -f environment.yml
conda activate multimodal-agent
cp .env.example .env
# 在 .env 中填写 QWEN_API_KEY
python app/main.py --query "分析目标对象夜间的网络流量是否异常" --dump-state
```

## 切回多场景

```bash
cp configs/active_plugins_multiscene_example.yaml configs/active_plugins.yaml
```

## 重要文档

- `docs/single_scenario_netflow_mode.md`
- `docs/query_understanding_upgrade.md`
- `docs/planner_expert_capability_architecture.md`
- `docs/intelligence_gap_review.md`


# Multimodal Agent System v11 Enterprise

这是一个面向企业交付的多场景智能体系统，强调：

- 多场景统一框架
- 智能 planner
- 智能 expert
- MCP-only 工具执行
- fail-closed 模型调用
- 可扩展的专家与工具注册机制

## 核心特性

### 1. 智能 Planner
Planner 调用真实 Qwen API，根据：
- 用户问题
- 预处理结果
- 专家领域与能力
自动完成：
- 场景匹配
- 专家选择
- 任务分解

### 2. 智能 Expert
每个专家会把自己的：
- 角色说明
- 领域说明
- 能力说明
- 工具白名单
- 工具 schema
注入到 LLM，上下文驱动自主选择工具。

### 3. MCP-only
工具不再以本地 adapter 作为主路径，而是通过 MCP server 调用。
这样后续新增工具时，更容易扩展和交付。

### 4. Fail-closed
模型调用失败不会静默降级。
Qwen 不可用、返回空内容或无效 JSON 时，系统直接报错。

## 环境变量

至少需要：

```bash
export QWEN_API_KEY="your_key"
export QWEN_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
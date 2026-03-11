# 单场景 Netflow 模式（v8）

这一版默认以 **网络流量单场景** 运行，但保留多场景扩展框架。

## 当前默认行为
- `configs/active_plugins.yaml` 只启用 `netflow_expert`
- Planner 仍然保留多场景接口（`modalities[]`、`tasks[]`）
- 但因为当前只有 `netflow_expert` 激活，所以系统会自动只规划并执行 netflow 场景
- `trajectory_expert` / `streetview_expert` 仍保留在仓库中，后续可直接重新启用

## 如何恢复多场景
将下面这个示例文件覆盖当前配置即可：

```bash
cp configs/active_plugins_multiscene_example.yaml configs/active_plugins.yaml
```

## 当前已做实的最小链路
- `load_netflow`：读取本地 CSV 样例数据
- `flow_aggregate`：做基础五元组聚合
- `anomaly_detect`：做规则式异常检测

## 数据文件
默认样例数据：

```text
data/samples/netflow/sample_packets.csv
```

## 当前目标
先确保单场景运行通畅，再逐步重新打开多场景。

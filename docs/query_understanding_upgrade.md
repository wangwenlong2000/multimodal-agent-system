# Query Understanding 升级说明（v7）

本版本将 `preprocess_query` 从“关键词匹配器”升级为“Qwen 驱动的轻量语义理解器”。

## 设计目标
- 不再仅靠关键词匹配模态和意图
- 利用当前系统实际可用的专家能力摘要做语义理解
- 输出稳定的 `parsed_query` 结构，供 planner 消费
- 解析失败时有规则 fallback，不让主链路中断

## 当前实现
`graph/nodes/preprocess_query.py` 执行顺序：
1. 读取可用专家列表
2. 从 `ExpertRegistry` 生成专家能力摘要
3. 调用 Qwen 输出结构化 `parsed_query`
4. 校验并规范化字段
5. 如果解析失败或字段缺失，用 fallback 自动补全

## 输出 schema
`parsed_query` 顶层字段：
- `title`
- `raw_query`
- `intent`
- `modalities`
- `entities`
- `constraints`
- `analysis_type`
- `requires_alignment`
- `confidence`

## 为什么更智能
- 可以理解“外联行为”“停留模式”“道路场景”等隐式表达
- 能结合当前激活专家能力判断模态，而不是死写关键词
- 对新增场景更友好：只要补专家能力摘要，理解器就更容易适配

## 仍然存在的限制
- 还没有单独的 schema validator 强制校验 `parsed_query`
- 还没有 few-shot query understanding case 注入
- 还没有用用户历史任务/案例库提升 query 理解

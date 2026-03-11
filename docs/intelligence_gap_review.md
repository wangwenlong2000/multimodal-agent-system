# 系统当前仍然不够智能、值得后续评估的点

这份文档列出当前仓库在“智能性”方面仍然偏工程骨架/原型的部分，供后续迭代时决策。

## 1. preprocess_query 已升级，但仍可继续增强
当前：
- 已用 Qwen 做轻量语义解析
- 已接入 expert registry 摘要
- 已有 fallback

仍待完善：
- 给 `parsed_query` 加严格 schema validator
- 增加 query understanding 的 few-shot 经典案例
- 时间表达标准化（如“昨天夜里”“上周末”）
- 实体抽取更细（device_id / ip / user / area）

## 2. planner 仍然偏“单轮静态规划”
当前：
- 会基于专家能力摘要生成任务卡片
- 不直接看工具

仍待完善：
- 规划质量自检（plan critique）
- 多步计划修正
- 当专家失败时动态重规划
- 更细的 success criteria 与 expected output 校验

## 3. expert 工具调用循环还比较基础
当前：
- 专家会在自己的白名单工具中自主选择
- 有运行时白名单校验

仍待完善：
- 每个专家的工具调用策略 still 很通用，缺少专家专属策略
- 没有根据 task card 智能调整最大步数
- 没有“工具失败后重新选择工具”的更强恢复逻辑
- 没有把工具返回 schema 强约束进 agent loop

## 4. 工具层的“智能”主要还在 mock/placeholder
当前：
- MCP 通道通了
- 工具白名单通了

仍待完善：
- `load_*` 接入真实数据
- `anomaly_detect / scene_classify / object_detect / stay_points` 做成真实逻辑
- 对齐工具不再是 placeholder

## 5. fusion 还是偏浅层
当前：
- 能执行 fusion plugin
- 能输出融合结果与总结

仍待完善：
- 真正基于时间/空间/实体做证据融合
- 对矛盾证据做冲突处理
- 输出更可解释的 evidence chain
- 根据不同任务类型选择不同 fusion plugin

## 6. 案例库还没有真正反哺智能体
当前：
- 有 classic cases
- 有 generated cases
- 有写回逻辑

仍待完善：
- planner few-shot from case library
- preprocess few-shot from case library
- expert tool strategy retrieval from similar cases
- case 质量评分和去重增强

## 7. 图层控制还偏线性
当前：
- 主链路已打通
- experts 在 `execute_experts` node 中运行

仍待完善：
- 针对失败专家的条件分支
- 更智能的跳过对齐/跳过融合
- 专家单独拆 node 的时机判断与监控

## 8. 评测体系还薄弱
当前：
- 可以 dump state
- 可以看 debug 信息

仍待完善：
- 单场景回归测试集
- 多场景任务级评测
- planner 质量评测
- tool-use 成功率与误调用统计

## 推荐优先级
最值得优先改的顺序：
1. 单场景真实数据接入（先 netflow）
2. `parsed_query` / `plan` / `expert_result` 三类 schema 严格校验
3. expert tool loop 错误恢复增强
4. case library 真正回灌 preprocess / planner
5. fusion 智能化

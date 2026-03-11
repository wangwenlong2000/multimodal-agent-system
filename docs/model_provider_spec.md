# Model Provider Spec

模型提供方必须实现：

```python
get_client()
```

返回对象至少提供：

```python
chat(system_prompt: str, user_prompt: str, model: str) -> str
```

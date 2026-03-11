# Setup

## 1. 创建 conda 环境

```bash
conda env create -f environment.yml
conda activate multimodal-agent
```

## 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入 QWEN_API_KEY
```

Linux / macOS 也可以直接导出：

```bash
export QWEN_API_KEY=your_qwen_api_key_here
export QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

Windows PowerShell：

```powershell
$env:QWEN_API_KEY="your_qwen_api_key_here"
$env:QWEN_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
```

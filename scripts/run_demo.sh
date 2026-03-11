#!/usr/bin/env bash
set -euo pipefail
python app/main.py --query "分析目标对象在夜间的轨迹、网络流量与街景情况" --dump-state

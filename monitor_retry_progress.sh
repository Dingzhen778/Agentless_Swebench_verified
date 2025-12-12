#!/bin/bash
echo "==================================================="
echo "监控 retry_15_fixed 进度"
echo "==================================================="
echo

if [ -f "model_patch/retry_15_fixed/output.jsonl" ]; then
    count=$(wc -l < model_patch/retry_15_fixed/output.jsonl)
    echo "✓ 已完成: $count/15"
    echo

    # 检查成功率
    python3 -c "
import json
fixed = 0
with open('model_patch/retry_15_fixed/output.jsonl') as f:
    for line in f:
        data = json.loads(line)
        raw = data.get('raw_output', [])
        content = raw[0] if isinstance(raw, list) and len(raw) > 0 and raw[0] else ''
        if content and len(content) > 50 and '<<<<<<< SEARCH' in content:
            fixed += 1
print(f'  成功修复: {fixed}/$count')
"
else
    echo "✗ 输出文件还未生成"
fi

echo
echo "最近的日志:"
tail -10 model_patch/logs/retry_15_fixed.log 2>/dev/null || echo "日志文件不存在"

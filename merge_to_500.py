#!/usr/bin/env python3
"""合并所有patches，生成最终的500个完整patches"""
import json
import os
from datetime import datetime

print("=" * 70)
print("合并patches生成最终500个")
print("=" * 70)
print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# 读取原始的final_all_patches.jsonl
print("[1/4] 读取原始patches...")
original_patches = {}
with open('model_patch/final_all_patches.jsonl') as f:
    for line in f:
        data = json.loads(line)
        instance_id = data['instance_id']
        original_patches[instance_id] = data

print(f"  原始patches: {len(original_patches)}个")

# 读取新生成的44个patches
print("[2/4] 读取新生成的44个patches...")
new_patches = {}
new_valid = 0
new_empty = 0

with open('model_patch/repair_only_43/output.jsonl') as f:
    for line in f:
        data = json.loads(line)
        instance_id = data['instance_id']
        new_patches[instance_id] = data

        # 检查是否有效
        raw_output = data.get('raw_output', [[]])[0]
        content = ''
        if isinstance(raw_output, list) and len(raw_output) > 0:
            content = str(raw_output[0]) if raw_output[0] else ''
        elif isinstance(raw_output, str):
            content = raw_output

        if content and len(content) > 50:
            new_valid += 1
        else:
            new_empty += 1

print(f"  新patches总数: {len(new_patches)}个")
print(f"  其中有效: {new_valid}个")
print(f"  其中空: {new_empty}个")
print()

# 合并：用新的patches更新原始patches
print("[3/4] 合并patches...")
updated_count = 0
for instance_id, new_data in new_patches.items():
    if instance_id in original_patches:
        original_patches[instance_id] = new_data
        updated_count += 1

print(f"  更新了 {updated_count} 个实例")
print()

# 写入最终文件
output_file = 'model_patch/final_500_patches.jsonl'
backup_file = f'model_patch/final_all_patches_backup_{int(datetime.now().timestamp())}.jsonl'

print("[4/4] 写入最终文件...")
# 备份原文件
os.system(f'cp model_patch/final_all_patches.jsonl {backup_file}')
print(f"  ✓ 原文件已备份: {backup_file}")

# 写入新文件（按instance_id排序）
with open(output_file, 'w') as f:
    for instance_id in sorted(original_patches.keys()):
        f.write(json.dumps(original_patches[instance_id]) + '\n')

print(f"  ✓ 最终文件: {output_file}")
print()

# 验证质量
print("=" * 70)
print("最终验证")
print("=" * 70)

total = 0
valid = 0
empty = 0

with open(output_file) as f:
    for line in f:
        total += 1
        data = json.loads(line)

        raw_output = data.get('raw_output', [])
        content = ''
        if isinstance(raw_output, list) and len(raw_output) > 0:
            content = str(raw_output[0]) if raw_output[0] else ''
        elif isinstance(raw_output, str):
            content = raw_output

        if content and len(content) > 50:
            valid += 1
        else:
            empty += 1

print(f"总实例数: {total}")
print(f"有效patches: {valid} ({valid/total*100:.1f}%)")
print(f"空patches: {empty} ({empty/total*100:.1f}%)")
print()

if total == 500:
    print("✅ 成功生成500个patches！")
else:
    print(f"⚠️  总数不是500，而是{total}")

print()
print("=" * 70)
print(f"最终文件: {output_file}")
print(f"有效patches: {valid}/500")
print("=" * 70)

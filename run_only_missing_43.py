#!/usr/bin/env python3
"""只处理缺失的43个实例"""
import os
import sys
import json
import subprocess

# 设置环境变量
os.environ['PYTHONPATH'] = '/volume/ai-infra/rhjiang/Agentless'
os.chdir('/volume/ai-infra/rhjiang/Agentless')

# 读取缺失实例列表
missing_instances = []
with open('missing_instances.txt') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('缺失') and not line.startswith('#'):
            missing_instances.append(line)

print(f"需要处理的缺失实例: {len(missing_instances)}个")

# 找到每个实例的定位结果
output_dir = "model_patch/repair_only_43"
os.makedirs(output_dir, exist_ok=True)

# 读取所有定位结果
all_locs = {}
for loc_file in ['model_patch/localization/loc_outputs.jsonl',
                 'model_patch/relocalize_44/loc_outputs.jsonl']:
    if os.path.exists(loc_file):
        with open(loc_file) as f:
            for line in f:
                data = json.loads(line)
                instance_id = data['instance_id']
                all_locs[instance_id] = data

# 创建只包含缺失实例的定位文件
missing_loc_file = f"{output_dir}/missing_43_loc.jsonl"
found_count = 0
not_found = []

with open(missing_loc_file, 'w') as out:
    for inst_id in missing_instances:
        if inst_id in all_locs:
            out.write(json.dumps(all_locs[inst_id]) + '\n')
            found_count += 1
        else:
            not_found.append(inst_id)

print(f"找到定位结果: {found_count}/{len(missing_instances)}")
if not_found:
    print(f"未找到定位结果: {len(not_found)}个")
    for inst in not_found[:5]:
        print(f"  - {inst}")

# 运行repair（只针对这43个）
print(f"\n开始repair {found_count}个实例...")

cmd = [
    sys.executable,
    'agentless/repair/repair.py',
    '--loc_file', missing_loc_file,
    '--output_folder', output_dir,
    '--loc_interval',
    '--top_n', '3',
    '--context_window', '10',
    '--max_samples', '10',
    '--cot',
    '--diff_format',
    '--gen_and_process',
    '--dataset', 'princeton-nlp/SWE-bench_Verified',
]

print(f"命令: {' '.join(cmd)}")
print("="*60)

result = subprocess.run(cmd)
sys.exit(result.returncode)

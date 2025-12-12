#!/usr/bin/env python3
"""重新repair 15个有文件但失败的实例"""
import json
import os
import subprocess
import sys

# 15个有定位文件但repair失败的实例
HAS_FILES_FAILED = [
    'astropy__astropy-14995', 'django__django-11163', 'django__django-12155',
    'django__django-13297', 'django__django-13344', 'django__django-13568',
    'django__django-14089', 'django__django-14787', 'django__django-15103',
    'django__django-15499', 'django__django-17087', 'django__django-9296',
    'pytest-dev__pytest-6197', 'sympy__sympy-11618', 'sympy__sympy-24066'
]

print("=" * 70)
print(f"重新Repair {len(HAS_FILES_FAILED)}个有文件但失败的实例")
print("=" * 70)
print()

# 读取这15个实例的定位结果
all_locs = {}
for loc_file in ['model_patch/localization/loc_outputs.jsonl',
                 'model_patch/relocalize_44/loc_outputs.jsonl']:
    if os.path.exists(loc_file):
        with open(loc_file) as f:
            for line in f:
                data = json.loads(line)
                instance_id = data['instance_id']
                if instance_id in HAS_FILES_FAILED:
                    all_locs[instance_id] = data

print(f"找到 {len(all_locs)} 个实例的定位结果")

# 创建定位文件
output_dir = "model_patch/retry_15"
os.makedirs(output_dir, exist_ok=True)

loc_file = f"{output_dir}/loc_inputs.jsonl"
with open(loc_file, 'w') as f:
    for inst_id in sorted(all_locs.keys()):
        f.write(json.dumps(all_locs[inst_id]) + '\n')

print(f"✓ 定位文件: {loc_file}")
print()

# 运行repair(使用更多samples)
print("=" * 70)
print("运行Repair - max_samples=20 (之前是10)")
print("=" * 70)
print()

cmd = [
    sys.executable,
    'agentless/repair/repair.py',
    '--loc_file', loc_file,
    '--output_folder', output_dir,
    '--loc_interval',
    '--top_n', '3',
    '--context_window', '10',
    '--max_samples', '20',  # 从10增加到20
    '--cot',
    '--diff_format',
    '--gen_and_process',
    '--dataset', 'princeton-nlp/SWE-bench_Verified',
]

print(f"命令: {' '.join(cmd)}")
print("=" * 60)
print()

result = subprocess.run(cmd)
sys.exit(result.returncode)

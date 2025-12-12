#!/usr/bin/env python3
"""诊断23个空patches的失败原因"""
import json
import os

# 23个空patches
EMPTY_INSTANCES = [
    'astropy__astropy-14995', 'django__django-10880', 'django__django-11163',
    'django__django-11740', 'django__django-12155', 'django__django-13112',
    'django__django-13297', 'django__django-13344', 'django__django-13568',
    'django__django-14089', 'django__django-14787', 'django__django-15103',
    'django__django-15499', 'django__django-15973', 'django__django-17087',
    'django__django-9296', 'pydata__xarray-3677', 'pydata__xarray-4687',
    'pytest-dev__pytest-6197', 'sphinx-doc__sphinx-10614', 'sphinx-doc__sphinx-7440',
    'sympy__sympy-11618', 'sympy__sympy-24066'
]

print("=" * 70)
print("诊断23个空Patches的失败原因")
print("=" * 70)
print()

# 读取所有定位结果
all_locs = {}
for loc_file in ['model_patch/localization/loc_outputs.jsonl',
                 'model_patch/relocalize_44/loc_outputs.jsonl']:
    if os.path.exists(loc_file):
        with open(loc_file) as f:
            for line in f:
                data = json.loads(line)
                instance_id = data['instance_id']
                all_locs[instance_id] = {
                    'file': loc_file,
                    'found_files': data.get('found_files', []),
                    'data': data
                }

# 分析每个空实例
no_localization = []
zero_files = []
has_files_but_failed = []

for inst in EMPTY_INSTANCES:
    if inst not in all_locs:
        no_localization.append(inst)
    elif len(all_locs[inst]['found_files']) == 0:
        zero_files.append(inst)
    else:
        has_files_but_failed.append((
            inst,
            len(all_locs[inst]['found_files']),
            all_locs[inst]['found_files'][:3]
        ))

# 输出分析结果
print("【失败原因分类】")
print()

print(f"1. 从未被定位 (No Localization): {len(no_localization)}/23")
print("   这些实例根本没有定位结果")
for inst in no_localization:
    print(f"   ✗ {inst}")
print()

print(f"2. 定位但找到0个文件 (Zero Files): {len(zero_files)}/23")
print("   定位运行了但没找到相关文件")
for inst in zero_files:
    print(f"   ✗ {inst}")
print()

print(f"3. 有定位文件但Repair失败: {len(has_files_but_failed)}/23")
print("   找到了文件但无法生成有效patch")
for inst, count, files in has_files_but_failed:
    print(f"   ~ {inst}: {count}个文件")
    for f in files:
        print(f"     - {f}")
print()

print("=" * 70)
print("【修复建议】")
print("=" * 70)
print()

if no_localization:
    print(f"针对{len(no_localization)}个未定位的实例:")
    print("  1. 运行完整的定位流程")
    print("  2. 检查这些实例是否在数据集中")
    print()

if zero_files:
    print(f"针对{len(zero_files)}个定位失败的实例:")
    print("  1. 使用更宽松的定位参数(增加top_n, context_window)")
    print("  2. 尝试不同的定位策略")
    print("  3. 手动查看issue,判断是否是定位算法问题")
    print()

if has_files_but_failed:
    print(f"针对{len(has_files_but_failed)}个Repair失败的实例:")
    print("  1. 增加max_samples (当前10, 建议15-20)")
    print("  2. 检查是否token超长导致截断过度")
    print("  3. 查看repair日志,了解具体失败原因")
    print("  4. 可能需要手动审查这些特别困难的实例")
    print()

# 保存详细信息到文件
output_file = "model_patch/empty_23_diagnosis.json"
diagnosis = {
    "total_empty": len(EMPTY_INSTANCES),
    "no_localization": no_localization,
    "zero_files": zero_files,
    "has_files_but_failed": [
        {
            "instance_id": inst,
            "file_count": count,
            "files": files
        }
        for inst, count, files in has_files_but_failed
    ]
}

with open(output_file, 'w') as f:
    json.dump(diagnosis, f, indent=2)

print(f"详细诊断信息已保存到: {output_file}")
print()

# 统计信息
print("=" * 70)
print("【统计总结】")
print("=" * 70)
print(f"空patches总数: {len(EMPTY_INSTANCES)}")
print(f"  - 未定位: {len(no_localization)} ({len(no_localization)/len(EMPTY_INSTANCES)*100:.1f}%)")
print(f"  - 定位失败(0文件): {len(zero_files)} ({len(zero_files)/len(EMPTY_INSTANCES)*100:.1f}%)")
print(f"  - Repair失败: {len(has_files_but_failed)} ({len(has_files_but_failed)/len(EMPTY_INSTANCES)*100:.1f}%)")
print()

# 预估修复潜力
estimated_fixable = len(has_files_but_failed) // 2  # 假设能修复一半
print(f"预估可修复数量: {estimated_fixable}-{len(has_files_but_failed)} 个")
print(f"预估最终成功率: {((477 + estimated_fixable)/500*100):.1f}% - {((477 + len(has_files_but_failed))/500*100):.1f}%")
print()

# Agentless v0.1.0 安装总结

## ✅ 完成的工作

### 1. 环境配置
- ✅ 创建了新的conda环境 `agentless` (Python 3.11)
- ✅ 安装了所有依赖包（openai, datasets, tiktoken, swebench等）
- ✅ Clone了Agentless v0.1.0到 `/volume/ai-infra/rhjiang/Agentless`

### 2. 代码修改（支持自定义API endpoint）
已修改以下文件以支持你的自定义API配置：

**`agentless/util/api_requests.py`**
- 添加了对`OPENAI_BASE_URL`环境变量的支持
- 支持自定义API endpoint和API key

**`agentless/fl/FL.py`**
- 添加了`AGENTLESS_MODEL`环境变量支持
- 将所有硬编码的模型名称改为可配置

**`agentless/repair/repair.py`**
- 修改`--model`参数从环境变量读取默认值
- 移除了模型选择限制

### 3. 配置文件
创建了以下配置和文档文件：

**`setup_env.sh`** - 环境变量配置脚本
```bash
source /volume/ai-infra/rhjiang/Agentless/setup_env.sh
```

**`QUICKSTART.md`** - 完整的快速入门指南

**`test_setup.py`** - 配置验证脚本

## 🚀 快速使用

### 激活环境并加载配置
```bash
# 激活conda环境
source /minconda3/etc/profile.d/conda.sh
conda activate agentless

# 加载环境变量
cd /volume/ai-infra/rhjiang/Agentless
source setup_env.sh
```

### 验证配置
```bash
python test_setup.py
```

### 运行示例（测试单个问题）
```bash
mkdir -p results

# 文件级定位
python agentless/fl/localize.py \
    --file_level \
    --target_id django__django-11039 \
    --output_folder results/test

# 查看输出
cat results/test/loc_outputs.jsonl
```

### 在SWE-bench Verified上运行
```bash
# 完整定位流程
python agentless/fl/localize.py \
    --file_level --related_level --fine_grain_line_level \
    --dataset princeton-nlp/SWE-bench_Verified \
    --output_folder results/verified/location \
    --top_n 3 --compress --context_window=10

# 生成补丁
python agentless/repair/repair.py \
    --loc_file results/verified/location/loc_outputs.jsonl \
    --output_folder results/verified/repair \
    --loc_interval --top_n=3 --context_window=10 \
    --max_samples 10 --cot --diff_format \
    --gen_and_process

# 选择最佳补丁
python agentless/repair/rerank.py \
    --patch_folder results/verified/repair \
    --num_samples 10 --deduplicate --plausible
```

## 📝 API配置详情

当前配置使用你提供的自定义API：

| 配置项 | 值 |
|--------|-----|
| Base URL | `https://console.scitix.ai/siflow/cetus/hisys/ylsun/eval-qwen2-5-72b-instruct/v1` |
| Model | `eval-qwen2-5-72b-instruct` |
| API Key | `dummy-key` |

如需修改，编辑 `setup_env.sh` 文件。

## 📚 文档位置

- **快速入门**: `/volume/ai-infra/rhjiang/Agentless/QUICKSTART.md`
- **原始README**: `/volume/ai-infra/rhjiang/Agentless/README.md`
- **配置脚本**: `/volume/ai-infra/rhjiang/Agentless/setup_env.sh`

## ⚠️ 注意事项

1. **Python版本**: 必须使用Python 3.11（agentless环境已配置）

2. **预处理数据**（可选）: 下载可以节省时间
   - 下载地址: https://github.com/OpenAutoCoder/Agentless/releases/tag/v0.1.0
   - 下载后设置: `export PROJECT_FILE_LOC=/path/to/data`

3. **并发处理**: v0.1.0版本没有`--num_threads`参数，任务按顺序处理

4. **Token计数**: 使用tiktoken，可能与自定义模型不完全匹配，但不影响功能

## 🔍 故障排查

如果遇到问题：

1. **检查环境变量是否加载**
   ```bash
   echo $OPENAI_BASE_URL
   echo $AGENTLESS_MODEL
   ```

2. **运行验证脚本**
   ```bash
   python test_setup.py
   ```

3. **检查API连接**
   - 确保BASE_URL可访问
   - 检查模型名称是否正确

4. **查看日志**
   - 定位日志: `results/*/localize.log`
   - 修复日志: `results/*/repair.log`

## 🎯 下一步建议

1. 先在单个实例上测试：`--target_id django__django-11039`
2. 确认API正常工作后，再运行完整数据集
3. 根据实际情况调整参数（`--top_n`, `--max_samples`等）

## 📧 参考资源

- Agentless GitHub: https://github.com/OpenAutoCoder/Agentless
- v0.1.0 Release: https://github.com/OpenAutoCoder/Agentless/releases/tag/v0.1.0
- SWE-bench: https://www.swebench.com/

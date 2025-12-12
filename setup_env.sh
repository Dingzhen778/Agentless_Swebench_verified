#!/bin/bash
# Agentless Environment Setup Script for Custom API Endpoint

# Set custom API configuration
export OPENAI_BASE_URL="https://console.scitix.ai/siflow/cetus/hisys/ylsun/eval-qwen2-5-72b-instruct/v1"
export OPENAI_API_KEY="dummy-key"  # Use any string since custom endpoint may not need real key
export AGENTLESS_MODEL="eval-qwen2-5-72b-instruct"

# Set Python path to include Agentless directory
export PYTHONPATH="${PYTHONPATH}:/volume/ai-infra/rhjiang/Agentless"

# Optional: Set project file location to use preprocessed data
# Download from: https://github.com/OpenAutoCoder/Agentless/releases/tag/v0.1.0
# export PROJECT_FILE_LOC=/path/to/swebench_lite_repo_structure

echo "Environment variables set:"
echo "  OPENAI_BASE_URL=$OPENAI_BASE_URL"
echo "  OPENAI_API_KEY=$OPENAI_API_KEY"
echo "  AGENTLESS_MODEL=$AGENTLESS_MODEL"
echo "  PYTHONPATH=$PYTHONPATH"
echo ""
echo "To use Agentless, activate the conda environment first:"
echo "  source /minconda3/etc/profile.d/conda.sh"
echo "  conda activate agentless"
echo "  source /volume/ai-infra/rhjiang/Agentless/setup_env.sh"

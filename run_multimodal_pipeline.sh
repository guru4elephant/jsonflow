#!/bin/bash
# 多模态SFT数据生成工具运行脚本

# 检查环境变量是否设置
if [ -z "$OPENAI_API_KEY" ]; then
    echo "错误: 未设置OPENAI_API_KEY环境变量"
    echo "请使用以下命令设置API密钥:"
    echo "export OPENAI_API_KEY=\"your-api-key\""
    exit 1
fi

# 检查images目录是否存在
if [ ! -d "images" ]; then
    echo "错误: images目录不存在"
    echo "请确保存在包含图片的images目录"
    exit 1
fi

# 默认参数
OUTPUT_FILE="multimodal_sft_data.jsonl"
MODEL="claude-3-7-sonnet-20250219"
BASE_URL="http://ai.wenyue8.com:15588/v1"

# 打印配置信息
echo "多模态SFT数据生成工具"
echo "================================================"
echo "图片目录: images"
echo "输出文件: $OUTPUT_FILE"
echo "使用模型: $MODEL"
echo "API端点: $BASE_URL"
echo "================================================"

# 运行生成脚本
python generate_multimodal_sft_data.py \
    --image-dir="images" \
    --output="$OUTPUT_FILE" \
    --model="$MODEL" \
    --base-url="$BASE_URL"

# 检查运行结果
if [ $? -eq 0 ]; then
    echo "================================================"
    echo "✅ 生成成功! 输出已保存到: $OUTPUT_FILE"
    echo "生成的示例数据:"
    head -n 5 "$OUTPUT_FILE"
    echo "================================================"
else
    echo "❌ 生成失败"
fi 
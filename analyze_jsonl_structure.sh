#!/bin/bash
#
# 分析目录中的所有JSONL文件结构的Shell脚本
#
# 使用方法:
#   ./analyze_jsonl_structure.sh [选项] 目录1 目录2 ...
#
# 选项:
#   -o, --output-dir DIR    指定输出目录，默认为 ./jsonl_analysis
#   -m, --method METHOD     指定分析方法 (basic 或 pipeline)，默认为 pipeline
#   -r, --recursive         是否递归子目录，默认开启
#   -h, --help              显示帮助信息

# 默认值
OUTPUT_DIR="./jsonl_analysis"
METHOD="pipeline"
RECURSIVE=true

# 解析命令行参数
PARAMS=""
while (( "$#" )); do
  case "$1" in
    -o|--output-dir)
      if [ -n "$2" ] && [ ${2:0:1} != "-" ]; then
        OUTPUT_DIR=$2
        shift 2
      else
        echo "错误: --output-dir 参数需要一个值" >&2
        exit 1
      fi
      ;;
    -m|--method)
      if [ -n "$2" ] && [ ${2:0:1} != "-" ]; then
        METHOD=$2
        if [ "$METHOD" != "basic" ] && [ "$METHOD" != "pipeline" ]; then
          echo "错误: method 必须是 'basic' 或 'pipeline'" >&2
          exit 1
        fi
        shift 2
      else
        echo "错误: --method 参数需要一个值" >&2
        exit 1
      fi
      ;;
    -r|--recursive)
      RECURSIVE=true
      shift
      ;;
    --no-recursive)
      RECURSIVE=false
      shift
      ;;
    -h|--help)
      echo "使用方法: $0 [选项] 目录1 目录2 ..."
      echo ""
      echo "选项:"
      echo "  -o, --output-dir DIR    指定输出目录，默认为 ./jsonl_analysis"
      echo "  -m, --method METHOD     指定分析方法 (basic 或 pipeline)，默认为 pipeline"
      echo "  -r, --recursive         是否递归子目录，默认开启"
      echo "  --no-recursive          不递归子目录"
      echo "  -h, --help              显示帮助信息"
      exit 0
      ;;
    --) # 参数结束标志
      shift
      break
      ;;
    -*|--*=) # 未知选项
      echo "错误: 未知选项 $1" >&2
      exit 1
      ;;
    *) # 保存剩余参数
      PARAMS="$PARAMS $1"
      shift
      ;;
  esac
done
# 恢复位置参数
eval set -- "$PARAMS"

# 检查是否提供了目录参数
if [ $# -eq 0 ]; then
  echo "错误: 请提供至少一个要分析的目录" >&2
  echo "使用 $0 --help 查看帮助" >&2
  exit 1
fi

# 创建输出目录
mkdir -p "$OUTPUT_DIR"
if [ ! -d "$OUTPUT_DIR" ]; then
  echo "错误: 无法创建输出目录 $OUTPUT_DIR" >&2
  exit 1
fi

# 获取当前时间作为分析会话标识
SESSION_ID=$(date +"%Y%m%d_%H%M%S")
SESSION_DIR="$OUTPUT_DIR/session_$SESSION_ID"
mkdir -p "$SESSION_DIR"

# 打印分析开始信息
echo "JSONL结构分析"
echo "=============="
echo "分析会话ID: $SESSION_ID"
echo "输出目录: $SESSION_DIR"
echo "分析方法: $METHOD"
echo "递归子目录: $RECURSIVE"
echo "=============="
echo ""

# 记录分析配置到会话目录
{
  echo "分析会话ID: $SESSION_ID"
  echo "开始时间: $(date)"
  echo "分析方法: $METHOD"
  echo "递归子目录: $RECURSIVE"
  echo "分析目录:"
  for dir in "$@"; do
    echo "  - $dir"
  done
  echo ""
} > "$SESSION_DIR/analysis_info.txt"

# 分析计数器
TOTAL_DIRS=0
TOTAL_FILES=0
PROCESSED_FILES=0
ERROR_FILES=0

# 处理每个目录
for dir in "$@"; do
  if [ ! -d "$dir" ]; then
    echo "警告: $dir 不是一个目录，已跳过" >&2
    continue
  fi
  
  TOTAL_DIRS=$((TOTAL_DIRS + 1))
  
  # 获取目录的绝对路径
  ABS_DIR=$(cd "$dir" && pwd)
  
  echo "处理目录: $ABS_DIR"
  
  # 查找JSONL文件
  if [ "$RECURSIVE" = true ]; then
    FIND_CMD="find \"$ABS_DIR\" -type f -name \"*.jsonl\""
  else
    FIND_CMD="find \"$ABS_DIR\" -maxdepth 1 -type f -name \"*.jsonl\""
  fi
  
  # 使用eval执行find命令，确保路径中的空格被正确处理
  eval $FIND_CMD > /tmp/jsonl_files_$$.txt
  while IFS= read -r file; do
    if [ -z "$file" ]; then
      continue
    fi
    
    TOTAL_FILES=$((TOTAL_FILES + 1))
    
    # 创建输出文件路径
    REL_PATH="${file#$ABS_DIR/}"
    OUTPUT_FILE="$SESSION_DIR/${REL_PATH//\//_}.analysis.txt"
    
    echo "  分析文件: $REL_PATH"
    
    # 创建输出文件所在目录
    mkdir -p "$(dirname "$OUTPUT_FILE")"
    
    # 运行分析命令
    {
      echo "文件: $file"
      echo "相对路径: $REL_PATH"
      echo "分析时间: $(date)"
      echo ""
      echo "分析结果:"
      echo "=========="
      python jsonflow_cli.py analyze --method "$METHOD" "$file" 2>&1
      if [ $? -eq 0 ]; then
        PROCESSED_FILES=$((PROCESSED_FILES + 1))
      else
        ERROR_FILES=$((ERROR_FILES + 1))
        echo ""
        echo "错误: 处理文件时出错"
      fi
    } > "$OUTPUT_FILE"
    
    echo "  结果保存到: $OUTPUT_FILE"
  done < /tmp/jsonl_files_$$.txt
  rm /tmp/jsonl_files_$$.txt
done

# 打印汇总信息
echo ""
echo "分析完成"
echo "========"
echo "处理的目录数: $TOTAL_DIRS"
echo "发现的JSONL文件数: $TOTAL_FILES"
echo "成功处理的文件数: $PROCESSED_FILES"
echo "处理失败的文件数: $ERROR_FILES"
echo "结果保存在: $SESSION_DIR"

# 将汇总信息添加到分析信息文件
{
  echo "分析汇总"
  echo "========"
  echo "结束时间: $(date)"
  echo "处理的目录数: $TOTAL_DIRS"
  echo "发现的JSONL文件数: $TOTAL_FILES"
  echo "成功处理的文件数: $PROCESSED_FILES"
  echo "处理失败的文件数: $ERROR_FILES"
} >> "$SESSION_DIR/analysis_info.txt"

# 创建汇总报告
SUMMARY_FILE="$SESSION_DIR/summary.txt"
{
  echo "JSONL结构分析汇总报告"
  echo "======================"
  echo "分析会话ID: $SESSION_ID"
  echo "开始时间: $(grep "开始时间:" "$SESSION_DIR/analysis_info.txt" | cut -d' ' -f2-)"
  echo "结束时间: $(grep "结束时间:" "$SESSION_DIR/analysis_info.txt" | cut -d' ' -f2-)"
  echo ""
  echo "分析统计"
  echo "=========="
  echo "处理的目录数: $TOTAL_DIRS"
  echo "发现的JSONL文件数: $TOTAL_FILES"
  echo "成功处理的文件数: $PROCESSED_FILES"
  echo "处理失败的文件数: $ERROR_FILES"
  echo ""
  echo "分析的文件"
  echo "=========="
  
  # 列出所有分析的文件
  for analysis_file in "$SESSION_DIR"/*.analysis.txt; do
    if [ -f "$analysis_file" ]; then
      FILE_PATH=$(grep "文件:" "$analysis_file" | cut -d' ' -f2-)
      REL_PATH=$(grep "相对路径:" "$analysis_file" | cut -d' ' -f2-)
      
      # 检查是否有错误
      if grep -q "错误:" "$analysis_file"; then
        STATUS="[失败]"
      else
        STATUS="[成功]"
      fi
      
      echo "$STATUS $REL_PATH"
    fi
  done
} > "$SUMMARY_FILE"

echo "汇总报告已保存到: $SUMMARY_FILE"

exit 0 
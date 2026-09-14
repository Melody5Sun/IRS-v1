#!/bin/bash
# Pre-commit 验证脚本
# 检查：1) 禁止 Co-Authored-By 行  2) 敏感文件未被提交

COMMIT_MSG_FILE="$1"

if [ -n "$COMMIT_MSG_FILE" ] && [ -f "$COMMIT_MSG_FILE" ]; then
  if grep -qi "Co-Authored-By" "$COMMIT_MSG_FILE"; then
    echo "错误: 提交信息不能包含 'Co-Authored-By' 行（学术项目要求，须以学生本人名义提交）"
    exit 1
  fi
fi

STAGED=$(git diff --cached --name-only)
for f in $STAGED; do
  case "$f" in
    .env|.env.local|*.key|*credentials*)
      echo "错误: 检测到敏感文件被提交: $f"
      echo "请从暂存区移除: git restore --staged \"$f\""
      exit 1
      ;;
  esac
done

exit 0

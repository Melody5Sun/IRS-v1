# Claude Code 工作流规则

本文档定义了 Claude 在 IRS 项目中的工作规范和自学规则。

## 提交规范

### ❌ 禁止事项
- **不添加 Co-Authored-By 行** — 所有提交必须以 Sun Wenjing 名义提交
  - Pre-commit 钩子会检查并拒绝包含 "Co-Authored-By" 的提交信息
  - 这是学术项目的要求，不能绕过

### ✓ 必须遵守
- **提交信息格式**: `[类型]: 描述 (关键词)`
  - 类型: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`
  - 例: `[feat]: 实现 NER 解析器 (NLP, ESCO)`
  - 例: `[fix]: 修复虚拟环境路径问题 (config)`

- **分支命名**:
  - Feature: `feature/user-auth-system`
  - Bugfix: `bugfix/env-loading-issue`
  - Docs: `docs/architecture-guide`
  - Never push to `main` directly — always use PR

## 代码风格与模式

### 禁用
- Python: 避免 `any` 类型，除非有明确的必要
- JS/TS: 避免过度工程化的抽象

### 优先
- 简洁方案胜过复杂方案
- 代码清晰胜过代码量少
- 复用现有工具库胜过重新实现

## 错误处理与自学规则

### 每次修复 bug 后的必做事项
1. 立即在 `.claude/lessons.md` 中记录新条目
2. 格式: `[日期] | 症状 | 规则 | 文件路径`
3. 例子:
   ```
   [2026-09-15] | ModuleNotFoundError | 检查虚拟环境激活（venv\Scripts\activate） | src/parser.py
   [2026-09-15] | 换行符问题 | Windows 上的 sed 需要 `-i.bak` 备份后缀，或使用 Python 替代 | build/convert.sh
   ```

### 知识查阅流程
- 开始新任务时，先查看 `.claude/lessons.md`
- 查找相关的规则提醒（用关键字搜索：文件名、错误类型、技术栈）
- 应用已知规则，避免重复踩坑

### 进度追踪
- 完成主要阶段后，更新 `.claude/primer.md`
- 记录: 当前进度、下一步优先项、新发现的限制
- 保持 < 100 行便于快速查阅

## 项目交付要求

**截止日期**: 2026-10-25

### 必须提交
- GitHub 仓库（包含 SystemCode/ 和 Report/ 目录）
- 项目报告 PDF
- 2 个演示视频（推广 + 系统演示）
- 成员属性文件

### GitHub 规范
- Branch protection on `main`
- All commits tracked with clear messages
- No direct pushes to main

## 快捷命令

```bash
# 查看 lessons 知识库
cat .claude/lessons.md

# 查看当前阶段
cat .claude/primer.md

# 检查 git 状态（提交前必做）
git status
git log --oneline -5
```

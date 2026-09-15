# IRS Project Primer

## ⏭️ 下一步
- [ ] 架构设计与技术栈确定（关键路径项）
- [ ] 第一批核心模块代码框架实现
- [ ] 更新 `launch.json`（待代码就位后填入真实启动命令）

## 📊 项目阶段
**当前**: 第 0 阶段 — 配置系统建立，等待代码实现
**截止日期**: 2026-10-25

## ✅ 已完成
- IRS-Project-Proposal-V1-CN.docx 最终版提案确定
- proposal-assets/ 目录整理（架构图、用户流程图、人设研究）
- `.claude/` 配置系统建立（本次任务）

## 📖 需要先读
- [CLAUDE.md](../CLAUDE.md) — 项目完整指南
- [lessons.md](lessons.md) — 团队学习规则

## ⚠️ 已知限制
- 项目尚无代码实现，`launch.json` 目前是占位模板
- Co-Authored-By 行禁用（学术项目要求，含协作者提交——一律以实际提交者自己的身份提交，不加共同作者标注）。强制机制是真正的 git `commit-msg` 钩子（`.claude/hooks/commit-msg`），**每台新克隆本仓库的机器都需手动运行一次** `git config core.hooksPath .claude/hooks`（本机已配置好）
- IRS-Project-Proposal-V1-CN.docx 是最终版本，其他草稿文件（.md）可忽略

## 🛠️ 快速启动
```bash
# 查看提交历史
git log --oneline -10

# 查阅规则提醒
cat .claude/lessons.md

# 检查 git 状态
git status
```

## 🗓️ 关键日期
- 2026-10-25 — 最终交付截止日期（代码、报告、视频、成员属性文件）

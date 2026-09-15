# IT CareerPilot — IRS Project

## 项目简介
- **名称**: IT CareerPilot — Intelligent Internship and Graduate Job Assistant for IT Students
- **课程**: NUS-ISS Intelligent Reasoning Systems (IRS) Practice Module
- **学生**: Sun Wenjing (A0326610N)
- **最终提案**: [IRS-Project-Proposal-V1-CN.docx](IRS-Project-Proposal-V1-CN.docx) — 其他草稿文件（.md/.pptx）仅供参考，可忽略

## 项目目标
面向 IT 学生的智能求职助手：简历解析 → JD 分析 → 智能匹配 → 可解释推荐 → 简历优化 → 面试准备 → 投递规划。

覆盖 IRS 四大技术方向：
1. **决策自动化**: 基于规则的资格筛选（签证、学历、经验约束）
2. **资源优化**: 遗传算法进行投递排期优化
3. **知识发现与挖掘**: 混合匹配（Sentence-BERT + 技能覆盖 + 经验契合度）
4. **认知技术**: NER 解析、知识图谱（ESCO + Neo4j）、LLM Agent、RAG

## 目录结构
```
IRS-v1/
├── IRS-Project-Proposal-V1-CN.docx   # 最终版提案
├── CLAUDE.md                          # 本文件
├── .claude/                           # Claude Code 配置系统
│   ├── CLAUDE.md                      # AI 工作流规则
│   ├── primer.md                      # 进度快照
│   ├── settings.json                  # 权限与钩子配置
│   ├── launch.json                    # 启动配置（占位，待代码实现）
│   ├── hooks/commit-msg               # 真正的 git commit-msg 钩子（需一次性激活，见下）
│   ├── templates/                     # 提交信息/PR/lesson 模板
│   └── lessons.md                     # 团队学习知识库
└── proposal-assets/                   # 架构图、用户流程图、人设研究
```

## 交付要求（截止 2026-10-25）
- [ ] GitHub 仓库（含 SystemCode/ 和 Report/ 目录，遵循 IRS-PM 模板）
- [ ] 项目报告 PDF
- [ ] 2 个演示视频（推广 + 系统演示，禁用 AI 配音）
- [ ] 成员属性文件

## 开发环境
> 代码实现尚未开始，此部分待架构确定后补充启动命令。
> 参见 [.claude/primer.md](.claude/primer.md) 获取当前进度。

## Claude Code 使用说明
- AI 工作流规则详见 [.claude/CLAUDE.md](.claude/CLAUDE.md)
- 开发进度追踪详见 [.claude/primer.md](.claude/primer.md)
- 踩坑记录详见 [.claude/lessons.md](.claude/lessons.md)
- **提交规范**: 禁止 Co-Authored-By 行——无论学生本人还是其他协作者提交，一律以实际提交者自己的身份提交，不加共同作者标注。详见 [.claude/CLAUDE.md](.claude/CLAUDE.md#提交规范)。首次克隆本仓库后需运行一次（`.git/hooks/` 不随仓库同步）：
  ```bash
  git config core.hooksPath .claude/hooks
  ```

# IRS Project Primer

> 最后更新: 2026-09-15

## ⏭️ 下一步
- [ ] 合并 [PR #3](https://github.com/Melody5Sun/IRS-v1/pull/3)（简历 PDF 解析 + schema/prompt 调整），合并前用真实 PDF 简历跑一次 `/parse-pdf` 检查输出质量
- [ ] 打通简历解析 → 推荐：`/recommendations` 目前吃的是旧的扁平 `ResumeProfile`，要改成接收 `ResumeDocument`（见已知限制）
- [ ] **用户偏好设置**模块：求职地点、期望职位等从简历 schema 移出的字段，改为用户手动填写
- [ ] JD 解析升级：目前是关键词词表匹配，按提案接入 Sentence-BERT 语义匹配 + ESCO 技能对齐
- [ ] 提案中尚未开始的部分：遗传算法投递排期、Neo4j 知识图谱、RAG 面试准备
- [ ] 更新 `launch.json`：现在仍是占位的 `node server.js`，后端实际启动命令是 `uvicorn app.main:app --reload`

## 📊 项目阶段
**当前**: 第 1 阶段 — 后端骨架已搭好，简历解析（LLM）可用，匹配还是基线版本
**截止日期**: 2026-10-25

## ✅ 已完成
- 提案定稿（IRS-Project-Proposal-V1-CN.docx）、proposal-assets/ 整理、`.claude/` 配置系统
- 后端 FastAPI 骨架（`SystemCode/backend/`）：health / resumes / jobs / recommendations 四组路由
- 简历解析：`POST /resumes/parse`（纯文本）+ `POST /resumes/parse-pdf`（pdfminer 提取文本），调用 Gemini（OpenAI 兼容接口）抽取成结构化 `ResumeDocument`，校验失败自动重试一次
- 简历 schema 定型（PR #3）：
  - 包含 name/email/phone、visa_status、about、experiences、projects、research、skills（`list[str]`）、educations、certificates、languages
  - `requires_sponsorship` 由程序根据 visa_status 推导，不让 LLM 填写
  - 已移出：location、desired_position（改到偏好设置）、skill level（不需要）
- `SYSTEM_PROMPT` 重写为英文：逐字段说明、禁止编造、强制英文输出，约 838 token
- 测试 `test_system_prompt_covers_every_schema_field`：schema 字段和 prompt 不同步时直接失败
- 推荐基线：技能关键词交集打分 + 硬约束（经验年限、签证担保）
- GitHub Actions CI 运行 backend pytest（PR #2）；当前共 9 个测试
- `settings.json` 的 deny 规则禁止 Claude 读取 `.env`、打印环境变量

## 📖 需要先读
- [CLAUDE.md](../CLAUDE.md) — 项目完整指南
- [lessons.md](lessons.md) — 踩坑记录（**本机 Python 环境搭建方法在这里**）

## ⚠️ 已知限制
- **解析结果和推荐接口的数据模型对不上**：`scorer.py` / `RecommendationRequest` 仍使用 `ResumeProfile`（skills/education 为字符串列表，另有 experience_years、work_authorization），和 `ResumeDocument` 不兼容，需要做转换或统一
- JD 技能抽取依赖 `skill_lexicon.py` 固定词表，词表外的技能识别不到
- 前端只有一个静态 demo（`SystemCode/frontend/IT CareerPilot-frontend demo.html`），还没接后端 API
- 仓库里没有样例简历，prompt 效果只能靠各自本地的真实简历人工验证
- 本机没有系统 Python，要用 uv 建 `SystemCode/backend/.venv`（步骤见 lessons.md）；`.venv`、`.uv-python` 已被 gitignore 忽略
- 各自机器要在 `SystemCode/backend/.env` 里填入真实的 Gemini `LLM_API_KEY` 才能调用 LLM（模板见 `.env.example`）
- 禁止 Co-Authored-By 行，PR 描述里也不加 "Generated with Claude Code"。由 `.claude/hooks/commit-msg` 钩子强制检查，新克隆的仓库需要运行一次 `git config core.hooksPath .claude/hooks`
- 禁止直接 push 到 main，一律开分支提 PR

## 🛠️ 快速启动
```bash
cd SystemCode/backend
.venv/Scripts/python.exe -m pytest tests/ -q          # 跑测试
.venv/Scripts/python.exe -m uvicorn app.main:app --reload   # 启动后端，文档在 /docs
```

## 🗓️ 关键日期
- 2026-10-25 — 最终交付截止日期（代码、报告、视频、成员属性文件）

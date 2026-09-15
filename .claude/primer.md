# IRS Project Primer

> 最后更新: 2026-09-15

## ⏭️ 下一步
- [ ] 用真实 PDF 简历走一遍 `/parse-pdf` → `GET/PUT /profile` → `/recommendations`，检查解析质量和推荐理由
- [ ] 画像持久化到数据库（目前存在内存里）
- [ ] 求职约束（目标岗位/行业/工作模式）参与推荐：JD schema 还没有这几个字段
- [ ] JD 解析升级：目前是关键词词表匹配，按提案接入 Sentence-BERT 语义匹配 + ESCO 技能对齐
- [ ] 提案中尚未开始的部分：遗传算法投递排期、Neo4j 知识图谱、RAG 面试准备

## 📊 项目阶段
**当前**: 第 1 阶段 — 后端骨架已搭好，简历解析（LLM）可用，匹配还是基线版本
**截止日期**: 2026-10-25

## ✅ 已完成
- 提案定稿（IRS-Project-Proposal-V1-CN.docx）、proposal-assets/ 整理、`.claude/` 配置系统
- 后端 FastAPI 骨架（`SystemCode/backend/`）：health / resumes / jobs / recommendations 四组路由
- 简历解析：只保留 `POST /resumes/parse-pdf`（pdfminer 提取文本，纯文本的 `/parse` 已删除），调用 Gemini（OpenAI 兼容接口）抽取成结构化 `ResumeDocument`，校验失败自动重试一次
- 简历 schema：
  - 包含 name/email/phone、about、experiences、projects、research、skills（`list[str]`）、educations、certificates、languages（`list[str]`）
  - 已移出：location、desired_position（改到求职约束）、skill level、language level、visa_status/requires_sponsorship（签证相关全部删除，岗位侧 `visa_sponsorship` 和签证硬约束也一并删除）
- 用户画像 + 求职约束（本地部署，单用户）：`parse-pdf` 解析后自动存入画像 → `GET /profile` 读取 → 用户修改画像、填写求职约束（target_roles / target_industries / work_modes: onsite|hybrid|remote / notes，均可多选）→ `PUT /profile` 整体保存；重新上传简历只替换画像，保留约束
- `SYSTEM_PROMPT` 重写为英文：逐字段说明、禁止编造、强制英文输出，约 838 token
- 测试 `test_system_prompt_covers_every_schema_field`：schema 字段和 prompt 不同步时直接失败
- 推荐基线：技能关键词交集打分 + 硬约束（经验年限）
- 简历解析 → 推荐已打通：`/recommendations` 的 `candidate` 直接接收 `ResumeDocument`。技能用 JD 同一套词表归一化；经验年限按 experiences 日期的月份并集计算，重叠不重复算
- GitHub Actions CI 运行 backend pytest（PR #2，只对目标为 main 的 PR 和 push 触发）；当前共 11 个测试
- `launch.json` 配置好后端启动（PR #5，已合并）；`config.py` 固定读取 `SystemCode/backend/.env`，从任何目录启动都能读到
- `settings.json` 的 deny 规则禁止 Claude 读取 `.env`、打印环境变量

## 📖 需要先读
- [CLAUDE.md](../CLAUDE.md) — 项目完整指南
- [lessons.md](lessons.md) — 踩坑记录（**本机 Python 环境搭建方法在这里**）

## ⚠️ 已知限制
- JD 和候选人的技能匹配都依赖 `skill_lexicon.py` 固定词表，词表外的技能识别不到（也不会出现在 matched/missing 里）；"React.js"、"ReactJS" 这类写法匹配不到 react
- 画像只存在进程内存里，后端重启后需要重新上传简历或 PUT；求职约束暂时不参与推荐
- 提案「决策自动化」里提到的签证约束已按需求删除，目前硬约束只剩经验年限
- 经验年限：只写了年份的日期按整年算，同一年起止的短经历会被高估；学历要求（`degree_required`）还没参与硬约束
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
- 也可以用 `.claude/launch.json` 里的 `backend` 配置启动（端口 8000，要先关掉占用该端口的进程）。路径 `.venv/Scripts/python.exe` 只适用于 Windows，macOS/Linux 改成 `.venv/bin/python`

## 🗓️ 关键日期
- 2026-10-25 — 最终交付截止日期（代码、报告、视频、成员属性文件）

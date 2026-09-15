# Lessons Learned

团队知识库 — 记录开发过程中踩过的坑和应遵守的规则。

**格式**: `[日期] | 症状/错误 | 规则/解决方案 | 涉及文件`

---

<!-- 新条目追加在此行下方，最新的在最上面 -->

[2026-09-15] | 简历解析接 Gemini 时把真实 API Key 误粘贴进了 `.env.example`（该文件不在 `.gitignore` 里，是要提交的模板） | 真实密钥只能放进 `.env`（已被 `.gitignore` 排除）；`.env.example` 永远只放占位注释，不放真实值；一旦真实密钥出现在了会被提交或会进入对话记录的地方，就当作已泄露处理——去申请方（如 Google AI Studio）重新生成一个 | .env.example, SystemCode/backend/.env
[2026-09-15] | 用 `gemini-2.5-flash` 调 Gemini 的 OpenAI 兼容接口报 404 "no longer available to new users" | Gemini 免费模型名会随时间下线/更替，接入时以报错信息里 Google 给出的替代模型名为准（当前是 `gemini-3.6-flash`），不要死记某个具体型号名 | SystemCode/backend/.env, .env.example
[2026-09-15] | 本机没有系统级 Python（`python`/`py` 只是 Windows Store 空壳，运行即 exit 49 无输出） | 用 `uv`（已装在 `~/.local/bin`）自建环境：`uv python install 3.12` 下载解释器 + `uv venv --python 3.12 .venv` + `uv pip install --python .venv -r requirements.txt`，不用等系统装 Python | SystemCode/backend
[2026-09-15] | `uv python install` 报错 `failed to rename file ... 系统无法将文件移到不同的磁盘驱动器` | 本机 `%APPDATA%\Roaming` 被重定向到了跟当前目录不同的物理盘符，uv 下载后"移动安装"这一步跨盘失败；设置 `UV_PYTHON_INSTALL_DIR` 指向当前项目所在盘符下的一个目录（比如项目内的 `.uv-python/`）即可绕过 | SystemCode/backend

[2026-09-15] | commit-msg 钩子用 `grep -qi "Co-Authored-By"` 做纯子串匹配，导致提交信息里只要*描述*这个功能（比如 "block Co-Authored-By trailer"）也会被误拦 | 只应匹配真正的尾注行，用 `grep -qiE "^Co-Authored-By:"`（限定行首+冒号），不要用宽松的子串匹配去检查提交信息里"提到某个词"和"真的包含该格式的行"这两件不同的事 | .claude/hooks/commit-msg
[2026-09-15] | settings.json 里写了 `"hooks": {"PreCommit": [...]}`，看起来配置正确但从未生效 | "PreCommit" 不是 Claude Code 合法的 hook 事件名（合法列表：PreToolUse/PostToolUse/Stop 等，没有 PreCommit）；真正要拦截 git commit（含手动终端提交）必须用真实 git 钩子——把脚本命名为 `commit-msg`（接收 `$1` 消息文件路径），放进 `.claude/hooks/`，并让每个克隆者运行一次 `git config core.hooksPath .claude/hooks` | .claude/settings.json, .claude/hooks/commit-msg
[2026-09-15] | 项目有多个草稿提案文件（.md/.pptx）容易混淆 | IRS-Project-Proposal-V1-CN.docx 是唯一最终版，其他文件仅供参考可忽略 | 根目录

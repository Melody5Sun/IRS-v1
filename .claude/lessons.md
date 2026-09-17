# Lessons Learned

团队知识库 — 记录开发过程中踩过的坑和应遵守的规则。

**格式**: `[日期] | 症状/错误 | 规则/解决方案 | 涉及文件`

---

<!-- 新条目追加在此行下方，最新的在最上面 -->

[2026-09-17] | 简历上传一直报 `LLM 未配置`，用户确认已经配置了 `LLM_API_KEY` 等变量，但报错不变 | `.env` 被放在了仓库根目录，而 `config.py` 里 `BACKEND_ROOT = Path(__file__).resolve().parents[2]` 固定只读 `SystemCode/backend/.env`，不认系统环境变量也不认根目录的 `.env`；用 `mv` 把文件挪到 `SystemCode/backend/.env`（不读取/打印文件内容）即可，不用改代码 | SystemCode/backend/.env, SystemCode/backend/app/core/config.py
[2026-09-17] | `gh pr merge <N> --auto --merge` 在仓库关闭了 `allow_auto_merge` 设置时不报错也不等待，如果此刻已满足合并条件就直接静默合并；随后 `gh pr merge` 命令切换本地工作目录回 base 分支，但没有 pull，导致本地文件短暂显示成合并前的旧内容（容易误判为改动丢失） | 判断 PR 是否已合并用 `gh pr view <N> --json state,mergedAt`，不要看 `--auto` 命令有没有报错；合并后如果本地分支被切回 base，先 `git pull` 同步再继续操作 | GitHub PR 流程
[2026-09-17] | Windows 新克隆仓库执行 `commit-msg` 钩子时报 `grep: command not found`，提交检查被跳过 | 钩子的核心校验应使用 POSIX shell 内建的 `while` 和 `case`，避免依赖目标机器未必提供的 `grep` | .claude/hooks/commit-msg
[2026-09-17] | 扩充技能同义词后，普通的 `API`/`APIs` 被识别成独立的 `api development` 技能，改变了既有推荐结果 | 技能别名应采用能明确代表能力的短语，避免把通用技术名词直接提升为额外技能；用完整回归测试检查 matched/missing 列表 | SystemCode/backend/app/parsers/skill_lexicon.py
[2026-09-17] | MIND 概念数据中同一个别名可能对应多个概念，若按唯一索引加载会阻断应用启动 | 概念别名索引必须保留全部候选；精确名称优先，歧义别名由调用方消歧 | SystemCode/backend/app/knowledge/mind_ontology.py
[2026-09-17] | 旧工作区和远端同时修改配置、技能解析与测试，直接拉取会产生冲突并可能静默删除经验年限字段 | 从最新远端创建独立集成分支，逐项迁移模块并保留远端 schema 契约，再运行完整测试 | SystemCode/backend
[2026-09-15] | 叠放 PR（#4 的目标分支是 #3 的分支）场景下，用 `gh pr merge 3 --merge --delete-branch` 合并 #3 后，#4 没有自动改为合并到 main，而是随目标分支被删而自动关闭，并且无法直接改目标分支 | 合并叠放 PR 的底层 PR 时，**先** `gh pr edit <上层PR> --base main`，**再**合并并删除底层分支。如果已经被关闭：把被删分支按原 commit 推回（`git push origin <sha>:refs/heads/<分支>`）→ `gh pr reopen` → `gh pr edit --base main` → 再删分支。另外，只改目标分支不会触发 `pull_request` CI，需要再推一个提交 | GitHub PR 流程

[2026-09-15] | JD 写 "Build APIs with Python, FastAPI and SQL." 时 sql 没被识别成必需技能；老测试用的就是这句话，但没断言 sql，所以一直没发现 | 技能词边界正则的后向断言不能直接排除 "."，否则位于句末的技能全部漏掉；只在 "." 后面还跟着字母数字时才算词的一部分（`(?![\w+#-]|\.\w)`）。写测试时要对抽取结果做完整断言（matched 和 missing 都要查），不能只看排序 | SystemCode/backend/app/parsers/text_parser.py

[2026-09-15] | 简历解析接 Gemini 时把真实 API Key 误粘贴进了 `.env.example`（该文件不在 `.gitignore` 里，是要提交的模板） | 真实密钥只能放进 `.env`（已被 `.gitignore` 排除）；`.env.example` 永远只放占位注释，不放真实值；一旦真实密钥出现在了会被提交或会进入对话记录的地方，就当作已泄露处理——去申请方（如 Google AI Studio）重新生成一个 | .env.example, SystemCode/backend/.env
[2026-09-15] | 用 `gemini-2.5-flash` 调 Gemini 的 OpenAI 兼容接口报 404 "no longer available to new users" | Gemini 免费模型名会随时间下线/更替，接入时以报错信息里 Google 给出的替代模型名为准（当前是 `gemini-3.6-flash`），不要死记某个具体型号名 | SystemCode/backend/.env, .env.example
[2026-09-15] | 本机没有系统级 Python（`python`/`py` 只是 Windows Store 空壳，运行即 exit 49 无输出） | 用 `uv`（已装在 `~/.local/bin`）自建环境：`uv python install 3.12` 下载解释器 + `uv venv --python 3.12 .venv` + `uv pip install --python .venv -r requirements.txt`，不用等系统装 Python | SystemCode/backend
[2026-09-15] | `uv python install` 报错 `failed to rename file ... 系统无法将文件移到不同的磁盘驱动器` | 本机 `%APPDATA%\Roaming` 被重定向到了跟当前目录不同的物理盘符，uv 下载后"移动安装"这一步跨盘失败；设置 `UV_PYTHON_INSTALL_DIR` 指向当前项目所在盘符下的一个目录（比如项目内的 `.uv-python/`）即可绕过 | SystemCode/backend

[2026-09-15] | commit-msg 钩子用 `grep -qi "Co-Authored-By"` 做纯子串匹配，导致提交信息里只要*描述*这个功能（比如 "block Co-Authored-By trailer"）也会被误拦 | 只应匹配真正的尾注行，用 `grep -qiE "^Co-Authored-By:"`（限定行首+冒号），不要用宽松的子串匹配去检查提交信息里"提到某个词"和"真的包含该格式的行"这两件不同的事 | .claude/hooks/commit-msg
[2026-09-15] | settings.json 里写了 `"hooks": {"PreCommit": [...]}`，看起来配置正确但从未生效 | "PreCommit" 不是 Claude Code 合法的 hook 事件名（合法列表：PreToolUse/PostToolUse/Stop 等，没有 PreCommit）；真正要拦截 git commit（含手动终端提交）必须用真实 git 钩子——把脚本命名为 `commit-msg`（接收 `$1` 消息文件路径），放进 `.claude/hooks/`，并让每个克隆者运行一次 `git config core.hooksPath .claude/hooks` | .claude/settings.json, .claude/hooks/commit-msg
[2026-09-15] | 项目有多个草稿提案文件（.md/.pptx）容易混淆 | IRS-Project-Proposal-V1-CN.docx 是唯一最终版，其他文件仅供参考可忽略 | 根目录

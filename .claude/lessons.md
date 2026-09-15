# Lessons Learned

团队知识库 — 记录开发过程中踩过的坑和应遵守的规则。

**格式**: `[日期] | 症状/错误 | 规则/解决方案 | 涉及文件`

---

<!-- 新条目追加在此行下方，最新的在最上面 -->

[2026-09-15] | commit-msg 钩子用 `grep -qi "Co-Authored-By"` 做纯子串匹配，导致提交信息里只要*描述*这个功能（比如 "block Co-Authored-By trailer"）也会被误拦 | 只应匹配真正的尾注行，用 `grep -qiE "^Co-Authored-By:"`（限定行首+冒号），不要用宽松的子串匹配去检查提交信息里"提到某个词"和"真的包含该格式的行"这两件不同的事 | .claude/hooks/commit-msg
[2026-09-15] | settings.json 里写了 `"hooks": {"PreCommit": [...]}`，看起来配置正确但从未生效 | "PreCommit" 不是 Claude Code 合法的 hook 事件名（合法列表：PreToolUse/PostToolUse/Stop 等，没有 PreCommit）；真正要拦截 git commit（含手动终端提交）必须用真实 git 钩子——把脚本命名为 `commit-msg`（接收 `$1` 消息文件路径），放进 `.claude/hooks/`，并让每个克隆者运行一次 `git config core.hooksPath .claude/hooks` | .claude/settings.json, .claude/hooks/commit-msg
[2026-09-15] | 项目有多个草稿提案文件（.md/.pptx）容易混淆 | IRS-Project-Proposal-V1-CN.docx 是唯一最终版，其他文件仅供参考可忽略 | 根目录

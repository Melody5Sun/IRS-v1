# MIND Tech Skills Ontology 数据快照

本目录保存 IT CareerPilot 使用的 MIND Tech Skills Ontology 固定快照。

- 上游仓库：https://github.com/MIND-TechAI/MIND-tech-ontology
- 上游提交：`2367527d1a2f5665f595d6e0518294cc69dfb0fe`
- 获取日期：2026-09-17
- 许可：MIT，全文见 `LICENSE-MIND`
- `skills.json`：3,333 个技能节点
- `concepts.json`：974 个概念节点

应用启动时通过 `app.knowledge.mind_ontology.get_mind_knowledge_graph()` 加载该快照。
本阶段仅加载和查询图谱数据，不将其接入简历/JD 技能提取或推荐评分。

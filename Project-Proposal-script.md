# IT CareerPilot: Intelligent Internship and Graduate Job Assistant for IT Students
## NUS-ISS Intelligent Reasoning Systems (IRS) Practice Module — Project Proposal

> 本文在小组 `Proposal_Framework_IT_Career_Assistant.md` 的 14 节框架基础上补全，主要新增：**§8 四大技术组映射与设计取舍**、**§10 量化实验设计**、**§9/§11 带日期的排期与交付清单**，并对三处原设计做了调整（见 §0 变更说明）。

---

## 0. 相对小组框架的变更说明（评审时可跳过，供组内对齐）

| # | 原框架 | 调整后 | 理由 |
|---|---|---|---|
| C1 | 只覆盖决策自动化 / 知识发现 / 认知技术 3 类 | 新增 **投递计划优化器（GA）**，覆盖 4/4 类 | 硬性要求是 ≥3 类，做到 4 类更稳；且"精力预算下投哪些岗"本身是真实痛点，不是硬凑 |
| C2 | 匹配 = 关键词 + 整体语义相似度 | 改为**结构化抽取后分维度加权打分**，整篇余弦降为实验基线 | JD 里公司介绍/福利占比大，整篇编码会稀释技能信号；分维度才可解释、可调权重、可做消融 |
| C3 | 技能知识库 = 人工整理 taxonomy | 改为 **ESCO 开放本体导入 Neo4j + KG embedding 补边** | 人工 taxonomy 维护成本高且规模小；ESCO 有 13,000+ 技能且开放，KG embedding（MR Day3 PyKEEN）能自动补充缺失关系 |
| C4 | Evaluation 以定性描述为主 | 改为 **7 组带基线、带指标、带消融的量化实验** | 评分表第 4 项「Experiments（quantitative evaluation）」是独立打分项，定性描述拿不到分 |

---

## 1. Project Title

**IT CareerPilot: Intelligent Internship and Graduate Job Assistant for IT Students**

本项目面向正在申请 IT 行业实习与校招岗位的学生，提供岗位推荐、JD 分析、技能差距解释、针对性简历优化与投递计划规划。

| 封面项 | 内容 |
|---|---|
| Project Title | IT CareerPilot |
| Group Number | (Canvas 注册组号，待填) |
| Group Members | (全名 + NUS Student ID / Masked ID，待填) |
| GitHub Repository | https://github.com/Melody5Sun/IRS-v1 |
| Date of Presentation | (待填) |

---

## 2. Introduction

### Project Overview

IT CareerPilot 是一个面向学生群体的**可解释**智能求职助手。系统根据学生的专业背景、技术栈、项目经历、实习经历和岗位意向，推荐匹配的 IT 校招或实习岗位，解释匹配原因与技能差距，并根据具体岗位 JD 帮助学生优化简历内容、准备面试材料、规划投递优先级。

与市面上"LLM 套壳"型工具的根本区别：**推理逻辑显式化**。硬性条件由规则引擎裁决，排序由可分解的加权模型给出，技能关系由知识图谱推理，精力分配由优化算法求解，LLM 只负责它真正擅长的语言生成，且被结构化约束与事实校验限制。

### Project Goals（可验收）

| # | 目标 | 验收标准 |
|---|---|---|
| G1 | 推荐更准 | Top-10 推荐的 Precision@10 相对"整篇 SBERT 余弦"基线提升 ≥ 15% |
| G2 | 推荐可解释 | ≥ 90% 推荐附带**结构化**解释（命中规则 / 已匹配技能 / 缺口技能 / 分数分解），而非 LLM 自由发挥的一段话 |
| G3 | 改写不编造 | 简历改写幻觉率 < 5%（人工抽检 100 条 bullet，判定是否引入原简历不存在的经历/技能/数字） |
| G4 | 技术覆盖 | 实打实覆盖 IRS 四大技术组中的 **全部 4 组**（硬性要求 ≥ 3 组） |

---

## 3. Project Background / Market Context

### Problem Background

IT 行业岗位类型多、技能要求变化快，Software Engineer、Data Analyst、AI/ML Engineer、Frontend / Backend Developer、DevOps Engineer、Cybersecurity Analyst 之间的要求差异明显。

学生求职的常见痛点：

- **信息分散**：岗位散落在 MyCareersFuture、InternSG、各公司官网 career page、LinkedIn、Telegram 群，同一岗位在不同渠道字段格式完全不同，筛选成本高。
- **匹配不透明**：JD 中技术关键词密集，学生难以判断自己是否真正匹配；平台按黑箱模型排序，不告诉你"为什么不匹配"，也就无从改进。
- **简历不针对**：多数学生用同一份通用简历投所有岗位，项目经历表达不贴近岗位要求。
- **缺少技能差距反馈**：不知道下一步该补什么，也分不清"可迁移的差距"和"硬差距"。
- **精力错配**：一份高质量定向简历需 1–2 小时。学生通常海投 100 份低质量简历，而不是精修 15 份高命中率的——这本质上是**预算约束下的组合优化问题**，但没有工具把它当优化问题解。

### Target Users

本科生、硕士生、应届毕业生；正在申请 IT 实习 / 校招 / graduate program 的学生；希望按目标岗位优化简历的求职者。

### Usage Scenario

1. 学生上传简历并输入岗位意向、地点偏好、可投入的每周时间预算。
2. 系统解析简历 → 构建学生画像（技能、教育、项目、偏好、签证状态）。
3. 系统采集并解析 JD → 规则初筛 → 混合打分排序 → 输出带解释的推荐列表。
4. 学生勾选意向岗位。
5. 系统输出：匹配解释与技能差距 → JD 定向简历改写 → 面试资料包 → **在时间预算下的投递优先级与排程**。
6. 学生确认后自行提交申请（系统不代投，见 §5）。

---

## 4. Literature Review / Market Research

### Market Research

| 类型 | 代表 | 做了什么 | 缺什么 |
|---|---|---|---|
| 招聘平台 | LinkedIn / Indeed / Glassdoor / Handshake / MyCareersFuture / InternSG / 学校 career portal | 岗位聚合、搜索、关键词或协同过滤推荐 | 推荐不针对学生项目经历；不解释；不改简历；不做技能缺口诊断 |
| AI 简历工具 | Teal / Rezi / Jobscan | JD 关键词覆盖率打分、简历改写 | 纯文本匹配，无技能知识结构；无岗位发现；幻觉无约束 |
| LLM Agent 类 | 各类 "AI job agent" | 端到端自动化 | 黑箱不可解释；无硬约束保证；易违反平台 ToS |

**机会点**：岗位推荐、JD 理解、简历优化、投递规划在现有产品里是**割裂**的，且都缺可解释性。IT CareerPilot 做的是把这四步串成一条**可审计的闭环**。

### Related Techniques（提案阶段方向，最终报告展开）

- **岗位-简历匹配**：双塔/DSSM 是工业界主流（RS Day3），小数据下 Sentence-BERT + 余弦已是强基线。已知问题是长 JD 噪声稀释技能信号 → 本项目改用先抽取后分维匹配。
- **技能本体与缺口推理**：ESCO（欧盟技能/胜任力/职业分类，13,000+ 技能，开放下载）、O\*NET。KG 多跳推理可区分"PyTorch → TensorFlow 同属 DL 框架，属**可迁移缺口**"与"完全没接触过 Kubernetes，属**硬缺口**"，纯 embedding 给不出这个区分。KG embedding（TransE / RotatE / ComplEx）+ link prediction 用于补全技能关系（MR Day3）。
- **规则 + ML 混合架构**：RS Day1 核心论点——ML 负责排序，业务规则负责准入与合规（Databricks fraud 框架、ED triage workshop 同一模式）。
- **RAG 与事实一致性**：CGS Day1 AM / RS Day5。简历改写建模为 **grounded rewriting**：所有改写 bullet 必须可回溯到原简历某个 span，并过一道显式一致性校验，而不是相信 LLM 自觉。
- **可解释推荐**：解释 = 命中规则 + 匹配技能证据 + 分数分解，而非事后生成的说辞。
- **组合优化**：RS Day4 遗传算法；预算约束下的选择与排程（背包/调度变体）。

**待补文献（最终报告）**：Bian et al. *Learning to Match Jobs with Resumes*；Yao et al. *ReAct* (2023)；Hu et al. *Implicit ALS* (2008)；Le & Mikolov *Doc2Vec*；ESCO / O\*NET 技术文档。

---

## 5. Project Scope

### In Scope

**岗位方向（7 条）**：Software Engineering / Backend / Frontend / Data Analytics & Data Science / AI & Machine Learning / Cloud & DevOps / Cybersecurity。

**核心模块**：

- Resume Parser — 解析教育背景、技能、项目经历、实习经历
- Student Profile Builder — 构建求职画像（含偏好与时间预算）
- Job Description Analyzer — 抽取职责、硬技能、软技能、经验与学历要求
- IT Skill Knowledge Graph — 技能与岗位方向之间的关系（ESCO 导入 + KG embedding 补边）
- Rule-based Eligibility Filter — 硬性条件准入裁决
- Hybrid Matching & Ranking Engine — 分维度加权匹配与排序
- Explanation Module — 结构化推荐理由与技能差距
- Resume Optimization Module — JD 定向 bullet 改写 + 事实一致性校验
- Interview Prep Retriever — RAG 检索题库与面经
- **Application Plan Optimizer — GA 在时间预算下规划投递组合与顺序**（新增）
- Agent Orchestrator — LLM function calling / ReAct 多步编排
- User Interface — 推荐列表、匹配分数、技能差距、改写建议、投递计划

### Out of Scope / Limitations

| 不做 | 原因 |
|---|---|
| **自动代替学生投递** | 绝大多数招聘网站 ToS 明令禁止自动化提交；不可逆操作必须人在回路。**替代方案**：系统生成"投递包"（定向简历 PDF + cover letter 草稿 + 岗位链接 + 面试提纲），一键打开申请页由学生点击提交——产品价值不减，且这一取舍本身是 RS Day1 责任 AI 的教学点，写进报告是加分 |
| 保证 offer 或面试结果 | 系统提供决策支持，不承诺结果 |
| 虚构学生经历 | 只做表达优化，不新增事实（G3 量化约束） |
| 非 IT 行业、社招 / 高管岗 | 技能本体差异大，10 man-day 预算内做不深 |
| 中文简历与 JD | 首版仅英文，列入 Future Work |
| 真实投递反馈闭环学习 | 冷启动无标签，见 §9 弱标签方案 |

**Constraints**：每人约 10 man-days；无真实投递反馈标签；LLM API 成本；简历含 PII 须本地脱敏；岗位数据受平台权限与质量限制。

---

## 6. Data Collection and Preparation

### Data Sources

| 数据 | 来源 | 规模目标 | 用途 |
|---|---|---|---|
| 岗位 JD | MyCareersFuture 公开 API（data.gov.sg）+ Kaggle 公开 job posting 数据集 | 5,000–20,000 条，IT 类筛后 ~3,000 | 主数据源 |
| 公司官网校招页 | ≤ 20 家目标公司 career page | ~200 条 | 演示多源接入；遵守 robots.txt，限速 1 req/s |
| 技能本体 | ESCO v1.2（开放）+ O\*NET | ~2,000 IT 相关技能节点 | 知识图谱 |
| 学生简历 | 组员脱敏简历 + Kaggle Resume Dataset | 50–100 份 | 测试与标注 |
| 面试资料 | 公开题库元数据 + 公开面经语料 | ~1,000 条 | RAG 向量库 |

**不把项目成败押在爬虫上**——主数据源是公开 API 与开放数据集，爬虫仅作多源整合能力的演示。

### Data Processing

**统一结构化 schema（简历与 JD 共用）**：
```
{education, degree_level, years_of_experience, skills[], projects[],
 location, visa_requirement, seniority, employment_type, languages[]}
```

- **JD 清洗**：MinHash 去重（title + company + 正文）、语言过滤、正文分段（职责 / 要求 / 福利 / EEO），**丢弃福利与 EEO 段**——这是分维度匹配能跑赢整篇余弦的关键一步。
- **技能抽取**：spaCy NER + ESCO 词典匹配作为主路径（高精度、可解释），LLM few-shot 抽取兜底长尾表述（"熟悉云原生技术栈" → Docker / Kubernetes / CI-CD）。两路取并集，人工抽样测 F1（实验 E1）。
- **知识图谱构建**：清洗为 Neo4j 三元组 `(Skill)-[:IS_A]->(SkillGroup)`、`(Skill)-[:SIMILAR_TO]->(Skill)`、`(Role)-[:REQUIRES]->(Skill)`；用 PyKEEN 训练 KG embedding，link prediction 补全缺失关系。
- **简历处理**：PII 脱敏（姓名 / 电话 / 邮箱替换为占位符）后再入库或调用任何外部 API。

### Data Challenges

| 挑战 | 应对 |
|---|---|
| JD 格式不统一，经验要求表述极乱（"3+ years" / "至少三年" / "fresh grads welcome"） | 正则 + 规则归一到整数区间 |
| 同一技能多种写法（JavaScript / JS，Machine Learning / ML） | ESCO 别名表 + 人工补充别名词典 |
| ~30% JD 无明确学历要求 | **缺失即视为"不约束"**，而非默认淘汰 |
| 简历内容不完整 | 缺失维度降权而非置零；在解释中提示"该维度信息不足" |
| ESCO 术语与真实 JD 用词不对齐 | KG embedding link prediction 补边 |
| LLM 改写 hallucination | 结构化约束 + 事实校验器 + 量化（E5） |

---

## 7. System Design

### Proposed Architecture

```text
        Student Resume + Career Preference + Weekly Time Budget
                              |
                              v
        ┌────────────────────────────────────────────────┐
        │  Agent Orchestrator (LLM function calling / ReAct) │  ← ④
        │        Plan → Act → Observe → Reflect            │
        └──────────────────────┬─────────────────────────┘
                               │ calls tools below
   ┌───────────────────────────┼──────────────────────────────┐
   v                           v                              v
┌────────────────┐   ┌──────────────────────┐    ┌────────────────────────┐
│ Job Ingestion  │   │ Resume Parser /       │    │ IT Skill Knowledge     │
│ API + crawler  │──▶│ JD Analyzer (④)       │───▶│ Graph  Neo4j + ESCO    │ ← ④
│                │   │ spaCy NER + ESCO      │    │ + KG embedding         │
└────────────────┘   │ + LLM fallback        │    └───────────┬────────────┘
                     └──────────┬───────────┘                 │
                                v                             │
                     ┌──────────────────────┐                 │
                     │ Rule-based Filter    │ ← ①             │
                     │ visa / degree /      │                 │
                     │ experience / location│                 │
                     └──────────┬───────────┘                 │
                       PASS / DEMOTE / REJECT + fired rules    │
                                v                             │
                     ┌────────────────────────────────────────┴───┐
                     │ Hybrid Matching & Ranking  (③)             │
                     │  S = w1·semantic(SBERT)                    │
                     │    + w2·skill coverage (KG-aware)          │
                     │    + w3·experience fit                     │
                     │    - w4·hard-gap penalty                   │
                     │  权重由实验 E3 标定，非拍脑袋               │
                     └──────────┬─────────────────────────────────┘
                                v
                  Job Ranking + Match Explanation + Skill Gap
                                v
                     ┌──────────────────────┐
                     │ User confirms targets │ ← human-in-the-loop
                     └──────────┬───────────┘
          ┌──────────────┬──────┴───────┬──────────────────┐
          v              v              v                  v
 ┌────────────────┐ ┌──────────┐ ┌──────────────┐ ┌────────────────┐
 │ Resume Rewrite │ │Interview │ │ Application  │ │ Explanation &  │
 │ template+LLM+  │ │ Prep RAG │ │ Plan (GA)    │ │ Audit Trail    │
 │ fact checker   │ │          │ │ time-budget  │ │ replayable     │
 │      ①④        │ │   ③④     │ │      ②       │ │                │
 └────────────────┘ └──────────┘ └──────────────┘ └────────────────┘
                                v
                          User Interface
```

### Main Components

- **Resume Parser** — 提取技能、教育背景、项目经历、工作经历
- **JD Analyzer** — 识别职责、硬技能、软技能、学历要求、岗位类别
- **IT Skill Knowledge Graph** — 技能层级与关联（React/Vue/Angular ∈ frontend frameworks；Docker/K8s/CI-CD ∈ DevOps；PyTorch/TensorFlow/scikit-learn ∈ ML tools）
- **Rule-based Eligibility Filter** — 硬性条件裁决，输出 PASS / DEMOTE / REJECT 及触发的规则列表
- **Hybrid Matching & Ranking Engine** — 四维加权打分，分数可分解
- **Explanation Module** — 结构化解释：命中规则、已匹配技能及其简历证据、缺口技能（区分可迁移 / 硬缺口）、分数分解
- **Resume Optimization Module** — JD 定向 bullet 改写，事实一致性校验
- **Interview Prep Retriever** — RAG 检索题库与面经，按岗位技能标签召回
- **Application Plan Optimizer** — GA 求解时间预算下的投递组合与排程
- **Agent Orchestrator** — 多步任务编排与自反思
- **User Interface** — Streamlit，展示推荐、分数、差距、改写建议、投递计划

---

## 8. Reasoning Techniques

### 8.1 四大技术组映射（硬性要求 ≥3，本项目覆盖 4/4）

| 技术组 | 本项目模块 | 具体技术 | 课程出处 |
|---|---|---|---|
| **① 决策自动化**<br>业务规则 / 知识推理 | 岗位硬约束准入引擎；简历改写的结构化槽位规则 | 前向链推理规则引擎（durable_rules / Experta）；冲突集与冲突消解（优先级 + 最长匹配）；决策树抽取规则 | MR Day2（前/后向链、冲突消解、规则抽取）；RS Day1（Rules + ML 混合模式） |
| **② 资源优化**<br>启发式搜索 / 进化计算 | 投递计划优化器：每周 N 小时精力预算下选择投哪些岗位、按什么顺序精修 | 遗传算法（排列编码、锦标赛选择、顺序交叉、变异、软约束罚函数）；对照组用贪心 Top-K 与 A\* | RS Day4（GA 全流程、罚函数、参数调优）；MR Day1（A\*、启发式搜索） |
| **③ 知识发现与数据挖掘** | 混合匹配打分与排序；岗位聚类；技能共现挖掘 | Sentence-BERT embedding + 余弦相似；TF-IDF 基线；k-means 岗位聚类；Apriori 挖掘技能共现规则；LightGBM 排序器（弱标签） | MR Day4（k-means、集成方法、评估指标）；RS Day2（TF-IDF、余弦、MBA/Apriori、P@K / NDCG） |
| **④ 认知技术** | Agent 编排；NER 结构化解析；技能知识图谱；RAG 面试包；自然语言交互界面 | LLM function calling / ReAct；spaCy + BIO 序列标注 NER；Neo4j + Cypher 多跳查询；KG embedding（TransE / RotatE，PyKEEN）；RAG grounded generation | CGS Day1 AM（NLU 流水线、NER、RAG、Agent 规划）；MR Day3 / RS Day5（KG、PyKEEN、Graph-RAG、Neo4j） |

### 8.2 各类推理的具体职责

**Rule-based Reasoning（①）** — 处理硬性筛选：岗位类型、地点、学历要求、毕业时间、实习/全职类型、工作签证要求。规则显式可读，例如：
```
IF jd.min_experience > profile.experience + 2   THEN REJECT (reason: experience_gap)
IF jd.visa_sponsorship = false AND profile.needs_sponsorship = true THEN REJECT (reason: visa)
IF jd.location NOT IN profile.preferred_locations THEN DEMOTE (reason: location)
IF jd.degree_required IS NULL                   THEN NO_CONSTRAINT
```

**Knowledge-based Reasoning（④）** — 通过 KG 理解技能关系，把"缺口"分成两类：
- *可迁移缺口*：会 PyTorch、岗位要 TensorFlow → 同属 `MachineLearningFramework`，一跳可达 → 提示"简历中强调框架迁移能力"
- *硬缺口*：完全没接触过 Kubernetes 且无相邻技能 → 提示"这是真实短板，建议补充或降低该岗优先级"

**Semantic Reasoning（③）** — SBERT embedding 计算简历项目经历与 JD 职责的语义相似度，解决关键词匹配识别不出相关经历的问题（"用 Flask 写过 REST API" ↔ "backend service development"）。

**Optimization Reasoning（②）** — GA 求解：给定候选岗位集合、各岗位的预估精修耗时、匹配分数、投递截止日期、每周可用小时数，最大化期望收益 `Σ (match_score × company_attractiveness)`，约束为总耗时 ≤ 预算且不超过任何截止日期，超限用罚函数处理。

**LLM-based Reasoning（④）** — 生成匹配解释的自然语言表述、总结技能差距、改写 bullet points。**受约束**：可引用的事实限定在原简历 span 内，输出须过事实一致性校验。

### 8.3 关键设计取舍（评分表要求的 "thinking process to compare and identify suitable techniques"）

| 决策点 | 候选 | 选择 | 理由 |
|---|---|---|---|
| 硬约束怎么处理 | (a) 当作打分模型的一个特征 (b) 显式规则引擎前置 | **(b)** | 签证 / 学历是**准入**不是**偏好**。模型分再高、没有签证资格也是零价值甚至负价值。规则前置还能把候选集从 3,000 缩到几百，大幅降低 embedding 成本 |
| 匹配用什么表示 | (a) 整篇 JD vs 整篇简历 embedding (b) 结构化抽取后分维打分 | **(b) 为主，(a) 保留为基线** | 整篇编码被公司介绍 / 福利稀释；分维可解释、可调权重、可做消融。(a) 留作对照正是 G1 增益的证明方式 |
| 技能相似度 | (a) 纯 embedding (b) 纯 KG 结构 (c) 融合 | **(c)** | embedding 给"多像"，KG 给"为什么像"。融合后才能输出可迁移缺口 vs 硬缺口这种**有行动价值**的区分 |
| 简历改写 | (a) 直接 prompt LLM (b) 结构化槽位 + LLM 填充 + 事实校验 | **(b)** | (a) 会编经历，直接违背 G3。(b) 里 LLM 只做措辞层改写，可改 span 与可引用事实都被限定，再过一道 NLI 式一致性校验 |
| 投递优先级 | (a) 按分数排序取 Top-K (b) GA 组合优化 | **(b)，(a) 为基线** | 排序忽略精修成本差异与截止日期。GA 能处理"高分但要重写整份简历" vs "中分但只需改三行"的真实权衡，并覆盖技术组② |
| 是否自动投递 | (a) 自动提交 (b) 生成投递包 + 人工点击 | **(b)** | ToS 合规 + 不可逆操作必须人在回路 |

---

## 9. Implementation Plan

### 技术栈

Python 3.11 / FastAPI（后端）/ Streamlit（前端，10 man-day 预算下不折腾 React）/ Neo4j Aura Free（KG）/ ChromaDB（向量库）/ sentence-transformers `all-MiniLM-L6-v2` / spaCy `en_core_web_trf` / durable_rules 或 Experta（规则引擎）/ DEAP（GA）/ PyKEEN（KG embedding）/ scikit-learn + LightGBM / LangChain（Agent 编排与 RAG）。全部开源，符合 briefing 中"避免重复造轮子、鼓励采用开源子模块与 API"的要求。

### 弱标签方案（无真实投递反馈时如何训练与评估）

三种代理标签，并报告三者的 Cohen's κ 一致性：
1. 组员人工标注 300 对 (简历, 岗位) 的三级匹配度（强匹配 / 一般 / 不匹配）
2. JD 中显式列出的 must-have 技能是否全覆盖 → 正 / 负样本
3. 同公司同职级岗位视为同类，用于一致性检验

### Phase 表（对齐小组原框架的 8 阶段，补上里程碑与周次）

| Phase | 周次 | Task | Expected Output |
|---|---|---|---|
| 1 | 提案期 | 确定岗位类别与数据来源 | 岗位分类列表、数据收集计划、可行性验证结论 |
| 2 | W1 (9/14–9/20) | 收集 JD 与样例简历，建管道 | 3,000 条清洗后 JD 入库、脱敏简历样本 |
| 3 | W1–W2 | JD parser 与 resume parser | 结构化 JD profile 与 student profile；**E1 完成** |
| 4 | W2 (9/21–9/27) | 规则引擎① + 混合打分③ + KG④ 骨架 | 端到端 CLI 可出排序 + 解释 |
| 5 | W3 (9/28–10/4) | 解释模块 + 简历优化模块①④ + 面试 RAG③④；**scope freeze** | 推荐理由、技能差距、改写 bullet；**E2/E4/E5 首轮** |
| 6 | W4 (10/5–10/11) | GA 投递优化② + Agent 编排④ | 可演示完整系统 |
| 7 | W4 | Streamlit demo UI | 可演示 Web 界面 |
| 8 | W5–W6 (10/12–10/25) | 实验全跑 + 报告 + 两段视频 + 打包提交 | 交付物齐全 |

**分工建议（5 人）**：数据与抽取 / 规则引擎与优化 / 匹配与实验 / KG 与 RAG / Agent 与前端；报告与视频全员分章节。

### Repo 结构（对齐 IRS-PM 官方提交模板）

```
IRS-v1/
├── ProjectReport/          # 报告 PDF
├── Miscellaneous/          # 提案、会议记录
├── SystemCode/
│   ├── ingest/             # 岗位采集与清洗
│   ├── parsing/            # ④ NER 结构化抽取
│   ├── rules/              # ① 规则引擎
│   ├── matching/           # ③ 混合打分与排序
│   ├── kg/                 # ④ Neo4j + KG embedding
│   ├── rewrite/            # ①④ 简历改写 + 事实校验
│   ├── rag/                # ③④ 面试包检索
│   ├── optimize/           # ② GA 投递规划
│   ├── agent/              # ④ 编排层
│   ├── app/                # Streamlit UI
│   └── experiments/        # 实验脚本与结果
└── README.md / member-github.txt
```

---

## 10. Expected Results / Evaluation

### 10.1 量化实验设计（评分表第 4 项，独立计分，重点做）

| # | 实验 | 基线 vs 方法 | 指标 | 对应目标 |
|---|---|---|---|---|
| E1 | 结构化抽取质量 | 词典匹配 vs 词典 + LLM 兜底 | 技能抽取 Precision / Recall / F1（200 条人工标注） | 支撑全链路 |
| E2 | 匹配排序 | B1 TF-IDF 余弦 / B2 整篇 SBERT 余弦 / M 分维混合 / M+ 加 KG 推理 | Precision@5、Precision@10、NDCG@10、MAP | **G1** |
| E3 | 权重标定与消融 | 网格搜索 w1–w4；逐项去除 | NDCG@10 曲线 + 消融表（每去掉一项降多少） | G1，证明每个组件都有用 |
| E4 | 规则引擎价值 | 有 / 无硬约束前置 | 不合格岗位混入 Top-10 的比例；候选集缩减率；端到端延迟 | G2，证明技术组① |
| E5 | 改写事实一致性 | 裸 LLM prompt vs 模板 + 约束 + 校验 | 幻觉率（人工判定 100 条 bullet）；JD 关键词覆盖率提升；语义保真度 | **G3** |
| E6 | 投递计划优化 | 贪心 Top-K vs GA（扫 popSize / mutationRate） | 预算内期望收益；收敛曲线；参数敏感性 | 证明技术组② |
| E7 | 端到端与可用性 | — | 任务完成率、端到端耗时、5 名同学试用的 SUS 分与"解释可理解性"打分 | G2 / G4，系统级评估（CGS Day2 三层评估框架） |

### 10.2 定性验收（沿用小组原框架）

**Recommendation** — Top-K 岗位是否符合学生意向；匹配分数是否体现技能 / 项目 / 岗位要求的相关性；解释是否清晰、可信、可操作。

**Resume Optimization** — 优化后是否覆盖更多目标 JD 关键词；改写内容是否严格基于真实经历；bullet 是否更具体、结果导向、突出技术栈；改写后匹配分数是否提升。

**User Experience** — 学生能否快速理解自己适合哪些岗位；能否明确看到技能差距；能否据建议快速改简历。

---

## 11. Challenges and Roadblocks

| 风险 | 影响 | 缓解 |
|---|---|---|
| 岗位数据获取受限 / 反爬 | 高 | 主用公开 API + Kaggle 数据集；爬虫限速且仅作演示；不把成败押在爬虫上 |
| 无真实投递反馈标签 | 高 | §9 三重弱标签方案；评估以排序质量而非转化率衡量 |
| LLM 幻觉编造经历 | 高 | 结构化约束 + 事实校验器 + E5 量化；这是项目核心卖点，必须做扎实 |
| IT 技能更新快，本体需维护 | 中 | ESCO 定期更新 + KG embedding link prediction 自动补边 |
| 同一岗位名称不同公司要求差异大 | 中 | 不依赖 title，以抽取出的技能与职责为准；k-means 聚类做岗位归组 |
| JD / 简历格式不统一，解析难 | 中 | 分段丢弃噪声段；缺失即"不约束"；抽取质量用 E1 量化盯住 |
| 范围过大做不完 | 中 | §5 已明确砍掉自动投递、中文、多行业；W3 设 scope-freeze 检查点 |
| 简历含 PII | 中 | 本地脱敏后再进任何外部 API；报告写明合规处理说明 |

---

## 12. Future Work

- 接入实时招聘平台 API 或定期增量更新岗位数据
- 扩展 IT 子领域：QA Engineer、Database Engineer、Cloud Security Engineer
- Cover letter 自动生成
- Mock interview question generation 与模拟面试对话
- 收集真实申请反馈，把弱标签换成真实标签，训练排序模型闭环
- 多语言简历与 JD（中文 / 英文）
- 为 career coach 或导师增加反馈入口与批量视图

---

## 13. Conclusion

IT CareerPilot 把一个学生每天都在经历的痛点，拆成四个可以用课程技术精确求解的子问题：**准入用规则、排序用模型、理解用知识图谱、分配用优化**，再由 Agent 把它们编排成一条可解释、可审计的链路。

它的价值不在于"又一个 AI 求职工具"，而在于证明——在**硬约束、稀疏反馈、需要解释**的真实决策场景里，混合推理系统比端到端 LLM 更可靠、更可审计，也更有可能被真的用起来。系统不仅给出推荐结果，还能说清推荐原因、区分可迁移差距与硬差距，并基于目标岗位生成可操作的简历优化建议与投递计划。

---

## 14. Supplementary Materials

**Appendix A — AI 使用声明**
本项目在以下环节使用 AI 工具：文献检索辅助、代码补全、文档润色，以及作为系统组件的 LLM API 调用（简历改写、抽取兜底、Agent 编排）。所有实验数据、人工标注与结论由组员自行完成与核验。演示视频讲解语音由组员本人录制，**未使用 AI 生成语音**（符合 briefing 要求）。

**Appendix B — 数据来源与合规说明**
岗位数据来自公开 API 与开放数据集；官网抓取遵守 robots.txt 并限速 1 req/s；简历数据经 PII 脱敏后使用；系统不执行自动投递。

**Appendix C — 其他附录**
IT 技能 taxonomy 示例（ESCO 片段）、系统架构图高清版、初步 UI mockup、参考文献、竞品分析表、Acknowledgements。

---

## 附：交付清单（对齐 exam briefing v2.17）

**提案阶段（2026-09-13 23:59 前，组长提交 Canvas「[Group Leader] Project Proposal」）**
- [ ] 提案文档（doc / docx / pdf）
- [ ] 提案答辩 PPT（按 guidelines v016 的 14 页结构）

**最终交付（2026-10-25 23:59 前）**
- [ ] `member-github.txt`（组名、全名、学号或 masked NRIC、repo 链接）
- [ ] 两段视频：`IRS-PM-<date>-<class>-GRP-<group>-IT_CareerPilot-promotion.mp4` 与 `-system.mp4`（**不得使用 AI 生成演讲语音**）
- [ ] GitHub repo zip（IRS-PM 官方模板结构）
- [ ] 组项目报告 PDF
- [ ] 以上打包成单个 zip，上传「[Group Leader] Project Deliverables」
- [ ] 每人各自提交 individual peer evaluation


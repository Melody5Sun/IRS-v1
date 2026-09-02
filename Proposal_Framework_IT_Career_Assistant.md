# Proposal Framework: IT CareerPilot

## 1. Project Title

**IT CareerPilot: Intelligent Internship and Graduate Job Assistant for IT Students**

本项目面向正在申请 IT 行业实习与校招岗位的学生，提供岗位推荐、JD 分析、技能差距解释和针对性简历优化功能。

建议封面包含：

- Project Title
- Group Number
- Group Members' Names and NUS Student ID / Masked ID
- Date of Presentation

## 2. Introduction

### Project Overview

IT CareerPilot 是一个面向学生群体的智能求职助手。系统根据学生的专业背景、技术栈、项目经历、实习经历和岗位意向，推荐匹配的 IT 校招或实习岗位，并根据具体岗位 JD 帮助学生优化简历内容。

### Project Goals

- 帮助学生快速找到与自身技能和职业目标匹配的 IT 岗位。
- 自动分析 JD 中的技术要求、职责要求和关键能力。
- 解释学生简历与岗位之间的匹配原因和技能差距。
- 基于目标 JD 对简历项目经历和技能表达进行针对性优化。
- 体现 intelligent reasoning systems 在学生就业支持场景中的应用价值。

## 3. Project Background / Market Context

### Problem Background

IT 行业岗位类型多、技能要求变化快，不同岗位之间的要求差异明显，例如 Software Engineer、Data Analyst、AI/ML Engineer、Frontend Developer、Backend Developer、DevOps Engineer 和 Cybersecurity Analyst 等。

学生在求职过程中常见痛点包括：

- 岗位信息分散，筛选实习和校招机会成本高。
- JD 中包含大量技术关键词，学生难以判断自己是否真正匹配。
- 很多学生使用同一份通用简历投递不同岗位，缺少针对性。
- 项目经历表达不够贴近岗位要求，无法突出相关技术栈和成果。
- 学生缺少清晰的技能差距反馈，不知道下一步该补什么。

### Target Users

- 本科生、硕士生和应届毕业生。
- 正在申请 IT 实习、校招或 graduate program 的学生。
- 希望根据目标岗位优化简历的求职者。

### Usage Scenario

1. 学生上传简历并输入岗位意向。
2. 系统解析学生技能、教育背景、项目经历和求职偏好。
3. 系统分析 IT 岗位 JD，并推荐匹配岗位。
4. 学生选择目标岗位后，系统输出匹配解释、技能差距和简历优化建议。

## 4. Literature Review / Market Research

### Market Research

现有平台包括 LinkedIn、Indeed、Glassdoor、Handshake、学校 career portal、MyCareersFuture、InternSG 等。这些平台主要解决岗位搜索和信息展示问题，但对学生来说，仍存在以下不足：

- 推荐结果往往不够针对学生背景和项目经历。
- 岗位推荐、JD 理解和简历优化通常是分离的。
- 学生很难获得可解释的匹配原因。
- 简历优化建议不一定严格基于真实经历，存在过度包装风险。

本项目的机会点是构建一个面向 IT 学生的闭环工具：从岗位推荐到 JD 分析，再到简历优化和技能差距解释。

### Related Techniques

可参考的技术方向包括：

- NLP-based resume parsing and job description parsing
- Job-resume semantic matching
- Skill extraction and skill taxonomy
- Knowledge-based reasoning for IT skill relationships
- Rule-based filtering for job eligibility and preferences
- LLM-based resume rewriting with factual constraints
- Explainable recommendation systems

## 5. Project Scope

### In Scope

本项目聚焦 IT 行业学生求职场景，初版优先支持以下岗位方向：

- Software Engineering
- Backend Development
- Frontend Development
- Data Analytics / Data Science
- AI / Machine Learning
- Cloud / DevOps
- Cybersecurity

核心功能范围：

- Resume Parser: 解析学生简历中的教育背景、技能、项目经历和实习经历。
- Student Profile Builder: 构建学生求职画像。
- Job Description Analyzer: 从 JD 中提取岗位职责、技术技能、经验要求和软技能。
- IT Skill Knowledge Base: 建立 IT 技能与岗位方向之间的关系。
- Recommendation Engine: 根据学生画像和岗位 JD 计算匹配度并排序。
- Explanation Module: 输出推荐理由和技能差距。
- Resume Optimization Module: 根据目标 JD 给出简历修改建议或改写 bullet points。

### Out of Scope / Limitations

- 不自动代替学生投递岗位。
- 不保证 offer 或面试结果。
- 不虚构学生经历，只基于用户已有经历进行表达优化。
- 初版不覆盖非 IT 行业岗位。
- 初版岗位数据可能来自公开样本、手动收集数据或小规模测试数据集。

## 6. Data Collection and Preparation

### Data Sources

- IT 实习和校招 JD：公开招聘网站、公司官网、学校 career portal、MyCareersFuture、InternSG 或公开 job posting dataset。
- 学生简历：匿名化样例简历、自建测试简历或小组成员提供的脱敏简历。
- IT 技能知识库：人工整理的技能 taxonomy，例如 programming languages、frameworks、databases、cloud platforms、ML tools 和 cybersecurity tools。

### Data Processing

- 清洗 JD 文本，移除无关格式和噪声。
- 提取岗位名称、公司、地点、岗位类型、职责、技术技能和经验要求。
- 解析简历中的教育背景、项目经历、技能、证书和实习经历。
- 将 JD 和简历转化为结构化 profile。
- 通过关键词匹配、技能关系映射和语义向量相似度计算匹配分数。

### Data Challenges

- JD 格式不统一，技术要求表达方式差异大。
- 同一技能可能存在不同写法，例如 JavaScript / JS、Machine Learning / ML。
- 学生简历内容可能不完整，影响匹配准确度。
- 简历优化需要避免 hallucination 和事实夸大。

## 7. System Design

### Proposed Architecture

```text
Student Resume + Career Preference
        |
        v
Resume Parser
        |
        v
Student Profile Builder
        |
        +-----------------------------+
                                      |
Job Posting / JD Data                 |
        |                             |
        v                             |
JD Analyzer                           |
        |                             |
        v                             |
Structured Job Profile                |
        |                             |
        +-----------> Recommendation and Reasoning Engine
                              |
                              v
                Job Ranking + Match Explanation + Skill Gap
                              |
                              v
                  JD-based Resume Optimization
                              |
                              v
                         User Interface
```

### Main Components

- **Resume Parser**: 从简历中提取学生技能、教育背景、项目经历和工作经历。
- **JD Analyzer**: 识别岗位职责、硬技能、软技能、学历要求和岗位类别。
- **IT Skill Knowledge Base**: 建立技能之间的层级和关联，例如 PyTorch 与 TensorFlow 属于 machine learning frameworks。
- **Recommendation and Reasoning Engine**: 综合规则筛选、技能匹配和语义匹配，输出岗位排序。
- **Explanation Module**: 解释推荐原因，例如已匹配技能、相关项目经历和缺失技能。
- **Resume Optimization Module**: 根据目标 JD 改写简历 bullet points，并保持事实一致。
- **User Interface**: 展示推荐岗位、匹配分数、技能差距和简历修改建议。

## 8. Reasoning Techniques

### Rule-based Reasoning

用于处理硬性筛选条件，例如岗位类型、地点、学历要求、毕业时间、实习/全职类型和工作签证要求。

### Knowledge-based Reasoning

通过 IT 技能知识库理解技能之间的关系。例如：

- React、Vue 和 Angular 属于 frontend frameworks。
- Docker、Kubernetes 和 CI/CD 属于 DevOps skill set。
- PyTorch、TensorFlow 和 scikit-learn 属于 machine learning tools。

### Semantic Reasoning

使用文本 embedding 计算简历项目经历与 JD 职责之间的语义相似度，解决仅靠关键词匹配无法识别相关经历的问题。

### LLM-based Reasoning

用于生成匹配解释、总结技能差距、改写简历 bullet points 和输出可读的求职建议。生成过程需要受到 factual constraints 限制，避免虚构经历。

## 9. Implementation Plan

| Phase | Task | Expected Output |
| --- | --- | --- |
| Phase 1 | 确定 IT 岗位类别和数据来源 | 岗位分类列表、数据收集计划 |
| Phase 2 | 收集 JD 和样例简历 | 小规模 JD 数据集、脱敏简历样本 |
| Phase 3 | 实现 JD parser 和 resume parser | 结构化 JD profile 和 student profile |
| Phase 4 | 实现技能匹配和岗位推荐 | 推荐岗位列表、匹配分数 |
| Phase 5 | 实现解释模块 | 推荐理由、技能差距分析 |
| Phase 6 | 实现 JD-based 简历优化模块 | 简历修改建议、改写后的 bullet points |
| Phase 7 | 搭建 demo UI | 可演示的 Web 界面 |
| Phase 8 | 测试与准备 final presentation | 测试结果、demo、final slides |

## 10. Expected Results / Evaluation

### Recommendation Evaluation

- Top-K 推荐岗位是否符合学生岗位意向。
- 匹配分数是否能体现技能、项目经历和岗位要求之间的相关性。
- 推荐解释是否清晰、可信、可操作。

### Resume Optimization Evaluation

- 优化后的简历是否覆盖更多目标 JD 关键词。
- 改写内容是否基于学生真实经历。
- bullet points 是否更具体、结果导向，并突出 IT 技术栈。
- 简历与 JD 的匹配分数是否有所提升。

### User Experience Evaluation

- 学生是否能快速理解自己适合哪些 IT 岗位。
- 学生是否能明确看到技能差距。
- 学生是否能根据建议快速修改简历。

## 11. Challenges and Roadblocks

- IT 岗位技能更新快，技能知识库需要维护。
- 不同公司对同一岗位名称的要求差异较大。
- JD 和简历文本格式不统一，解析难度较高。
- LLM 可能产生 hallucination，需要加入事实约束和输出检查。
- 匹配分数需要兼顾关键词、语义和可解释性。
- 岗位数据获取可能受平台权限和数据质量限制。

## 12. Future Work

- 接入实时招聘平台 API 或定期更新岗位数据。
- 支持更多 IT 子领域，例如 QA Engineer、Database Engineer、Cloud Security Engineer。
- 增加 cover letter generation。
- 增加 mock interview question generation。
- 根据学生申请反馈优化推荐模型。
- 支持多语言简历和 JD，例如英文、中文。
- 为 career coach 或导师增加反馈入口。

## 13. Conclusion

IT CareerPilot 针对 IT 学生实习和校招申请中的真实痛点，结合岗位推荐、JD 分析、技能差距解释和简历优化，帮助学生更高效、更有针对性地申请岗位。

本项目体现了 intelligent reasoning systems 在教育就业服务场景中的实际价值：系统不仅给出推荐结果，还能解释推荐原因、识别技能差距，并基于目标岗位生成可操作的简历优化建议。

## 14. Supplementary Materials

可在 appendix 中补充：

- AI 使用说明
- 数据来源说明
- IT 技能 taxonomy 示例
- 系统架构图
- 初步 UI mockup
- 参考文献和竞品分析表

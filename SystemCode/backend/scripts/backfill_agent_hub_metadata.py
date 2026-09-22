"""一次性脚本：为 agent-interview-hub 的 83 条题目回填 difficulty_level / skills_json / keywords_json。

difficulty_level：按题目本身的技术深度人工评估（easy/medium/hard），不是自动推断。
skills_json：仅在题目明确提到 MIND 技能图谱（data/mind_ontology/skills.json）里存在的具体技术名称时才打标，
    概念性提问（如"什么是 Agent"）不强行关联某个产品名。
keywords_json：参照库里其余数据（如 Devinterview.io 那批）的风格——英文小写短语，覆盖题目涉及的概念/技术点，
    替换掉之前占位的分类标题（如"一、Agent 核心面试题"）。

用一次即弃，不接入常规导入流程。
"""

import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "careerpilot.db"

# id -> (difficulty, skills, keywords)
DATA: dict[int, tuple[str, list[str], list[str]]] = {
    1: ("easy", [], ["agent", "llm", "autonomy", "tool use"]),
    2: ("medium", [], ["context window", "context management", "memory", "agent"]),
    3: ("medium", [], ["tool calling", "error handling", "agent", "function calling"]),
    4: ("medium", [], ["agent memory", "short-term memory", "long-term memory", "vector store"]),
    5: ("hard", [], ["multi-agent", "orchestration", "agent selection", "routing"]),
    6: ("easy", [], ["rag", "retrieval augmented generation", "pipeline"]),
    7: ("medium", [], ["lost in the middle", "long context", "retrieval", "rag"]),
    8: ("easy", [], ["vector search", "keyword search", "retrieval", "bm25"]),
    9: ("medium", ["lora", "qlora"], ["lora", "qlora", "fine-tuning", "gpu memory"]),
    10: ("medium", ["lora"], ["lora", "fine-tuning", "troubleshooting", "hyperparameters"]),
    11: ("hard", [], ["search agent", "search engine", "information retrieval", "system design"]),
    12: ("hard", [], ["autonomous driving", "agent", "safety", "feasibility"]),
    13: ("medium", [], ["function calling", "plugin system", "tool use", "ernie bot"]),
    14: ("hard", [], ["rag", "query rewriting", "multi-path retrieval", "recall"]),
    15: ("hard", [], ["hallucination", "agent", "reliability", "detection"]),
    16: ("hard", [], ["scaling laws", "model size", "inference cost", "agent"]),
    17: ("medium", [], ["group chat", "agent design", "wechat", "multi-turn dialogue"]),
    18: ("medium", [], ["game ai", "npc", "agent architecture", "behavior design"]),
    19: ("medium", [], ["agent evaluation", "conversational ai", "metrics", "accuracy"]),
    20: ("hard", ["anthropic-claude"], ["hunyuan", "gpt", "claude", "agent application", "model comparison"]),
    21: ("hard", [], ["scalability", "system architecture", "high availability", "dau"]),
    22: ("medium", [], ["rich media", "multimodal", "wechat mini program", "content generation"]),
    23: ("easy", [], ["ai agent", "automation", "definition", "autonomy"]),
    24: ("easy", [], ["agent architecture", "planning", "memory", "tool use"]),
    25: ("easy", [], ["llm", "agent", "capability limitation", "reasoning"]),
    26: ("medium", [], ["react framework", "reasoning", "acting", "agent loop"]),
    27: ("easy", [], ["agent", "rag", "knowledge retrieval", "integration"]),
    28: ("medium", [], ["mcp", "model context protocol", "tool invocation", "agent"]),
    29: ("medium", [], ["single agent", "multi-agent", "architecture tradeoff", "decision"]),
    30: ("hard", [], ["general-purpose agent", "framework design", "extensibility"]),
    31: ("medium", ["hugging-face-transformers"], ["transformer", "self-attention", "rnn", "long sequence"]),
    32: ("hard", [], ["rope", "rotary position embedding", "positional encoding"]),
    33: ("hard", [], ["mha", "mqa", "gqa", "attention", "kv cache"]),
    34: ("medium", [], ["customer service agent", "local services", "system integration"]),
    35: ("hard", [], ["dispatch scheduling", "operations research", "optimization", "agent"]),
    36: ("medium", [], ["recommendation system", "personalization", "conversational agent"]),
    37: ("medium", [], ["agent evaluation", "debugging", "production issues", "optimization"]),
    38: ("medium", [], ["token cost", "cost control", "user experience", "agent"]),
    39: ("hard", [], ["edge deployment", "mobile", "iot", "on-device inference"]),
    40: ("hard", [], ["data privacy", "compliance", "security", "agent"]),
    41: ("hard", [], ["harmonyos", "android", "ios", "distributed computing"]),
    42: ("hard", [], ["npu", "gpu", "ascend", "nvidia", "inference architecture"]),
    43: ("hard", [], ["tool calling", "security audit", "access control", "agent"]),
    44: ("hard", [], ["offline agent", "degraded mode", "local inference"]),
    45: ("medium", [], ["enterprise copilot", "consumer agent", "architecture comparison"]),
    46: ("medium", ["semantic-kernel", "langchain"], ["azure ai", "semantic kernel", "langchain", "tech stack"]),
    47: ("medium", [], ["copilot", "data privacy", "retrieval augmentation", "enterprise data"]),
    48: ("medium", ["openapi"], ["tool description protocol", "openapi", "json schema", "agent"]),
    49: ("medium", [], ["error recovery", "retry mechanism", "tool calling", "fault tolerance"]),
    50: ("hard", ["google-gemini-api"], ["gemini", "gpt-4v", "multimodal architecture", "native multimodal"]),
    51: ("hard", [], ["ml pipeline", "big data", "data pipeline", "scalability"]),
    52: ("medium", [], ["search agent", "reliability", "hallucination", "generative search"]),
    53: ("medium", [], ["a2a protocol", "mcp", "agent-to-agent", "interoperability"]),
    54: ("hard", [], ["tpu", "gpu", "inference optimization", "throughput", "cost"]),
    55: ("medium", [], ["short video", "content understanding", "multimodal analysis"]),
    56: ("medium", [], ["short video", "content creation", "agent assistance"]),
    57: ("medium", [], ["user profiling", "recommendation system", "llm"]),
    58: ("medium", [], ["content moderation", "video safety", "rule-based review"]),
    59: ("medium", [], ["a/b testing", "agent evaluation", "experimentation"]),
    60: ("hard", [], ["multi-agent architecture", "platform design"]),
    61: ("medium", [], ["end-to-end agent", "content publishing", "workflow automation"]),
    62: ("medium", [], ["agent architecture", "evolution", "design history"]),
    63: ("medium", [], ["error handling", "ambiguity", "agent robustness"]),
    64: ("medium", [], ["llama", "llama 2", "llama 3", "model comparison"]),
    65: ("easy", [], ["model size", "parameter count", "7b", "13b"]),
    66: ("hard", ["vllm"], ["vllm", "inference acceleration", "paged attention", "throughput"]),
    67: ("easy", [], ["ai content ecosystem", "opportunity", "challenge"]),
    68: ("easy", [], ["product strategy", "ai feature", "xiaohongshu"]),
    69: ("hard", [], ["multimodal agent", "vision", "language", "speech", "decision making"]),
    70: ("hard", [], ["embodied ai", "physical interaction", "agent", "robotics"]),
    71: ("hard", [], ["vision-language model", "gui agent", "screen understanding"]),
    72: ("medium", [], ["visual agent evaluation", "multimodal metrics"]),
    73: ("hard", [], ["multimodal training", "data collection", "annotation"]),
    74: ("medium", [], ["fintech", "compliance", "security", "agent"]),
    75: ("medium", ["langchain"], ["agentuniverse", "langchain", "framework comparison"]),
    76: ("medium", [], ["risk control", "fintech", "real-time", "agent"]),
    77: ("hard", [], ["multi-turn dialogue", "state management", "long conversation", "context accuracy"]),
    78: ("medium", [], ["agent evaluation", "online offline testing", "quality assurance"]),
    79: ("medium", [], ["mvp", "tech stack selection", "rapid prototyping", "agent product"]),
    80: ("medium", [], ["product-market fit", "agent product", "metrics", "value validation"]),
    81: ("hard", [], ["resource constraints", "evaluation framework", "quality assurance"]),
    82: ("medium", [], ["moat", "startup strategy", "competitive advantage", "agent"]),
    83: ("medium", [], ["pricing model", "usage-based pricing", "outcome-based pricing", "agent product"]),
}


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT id FROM interview_questions WHERE difficulty_level = 'not_stated'"
    )
    remaining_ids = {row[0] for row in cur.fetchall()}
    missing = remaining_ids - DATA.keys()
    extra = DATA.keys() - remaining_ids
    if missing:
        raise SystemExit(f"缺少映射: {sorted(missing)}")
    if extra:
        raise SystemExit(f"多余映射（对应行已不是 not_stated）: {sorted(extra)}")

    for qid, (difficulty, skills, keywords) in DATA.items():
        cur.execute(
            "UPDATE interview_questions SET difficulty_level = ?, skills_json = ?, keywords_json = ? WHERE id = ?",
            (difficulty, json.dumps(skills), json.dumps(keywords), qid),
        )
    conn.commit()

    cur.execute("SELECT difficulty_level, COUNT(*) FROM interview_questions GROUP BY difficulty_level")
    print("difficulty_level 分布:", cur.fetchall())
    conn.close()


if __name__ == "__main__":
    main()

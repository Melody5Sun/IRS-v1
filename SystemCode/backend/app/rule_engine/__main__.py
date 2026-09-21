"""命令行入口：python -m app.rule_engine <profile.json> <db_path> [--stats]"""

import argparse
import json
import logging
from collections import Counter
from pathlib import Path

from app.rule_engine.engine import connect_read_only, evaluate
from app.schemas.profile import UserProfile


def main() -> None:
    parser = argparse.ArgumentParser(description="按硬规则筛选岗位，输出通过全部规则的岗位 id")
    parser.add_argument("profile", help="UserProfile JSON 文件路径")
    parser.add_argument("db_path", help="SQLite 数据库路径（只读打开）")
    parser.add_argument("--stats", action="store_true", help="改为输出每条规则单独剔除的岗位数")
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")
    profile = UserProfile.model_validate_json(Path(args.profile).read_text(encoding="utf-8"))
    connection = connect_read_only(args.db_path)
    try:
        kept, rejections = evaluate(profile, connection)
    finally:
        connection.close()

    if args.stats:
        # 单独剔除数：被该规则拒绝的岗位数，不管其他规则是否也拒绝了它（不是累计）
        per_rule = Counter(rule for rules in rejections.values() for rule in rules)
        result = {
            "total_jobs": len(kept) + len(rejections),
            "rejected_by_rule": dict(sorted(per_rule.items())),
            "kept": len(kept),
        }
    else:
        result = {"job_ids": kept}
    print(json.dumps(result, ensure_ascii=False, indent=2 if args.stats else None))


if __name__ == "__main__":
    main()

# ============================================
# 工艺关键词提取器
# ============================================
import json
from backend.paths import resolve_path


class CraftExtractor:
    """从文本中提取工艺关键词"""

    def __init__(self, craft_tags_file: str = "data/craft_tags.json"):
        with open(resolve_path(craft_tags_file), "r", encoding="utf-8") as f:
            self.tags: list[str] = json.load(f)

        # 按长度降序（优先匹配长的，如"镭射银" > "镭射"）
        self.tags.sort(key=len, reverse=True)

    def extract(self, text: str) -> list[str]:
        """返回匹配到的工艺关键词列表"""
        found = []
        for tag in self.tags:
            if tag in text:
                found.append(tag)
        return found

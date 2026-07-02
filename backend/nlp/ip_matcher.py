# ============================================
# IP 名称匹配器
# ============================================
import json
from backend.paths import resolve_path


class IPMatcher:
    """
    通过别名映射表匹配 IP 名称

    ip_aliases.json 格式:
        { "魔道祖师": ["魔道", "mdzs", "魔道祖師", ...], ... }

    匹配逻辑:
        1. 先精确匹配标准名
        2. 再逐个别名匹配
        3. 返回 (标准名, ip_db_id, 匹配到的别名)
    """

    def __init__(self, aliases_file: str = "data/ip_aliases.json"):
        with open(resolve_path(aliases_file), "r", encoding="utf-8") as f:
            self.aliases: dict[str, list[str]] = json.load(f)

        # 构建别名 → 标准名反向索引
        self._alias_to_name: dict[str, str] = {}
        for std_name, alias_list in self.aliases.items():
            for alias in alias_list:
                self._alias_to_name[alias.lower()] = std_name
            self._alias_to_name[std_name.lower()] = std_name

    def match(self, text: str) -> tuple[str | None, int | None, str | None]:
        """
        在文本中匹配 IP

        返回:
            (standard_name, db_id_or_None, matched_alias)
        """
        if not text:
            return None, None, None

        text_lower = text.lower()

        # 按别名长度降序匹配（优先匹配长的，避免"魔道"先于"魔道祖师"被匹配）
        sorted_aliases = sorted(
            self._alias_to_name.items(),
            key=lambda x: len(x[0]),
            reverse=True,
        )

        for alias_lower, std_name in sorted_aliases:
            if alias_lower in text_lower:
                return std_name, None, alias_lower

        return None, None, None

    def get_all_names(self) -> list[str]:
        """返回所有标准 IP 名"""
        return list(self.aliases.keys())

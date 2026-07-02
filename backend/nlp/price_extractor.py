# ============================================
# 价格提取器
# ============================================
import re


class PriceExtractor:
    """
    从中文文本中提取价格

    匹配模式:
        - 38元、38.5元
        - ¥38、¥38.5
        - 38rmb、38RMB
        - 售价38、价格38
    """

    PATTERNS = [
        re.compile(r'(?:售价|价格|定价|单价)?\s*(\d+\.?\d*)\s*(?:元|rmb|¥|RMB|块)'),
        re.compile(r'[¥￥]\s*(\d+\.?\d*)'),
        re.compile(r'(\d+)\s*(?:元|块)(?:/|每)(?:抽|发|个|只)'),  # 38元/抽
    ]

    # 噪声过滤：这些数字不是价格
    NOISE_PATTERNS = [
        re.compile(r'^\d{4}$'),          # 纯年份 2024
        re.compile(r'^\d{1,2}$'),         # 纯个位数
        re.compile(r'^\d{4}年'),          # 日期年份
        re.compile(r'^\d{2}:\d{2}'),      # 时间
        re.compile(r'^\d+cm$'),           # 尺寸
        re.compile(r'^\d+mm$'),           # 尺寸
    ]

    def extract(self, text: str) -> float | None:
        """返回提取到的价格，找不到返回 None"""
        candidates = []

        for pattern in self.PATTERNS:
            matches = pattern.findall(text)
            for m in matches:
                val = float(m)
                if self._is_valid(val):
                    candidates.append((val, text.find(str(m))))

        if not candidates:
            return None

        # 取文本中最早出现的合理价格
        candidates.sort(key=lambda x: x[1])
        return round(candidates[0][0], 2)

    def _is_valid(self, value: float) -> bool:
        """过滤噪声"""
        if value < 1 or value > 99999:
            return False
        return True

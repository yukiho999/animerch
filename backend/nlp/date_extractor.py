# ============================================
# 日期提取器
# ============================================
import re
from datetime import date, datetime, timedelta


class DateExtractor:
    """
    从文本中提取发售日期

    支持:
        - 2026年6月27日
        - 2026-06-27
        - 6月27日
        - 明日 / 明天
        - 12月25日
    """

    PATTERNS = [
        re.compile(r'(\d{4})年(\d{1,2})月(\d{1,2})日'),
        re.compile(r'(\d{4})-(\d{1,2})-(\d{1,2})'),
        re.compile(r'(?:发售日|开售日|发售日期|开售日期)[：:]\s*(\d{4})[年/-](\d{1,2})[月/-](\d{1,2})'),
        re.compile(r'(?:于|在)?(\d{1,2})月(\d{1,2})日'),   # 缺少年份
    ]

    RELATIVE_PATTERNS = [
        re.compile(r'(明日|明天)'),         # 明天
        re.compile(r'(后天)'),              # 后天
        re.compile(r'(今天|今日)'),          # 今天
        re.compile(r'(本周[一二三四五六日])'),
        re.compile(r'(下周[一二三四五六日])'),
    ]

    def extract(self, text: str) -> date | None:
        """返回提取到的日期，找不到返回 None"""
        today = date.today()

        # 先匹配绝对日期
        for pattern in self.PATTERNS:
            m = pattern.search(text)
            if not m:
                continue
            groups = m.groups()
            if len(groups) == 3 and groups[0]:
                try:
                    year = int(groups[0])
                    month = int(groups[1])
                    day = int(groups[2])
                    if month < 1 or month > 12 or day < 1 or day > 31:
                        continue
                    return date(year, month, day)
                except (ValueError, TypeError):
                    continue
            elif len(groups) == 2:
                try:
                    month = int(groups[0])
                    day = int(groups[1])
                    if month < 1 or month > 12 or day < 1 or day > 31:
                        continue
                    # 无年份，默认当前年（如果已过则为明年）
                    result = date(today.year, month, day)
                    if result < today - timedelta(days=1):
                        result = date(today.year + 1, month, day)
                    return result
                except (ValueError, TypeError):
                    continue

        # 相对日期
        if re.search(r'(明日|明天)', text):
            return today + timedelta(days=1)
        if re.search(r'(后天)', text):
            return today + timedelta(days=2)
        if re.search(r'(今天|今日)', text):
            return today

        return None

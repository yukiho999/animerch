# ============================================
# NLP 主解析器 — 串联所有子模块
# ============================================
import json
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models import PostRaw, MerchPost, CraftTag
from backend.nlp.ip_matcher import IPMatcher
from backend.nlp.craft_extractor import CraftExtractor
from backend.nlp.price_extractor import PriceExtractor
from backend.nlp.date_extractor import DateExtractor


class NLPParser:
    """
    NLP 解析管道：读取 post_raw → 提取结构化字段 → 写入 merch_post

    Usage:
        parser = NLPParser(confidence_threshold=0.3)
        count = parser.parse_pending()  # 处理所有待解析帖子
    """

    def __init__(
        self,
        ip_aliases_file: str = "data/ip_aliases.json",
        craft_tags_file: str = "data/craft_tags.json",
        confidence_threshold: float = 0.3,
    ):
        self.ip_matcher = IPMatcher(ip_aliases_file)
        self.craft_extractor = CraftExtractor(craft_tags_file)
        self.price_extractor = PriceExtractor()
        self.date_extractor = DateExtractor()
        self.confidence_threshold = confidence_threshold

    # ── 品类识别规则 ──
    CATEGORY_RULES = [
        (['吧唧', '徽章', 'badge', '铁皮'], '吧唧'),
        (['色纸', 'shikishi', '色紙'], '色纸'),
        (['亚克力立牌', '亚克力', 'acrylic stand', '立牌'], '亚克力立牌'),
        (['粘土人', '黏土人', 'ねんどろいど', 'nendoroid'], '粘土人'),
        (['挂件', '钥匙扣', 'keychain', '吊饰', '手机链'], '挂件'),
        (['文件夹', 'clear file', 'クリアファイル'], '文件夹'),
        (['海报', 'poster', 'ポスター'], '海报'),
        (['立牌', '站立牌'], '立牌'),
    ]

    # ── 发售方式规则 ──
    RELEASE_RULES = [
        (['通贩', '一般贩卖', '一般贩售', '网络贩卖', '网购', '线上贩售', '网上贩售'], '通贩'),
        (['场贩', '会场', '现场', '展会', '展场', '线下贩售', '线下', '实体会场'], '场贩'),
        (['受注', '受注生产', '预约生产', '订单生产', '完全受注', '予約販売', '受注販売'], '受注'),
        (['限定', '期间限定', '数量限定', '完全限定', '限定品', '限定商品', '限量'], '限定'),
        (['抽选', '应募', '抽签', '受付抽选', '抽選', '抽選販売', '应募抽选'], '抽选'),
    ]

    def _detect_category(self, text: str) -> tuple[str | None, str | None]:
        """返回 (category, hint)"""
        for keywords, category in self.CATEGORY_RULES:
            for kw in keywords:
                if kw.lower() in text.lower():
                    return category, kw
        return None, None

    def _detect_release_method(self, text: str) -> str:
        for keywords, method in self.RELEASE_RULES:
            for kw in keywords:
                if kw in text:
                    return method
        return '未知'

    def parse_one(self, post_raw: PostRaw, db: Session | None = None) -> MerchPost:
        """解析单条帖子，返回 MerchPost 对象（未提交）"""
        text = (post_raw.title or '') + ' ' + (post_raw.content or '')

        # Step 1: IP 识别
        ip_name, ip_id, _ = self.ip_matcher.match(text)

        # Step 2: 品类
        category, category_hint = self._detect_category(text)

        # Step 3: 工艺
        crafts = self.craft_extractor.extract(text)

        # Step 4: 价格
        price = self.price_extractor.extract(text)

        # Step 5: 日期
        rel_date = self.date_extractor.extract(text)

        # Step 6: 发售方式
        method = self._detect_release_method(text)

        # Step 7: 名称（截取原文前缀）
        merch_name = text[:700]

        # 置信度计算
        confidence = self._calc_confidence({
            'ip': ip_name is not None,
            'category': category is not None,
            'craft': len(crafts) > 0,
            'price': price is not None,
            'date': rel_date is not None,
            'method': method != '未知',
            'name': len(text) > 10,
        })

        return MerchPost(
            post_raw_id=post_raw.id,
            ip_name_hint=ip_name,
            ip_id=ip_id,
            merch_name=merch_name,
            category_hint=category_hint,
            category=category,
            official_price=price,
            release_date=rel_date,
            release_method=method,
            craft_keywords=crafts,
            confidence=confidence,
            need_review=1 if confidence < self.confidence_threshold else 1,  # 初期全部审核
            review_status='pending',
        )

    def parse_pending(self, db: Session | None = None) -> int:
        """解析所有 pending 状态的帖子，返回处理数量"""
        db = db or SessionLocal()
        own_db = db is None
        try:
            posts = db.query(PostRaw).filter(
                PostRaw.status == 'pending'
            ).order_by(PostRaw.id).all()

            count = 0
            for post in posts:
                merch_post = self.parse_one(post, db)
                db.add(merch_post)
                post.status = 'parsed'
                count += 1

            db.commit()
            print(f"== NLP 解析完成: {count} 条")
            return count
        finally:
            if own_db:
                db.close()

    def _calc_confidence(self, flags: dict[str, bool]) -> float:
        """计算置信度 0-1"""
        total = len(flags)
        hit = sum(1 for v in flags.values() if v)
        return round(hit / total, 2)


# ── 手动运行 ──
if __name__ == "__main__":
    parser = NLPParser()
    parser.parse_pending()

# ============================================
# 云端爬虫 — 使用 cookie 直接发 HTTP 请求，在 GitHub Actions / Render 上运行
# ============================================
import json
import os
import re
import time
import yaml
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import PostRaw
from backend.paths import resolve_path

# 从环境变量读取 cookie
WEIBO_COOKIE = os.environ.get("WEIBO_COOKIE", "")


def load_config():
    with open(resolve_path("config.yaml"), "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

import httpx

class WeiboSpider:
    """云端微博爬虫 — 用 httpx + cookie 直接调搜索 API"""

    def __init__(self, db: Optional[Session] = None):
        self.db = db or SessionLocal()
        self.config = load_config()
        self.client = httpx.Client(
            headers={
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
                "Cookie": WEIBO_COOKIE,
                "Referer": "https://m.weibo.cn/",
                "X-Requested-With": "XMLHttpRequest",
            },
            timeout=30,
            follow_redirects=True,
        )

    def search(self, keyword: str, max_pages: int = 3) -> int:
        saved = 0
        for pg in range(1, max_pages + 1):
            containerid = f"100103type=1&q={keyword}"
            url = (
                f"https://m.weibo.cn/api/container/getIndex"
                f"?containerid={containerid}&page={pg}"
            )
            try:
                resp = self.client.get(url)
                data = resp.json()
            except Exception as e:
                print(f"  [{keyword}] request failed: {e}")
                break

            cards = data.get("data", {}).get("cards", []) if isinstance(data, dict) else []
            page_count = 0
            for card in cards:
                mblogs = []
                self._collect_mblogs(card, mblogs)
                for mblog in mblogs:
                    tid = str(mblog.get("id", "") or mblog.get("mid", "") or "")
                    if not tid:
                        continue
                    if self.db.query(PostRaw).filter(
                        PostRaw.platform == "weibo",
                        PostRaw.post_id == tid,
                    ).first():
                        continue
                    text = self._clean_html(mblog.get("text", "") or "")
                    user = mblog.get("user", {}) or {}
                    author = user.get("screen_name", "") if isinstance(user, dict) else ""
                    images = []
                    for pic in mblog.get("pics") or []:
                        if isinstance(pic, dict):
                            u = pic.get("large", {}).get("url") or pic.get("url", "")
                            if u:
                                images.append(u)
                    ct = mblog.get("created_at", "")
                    try:
                        created = datetime.fromisoformat(ct.replace(" +0800", "")) if ct else datetime.utcnow()
                    except:
                        created = datetime.utcnow()

                    self.db.add(PostRaw(
                        platform="weibo",
                        post_id=tid,
                        author_name=author or "",
                        author_uid="",
                        title=text[:700] if text else "",
                        content=text,
                        images=images,
                        video_url="",
                        post_url=f"https://m.weibo.cn/detail/{tid}",
                        post_time=created,
                        raw_json=mblog,
                    ))
                    page_count += 1
                if page_count and page_count % 10 == 0:
                    self.db.commit()
            if page_count:
                self.db.commit()
            saved += page_count
            print(f"  [{keyword}] page {pg}: {page_count} items")
            if page_count == 0:
                break
            time.sleep(2)

        return saved

    def run_all(self, keywords: list[str] = None, max_pages: int = None) -> dict:
        if keywords is None:
            keywords = self.config["crawler"]["search_keywords"]
        if max_pages is None:
            max_pages = self.config["crawler"]["weibo"]["max_pages_per_keyword"]
        result = {}
        for i, kw in enumerate(keywords):
            print(f"[{i+1}/{len(keywords)}] {kw}")
            count = self.search(kw, max_pages=max_pages)
            result[kw] = count
            time.sleep(2)
        total = sum(result.values())
        print(f"Done: {total} new posts")
        return result

    def close(self):
        self.client.close()
        try:
            self.db.close()
        except:
            pass

    @staticmethod
    def _collect_mblogs(obj, result):
        if isinstance(obj, dict):
            if obj.get("mblog"):
                result.append(obj["mblog"])
            for v in obj.values():
                WeiboSpider._collect_mblogs(v, result)
        elif isinstance(obj, list):
            for item in obj:
                WeiboSpider._collect_mblogs(item, result)

    @staticmethod
    def _clean_html(text: str) -> str:
        text = re.sub(r"<br\s*/?>", "\n", text)
        text = re.sub(r'<img\s+[^>]*alt="([^"]*)"[^>]*>', r'\1', text)
        text = re.sub(r"<a\s[^>]*>", "", text)
        text = re.sub(r"</a>", "", text)
        text = re.sub(r"<span[^>]*>", "", text)
        text = re.sub(r"</span>", "", text)
        text = re.sub(r"<[^>]+>", "", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = text.rstrip()
        if text.endswith('...全文'):
            text = text[:-4]
        elif text.endswith('全文'):
            text = text[:-2]
        return text.strip().rstrip('...').rstrip()


if __name__ == "__main__":
    spider = WeiboSpider()
    try:
        spider.run_all()
    finally:
        spider.close()

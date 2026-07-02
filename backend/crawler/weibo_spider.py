# ============================================
# 爬虫核心 — 浏览器内拦截 API 响应获取搜索结果
# 使用方式：
#   1. 双击 D:\animerch\data\start_chrome_debug.bat 启动专用 Chrome
#   2. 在专用 Chrome 中完成微博验证码
#   3. 在审核后台点"手动抓取"
# ============================================
import json
import os
import re
import time
from datetime import datetime
from typing import Optional

import yaml
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models import PostRaw
from backend.paths import resolve_path

CDP_URL = "http://127.0.0.1:9223"


def load_config():
    with open(resolve_path("config.yaml"), "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class WeiboSpider:
    """微博搜索爬虫 — 浏览器内拦截 API 响应获取数据"""

    def __init__(self, db: Optional[Session] = None):
        self.db = db or SessionLocal()
        self.config = load_config()
        self._page = None
        self._pw = None
        self._browser = None
        self._api_result = None  # 存储拦截到的 API 响应

    def _handle_response(self, response):
        """拦截 API 响应"""
        try:
            if "container/getIndex" in response.url and "100103type" in response.url:
                self._api_result = response.json()
        except:
            pass

    def _ensure_page(self, silent: bool = False):
        """连接 Chrome CDP"""
        if self._page is not None:
            try:
                self._page.title()
                return
            except:
                self._page = None

        from playwright.sync_api import sync_playwright

        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.connect_over_cdp(CDP_URL)

        ctx = self._browser.contexts[0] if self._browser.contexts else self._browser.new_context()

        for pg in ctx.pages:
            try:
                if "weibo" in pg.url:
                    self._page = pg
                    self._page.on("response", self._handle_response)
                    return
            except:
                pass

        self._page = ctx.new_page()
        self._page.on("response", self._handle_response)
        self._page.goto("https://m.weibo.cn/", timeout=30000, wait_until="domcontentloaded")
        time.sleep(2)

    def _wait_verify(self):
        """等待用户在浏览器手动过验证码"""
        print()
        print("  >>> 微博要验证码，请在 Chrome 窗口滑动验证 <<<")
        for i in range(180):
            time.sleep(1)
            try:
                t = self._page.title()
                if "验证" not in t and "captcha" not in self._page.url.lower():
                    print("  [OK] 验证通过")
                    time.sleep(2)
                    return True
            except:
                pass
            if i == 59:
                print("  ...1分钟了，还在等验证...")
        print("  [SKIP] 超时，跳过")
        return False

    def search(self, keyword: str, max_pages: int = 3) -> int:
        import urllib.parse

        saved = 0
        for pg in range(1, max_pages + 1):
            containerid = f"100103type%3D1%26q%3D{urllib.parse.quote(keyword)}"
            url = f"https://m.weibo.cn/search?containerid={containerid}&page={pg}"

            self._ensure_page()
            self._api_result = None

            print(f"  [{keyword}] p{pg} ", end="", flush=True)

            try:
                self._page.goto(url, timeout=30000, wait_until="networkidle")
            except:
                print("加载失败")
                continue

            time.sleep(2)

            # 验证码检测
            title = self._page.title()
            if "验证" in title or "captcha" in self._page.url.lower():
                if not self._wait_verify():
                    break
                # 验证后重试
                self._api_result = None
                self._page.goto(url, timeout=30000, wait_until="networkidle")
                time.sleep(2)

            # 从拦截的 API 结果中提取帖子
            data = self._api_result
            if not data or data.get("ok") != 1:
                # 回退：从 DOM 提取 script 数据
                data = self._fallback_extract()
                print(f" API拦截失败，回退: {data is not None}", end="", flush=True)

            cards = data.get("data", {}).get("cards", []) if data else []
            page_count = 0
            print(f" API_raw:{len(cards)}cards ", end="", flush=True)

            for card in cards:
                # 收集所有 mblog（递归遍历卡片树）
                mblogs = []
                self._collect_mblogs(card, mblogs)

                for mblog in mblogs:
                    tid = str(mblog.get("id", "") or mblog.get("mid", "") or "")
                    if not tid:
                        continue

                    # 去重
                    if self.db.query(PostRaw).filter(
                        PostRaw.platform == "weibo",
                        PostRaw.post_id == tid,
                    ).first():
                        continue

                    text = WeiboSpider._clean_html(mblog.get("text", "") or "")

                    # 提取作者
                    user = mblog.get("user", {}) or {}
                    author = user.get("screen_name", "") if isinstance(user, dict) else ""

                    # 图片
                    images = []
                    for pic in (mblog.get("pics") or []):
                        if isinstance(pic, dict):
                            u = pic.get("large", {}).get("url") or pic.get("url", "")
                            if u:
                                images.append(u)

                    # 时间
                    ct = mblog.get("created_at", "")
                    try:
                        created = datetime.fromisoformat(str(ct).replace(" +0800", "")) if ct else datetime.utcnow()
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

                # 每处理一个card就commit一次
                if page_count and page_count % 10 == 0:
                    self.db.commit()

            if page_count:
                self.db.commit()
            saved += page_count
            print(f"{page_count}条(总{saved})")

            if page_count == 0:
                break
            if pg < max_pages:
                time.sleep(2)

        return saved

    def _fallback_extract(self) -> Optional[dict]:
        """DOM 回退提取"""
        try:
            data = self._page.evaluate("""() => {
                for (const s of document.querySelectorAll('script')) {
                    const t = s.textContent || '';
                    const i = t.indexOf('"card_type"');
                    if (i < 0) continue;
                    // 往后找完整 JSON
                    for (let j = i; j > 0; j--) {
                        if (t[j] === '{') {
                            let d = 1, end = j + 1;
                            while (d > 0 && end < t.length) {
                                if (t[end] === '{') d++;
                                else if (t[end] === '}') d--;
                                end++;
                            }
                            try { return JSON.parse(t.substring(j, end)); } catch(e) {}
                            break;
                        }
                    }
                }
                return null;
            }""")
            if data and isinstance(data, dict):
                return data
        except:
            pass
        return None

    @staticmethod
    def _collect_mblogs(obj, result):
        """递归收集卡片中所有 mblog"""
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
        # 先替换 <br> 为换行
        text = re.sub(r"<br\s*/?>", "\n", text)
        # 提取 img alt 文字（表情[xxx]）
        text = re.sub(r'<img\s+[^>]*alt="([^"]*)"[^>]*>', r'\1', text)
        # 去掉 <a href=...> 标签但保留文本（链接中的文字是正文的一部分）
        text = re.sub(r"<a\s[^>]*>", "", text)
        text = re.sub(r"</a>", "", text)
        # 去掉 <span> 标签但保留文本
        text = re.sub(r"<span[^>]*>", "", text)
        text = re.sub(r"</span>", "", text)
        # 去掉剩余的 HTML 标签
        text = re.sub(r"<[^>]+>", "", text)
        # 合并多余空白行
        text = re.sub(r"\n{3,}", "\n\n", text)
        # 去掉微博短文末尾的展开提示
        text = text.rstrip()
        if text.endswith('...全文'):
            text = text[:-4]
        elif text.endswith('全文'):
            text = text[:-2]
        text = text.rstrip().rstrip('...').rstrip()
        return text.strip()

    def _fetch_full_text(self, post_id: str) -> Optional[str]:
        """通过 statuses/show API 获取帖子的完整文本"""
        try:
            data = self._page.evaluate(f"""
                async () => {{
                    const r = await fetch('/api/statuses/show?id={post_id}',
                        {{ headers: {{ 'X-Requested-With': 'XMLHttpRequest' }} }}
                    );
                    const d = await r.json();
                    return d;
                }}
            """)
            if isinstance(data, dict) and data.get('ok') == 1:
                full = data.get('data', {}).get('text', '')
                if full:
                    return self._clean_html(full)
        except Exception as e:
            print(f"  [DEBUG] 展开全文失败({post_id}): {e}")
        return None

    def run_all(self, keywords: list[str] = None, max_pages: int = None) -> dict:
        if keywords is None:
            keywords = self.config["crawler"]["search_keywords"]
        if max_pages is None:
            max_pages = self.config["crawler"]["weibo"]["max_pages_per_keyword"]

        result = {}
        total = len(keywords)
        for i, kw in enumerate(keywords, 1):
            print(f"\n[{i}/{total}] {kw}")
            count = self.search(kw, max_pages=max_pages)
            result[kw] = count
            time.sleep(2)

        total_saved = sum(result.values())
        print(f"\n== 完成! 新入库 {total_saved} 条 ==")
        return result

    def close(self):
        self._page = None
        if self._pw:
            try:
                self._pw.stop()
            except:
                pass
        self._pw = None
        self._browser = None
        try:
            self.db.close()
        except:
            pass

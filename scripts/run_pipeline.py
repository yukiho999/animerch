#!/usr/bin/env python
# ============================================
# 手动运行脚本: 完整采集+解析流水线
# 用法: python scripts/run_pipeline.py
# ============================================
import sys
import os
import io

# 强制 UTF-8 输出，解决 Windows GBK 终端乱码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.crawler.weibo_spider import WeiboSpider
from backend.nlp.parser import NLPParser


def main():
    print("=" * 50)
    print("  二次元周边聚合 -- 采集+解析流水线")
    print("=" * 50)

    # Step 1: 爬取微博
    print("\n[1/2] 开始微博搜索...")
    spider = WeiboSpider()
    try:
        result = spider.run_all(max_pages=3)
        total = sum(result.values())
        print(f"  -> 新入库 {total} 条帖子")
    finally:
        spider.close()

    # Step 2: NLP 解析
    print("\n[2/2] NLP 解析...")
    parser = NLPParser()
    count = parser.parse_pending()
    print(f"  -> 解析完成 {count} 条")

    print("\n== 流水线完成！")
    print("  打开 http://localhost:8000/admin/review 进行审核")
    print("  审核通过后，前端即可展示数据")


if __name__ == "__main__":
    main()

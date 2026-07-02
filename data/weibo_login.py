
from playwright.sync_api import sync_playwright
import json, os, time

storage_path = 'D:/animerch/data/weibo_storage.json'
print(f'保存路径: {storage_path}')

os.makedirs('D:/animerch/data', exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Linux; Android 13; SM-G9980) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.135 Mobile Safari/537.36',
        viewport={'width': 393, 'height': 851},
        locale='zh-CN',
        storage_state=storage_path if os.path.exists(storage_path) else None,
    )
    page = context.new_page()
    
    # 如果已有登录态，直接保存
    page.goto('https://m.weibo.cn/', timeout=30000, wait_until='networkidle')
    time.sleep(2)
    cookies = context.cookies()
    has_login = any(c.get('name') == 'SUB' for c in cookies)
    
    if has_login:
        print('已有登录态，无需重新登录')
    else:
        print('请在弹出的浏览器中登录微博...')
        print('打开登录页面...')
        page.goto('https://passport.weibo.cn/signin/login?entry=mweibo', timeout=30000, wait_until='networkidle')
        print('请在浏览器中完成登录，程序会等待60秒...')
        time.sleep(60)
        # 登录后刷新
        page.goto('https://m.weibo.cn/', timeout=30000, wait_until='networkidle')
        time.sleep(2)
    
    # 保存 storage state
    context.storage_state(path=storage_path)
    cookies = context.cookies()
    has_sub = any(c.get('name') == 'SUB' for c in cookies)
    print(f'登录状态: {"已登录 ✓" if has_sub else "未登录 ✗"}')
    print(f'Cookie 已保存到 {storage_path}')
    browser.close()

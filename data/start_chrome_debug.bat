@echo off
REM 为爬虫启动专用的 Chrome 远程调试实例
REM 这个实例使用独立的配置文件，不会影响你正在使用的 Chrome

set CHROME_DIR=D:\animerch\data\chrome_profile
if not exist "%CHROME_DIR%" mkdir "%CHROME_DIR%"

REM 先确保没有占用 9223 端口的旧进程
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :9223') do taskkill /F /PID %%a 2>nul

REM 启动 Chrome（使用独立 profile + 远程调试端口）
start "AnimeSpider" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9223 --no-first-run --no-default-browser-check --user-data-dir="%CHROME_DIR%" --disable-blink-features=AutomationControlled "https://m.weibo.cn/"

echo Chrome 已启动，请在浏览器中登录微博
echo 登录后爬虫将复用此浏览器的已验证会话

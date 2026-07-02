# 🌸 周边聚合 — 二次元周边信息平台

聚合国内社交媒体平台上官方发布的二次元周边（动漫/小说/游戏 IP 授权制品）发行通知，提取结构化信息并展示。

**当前 MVP**：微博单平台 + NLP 自动解析 + 人工审核 + Web 展示。

## 技术栈

| 层 | 技术 |
|---|------|
| 前端 | React 18 + TypeScript + Tailwind CSS + Framer Motion |
| 后端 | Python FastAPI |
| 数据库 | MySQL 8.0 |
| 爬虫 | httpx (微博移动端 API) |
| NLP | jieba + 正则规则 |

## 项目结构

```
animerch/
├── backend/           # FastAPI 后端
│   ├── main.py        # 入口
│   ├── database.py    # 数据库连接
│   ├── models.py      # ORM 模型
│   ├── schemas.py     # Pydantic 模型
│   ├── routers/       # API 路由 (ip / merch / admin)
│   ├── crawler/       # 微博爬虫
│   ├── nlp/           # NLP 解析器 (IP/工艺/价格/日期)
│   └── templates/     # 审核后台 HTML
├── frontend/          # React 前端
│   └── src/
│       ├── pages/     # 页面组件
│       ├── components/# 通用组件
│       ├── api/       # API 客户端
│       └── types/     # TypeScript 类型
├── data/              # 映射数据 (IP别名/工艺标签)
├── scripts/           # SQL 脚本 + 运行脚本
├── config.yaml        # 配置文件
└── docker-compose.yml
```

## 快速开始

### 1. 启动数据库

```bash
docker compose up -d mysql
```

### 2. 安装依赖

```bash
# 后端
pip install -r requirements.txt

# 前端
cd frontend && npm install
```

### 3. 配置

编辑 `config.yaml`，修改数据库密码等配置。

### 4. 初始化数据

```bash
# 建表 + 种子数据（Docker 启动时自动执行）
# 或手动:
docker compose exec mysql mysql -uroot -panimerch123 animerch < scripts/init_db.sql
docker compose exec mysql mysql -uroot -panimerch123 animerch < scripts/seed_data.sql
```

### 5. 启动后端

```bash
cd backend
uvicorn main:app --reload --port 8000
```

### 6. 启动前端

```bash
cd frontend
npm run dev
```

### 7. 运行采集流水线

```bash
python scripts/run_pipeline.py
```

### 8. 审核数据

打开 `http://localhost:8000/admin/review`，逐条审核 NLP 解析结果。

审核通过后，数据自动出现在前端页面。

## API 文档

启动后端后访问 `http://localhost:8000/docs`

## 数据流

```
微博搜索 → 爬虫抓取 → post_raw 表
                        ↓
                   NLP 解析器
                        ↓
                 merch_post 表（待审核）
                        ↓
                  人工审核后台
                  ↙    ↓    ↘
              确认   编辑   拒绝
                ↓     ↓     ↓
            入库    修改   丢弃
                ↘    ↙
            merch 正式表
                  ↓
            前端 API 展示
```

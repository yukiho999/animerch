# ============================================
# 数据库连接
# ============================================
import os
import yaml

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 优先使用环境变量 DATABASE_URL（Render / TiDB Cloud 部署用）
DB_URL = os.environ.get("DATABASE_URL")
if DB_URL:
    # TiDB Cloud 连接 URL 可能需要 SSL 参数
    DATABASE_URL = DB_URL
else:
    # 读取配置 — 从项目根目录查找（本地开发用）
    _config_path = os.environ.get("CONFIG_PATH", "config.yaml")
    if not os.path.isabs(_config_path):
        _current = os.path.dirname(os.path.abspath(__file__))
        for _ in range(5):
            _candidate = os.path.join(_current, _config_path)
            if os.path.exists(_candidate):
                _config_path = _candidate
                break
            _current = os.path.dirname(_current)
    with open(_config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    db_cfg = config["database"]
    DB_PASSWORD = os.environ.get("DB_PASSWORD", db_cfg["password"])

    DATABASE_URL = (
        f"mysql+pymysql://{db_cfg['user']}:{DB_PASSWORD}"
        f"@{db_cfg['host']}:{db_cfg['port']}/{db_cfg['database']}"
        f"?charset={db_cfg['charset']}"
    )

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI 依赖注入：获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

"""将本地 MySQL 数据导入 TiDB Cloud"""
import pymysql

TIDB_HOST = "gateway01.ap-northeast-1.prod.aws.tidbcloud.com"
TIDB_PORT = 4000
TIDB_USER = "2vdrq8VoBxL4Rkw.root"
TIDB_PASSWORD = "0GiFk1kkczwc5fli"
TIDB_DB = "test"

local = pymysql.connect(
    host='localhost', port=3306, user='root', password='root',
    database='animerch', charset='utf8mb4'
)
lc = local.cursor()

tidb = pymysql.connect(
    host=TIDB_HOST, port=TIDB_PORT, user=TIDB_USER, password=TIDB_PASSWORD,
    database=TIDB_DB, charset='utf8mb4',
    ssl={'verify_cert': True, 'verify_identity': True}
)
tc = tidb.cursor()

# 手动建表（逐张）
create_sqls = [
    """CREATE TABLE IF NOT EXISTS ip (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(200) NOT NULL,
        aliases JSON,
        category VARCHAR(50),
        cover_url VARCHAR(1000),
        description TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY uk_name (name)
    )""",
    """CREATE TABLE IF NOT EXISTS craft_tag (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(50) NOT NULL UNIQUE
    )""",
    """CREATE TABLE IF NOT EXISTS merch (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        ip_id BIGINT NOT NULL,
        name VARCHAR(500) NOT NULL,
        category VARCHAR(50),
        official_price DECIMAL(10,2),
        release_date DATE,
        release_method VARCHAR(50) DEFAULT '未知',
        is_discontinued TINYINT(1) DEFAULT 0,
        attributes JSON,
        image_url VARCHAR(2000),
        source_platform VARCHAR(50) DEFAULT 'weibo',
        source_url VARCHAR(2000),
        original_post_id BIGINT,
        status VARCHAR(50) DEFAULT 'active',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_ip (ip_id),
        INDEX idx_category (category),
        INDEX idx_release_date (release_date),
        INDEX idx_is_discontinued (is_discontinued),
        INDEX idx_status (status)
    )""",
    """CREATE TABLE IF NOT EXISTS merch_craft (
        merch_id BIGINT NOT NULL,
        craft_id BIGINT NOT NULL,
        PRIMARY KEY (merch_id, craft_id)
    )""",
]

for s in create_sqls:
    try:
        tc.execute(s)
        print(f"OK: {s.split()[2]} created")
    except Exception as e:
        print(f"SKIP: {e}")

tc.execute("SET FOREIGN_KEY_CHECKS = 0")
tidb.commit()

tables_in_order = ['ip', 'craft_tag', 'merch', 'merch_craft']
for table in tables_in_order:
    lc.execute(f'SELECT * FROM {table}')
    rows = lc.fetchall()
    cols = [d[0] for d in lc.description]
    if not rows:
        print(f"{table}: 0 rows, skip")
        continue
    ph = ','.join(['%s'] * len(cols))
    sqli = f"REPLACE INTO {table} ({','.join(cols)}) VALUES ({ph})"
    ok, fail = 0, 0
    for row in rows:
        try:
            tc.execute(sqli, row)
            ok += 1
        except Exception as e:
            fail += 1
            if fail <= 2:
                print(f"  ERR: {e}")
    tidb.commit()
    print(f"{table}: {ok} ok, {fail} fail")

tc.execute("SET FOREIGN_KEY_CHECKS = 1")
tidb.commit()

tc.close(); tidb.close()
lc.close(); local.close()
print("\nAll done!")

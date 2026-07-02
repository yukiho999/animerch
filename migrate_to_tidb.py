"""导出本地 MySQL 数据为 SQL INSERT 语句，用于导入 TiDB Cloud"""
import pymysql

conn = pymysql.connect(
    host='localhost', port=3306, user='root', password='root',
    database='animerch', charset='utf8mb4'
)
cursor = conn.cursor()

# 替换为你 TiDB Cloud 的连接信息
# 在 TiDB Cloud → Connect → Standard Connection 里获取
TIDB_HOST = "gw.us-east-1.sql.tidbcloud.com"  # 改成你的
TIDB_PORT = 4000
TIDB_USER = "你的用户名"  # 改成你的
TIDB_PASSWORD = "你的密码"  # 改成你的

tables = ['ip', 'merch', 'craft_tag', 'merch_craft']

for table in tables:
    # 读本地数据
    cursor.execute(f"SELECT * FROM {table}")
    rows = cursor.fetchall()
    cols = [d[0] for d in cursor.description]

    if not rows:
        print(f"-- {table}: 空表，跳过")
        continue

    print(f"-- {table}: {len(rows)} 条")

    # 连接 TiDB Cloud
    tidb = pymysql.connect(
        host=TIDB_HOST, port=TIDB_PORT, user=TIDB_USER, password=TIDB_PASSWORD,
        database='animerch', charset='utf8mb4',
        ssl={'ssl': {'ca': None}}  # TiDB Cloud 需要 SSL
    )
    tc = tidb.cursor()

    # 逐条插入
    placeholders = ','.join(['%s'] * len(cols))
    sql = f"INSERT INTO {table} ({','.join(cols)}) VALUES ({placeholders})"
    for row in rows:
        try:
            tc.execute(sql, row)
        except Exception as e:
            print(f"  SKIP: {e}")
    tidb.commit()

    tc.close()
    tidb.close()
    print(f"  ✓ 完成")

cursor.close()
conn.close()
print("\n全部完成！")

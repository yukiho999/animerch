"""导出本地 MySQL 数据为 SQL 文件，用于导入 TiDB Cloud"""
import pymysql, json

conn = pymysql.connect(
    host='localhost', port=3306, user='root', password='root',
    database='animerch', charset='utf8mb4'
)
c = conn.cursor()

tables = ['craft_tag', 'ip', 'merch', 'merch_craft']

with open('data_dump.sql', 'w', encoding='utf8') as f:
    for table in tables:
        c.execute(f'SELECT * FROM {table}')
        rows = c.fetchall()
        cols = [d[0] for d in c.description]
        f.write(f'-- Table: {table} ({len(rows)} rows)\n')
        for row in rows:
            vals = []
            for v in row:
                if v is None:
                    vals.append('NULL')
                elif isinstance(v, (list, dict)):
                    escaped = json.dumps(v, ensure_ascii=False).replace("'", "\\'")
                    vals.append(f"'{escaped}'")
                elif isinstance(v, str):
                    escaped = v.replace("\\", "\\\\").replace("'", "\\'")
                    vals.append(f"'{escaped}'")
                else:
                    vals.append(str(v))
            f.write(f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join(vals)});\n")
        f.write('\n')

count = sum(1 for _ in open("data_dump.sql", encoding="utf8"))
print(f'OK: {count} lines')

c.close(); conn.close()

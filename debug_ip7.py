from backend.database import SessionLocal
from backend.models import Merch
from sqlalchemy import desc

db = SessionLocal()
try:
    rows = db.query(Merch).filter(Merch.ip_id == 7, Merch.status == 'active').order_by(desc(Merch.release_date)).all()
    print(f"Total: {len(rows)}")
    for r in rows:
        name = (r.name or 'NULL')[:50]
        price = r.official_price
        attrs = str(r.attributes)[:100] if r.attributes else 'NULL'
        img = str(r.image_url)[:60] if r.image_url else 'NULL'
        method = r.release_method or 'NULL'
        print(f"id={r.id} | name={name} | price={price} | attrs={attrs} | img={img} | method={method}")
except Exception as e:
    import traceback
    traceback.print_exc()
finally:
    db.close()

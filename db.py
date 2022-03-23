from sqlalchemy import create_engine
from sqlalchemy.sql import text 
import datetime

engine = create_engine("mysql://admin:admin12345@database-1.ctb0mvbckgia.ap-northeast-2.rds.amazonaws.com:3306/ids", echo=True, future=True)

def add(json):
    txt = '''Adding record'''
    with engine.connect() as conn:
        conn.execute(
            text("INSERT INTO ids VALUE (:x)"),
            [{"x":json}]
        )
        conn.commit()
    return txt

def view():
    with engine.connect() as conn:
        return conn.execute(text("SELECT json FROM ids"))
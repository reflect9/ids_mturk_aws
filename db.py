from sqlalchemy import create_engine
from sqlalchemy.sql import text 
import datetime, json

engine = create_engine("mysql+pymysql://admin:admin12345@database-1.ctb0mvbckgia.ap-northeast-2.rds.amazonaws.com:3306/ids", echo=True, future=True)

def add(data):
    txt = '''Adding record'''
    with engine.connect() as conn:
        conn.execute(
            text("INSERT INTO ids VALUE (:PersonID,:Timestamp,:JSON)"),
            [{
                "PersonID":data["PersonID"],
                "Timestamp":datetime.datetime.now(),
                "JSON":json.dumps(data["json"])
            }]
        )
        conn.commit()
    return txt

def view():
    with engine.connect() as conn:
        return conn.execute(text("SELECT * FROM ids"))

def reset():
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM ids"))
        conn.commit()

def dropTable():
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS ids"))
        conn.commit()

def createTable():
    with engine.connect() as conn:
        conn.execute(text("CREATE TABLE ids (PersonID varchar(255), datetime Timestamp, json JSON)"))
        conn.commit()

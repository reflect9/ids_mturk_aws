from curses import meta
from sqlalchemy import create_engine
from sqlalchemy.schema import MetaData
from sqlalchemy.sql import text
import datetime, json

engine = create_engine("mysql+pymysql://admin:admin12345@database-1.ctb0mvbckgia.ap-northeast-2.rds.amazonaws.com:3306/ids", echo=True, future=True)

def add(data):
    txt = '''Adding record'''
    with engine.connect() as conn:
        conn.execute(
            text("INSERT INTO ids VALUE (:PersonID, :CompletionCode, :Timestamp,:JSON)"),
            [{
                "PersonID":data["PersonID"],
                "CompletionCode":data["CompletionCode"],
                "Timestamp":datetime.datetime.now(),
                "JSON":json.dumps(data["json"])
            }]
        )
        conn.commit()
    return txt

def view():
    with engine.connect() as conn:
        # PATTERN 1. GETTING COLUMN NAMES
        # return conn.execute(text("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = Database() AND TABLE_NAME = 'ids'"))
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
        conn.execute(text("CREATE TABLE ids (PersonID varchar(255), CompletionCode varchar(255), Timestamp datetime, json JSON)"))
        conn.commit()

def myOperation():
    with engine.connect() as conn:
        conn.execute(text(""))
        conn.commit()

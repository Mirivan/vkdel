from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from sqlalchemy import Column, Integer, String, UnicodeText

from config import DB_URI

from . import LOGS

def start() -> scoped_session:
    engine = create_engine(DB_URI)
    BASE.metadata.bind = engine
    BASE.metadata.create_all(engine)
    return scoped_session(sessionmaker(bind=engine, autoflush=False))

try:
    BASE = declarative_base()
    SESSION = start()
except AttributeError as e:
    LOGS.info(
        "DB_URI is not configured. Features depending on the database might have issues."
    )
    LOGS.info(str(e))

class Database(BASE):
    __tablename__ = "database"
    vk_mid = Column(String, primary_key=True)
    tg_mid = Column(String, primary_key=True)

    def __init__(self, vk_mid, tg_mid):
        self.vk_mid = str(vk_mid)
        self.tg_mid = str(tg_mid)

Database.__table__.create(checkfirst=True)

def get_vk(vk_mid):
    try:
        return SESSION.query(Database).get(str(vk_mid))
    finally:
        SESSION.close()

def get_tg(tg_mid):
    try:
        return SESSION.query(Database).get(str(tg_mid))
    finally:
        SESSION.close()

def reg_reply(vk_mid, tg_mid):
    adder = Database(str(vk_mid), str(tg_mid))
    SESSION.add(adder)
    SESSION.commit()

def unreg_reply(tg_mid):
    rem = SESSION.query(Database).get(str(tg_mid))
    SESSION.delete(rem)
    SESSION.commit()

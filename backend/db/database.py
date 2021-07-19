from sqlalchemy import Column, String

from backend.db.config import Base, engine



async def dbstartup():
    # create db tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all) # only do this in testing lol
        await conn.run_sync(Base.metadata.create_all)


class User(Base):
    __tablename__ = 'UserTable'
    userid = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    pubkey = Column(String, nullable=False)


class Message(Base):
    __tablename__ = 'MessageTable'
    userid = Column(String, primary_key=True)
    msgid = Column(String, primary_key=True)
    data = Column(String, nullable=False)
    


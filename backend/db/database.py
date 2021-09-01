import asyncio
import logging

from sqlalchemy import Column, String, Integer

from backend.db.config import Base, engine
from backend.asyncrun import run


class User(Base):
    __tablename__ = 'UserTable'
    userid = Column(String, primary_key=True)
    pubkey = Column(String, nullable=False)


class Message(Base):
    __tablename__ = 'MessageTable'
    messageid = Column(String, primary_key=True)
    fromuserid = Column(String)
    touserid = Column(String)
    data = Column(String, nullable=False)
    creation_time = Column(Integer, nullable=False)
    

class DBManager:
    def __init__(self, dbsesh) -> None:
        self.dbsesh = dbsesh
        self.valid = False
        run(self.dbstartup())

    async def dbstartup(self):
        # create db tables
        logging.debug("Created db if not existant")
        async with engine.begin() as conn:
            # await conn.run_sync(Base.metadata.drop_all) # only do this in testing lol
            await conn.run_sync(Base.metadata.create_all)

        self.valid = True

    def waitfordb(func):
        async def f(self, *args, **kwargs):
            while not self.valid:
                await asyncio.sleep(.2)
            return await func(self, *args, **kwargs)
        return f

    @waitfordb
    async def add(self, *args):
        async with self.dbsesh() as session:
            session.add_all(args)
            await session.commit()

    @waitfordb
    async def execute(self, command):  # TODO: filter out and secure data to prevent sql injection
        async with self.dbsesh() as session:
                async with session.begin():
                    ret = await session.execute(command)
                    await session.commit()
                    return ret

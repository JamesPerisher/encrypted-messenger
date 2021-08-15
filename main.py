from backend.node import *
from backend.packet import *
from backend.db.database import *
from app.usersession import Session
import asyncio

from backend.db.config import *


SESSION_FILE = "userdata/session.json"


async def server():
    db = DBManager(async_session)
    authnode = Authority(10, db, AUTHORITIES)
    return authnode.start()

async def client():
    from app.main import Main

    clinode = Client(AUTHORITIES)
    
    sesh = Session.from_file(SESSION_FILE) # realy need to store this in secure place idk yet
    await sesh.save()
    gui =  Main(clinode, sesh)

    return gui.async_run(async_lib='asyncio')

async def fullstack():
    return asyncio.gather(await server(), await client())




def runapp(coroutine):
    loop = asyncio.get_event_loop()
    approutine = loop.run_until_complete(coroutine)
    try:
        loop.run_until_complete(approutine)
    except RuntimeError:
        pass # program was killed or crashed (idk which one) its eather ur fault or mine I blame you
    loop.close()


if __name__ == "__main__":
    # print(runapp(fullstack()))
    # print(runapp(server()))
    print(runapp(client()))



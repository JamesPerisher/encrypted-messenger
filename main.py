from backend.node import *
from backend.packet import *
from backend.db.database import *
from backend.asyncrun import asynclambda
from app.usersession import Session
import asyncio

from backend.db.config import *


SESSION_FILE = "userdata/session.json"
SESSION_CACHE = "userdata/cache.json"

async def server(interactive):
    db = DBManager(async_session)
    authnode = Authority(10, db, AUTHORITIES)
    return asyncio.gather(authnode.start(), authnode.interactive() if interactive else asynclambda(lambda x: x))

async def client():
    from app.main import Main


    clinode = Client(AUTHORITIES)
    
    cache = CacheProxy.from_file(clinode, SESSION_CACHE)
    sesh = Session.from_file(SESSION_FILE)
    clinode.cache = cache


    await sesh.save()
    gui =  Main(clinode, sesh)

    return gui.async_run(async_lib='asyncio')

async def fullstack(interactive):
    return asyncio.gather(await server(interactive), await client())




def runapp(coroutine):
    loop = asyncio.get_event_loop()
    approutine = loop.run_until_complete(coroutine)
    try:
        loop.run_until_complete(approutine)
    except RuntimeError:
        pass # program was killed or crashed (idk which one) its eather ur fault or mine I blame you
    loop.close()


if __name__ == "__main__":
    print(runapp(fullstack(False)))
    # print(runapp(server()))
    # print(runapp(client()))



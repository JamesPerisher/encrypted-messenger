from backend.clienthandler import *
from app.usersession import Session

from globalconfig import SESSION_FILE, SESSION_CACHE


async def client():
    from app.main import Main


    clinode = Client(AUTHORITIES)
    
    cache = CacheProxy.from_file(clinode, SESSION_CACHE)
    sesh = Session.from_file(SESSION_FILE)
    clinode.cache = cache


    await sesh.save()
    gui =  Main(clinode, sesh)

    return gui.async_run(async_lib='asyncio')


def runapp(coroutine):
    loop = asyncio.get_event_loop()
    approutine = loop.run_until_complete(coroutine)
    try:
        loop.run_until_complete(approutine)
    except RuntimeError:
        pass # program was killed or crashed (idk which one) its eather ur fault or mine I blame you
    loop.close()


if __name__ == "__main__":
    print(runapp(client()))



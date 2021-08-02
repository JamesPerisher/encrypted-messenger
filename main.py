from backend.node import *
from backend.packet import *
from kivy.app import async_runTouchApp
from app.main import Main
import asyncio

from threading import Thread


if __name__ == "__main__":
    clinode = Client("idk1", "idk1", AUTHORITIES)
    gui = Main(clinode).async_run(async_lib='asyncio')
    print(gui)


    authnode = Authority("idk", "idk", AUTHORITIES, 10)
    events = asyncio.gather(authnode.start(), gui)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(events)
    # loop.close()




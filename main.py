from sqlalchemy.orm import session
from backend.node import *
from backend.packet import *
from backend.db.database import *
from backend.asyncrun import run
from app.main import Main
from app.usersession import Session
import asyncio

from backend.db.config import *




if __name__ == "__main__":
    clinode = Client("idk1", "idk1", AUTHORITIES)
    
    db = DBManager(async_session)
    sesh = Session.from_file("userdata/session.json") # realy need to store this in secure place idk yet
    run(sesh.save())

    gui = Main(clinode, sesh).async_run(async_lib='asyncio')

    authnode = Authority("idk", "idk", AUTHORITIES, 10)
    events = asyncio.gather(authnode.start(db), gui)

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(events)
    except RuntimeError:
        pass # program was killed or crashed (idk which one) its eather ur fault or mine I blame you
    loop.close()




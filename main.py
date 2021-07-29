# from backend.node import *
# from backend.packet import *
# import asyncio


# if __name__ == "__main__":
#     authnode = Authority("idk", "idk", AUTHORITIES, 10)
#     clinode = Client("idk1", "idk1", AUTHORITIES)



#     events = asyncio.gather(authnode.start(), clinode.debug())

#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(events)
#     loop.close()


from app.main import Main

Main().run()
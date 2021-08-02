import asyncio


def run(coroutine): # insert event into the event loop
    return asyncio.get_event_loop().create_task(coroutine)
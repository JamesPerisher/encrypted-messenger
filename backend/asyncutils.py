from asyncio import Event
from threading import Thread

from backend.packet import Packet



class CEvent(Event):
    def set(self):
        if self._loop is not None:
            self._loop.call_soon_threadsafe(super().set)
        else:
            super().set()


class ResetEvent(Event):
    def _set(self):
        super().set()
        self.clear()

    def set(self):
        if self._loop is not None:
            self._loop.call_soon_threadsafe(super()._set)
        else:
            super()._set()

class AsyncWrapper:
    def __init__(self, oject):
        self.object = oject
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self.object.__repr__()})>" 

class FlaggingThread(Thread):
    def __init__(self, func, event, *args, **kwargs):
        self.func = func
        self.out = None
        self.event = event
        self.args = args
        self.kwargs = kwargs
        super().__init__()

    def run(self):
        self.out = self.func(*self.args, **self.kwargs)
        self.event.set()

def threadasync(func):
    event = CEvent()
    async def wrapper(*args, **kwargs):
        thread = FlaggingThread(func, event, *args, **kwargs) # push bloking func to thread to not block asyncio loop
        thread.start()
        await event.wait() # wait for thread to finish in async way
        event.clear()
        return thread.out
    return wrapper

def isalive(func):
    async def wrapper(self, *args, **kwargs):
        await self.object.alive.wait() # doesnt trigger for some reason i think asyncio is broken fuuuuuuuck
        return await func(self, *args, **kwargs)
    return wrapper

class Asyncable:
    def __init__(self):
        self.run = None # thread where this proccess runs

    def run(self): # overwritable method to be run in a thread as async task
        pass

    async def start(self): # finishes when run is finished
        return await threadasync(self.run)()

class asyncConnection(AsyncWrapper):
    def __init__(self, object: Asyncable):
        super().__init__(object)

    def kill(self):
        self.object.kill()

    def start(self, *args, **kwargs):
        return self.object.start(*args, **kwargs)

    @isalive
    @threadasync
    def recv_packet(self):
        p = Packet.from_socket(self.object.socket)
        return p

    @isalive
    @threadasync
    def send_packet(self, packet: Packet):
        return packet.send(self.object.socket)
        
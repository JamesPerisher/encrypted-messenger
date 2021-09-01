import asyncio
import threading

def run(coroutine): # insert event into the event loop
    return asyncio.get_event_loop().create_task(coroutine)


async def asynclambda(func):
    return func()


class AsyncIterator:
    def __init__(self, seq):
        self.iter = iter(seq)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self.iter)
        except StopIteration:
            raise StopAsyncIteration


def AsyncInput(txt):
    return asyncio.to_thread(input, txt)

class InputIterator:
    def __init__(self, txt) -> None:
        self.txt = txt
    def __aiter__(self):
        return self

    async def __anext__(self):
        return await AsyncInput(self.txt)


if __name__ == "__main__":

    async def test():
        async for x in InputIterator(": "):
            print(x)

    asyncio.get_event_loop().run_until_complete(test())
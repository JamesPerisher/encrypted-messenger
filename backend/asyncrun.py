import asyncio
import functools
import contextvars

def run(coroutine): # insert event into the event loop
    return asyncio.get_event_loop().create_task(coroutine)

# asyncronously run a function when possible
def asyncrun(func):
    async def wrapper(*args, **kwargs):
        return asyncio.run_coroutine_threadsafe(func(*args, **kwargs), asyncio.get_event_loop())
    return wrapper

async def asynclambda(func):
    return func

async def to_thread(func, /, *args, **kwargs):
    loop = asyncio.get_running_loop()
    ctx = contextvars.copy_context()
    func_call = functools.partial(ctx.run, func, *args, **kwargs)
    return await loop.run_in_executor(None, func_call)

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
    return asyncio.sleep(100000000)
    return to_thread(input, txt)

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
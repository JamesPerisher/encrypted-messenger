import asyncio
import functools
import contextvars

# insert event into the event loop
def run(coroutine):
    return asyncio.get_event_loop().create_task(coroutine)

# asyncronously run a function when possible
def asyncrun(func):
    async def wrapper(*args, **kwargs):
        return asyncio.run_coroutine_threadsafe(func(*args, **kwargs), asyncio.get_event_loop())
    return wrapper

# make a lambda an async
async def asynclambda(func):
    return func

# python3.9 code for pre 3.9 versions
async def to_thread(func, /, *args, **kwargs):
    loop = asyncio.get_running_loop()
    ctx = contextvars.copy_context()
    func_call = functools.partial(ctx.run, func, *args, **kwargs)
    return await loop.run_in_executor(None, func_call)

# asyncronously iterate over syncronouse list
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

# input that return when input provided
def AsyncInput(txt):
    return asyncio.sleep(100000000)
    return to_thread(input, txt)

# asyncronouse input in an async loop
class InputIterator:
    def __init__(self, txt) -> None:
        self.txt = txt
    def __aiter__(self):
        return self

    async def __anext__(self):
        return await AsyncInput(self.txt)
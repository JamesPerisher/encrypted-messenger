from backend.basics import BaseObject

import json



class Cache(BaseObject):
    def __init__(self, prog, data=dict()) -> None:
        super().__init__(prog)
        self.data = data

    @classmethod
    def from_file(cls, prog, file):
        with open(file, "r") as f:
            try:
                return cls(json.loads(f.read()))
            except json.decoder.JSONDecodeError:
                return cls(prog.config.DEFAULT_CACHE)

    @classmethod
    def from_prog(cls, prog):
        return cls.from_file(prog, prog.config.CACHE_FILE)
    

    def add(self, key, data):
        self.data[key] = data

    async def get(self, key, passthough):
        rt = self.data.get(key, None)
        print("hmm", rt)

        if rt: return rt # return if cached

        gt = await passthough
        self.add(key, gt)

        return gt
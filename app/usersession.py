import json
import os
from backend.jsonifyer import JsonSaver

BASE_SESSION = {
    "friends": {
        # can add a default friend here like a bot or a help account idfk
    }
}

class Session(JsonSaver):
    def __init__(self, data, filepath) -> None:
        print(data, filepath)
        super().__init__(data, filepath=filepath)
        self.user = None

    def pop(self, id):
        try:
            return self.data.pop(id)
        except KeyError:
            return None

    def get(self, id, default=None):
        return self.data.get(id, default)

    def clear(self):
        self.data = BASE_SESSION.copy()

    @classmethod
    def from_file(cls, filepath):
        return super().from_file(filepath, BASE_SESSION)

    async def update(self):
        try:
            self.data["privkey"] = self.data["_privkey"]
        except KeyError:
            pass
        await self.save()
    
    async def cleanup(self):
        return await self.fixdata(self.data, True)

    async def fixdata(self, data, autoset=False): # remove tmp variables from memory as a security measure
        data = {x:data[x] for x in data if not x.startswith("_")}
        if autoset:
            self.data = data
        else:
            return data


        
import json
import os

BASE_SESSION = {
    "friends": {
        # can add a default friend here like a bot or a help account idfk
    }
}

class Session(object):
    def __init__(self, filepath, data) -> None:
        self.filepath = filepath
        self.user = None
        self.data = data

    def __getitem__(self, index):
        try:
            return self.data.__getitem__(index)
        except KeyError:
            return ""

    def __setitem__(self, index, value):
        return self.data.__setitem__(index, value)

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
        if not os.path.exists(filepath): # create file if it doesn't exist
            os.mknod(filepath)

        with open(filepath, "r") as f:
            raw = f.read()
            data = json.loads("{}" if raw.strip() == "" else raw)
            data = BASE_SESSION.copy() if data == dict() else data
            return cls(filepath, data)

    async def save(self, filepath=None):
        filepath = self.filepath if filepath == None else filepath
        tmpdata = json.dumps(await self.cleanup())
        with open(filepath, "w") as f:
            f.write(tmpdata)
        return self

    async def update(self):
        try:
            self.data["privkey"] = self.data["_privkey"]
        except KeyError:
            pass
        await self.save()

    async def cleanup(self, autoset=False): # remove tmp variables from memory as a security measure
        data = {x:self.data[x] for x in self.data if not x.startswith("_")}
        if autoset:
            self.data = data
        else:
            return data


        
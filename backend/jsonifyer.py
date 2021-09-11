import os
import json



class JsonSaver:
    def __init__(self, data, filepath="") -> None:
        self.data = data
        self.filepath = filepath

    def __getitem__(self, index):
        try:
            return self.data.__getitem__(index)
        except KeyError:
            return ""
    def __setitem__(self, index, value):
        return self.data.__setitem__(index, value)

    async def fixdata(self, data):
        return data

    def clear(self):
        self.data = dict()

    @classmethod
    def from_file(cls, filepath, default={}):
        if not os.path.exists(filepath): # create file if it doesn't exist
            os.mknod(filepath)

        with open(filepath, "r") as f:
            raw = f.read()
            data = json.loads("{}" if raw.strip() == "" else raw)
            data = default.copy() if data == dict() else data
            return cls(data, filepath)

    async def save(self, filepath=None):
        filepath = self.filepath if filepath == None else filepath
        tmpdata = json.dumps(await self.fixdata(self.data))
        with open(filepath, "w") as f:
            f.write(tmpdata)
        return self
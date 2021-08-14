import json
import os

class Session(object):
    def __init__(self, filepath, data) -> None:
        self.filepath = filepath
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
        self.data = dict()

    
    @classmethod
    def from_file(cls, filepath):
        if not os.path.exists(filepath): # create file if it doesn't exist
            os.mknod(filepath)

        with open(filepath, "r") as f:
            raw = f.read()
            data = json.loads("{}" if raw.strip() == "" else raw)
            return cls(filepath, data)

    async def save(self, filepath=None):
        filepath = self.filepath if filepath == None else filepath
        self.data = {x:self.data[x] for x in self.data if not x.startswith("_")} # remove tmp variables we dont want to save
        data = json.dumps(self.data)
        with open(filepath, "w") as f:
            f.write(data)
        return self


        
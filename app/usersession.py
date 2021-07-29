import json


class Session(object):
    def __init__(self, filepath, data) -> None:
        self.filepath = filepath
        self.data = data

    
    @classmethod
    def from_file(cls, filepath):
        with open(filepath, "a") as f:
            f.close()
        with open(filepath, "r") as f:
            raw = f.read()
            data = json.loads("{}" if raw.strip() == "" else raw)
            return cls(filepath, data)

    def save(self, filepath=None):
        filepath = self.filepath if filepath == None else filepath
        data = json.dumps(self.data)
        with open(filepath, "w") as f:
            f.write(data)
        return self
import json



class BaseObject:
    def __init__(self, prog, data="") -> None:
        self.prog = prog
        self.data = data

    @classmethod
    def from_prog(cls, prog):
        return cls(prog)

    @classmethod
    def from_file(cls, prog, file, default=""):
        with open(file, "r") as f:
            try:
                return cls(prog, json.loads(f.read()))
            except json.decoder.JSONDecodeError:
                return cls(prog, default)

    async def save(self, file):
        with open(file, "w") as f:
            f.write(json.dumps(self.data))
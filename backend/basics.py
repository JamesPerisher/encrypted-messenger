import json


# Base jsonable object for prog (Program) to handle
class BaseObject:
    def __init__(self, prog, data="") -> None:
        self.prog = prog
        self.data = data

    # make it from the current prog
    @classmethod
    def from_prog(cls, prog):
        return cls(prog)

    # make it from the json file
    @classmethod
    def from_file(cls, prog, file, default=""):
        with open(file, "r") as f:
            try:
                return cls(prog, json.loads(f.read()))
            except json.decoder.JSONDecodeError:
                return cls(prog, default)

    # save it as the json file
    async def save(self, file):
        with open(file, "w") as f:
            f.write(json.dumps(self.data))
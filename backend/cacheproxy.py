from backend.packet import *
import os


BASE_CACHE = dict()


class CacheProxy:
    def __init__(self, node, filepath, data) -> None:
        self.node = node
        self.filepath = filepath
        self.data = data

    async def get(self, req):
        return self.data.get(req, False)
        
    async def set(self, req, res):
        if req.pactype in (PAC.GMS, PAC.INF):
            self.data[req] = res

    async def save(self, filepath=None):
        filepath = self.filepath if filepath == None else filepath
        tmpdata = json.dumps({x.jexport():self.data[x].jexport() for x in self.data})
        with open(filepath, "w") as f:
            f.write(tmpdata)
        return self

    def clear(self):
        self.data = BASE_CACHE.copy()

    @classmethod
    def from_file(cls, node, filepath):
        if not os.path.exists(filepath): # create file if it doesn't exist
            os.mknod(filepath)

        with open(filepath, "r") as f:
            raw = f.read()
            data = json.loads("{}" if raw.strip() == "" else raw)
            data = BASE_CACHE.copy() if data == dict() else {Packet.jimport(x):Packet.jimport(data[x]) for x in data}
            return cls(node, filepath, data)

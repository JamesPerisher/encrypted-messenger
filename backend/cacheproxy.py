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
        if req.pactype in (PAC.GMS, PAC.NAN):
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
            if data == dict():
                data = BASE_CACHE.copy()
            else:
                _data = dict()
                for x in data:
                    try:
                        k, d = Packet.jimport(x), Packet.jimport(data[x])
                    except TypeError:
                        k, d = Packet.jimport(x), data[x]
                    _data[k] = d
                data = _data
            return cls(node, filepath, data)

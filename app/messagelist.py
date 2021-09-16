import asyncio
import bisect
import json
from datetime import datetime
from backend.keymanagement import *

from globalconfig import DATE_FONT_SIZE


class Message:
    def __init__(self, data) -> None:
        self.data = data

    @classmethod
    def from_bits(cls, time, data, messageid, fromname, fromcolour):
        data = {
            "time"       : time,
            "data"       : data,
            "messageid"  : messageid,
            "fromname"   : fromname,
            "fromcolour" : fromcolour
        }
        return cls(data)


class MessageList:
    def __init__(self, renderer, data=[], key=None) -> None:
        self.renderer = renderer
        self.data = sorted(data, key=lambda x: x["time"])
        self.keys = [x["time"] for x in self.data]
        self._next = -1
        self.key = key
    
    @property
    def next(self):
        self._next += 1
        return self._next

    async def add_message(self, item):
        if item in self.data: return # prevent duplicate messages

        # render message data
        item["data"] = await self.renderer.render_controls (item["data"])
        item["data"] = await self.renderer.render_text_refs(item["data"])

        k = item["time"]
        i = bisect.bisect_right(self.keys, k)  # Determine where to insert item.
        self.keys.insert(i, k)  # Insert key of item to keys list.
        self.data.insert(i, item)  # Insert the item itself in the corresponding place.

    async def export(self): # could have errors if exporting the same messagelist symultanisly
        colourtable = dict()
        out = [""]
        self._next = -1
        for i in self.data:
            index = self.next
            colourtable[index] = i["fromcolour"]
            line1 = "[color={}]{}[anchor={}][/color]    [size={}]{}[/size]\n{}".format(i["fromcolour"][1::], i["fromname"], index, DATE_FONT_SIZE, datetime.fromtimestamp(i["time"]).strftime("%a %d %b %y  %I:%M %p"), i["data"])
            out.append(line1)
        out.append(".[anchor={}].".format(self.next))
        out.append(".[anchor={}].".format(self.next))
        out = "\n".join(out)
        return colourtable, out
    
    @classmethod
    def jimport(cls, renderer, data, key):
        try:
            data = json.loads(decrypt(key, get_pub(key), data))
        except json.decoder.JSONDecodeError:
            data = {"data":{}, "next":-1}
        ret = cls(renderer, data["data"], key)
        ret._next = data["next"]
        return ret
    def jexport(self):
        return encrypt(self.key, get_pub(self.key), json.dumps({"next":self._next, "data": self.data})) 
    


async def main():
    ml = MessageList(None)

    await ml.add_message(Message.from_bits(1, "b", "fromid", "from", "fromcol").data)
    await ml.add_message(Message.from_bits(0, "a", "fromid", "from", "fromcol").data)
    await ml.add_message(Message.from_bits(2, "c", "fromid", "from", "fromcol").data)

    print(await ml.export())


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
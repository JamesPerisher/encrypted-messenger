import asyncio
import bisect
from datetime import datetime


DATE_FONT_SIZE = 11


class Message:

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        # render message txt to interactive text
        self._data = value
        self._data["data"] = self._data["data"].replace("[", "&bl;").replace("]", "&br;").replace("&", "&amp;")

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
    def __init__(self, data=[]) -> None:
        self.data = sorted(data, key=lambda x: x["time"])
        self.keys = [x["time"] for x in self.data]
        self._next = -1
    
    @property
    def next(self):
        self._next += 1
        return self._next

    async def add_message(self, item):
        if item in self.data: return # prevent duplicate messages

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
    def jimport(cls, data):
        ret = cls(data["data"])
        ret._next = data["next"]
        return ret
    def jexport(self):
        return {"next":self._next, "data": self.data}
    


async def main():
    ml = MessageList()

    await ml.add_message(Message.from_bits(1, "b", "fromid", "from", "fromcol").data)
    await ml.add_message(Message.from_bits(0, "a", "fromid", "from", "fromcol").data)
    await ml.add_message(Message.from_bits(2, "c", "fromid", "from", "fromcol").data)

    print(await ml.export())


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
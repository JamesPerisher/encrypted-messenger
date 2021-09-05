import asyncio
import bisect
from datetime import datetime


DATE_FONT_SIZE = 11


class Message:
    def __init__(self, data) -> None:
        self.data = data
    @classmethod
    def from_bits(cls, time, data, fromid, fromname, fromcolour):
        data = {
            "time"       : time,
            "data"       : data,
            "fromid"     : fromid,
            "fromname"   : fromname,
            "fromcolour" : fromcolour
        }
        return cls(data)


class MessageList:
    def __init__(self, data=[]) -> None:
        self.data = sorted(data, key=lambda x: x["time"])
        self.keys = [x["time"] for x in self.data]

    async def add_message(self, item):

        k = item["time"]
        i = bisect.bisect_right(self.keys, k)  # Determine where to insert item.
        self.keys.insert(i, k)  # Insert key of item to keys list.
        self.data.insert(i, item)  # Insert the item itself in the corresponding place.

    async def export(self):
        out = []
        for i in self.data:
            line1 = "[color={}]{}[/color]    [size={}]{}[/size]".format(i["fromcolour"][1::], i["fromname"], DATE_FONT_SIZE, datetime.fromtimestamp(i["time"]).strftime("%a %d %b %y  %I:%M %p"))
            line2 = i["data"].replace("[", "&bl;").replace("]", "&br;").replace("&", "&amp;")
            out.append(line1)
            out.append(line2)
        return "\n".join(out)




async def main():
    ml = MessageList()

    await ml.add_message(Message.from_bits(1, "b", "fromid", "from", "fromcol").export())
    await ml.add_message(Message.from_bits(0, "a", "fromid", "from", "fromcol").export())
    await ml.add_message(Message.from_bits(2, "c", "fromid", "from", "fromcol").export())

    print(await ml.export())




if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
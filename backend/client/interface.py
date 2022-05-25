
from backend.client.user import User
from backend.client.crypto_utils import key_import


class UserInterface:
    def __init__(self, client) -> None:
        self.client = client
    async def none(self): # nothing to do to ui, but is called every time a packet is handled
        pass

    async def actionloop(self):
        print("WE RUNNING BABY")

    async def get_name(self):
        return input("Name: ")

    async def get_key(self, reason=""):
        return key_import(input(f"{reason} keystring: "))

    async def get_pin(self):
        return input("pin: ")

    async def add_friend(self):
        while True:
            k = await self.get_key("Friend")
            if k:
                return User.from_key(k, self.client)

            if await self.is_do_thing("Cancel adding friend"):
                break
            
    async def get_friends(self):
        friends = []
        while True:
            friend = await self.add_friend()
            if friend:
                friends.append(friend)
                print(f"Added {friend}")

            if await self.is_do_thing("Cancel adding friends"):
                break
        return friends

    async def is_do_thing(self, thing: str):
        return input(f"{thing} (Y/n)?").lower().strip() in ("y", "yes")



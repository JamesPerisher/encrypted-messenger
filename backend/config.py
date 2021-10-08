from backend.basics import BaseObject


class Config(BaseObject):

    USERDATA_DIR = "userdata"

    CACHE_FILE    = "{}/cache.json".format(USERDATA_DIR)
    PRIV_KEY      = "{}/privkey.pem".format(USERDATA_DIR)
    XMPPDATA_FILE = "{}/xmpdata.json".format(USERDATA_DIR)

    DEFAULT_CACHE = {}
    DEFAULT_XMPP  = {"jid":"user1@localhost", "name":"NameError", "colour":"#ff00ff"}


    APPNAMELINK = "Kryptos"


    # Theme
    SUPERDARK           = "#000000"
    SUPERBRIGHT         = "#121212"
    BRIGHT              = "#2E2E2E"
    DARK                = "#3B3B3B"
    BACKGROUND          = "#787878"
    LIGHTBACKGROUND     = "#aaaaaa"
    BUTTONBACKGROUND    = "#ffffff"
    ERROR               = "#aa0000"
    APP_COLOUR          = "#290f47"
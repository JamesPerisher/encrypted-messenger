from backend.basics import BaseObject


class Config(BaseObject):

    USERDATA_DIR = "userdata"

    CACHE_FILE    = "{}/cache.json".format(USERDATA_DIR)
    PRIV_KEY      = "{}/privkey.pem".format(USERDATA_DIR)
    XMPPDATA_FILE = "{}/xmpdata.json".format(USERDATA_DIR)

    DEFAULT_SESSION = {"active":False}
    DEFAULT_XMPP  = {"jid":"", "name":"", "colour":""}


    APPNAMELINK = "Kryptos"

    # Theme

    SUPERBRIGHT       = "#000000"
    DARK              = "#121212"
    LIGHTBACKGROUND   = "#2E2E2E"
    BACKGROUND        = "#3B3B3B"
    BRIGHT            = "#787878"
    BUTTONBACKGROUND  = "#aaaaaa"
    SUPERDARK         = "#ffffff"
    
    ERROR             = "#aa0000"
    HEIGHLIGHT_COLOUR = "#064ca0"
    APP_COLOUR        = "#290f47"


    NOTIFICATION_DISPLAY_TIME = 1.5
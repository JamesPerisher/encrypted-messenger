class Config:

    USERDATA_DIR = "userdata"

    SESSION_FILE    = "{}/session.json".format(USERDATA_DIR)
    XMPPDATA_FILE   = "{}/xmpdata.json".format(USERDATA_DIR)
    CACHE_FILE      = "{}/cache.txt"   .format(USERDATA_DIR)
    QRCODE_FILE     = "{}/shaire.png"  .format(USERDATA_DIR)

    SIGNUP_TEXT     = "app/data/signuptext.txt"
    LICENCE         = "LICENCE"
    TERMS           = "app/data/terms.txt"
    
    # TODO: Fix this idk why it doesnt work
    DEFAULT_CACHE   = {
        "colorindex": dict()
    }
    
    DEFAULT_SESSION = {
        "active":False,
        "friends":{
            # deafault data "Pending..." encoded in public key
            "empty"            : "-----BEGIN PGP PUBLIC KEY BLOCK-----\n\nxsFNBGFvj3QBEADQLuj5cNE/8LLRBLFstAdtXUigFAvgdnyU3qtYNKP4oCD0qIM7\nhOrzR5QIYykayN/xGcVfxDc7edIqcna3Z2jxVZIAxlhFocEAP2RyKx1zz8E4CYpk\ngmKiKVR3SY82Nao5I6eVGR3hjMcmWyVTobw18BJwprpini6+cPWofzxHA397ePxL\nQ+n4yjrFR9K2UfTH/CWKyzkVZfz2KxsR3ONqhFeBn/uEBv3a1v0E5Xru1YNExRmG\nYMqNpOKRIrCUsXOatXbzOWoID4fzTh5OOMi4LY7OPiMEaERfHuMLvU+4xBmAkhyh\nqlbHw5H3HPDCeE7f/NugeJFj+XBOtIK1mHrvu29I4bhMz1AfWGMIFwfxjWx8z6IY\nvii7UXp4h6tWoJIa5JzkMTw8XbuZbupOBHBldJf84gS/NhMC1KbLB9KSlIU43Do/\nUMzI8gfzRFIiyg1EknZJlADQbkTo5hjtE5DTaE8urmrvbYZcdzkXuss6Dt8Bi7jR\nFSjkuL8oxFwSJF7agZmCEvCrh4Xg+p6SPkWsgl/UqjiowbIpdS/nlZ7tJU+YNtCH\nd4K36X3S076X2m2LEWyLyYDSzyR+MnliDzryG2S1RpWLlUNKfmBVshfxbZg/5/pl\nd8Xl0GhuWPp7sYQLfGq+JWMDmFKBYJAhEokIk5OExQpvazaE/D96lvW9qwARAQAB\nzRRQZW5kaW5nLi4uICgjZmYwMGZmKcLBigQTAQgANAUCYW+PdQIbDgQLCQgHBRUI\nCQoLBRYCAwEAAh4BFiEEnRNL+LU/iHMscwx9FrmyUNF//mMACgkQFrmyUNF//mMl\nIBAAiUKWdgaEO9MNp7waQ0L0nd/DZNS9/aPs1bJgDhWIdZpss8TD7Yv3xQKXJS7t\n+YpnTv64fBJA6AInccVrPxVd3NkFEWrk119lUFeMKlz1NcOvYADoVi/+M2m7ZF0Y\n/Lbkf/4uOb1VbfsMHvHVyNo9GDzrpo6JUbJYk3tGcb1cW2gwUh4eZzv/pFQJLEB/\nlc/a7i+7ZGoh95RHlEnJqsP5DSerC2lQz5P2X4kUtSr9CYQK78faPiXDwXAzTfUZ\n5KuTsOxBPXwogHV7gsqzC/MmQGuRCl0SgHvjjpRXMzIViP4cPI6gexAC23wtCo3P\n/FnixJDbicCupHcJ6SOWTi1+SPUCwzWuJ5tcbk+ljNVUdbQgXNMzbcwl+ut5N5SZ\nGJau7KAy2tK1iWJaHlJDSDmSEfIjl5TWfQojVDSRh6eDBjvPaFWw1PO0OnLDGDV5\na5vx8XQVlHAsmtylc247qUwkqBr+dzDEM/PYTZPOug9hGuAAd/50fcSLPWFrtSNT\nyBN2lQeZDxdEkv6vSq81gG1JZdVOt+qtr3D3/hjo0mOlQ7c7H7due+97p9f84kQC\nHSyIcGeuxOisCopGw/GEdgbQ8hLyzX5CwxMiFiHPOiMB3qjzVxRYrjsJCw9h4VLO\ny4ftX4r9e/5nuhhrrL/xzCPRQ34tDVFId/2fulLDfHhD8xs=\n=eXjJ\n-----END PGP PUBLIC KEY BLOCK-----\n"
        }
    }

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

    DATE_FONT_SIZE   = 12
    FONT = "app/fonts/LEMONMILK-Medium.ttf"


    NOTIFICATION_DISPLAY_TIME = 1.5
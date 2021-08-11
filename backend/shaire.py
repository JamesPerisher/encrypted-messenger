import pyqrcode
from PIL import Image
import asyncio


def make_code(data, upscale=10, fillpercent=1/4) -> Image: # make this a True async function

    qrcode = pyqrcode.QRCode(data,error = 'H') # 30% image backup for overlay loss
    qrcode.png('userdata/qrcode.png.cache',scale=upscale)

    im = Image.open('userdata/qrcode.png.cache', formats=("png",)) # edit image on qrcode
    im = im.convert("RGBA")
    logo = Image.open('app/images/logo1.png')

    x = im.width / upscale
    a = fillpercent

    box = (
        int(10*(x-a*x)/2)+2,
        int(10*(x-a*x)/2)+2,
        int(10*(x+a*x)/2),
        int(10*(x+a*x)/2)
    ) 

    im.crop(box)
    region = logo
    region = region.resize((box[2] - box[0], box[3] - box[1]))
    im.paste(region,box)
    return im


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    a = loop.run_until_complete(make_code("https://www.google.com"))

    a.show()
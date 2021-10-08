import pyqrcode
from PIL import Image
import asyncio


def make_code(data, upscale=10, fillpercent=1/4, userdata_path="idfk") -> Image: # make this a True async function

    qrcode = pyqrcode.QRCode(data,error = 'H') # 30% image backup for overlay loss
    qrcode.png('{}/qrcode.png'.format(userdata_path),scale=upscale)

    im = Image.open('{}/qrcode.png'.format(userdata_path)) # edit image on qrcode
    im = im.convert("RGBA")
    logo = Image.open('app/images/logo1.png')

    x = im.width / upscale
    a = fillpercent

    box = (
        int(10*(x-a*x)/2)+2,
        int(10*(x-a*x)/2)+2,
        int(10*(x+a*x)/2)-1,
        int(10*(x+a*x)/2)-1
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
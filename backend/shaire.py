import pyqrcode
from PIL import Image, ImageDraw
import asyncio


def make_code(data, upscale=10, fillpercent=1/4, userdata_path="userdata") -> Image: # make this a True async function

    qrcode = pyqrcode.QRCode(data,error = 'H') # 30% image backup for overlay loss
    qrcode.png('{}/qrcode_raw.png'.format(userdata_path),scale=upscale)

    im = Image.open('{}/qrcode_raw.png'.format(userdata_path)).convert("RGBA") # edit image on qrcode
    logo = Image.open('app/images/logo.png').convert("RGBA")


    bg_w, bg_h = im.size
    maxsize = (int(bg_w*fillpercent), int(bg_h*fillpercent))
    logo.thumbnail(maxsize, Image.ANTIALIAS)

    img_w, img_h = logo.size
    offset = ((bg_w - img_w) // 2, (bg_h - img_h) // 2)


    r = int(1.4142 * (max(img_w, img_h)/2))       
    pos = bg_w/2-r, bg_h/2-r, bg_w/2+r, bg_h/2+r

    draw = ImageDraw.Draw(im)
    draw.ellipse(pos, fill=(255, 255, 255), outline=(255, 255, 255))

    im.paste(logo,offset, logo)
    return im


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    a = make_code("https://www.google.com")

    a.show()
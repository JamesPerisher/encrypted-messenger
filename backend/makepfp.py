from backend.config import Config
from backend.keymanagement import *
from kivy.utils import get_color_from_hex
from PIL import Image, ImageChops, ImageFont, ImageDraw

# Convert name into initials
def name_to_innitials(name):
    # Custom for developers
    if name == "PaulN07"  : return["P","0","7"]
    if name == "PRThomas" : return["P","R","T"]
    if name == "IBEGames" : return["I","B","E"]
    
    #bob smith, Bob Smith
    if split_test(name.split(" "))==True:
        return [name.split(" ")[0][0],name.split(" ")[1][0]]
    
    #bob_smith
    elif split_test(name.split("_"))==True:
        return [name.split("_")[0][0],name.split("_")[1][0]]

    #bob-smith
    elif split_test(name.split("-"))==True:
        return [name.split("-")[0][0],name.split("-")[1][0]]

    #bob.smith
    elif split_test(name.split("."))==True:
        return [name.split(".")[0][0],name.split(".")[1][0]]
    
    output=[]
    for i in name:
        if ord(i)>64 and ord(i)<91:
            output.append(i)
    if len(output)!=2:#no innitials found, using first letter
        for i in name:
            if ord(i)>64 and ord(i)<91:
                return [i]
            elif ord(i)>96 and ord(i)<123:
                return [i]
        return [name[0] if len(name) != 0 else "E"]#no letters found
    else:
        return output#BobSmith, Bob

# checker for if shit is ok
def split_test(splitlist): # Checks there are 2 elements both with letters
    if len(splitlist)!=2:
        return False
    for i in splitlist:
        count=0
        for j in i:
            if ord(j)>64 and ord(j)<91:
                count+=1
            elif ord(j)>96 and ord(j)<123:
                count+=1
        if count==0:
            return False
    return True
    

# determines if light or dark is better text overlay
def text_colour(colour):
    mathcolour = get_color_from_hex(colour)
    # is the average > 0.5 etc
    return Config.BRIGHT if round((mathcolour[3]/3)*(mathcolour[0] + mathcolour[1] + mathcolour[2])) == 0 else Config.DARK

# make a profile picture form initials and color
def make_pf_pic(id, name, colour):
    # get the initials
    initials = name_to_innitials(name)
    rtext = "".join(initials).upper()
    # color a copy of the base
    im1 = Image.open("app/images/useraccountbase.png")
    im2 = Image.new("RGBA", im1.size, validate_hex(colour))
    
    # draw text onto the image
    image = ImageChops.multiply(im1, im2)
    draw = ImageDraw.Draw(image)
    fontsize = 320 if len(initials) == 2 else 210
    font = ImageFont.truetype(Config.FONT, fontsize)
    box = font.getsize(rtext)
    draw.text(( (im1.width -box[0])/2, (im1.height-1.25*box[1])/2 ), rtext, fill = text_colour(validate_hex(colour)), font = font, align="left")

    # export all the data to a file
    exportname = "userdata/userimage-{}.png".format(id)
    image.save(exportname, formats=("png",))

    return exportname
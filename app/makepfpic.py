from PIL import Image, ImageChops, ImageFont, ImageDraw
from kivy.utils import get_color_from_hex


FONT = "LemonMilkMedium-mLZYV.otf"
BRIGHT = "#eeeeee"
DARK   = "#333333"

def name_to_innitials(name):
    # Custom fro developers
    if name == "PaulN07"  : return["P","0","7"]
    if name == "PRThomas" : return["P","R","T"]
    
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
        return [name[0]]#no letters found
    else:
        return output#BobSmith, Bob
    
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

def text_colour(colour):
    mathcolour = get_color_from_hex(colour)
    return BRIGHT if round((mathcolour[3]/3)*(mathcolour[0] + mathcolour[1] + mathcolour[2])) == 0 else DARK

def make_pf_pic(id, name, colour):
    initials = name_to_innitials(name)
    rtext = "".join(initials).upper()
    
    im1 = Image.open("app/images/useraccountbase.png")
    im2 = Image.new("RGBA", im1.size, colour)
    
    image = ImageChops.multiply(im1, im2)
    draw = ImageDraw.Draw(image)

    fontsize = 320 if len(initials) == 2 else 210
    font = ImageFont.truetype("app/{}".format(FONT), fontsize)
    box = font.getsize(rtext)

    draw.text(( (im1.width -box[0])/2, (im1.height-1.25*box[1])/2 ), rtext, fill = text_colour(colour), font = font, align="left")

    exportname = "userdata/{}.png".format(id)
    image.save(exportname, formats=("png",))

    return exportname

if __name__ == "__main__":
    print(make_pf_pic("id0", "SteveJobs", "#333333"))
    print(make_pf_pic("id1", "PaulN07", "#00FFFF"))
    print(make_pf_pic("id2", "PRThomas", "#ffffff"))
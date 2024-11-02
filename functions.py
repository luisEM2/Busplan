from PIL import Image
from pygame import image as load_pygame_image
import time


def get_bus_with_color(rgb, icon_chooser):
    if icon_chooser == "B":
        IMAGE = r"bilder\bus_icon.png"
    elif icon_chooser == "Z":
        IMAGE = r"bilder\zug_icon.png"
    else:
        exit(icon_chooser)
    image = Image.open(IMAGE)
    # Get the size of the image
    width, height = image.size
    # Process every pixel
    for x in range(0, width - 1):
        for y in range(0, height - 1):
            color = image.getpixel((x, y))

            if type(color) != int and color[0] != 0 and color[1] != 0 and color[2] != 0:
                color = rgb

            image.putpixel((x, y), color)

    new_image = image.resize((30, 30))

    # Calculate mode, size and data
    mode = new_image.mode
    size = new_image.size
    data = new_image.tobytes()

    # Convert PIL image to pygame surface image
    py_image = load_pygame_image.fromstring(data, size, mode)
    return py_image

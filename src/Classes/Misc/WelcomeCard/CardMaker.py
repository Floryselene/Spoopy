from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageFilter



def is_color_too_dark(color):
    if isinstance(color, str):
        # Hex color code
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
    elif isinstance(color, tuple) and len(color) == 3:
        # RGB tuple
        r, g, b = color
    else:
        raise ValueError("Invalid color format. Use either a hex color code (e.g. '#00FF00') or an RGB tuple (e.g. (0, 255, 0))")

    brightness = (r * 0.299 + g * 0.587 + b * 0.114) / 255
    # Threshold for "too dark"
    return brightness < 0.3


class ImageEditor:
    def add_blur(self, image, pixels_from_edge=20):
        width, height = image.size
        section_width = width - (pixels_from_edge * 2)
        section_height = height - (pixels_from_edge * 2)
        left = pixels_from_edge
        top = pixels_from_edge
        right = left + section_width
        bottom = top + section_height
        middle_section = image.crop((left, top, right, bottom))
        mask = Image.new("L", middle_section.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), middle_section.size], radius=50, fill=255)
        blurred_section = middle_section.filter(ImageFilter.GaussianBlur(radius=500))
        blurred_section.putalpha(mask)
        image.paste(blurred_section, (left, top), mask=blurred_section)


    def recolor(self, image, new_color=(255, 0, 0, 255)):
        recolored_image = ImageChops.multiply(image, Image.new("RGBA", image.size, new_color))
        return recolored_image


    def add_circular_image(self, foreground_image, new_size=(128, 128), add_border=True, border_width=10):
        foreground_image = foreground_image.resize(new_size)

        # Make the foreground image circular
        mask = Image.new("L", foreground_image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, foreground_image.width, foreground_image.height), fill=255)
        new_foreground_image = Image.new("RGBA", foreground_image.size, (255, 255, 255, 0))
        new_foreground_image.paste(foreground_image, (0, 0), mask)

        # Add a circular border around the circular image
        if add_border == True:
            border_image = Image.new("RGBA", (new_foreground_image.width + border_width * 2, new_foreground_image.height + border_width * 2), (255, 255, 255, 0))
            draw = ImageDraw.Draw(border_image)
            center = (border_image.width // 2, border_image.height // 2)
            radius = min(border_image.width, border_image.height) // 2 - border_width // 2
            draw.ellipse((center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius), fill=(255, 255, 255, 255))
            border_image.paste(new_foreground_image, (border_width, border_width), new_foreground_image)
            return border_image

        return new_foreground_image


    def add_text(self, image, text, font_path, font_size, text_position):
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(font_path, size=font_size)
        draw.text(text_position, text, font=font, fill=(255, 255, 255))

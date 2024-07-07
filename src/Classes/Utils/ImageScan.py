from PIL import Image



class ColorScanner:
    def __init__(self, image_path):
        self.image_path = image_path


    def get_dominant_rgb(self):
        image = Image.open(self.image_path)
        image = image.convert("RGBA")
        pixels = image.getdata()
        filtered_pixels = [pixel[:3] for pixel in pixels if pixel[3] != 0]

        color_counts = {}
        for rgb in filtered_pixels:
            if rgb in color_counts:
                color_counts[rgb] += 1
            else:
                color_counts[rgb] = 1

        dominant_rgb = max(color_counts, key=color_counts.get)
        return dominant_rgb


    def rgb_to_hex(self, rgb):
        return '#%02x%02x%02x' % rgb

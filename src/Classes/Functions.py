import io
import aiohttp

from .Utils.ImageScan import ColorScanner



async def download_asset(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(str(url)) as resp:
            if resp.status != 200:
                return None
            data = await resp.read()
    return data


def color_thief(data):
    scanner = ColorScanner(io.BytesIO(data))
    color = scanner.get_dominant_rgb()
    hex_color = scanner.rgb_to_hex(color)
    return hex_color

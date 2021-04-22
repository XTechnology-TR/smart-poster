import io
from colorthief import ColorThief
from PIL import Image, ImageEnhance
from colormap import rgb2hex as rgb2hex_
from colorsys import rgb_to_hsv, hsv_to_rgb, rgb_to_hls

from src.image import ImageWrapper


class ColorPicker(ImageWrapper):

    def __init__(self) -> None:
        pass

    def scan_image(self):
        self.get_contrast_color(self.img)
        self.get_dominant_color(self.img)

    def get_most_saturated_color(self, rgb_palette: list) -> tuple:
        hsl_palette = [rgb_to_hls(*c) for c in rgb_palette]
        i = hsl_palette.index(min(hsl_palette, key=lambda t: t[2]))
        most_sat_color = rgb_palette[i]
        return most_sat_color

    def saturate_color(self, rgb: tuple, sat: float = 1) -> tuple:
        hsv = rgb_to_hsv(*rgb)
        output_hsv = (hsv[0], sat, hsv[2])
        return hsv_to_rgb(*output_hsv)

    def increase_brightness(self, rgb, pct: float = 0.5) -> tuple:
        r, g, b = rgb
        r = min(255, r*(1+pct))
        g = min(255, g*(1+pct))
        b = min(255, b*(1+pct))
        return (r, g, b)

    def get_dominant_color(self, img: Image, quality: int = 5) -> tuple:

        with io.BytesIO() as file_object:
            img.save(file_object, "PNG")
            cf = ColorThief(file_object)
            self.dominant_color = cf.get_color(quality=quality)

        return self.dominant_color

    def get_color_palette(self, img: Image, quality: int = 5, color_count: int = 6):

        with io.BytesIO() as file_object:
            img.save(file_object, "PNG")
            cf = ColorThief(file_object)
            self.palette = cf.get_palette(
                color_count=color_count, quality=quality)

        return self.palette

    def rgb2hex(self, rgb: tuple) -> str:
        return rgb2hex_(*(int(c) for c in rgb))

    def get_contrast_color(self, image: Image, sat: float = 1, brightness: float = .5) -> tuple:
        palette = self.get_color_palette(image.convert("RGBA"))
        most_sat_color = self.get_most_saturated_color(palette)
        contrast_color = self.increase_brightness(
            self.saturate_color(most_sat_color, sat=1), pct=brightness)
        self.contrast_color = contrast_color
        return self.contrast_color

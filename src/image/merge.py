import io
import numpy as np
from PIL import Image, ImageEnhance
from src.image.detect import flip_if_necessary
from src.image.color import get_contrast_color
from src.image.draw import draw_text, resize_img
from src.paths import LOCAL_GLOBAL_DATA


def merge_text_to_image(img: Image, txt: str, bottom_right_txt: str = None, top_right_txt: str = None, overlay: str = 'OVERLAY_80%OP_BLACK_BOTTOM_LEFT_SOFT', padding: float = 60, txt_aspect_ratio: float = 0.3, txt_brightness: float = 1, max_words: int = 16):
    """
    Merges text `txt` to image `img` with possible overlays below:

    - 'OVERLAY_100%OP_BLACK_BOTTOM_LEFT'
    - 'OVERLAY_100%OP_BLACK_BOTTOM_LEFT_SOFT'
    - 'OVERLAY_80%OP_BLACK_BOTTOM_LEFT'
    - 'OVERLAY_80%OP_BLACK_BOTTOM_LEFT_SOFT'

    Output with squared aspect ratio.
    """

    txt2draw = ' '.join(txt.split(' ')[:max_words])
    caption = ''

    if max_words < len(txt.split(' ')):
        txt2draw += ' ...'
        caption = '... ' + ' '.join(txt.split(' ')[max_words:])

    canvas = Image.open(
        str(LOCAL_GLOBAL_DATA / 'SQUARED_CANVAS.png')).convert("RGBA")

    img_ = flip_if_necessary(img.convert("RGB"))

    if canvas.size != img_.size:
        overlay = Image.open(
            str(LOCAL_GLOBAL_DATA / 'OVERLAY_100%OP_BLACK_BOTTOM_LEFT_SOFT.png'))
    else:
        overlay = Image.open(str(LOCAL_GLOBAL_DATA / f'{overlay}.png'))

    txt_color = get_contrast_color(img_, brightness=txt_brightness)
    txt_ = resize_img(draw_text(txt2draw, fontsize=200,
                      fontcolor_hex=txt_color, target_ar=txt_aspect_ratio), (0, 1000))
    txt_ = ImageEnhance.Brightness(txt_).enhance((1+txt_brightness))

    top_right_txt_ = resize_img(draw_text(f'{top_right_txt}',
                                          font='Poppins-Light.otf', fontsize=200, fontcolor_hex=txt_color), (0, 40))
    top_right_txt_ = ImageEnhance.Brightness(
        top_right_txt_).enhance((1+txt_brightness))

    bottom_right_txt_ = resize_img(draw_text(f'{bottom_right_txt}',
                                             font='Poppins-Italic.otf', fontsize=200, fontcolor_hex=txt_color), (0, 40))
    bottom_right_txt_ = ImageEnhance.Brightness(
        bottom_right_txt_).enhance((1+txt_brightness))

    canvas.paste(img_, (int(canvas.size[0] - img_.size[0]), 0), img_)
    canvas.paste(overlay, (0, 0), overlay)
    canvas.paste(txt_, (padding,
                        int((img_.size[1] - txt_.size[1])/2)), txt_)

    if top_right_txt:
        canvas.paste(top_right_txt_, (int(img_.size[0]-padding/2-top_right_txt_.size[0]),
                     int(padding/2)), top_right_txt_)

    if bottom_right_txt:
        canvas.paste(bottom_right_txt_, (int(img_.size[0]-padding/2-bottom_right_txt_.size[0]),
                     int(img_.size[1]-padding/2-bottom_right_txt_.size[1])), bottom_right_txt_)

    canvas_black = Image.open(
        str(LOCAL_GLOBAL_DATA / 'SQUARED_CANVAS_BLACK.png')).convert("RGBA")

    with io.BytesIO() as f:
        canvas.save(f, "PNG")
        canva_reloaded = Image.open(f).convert('RGBA')
        canvas_black.paste(canva_reloaded, (0, 0), canva_reloaded)
        return canvas_black.convert('RGB')


def np2img(numpy_image: np.array):
    return Image.fromarray(numpy_image.astype('uint8'), 'RGBA')


from src.text import Quote
from src.image.merge import Creative

from src.text.extract import QuoteExtractor
from src.image.extract import ApiImgExtractor

from src.paths import LOCAL_PROCESSED_DATA_PATH

from pathlib import Path


class Post():

    def __init__(self, quote: Quote, img_url: str, profile_name: str,
                 output_size: tuple = (1080, 1080), txt_aspect_ratio: str = 'NARROW',
                 font_family: str = 'Poppins', font_style: str = 'Bold',
                 font_color: str = 'AUTO') -> None:
        self.quote = quote
        self.img_url = img_url
        self.profile_name = profile_name
        self.output_size = output_size
        self.txt_aspect_ratio = txt_aspect_ratio
        self.font_family = font_family
        self.font_style = font_style
        self.font_color = font_color
        self.caption = quote.caption
        self.hashtags = quote.hashtags
        self.txt2draw = quote.main_txt
        self.creative, self.caption = self.build_post()

    def build_post(self) -> tuple:

        c = Creative(
            txt=self.quote.main_txt,
            bottom_right_txt=self.quote.author,
            top_right_txt=self.profile_name,
            img_url=self.img_url,
            txt_aspect_ratio=self.txt_aspect_ratio,
            font_family=self.font_family,
            font_style=self.font_style,
            font_color=self.font_color,
            output_size=self.output_size
        )

        self.creative = c.creative

        cta = ['\n']

        cta.append(
            f'📕 {self.quote.source_type.title()}: {self.quote.source.title()}')
        cta.append(f'✍️ Author: {self.quote.author.title()}')

        cta.extend([
            '\n💥 Pages for you to like!',
            f'👉 {self.profile_name}',
            10*'➖',
            '🤐 Comment 6x with 💪 and like our post! 🤫',
            10*'➖',
            '❤️Like 💬Comment 👣Follow us',
            10*'➖',
            '#️⃣Hashtags⠀',
        ])

        cta.append(' '.join(self.hashtags))

        cta.extend([
            10*'➖',
            '☆ We wish you a lot of wisdom!'
        ])

        self.caption += '\n'.join(cta)

        self.caption = self.caption.strip()

        return self.creative, self.caption

    def export_post(self, filepath: Path, format_: str = 'PNG') -> None:
        self.creative.save(filepath, format_, quality=90)

    def export_caption(self, filepath: Path) -> None:
        with open(filepath, mode='w', encoding='utf8') as fp:
            fp.write(self.caption)


class ContentProducer():

    def __init__(self, themes: list, posts_per_theme: int,
                 profile_name: str, txt_aspect_ratio: str = "NARROW",
                 font_family: str = 'Poppins', font_style: str = 'Bold',
                 font_color: str = 'AUTO', format_: str = "PNG", max_words: int = 16,
                 output_size: tuple = (1080, 1080), api_: str = 'unsplash') -> None:

        self.themes = themes
        self.posts_per_theme = posts_per_theme
        self.profile_name = profile_name
        self.txt_aspect_ratio = txt_aspect_ratio
        self.format_ = format_
        self.max_words = max_words
        self.output_size = output_size
        self.api_ = api_
        self.font_family = font_family
        self.font_style = font_style
        self.font_color = font_color

    def produce_content(self):
        content = []

        for t in self.themes:
            ie = ApiImgExtractor(self.api_)
            qe = QuoteExtractor(
                query=t, ext_source='QUOTE_API', limit=self.posts_per_theme)
            ie.query(_search_params={
                'q': t,
                'imgType': 'photos'
            })

            if not qe.results:
                continue

            for i, (q, img_url) in enumerate(zip(qe.results, ie.img_urls)):

                filepath_img = LOCAL_PROCESSED_DATA_PATH / \
                    f"{t}_{i}.{self.format_}"
                filepath_txt = LOCAL_PROCESSED_DATA_PATH / f"{t}_{i}.txt"

                if not q or not img_url:
                    break

                p = Post(quote=q, img_url=img_url,
                         profile_name=self.profile_name,
                         output_size=self.output_size,
                         txt_aspect_ratio=self.txt_aspect_ratio,
                         font_family=self.font_family,
                         font_style=self.font_style,
                         font_color=self.font_color,
                         )

                p.export_post(filepath_img)
                p.export_caption(filepath_txt)

                content.append({
                    'id': filepath_img.stem,
                    'theme': t,
                    'filepath': filepath_img,
                    'filepath_txt': filepath_txt
                })

        return content

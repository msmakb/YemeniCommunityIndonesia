"""
* Image Processing Module For Detecting Faces 
* And Resizing The Image. Generating Membership
* Card With Rounded Personal Image.
* Created For Yemeni Community In Indonesia.
* 
* Module Requirements:
* arabic_reshaper
* python-bidi
* opencv-python
* pillow
* rembg
* cairo
* 
* Created By: Mohammed Ba Karman
* E-Mail: msmabk11@gmail.com
* Version: 1.0.0
"""
import os

from io import BytesIO
from logging import Logger
from pathlib import Path
from typing import Final
from tempfile import NamedTemporaryFile as TemporaryFile

import arabic_reshaper
import logging
import requests
import cairo
import cv2

from bidi.algorithm import get_display
from django.conf import settings
from numpy import array as numpyArray
from numpy import ndarray as NDArray

from PIL import Image as Img
from PIL import ImageDraw as ImgDraw
from PIL import ImageFont, ImageOps
from PIL.Image import Image
from PIL.ImageDraw import ImageDraw

from main.constants import PARAMETERS
from parameter.service import getParameterValue

logger: Logger = logging.getLogger("YCI.Main")


class ImageProcessingError(Exception):
    pass


class ImageProcessor:

    @staticmethod
    def validateAndResizePhotograph(fp: str | bytes | Path) -> bytes:
        EXPECTED_WIDTH: Final[int] = 400
        EXPECTED_HIGHT: Final[int] = 400
        # higher is better, but coste more processing
        RESIZE_ACCURACY: Final[int] = 10
        CASCADE_PATH: Final[Path] = Path(cv2.__file__).parent.absolute(
        ) / 'data/haarcascade_frontalface_default.xml'

        # first image resizing
        image: Image = Img.open(fp)
        width, height = image.size
        ratio: int = 0

        if width < EXPECTED_WIDTH or height < EXPECTED_HIGHT:
            raise ImageProcessingError(
                f"عذرا، يجب أن يكون حجم الصورة ({EXPECTED_WIDTH}X{EXPECTED_HIGHT})px او اكثر")

        temp = width
        expected = EXPECTED_WIDTH
        if width > height:
            temp = height
            expected = EXPECTED_HIGHT

        while temp > expected / RESIZE_ACCURACY:
            ratio += 1 / RESIZE_ACCURACY
            temp -= expected / RESIZE_ACCURACY

        if ratio < 0:
            ratio = 1

        size: tuple[int, int] = (int(width / ratio), int(height / ratio))
        image: Image = image.resize(size)

        # Face detection
        # Validate the photograph (it has a person face)
        face_cascade = cv2.CascadeClassifier(str(CASCADE_PATH))
        gray: NDArray = cv2.cvtColor(numpyArray(image), cv2.COLOR_BGR2GRAY)
        faces: NDArray = face_cascade.detectMultiScale(
            gray,
            1.1,
            minNeighbors=10,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        if len(faces) == 1:
            x, y, width, height = faces[0]

            if width < 160 or height < 160:
                image.close()
                raise ImageProcessingError(
                    "الصورة بعيدة جدًا، يرجى اختيار صورة شخصية رسمية")
            if width > 270 or height > 270:
                image.close()
                if abs(size[0] - size[1]) > 70:
                    raise ImageProcessingError(
                        "الصورة قريبة جدًا ، يرجى التأكد من أن الطول مساوٍ للعرض أو قريب منه")
                raise ImageProcessingError(
                    "الصورة قريبة جدًا، يرجى اختيار صورة شخصية رسمية")

            left = x
            top = y

            temp = (EXPECTED_WIDTH - width) / 2
            if left >= temp:
                left -= temp
            else:
                left = 0

            temp = (EXPECTED_WIDTH - height) / 2
            if top >= temp:
                top -= temp
            else:
                top = 0

            # crop the image and make the final resizing
            image = image.crop(
                (
                    left,
                    top,
                    EXPECTED_WIDTH + left,
                    EXPECTED_HIGHT + top
                )
            )

        else:
            raise ImageProcessingError(
                "صورة غير صالحة ، الرجاء اختيار صورة شخصية رسمية")

        # Convert to JPEG and return image in bytes
        image_io: BytesIO = BytesIO()
        image = image.convert('RGB')
        image.save(image_io, format="JPEG", quality=85)
        image.close()

        return image_io.getvalue()

    @staticmethod
    def generateMembershipCardImage(
        fp: str | bytes | Path,
        name_ar: str,
        name_en: str,
        city_ar: str,
        city_en: str,
        membership_type_ar: str,
        membership_type_en: str,
        issue_date: str,
        expire_date: str,
        card_number: str
    ) -> bytes:
        
        logger.info("***** Generate Membership Card Started *****")

        BLACK: Final[tuple[int, ...]] = (0, 0, 0)
        WHITE: Final[tuple[int, ...]] = (255, 255, 255)
        STATIC_ROOT: Path = settings.STATICFILES_DIRS[0]
        MEMBERSHIP_TEMPLATE: Path = settings.MEDIA_ROOT / \
            'templates/membership_template.jpg'
        FONTS_DIR: Path = STATIC_ROOT / 'fonts'

        # init
        logger.info("== Initializing Image Processing Started ==")
        image: Image = Img.open(fp)
        logger.info("   - Person Image Initialized")
        template: Image = Img.open(MEMBERSHIP_TEMPLATE)
        logger.info("   - Template Image Initialized")
        draw_interface: ImageDraw = ImgDraw.Draw(template)
        arabic_font = ImageFont.truetype(
            str(FONTS_DIR / "NotoNaskhArabic-Regular.ttf"), 36)
        english_font = ImageFont.truetype(
            str(FONTS_DIR / "FiraSans-Regular.ttf"), 28)
        logger.info("   - Fonts Initialized")
        logger.info("== Initializing Image Processing Done ==")

        # Rounded image
        logger.info("Rounding Personal Image Started")
        mask: Image = Img.new('L', image.size, 0)
        draw: ImageDraw = ImgDraw.Draw(mask)
        draw.ellipse((0, 0) + image.size, fill=255)
        image = ImageOps.fit(
            image, mask.size, centering=(0.5, 0.5))
        image.putalpha(mask)
        logger.info("Rounding Personal Image Done")

        # Request remove background image from 'remove.bg' website
        logger.info("== Remove Person Image Background Started ==")
        logger.info("   - Start Request Remove Image Background")
        api_key: str = getParameterValue(PARAMETERS.REMOVE_BG_API_KEY)
        logger.info(f"   - API Key: {api_key[:5]}***************")
        if api_key != "None":
            image_io: BytesIO = BytesIO()
            image = image.convert('RGBA')
            image.save(image_io, format="PNG", quality=85)
            logger.info("   - Sending Request")
            response = requests.post(
                'https://api.remove.bg/v1.0/removebg',
                files={'image_file': image_io.getvalue()},
                data={'size': 'auto'},
                headers={'X-Api-Key': api_key},
            )
            logger.info(f"   - Response Code: {response.status_code}")
            if response.status_code == requests.codes.ok:
                logger.info("   - Resize Image After Response")
                image: Image = Img.open(
                    BytesIO(response.content)
                ).resize((230, 230))
            else:
                raise ImageProcessingError(
                    f"Response Code: {response.status_code} - Error: {response.text}"
                )
        else:
            logger.warning("API KEY IS NONE, SKIP REMOVE IMAGE BACKGROUND")
            image = image.resize((230, 230))
        logger.info("== Remove Person Image Background Done ==")

        logger.info("== Start Processing Membership Card Data Started ==")
        # Put the rounded cleared bg image to the membership template
        template.paste(
            image,
            (41, 240),
            mask=image.convert('RGBA').split()[-1]
        )
        image.close()
        logger.info("   - Personal Image Processing Done")

        # name english
        draw_interface.text((430, 255), name_en,
                            font=english_font, fill=BLACK)
        logger.info("   - Name English Done")

        # city english
        draw_interface.text((402, 314),
                            city_en, font=english_font, fill=BLACK)
        logger.info("   - City English Done")

        # membership type english
        draw_interface.text((608, 377),
                            membership_type_en, font=english_font, fill=BLACK)
        logger.info("   - Membership Type English Done")

        # issue date
        english_font = ImageFont.truetype(
            str(FONTS_DIR / "FiraSans-Regular.ttf"), 32)
        draw_interface.text((615, 435), issue_date,
                            font=english_font, fill=BLACK)
        logger.info("   - Issue Date Done")

        # card number
        draw_interface.text((505, 518), card_number,
                            font=arabic_font, fill=WHITE)
        logger.info("   - Card Number Done")

        # expire date
        english_font = ImageFont.truetype(
            str(FONTS_DIR / "FiraSans-Regular.ttf"), 26)
        draw_interface.text((472, 586), expire_date,
                            font=english_font, fill=WHITE)
        logger.info("   - Expire Date Done")

        # Convert to JPEG and return image in bytes
        logger.info("   - Converting Image To Bytes For Arabic Data Processing")
        image_io: BytesIO = BytesIO()
        template = template.convert('RGB')
        template.save(image_io, format="PNG", quality=85)
        template.close()

        temp_file_name = ""
        with TemporaryFile(suffix='.png', delete=False) as temp_file:

            temp_file_name = temp_file.name
            temp_file.write(image_io.getvalue())
            image_io.seek(0)
            image_io.truncate(0)

            # Initialize cairo settings
            logger.info("   - Initialize Cairo Settings Bytes For Arabic Data Processing")
            surface = cairo.ImageSurface.create_from_png(temp_file_name)
            context = cairo.Context(surface)
            context.select_font_face("Noto Naskh Arabic")
            context.set_font_size(36)
            context.set_source_rgb(*BLACK)

            # Name Arabic
            name_ar_reshaped = get_display(
                arabic_reshaper.reshape(name_ar), base_dir='L')
            text_size = draw_interface.textlength(
                name_ar_reshaped, arabic_font)
            context.move_to(950 - text_size, 238)
            context.show_text(name_ar_reshaped)
            logger.info("   - Name Arabic Done")

            # City Arabic
            city_ar_reshaped = get_display(
                arabic_reshaper.reshape(city_ar), base_dir='L')
            text_size = draw_interface.textlength(
                city_ar_reshaped, arabic_font)
            context.move_to(940 - text_size, 338)
            context.show_text(city_ar_reshaped)
            logger.info("   - City Arabic Done")

            # Membership Type Arabic
            membership_type_ar_reshaped = get_display(
                arabic_reshaper.reshape(membership_type_ar), base_dir='L')
            text_size = draw_interface.textlength(
                membership_type_ar_reshaped, arabic_font)
            context.move_to(856 - text_size, 409)
            context.show_text(membership_type_ar_reshaped)
            logger.info("   - Membership Type Arabic Done")

            # Save the surface to the temp file
            logger.info("   - Finishing Cairo Process")
            surface.write_to_png(temp_file_name)
            surface.finish()
            surface.flush()
            logger.info("== Start Processing Membership Card Data Done ==")

        # Convert to JPEG
        logger.info("Converting Image to JPEG Format")
        image: NDArray = cv2.imread(temp_file_name)
        quality: tuple[int, int] = (int(cv2.IMWRITE_JPEG_QUALITY), 85)
        image: NDArray = cv2.imencode(".jpg", image, quality)[1]

        # Delete temp file
        logger.info("Cleanup...")
        if os.path.isfile(temp_file_name):
            os.remove(temp_file_name)

        logger.info("***** Generate Membership Card Done *****")
        return image.tobytes()

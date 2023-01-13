"""
Image Processing Module For Detecting Faces 
And Resizing The Image. Generating Membership
Card With Rounded Personal Image.
Created For Yemeni Community In Indonesia.

Module Requirements:
arabic_reshaper
python-bidi
opencv-python
pillow
rembg

Created By: MsMaB.
Name: Mohammed Ba Karman
E-Mail: msmabk11@gmail.com
"""
from io import BytesIO
from pathlib import Path
from typing import Final

import arabic_reshaper
from bidi.algorithm import get_display
import cv2
from django.conf import settings
import numpy
from PIL import Image, ImageDraw, ImageFont, ImageOps
import rembg


class ImageProcessingError(Exception):
    pass


class ImageProcessor:

    @staticmethod
    def validateAndResizePhotograph(fp: str | bytes | Path) -> bytes:
        EXPECTED_WIDTH: Final[int] = 600
        EXPECTED_HIGHT: Final[int] = 600
        # higher is better, but coste more processing
        RESIZE_ACCURACY: Final[int] = 10
        CASCADE_PATH: Final[Path] = Path(cv2.__file__).parent.absolute(
        ) / 'data/haarcascade_frontalface_default.xml'

        # first image resizing
        image: Image = Image.open(fp)
        width, height = image.size
        ratio: int = 0

        if str(fp)[-19:] == "female_no_image.jpg":
            # Convert to JPEG and return image in bytes
            image_io: BytesIO = BytesIO()
            image = image.convert('RGB')
            image.save(image_io, format="JPEG", quality=100)
            return image_io.getvalue()

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

        size = (int(width / ratio), int(height / ratio))
        image: Image = image.resize(size)

        # Face detection
        # Validate the photograph (it has a person face)
        face_cascade = cv2.CascadeClassifier(str(CASCADE_PATH))
        gray = cv2.cvtColor(numpy.array(image), cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(
            gray,
            1.1,
            minNeighbors=10,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        if len(faces) == 1:
            x, y, width, height = faces[0]

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
        image.save(image_io, format="JPEG", quality=100)

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

        STATIC_ROOT: Path = settings.STATICFILES_DIRS[0]
        MEMBERSHIP_TEMPLATE: Path = settings.MEDIA_ROOT / \
            'templates/membership_template.jpg'
        FONTS_DIR: Path = STATIC_ROOT / 'fonts'

        # init
        image: Image = Image.open(fp)

        template: Image = Image.open(MEMBERSHIP_TEMPLATE)
        draw_interface: ImageDraw = ImageDraw.Draw(template)
        arabic_font = ImageFont.truetype(
            str(FONTS_DIR / "IBMPlexSansArabic-Regular.ttf"), 32)
        english_font = ImageFont.truetype(
            str(FONTS_DIR / "FiraSans-Regular.ttf"), 24)

        # Rounded image
        mask: Image = Image.new('L', image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + image.size, fill=255)
        image = ImageOps.fit(
            image, mask.size, centering=(0.5, 0.5))
        image.putalpha(mask)

        # Remove background from the image
        image = rembg.remove(image).resize((230, 230))

        # Put the rounded cleared bg image to the membership template
        template.paste(
            image,
            (41, 240),
            mask=image.convert('RGBA').split()[-1]
        )

        # name arabic
        name_ar_reshaped = get_display(
            arabic_reshaper.reshape(name_ar), base_dir='L')
        text_size = draw_interface.textlength(name_ar_reshaped, arabic_font)
        draw_interface.text((950 - text_size, 204),
                            name_ar_reshaped, font=arabic_font, fill=(0, 0, 0))

        # name english
        draw_interface.text((430, 257), name_en,
                            font=english_font, fill=(0, 0, 0))

        # city arabic
        city_ar_reshaped = get_display(
            arabic_reshaper.reshape(city_ar), base_dir='L')
        text_size = draw_interface.textlength(city_ar_reshaped, arabic_font)
        draw_interface.text((940 - text_size, 302),
                            city_ar_reshaped, font=arabic_font, fill=(0, 0, 0))

        # city english
        draw_interface.text((402, 315),
                            city_en, font=english_font, fill=(0, 0, 0))

        # membership type arabic
        membership_type_ar_reshaped = get_display(
            arabic_reshaper.reshape(membership_type_ar), base_dir='L')
        text_size = draw_interface.textlength(
            membership_type_ar_reshaped, arabic_font)
        draw_interface.text((857 - text_size, 375),
                            membership_type_ar_reshaped, font=arabic_font, fill=(0, 0, 0))

        # membership type english
        draw_interface.text((608, 380),
                            membership_type_en, font=english_font, fill=(0, 0, 0))

        # issue date
        draw_interface.text((615, 435), issue_date,
                            font=arabic_font, fill=(0, 0, 0))

        # card number
        draw_interface.text((525, 520), card_number,
                            font=arabic_font, fill=(255, 255, 255))

        # expire date
        draw_interface.text((480, 586), expire_date,
                            font=english_font, fill=(255, 255, 255))

        # Convert to JPEG and return image in bytes
        image_io: BytesIO = BytesIO()
        template = template.convert('RGB')
        template.save(image_io, format="JPEG", quality=100)

        return image_io.getvalue()

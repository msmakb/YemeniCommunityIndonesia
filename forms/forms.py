from copy import copy
from django import forms

from main import constants

form_classes: str = 'form-control shadow-sm rounded'


class TooltipSelect(forms.Select):
    def __init__(self, *args, **kwargs):
        self.tooltips = kwargs.pop('tooltips', {})
        super().__init__(*args, **kwargs)

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected,
                                       index, subindex=subindex, attrs=attrs)
        if value in self.tooltips:
            option['attrs']['title'] = self.tooltips[value]
        return option


class CustomFormItemForm(forms.Form):
    itemTypeChoices: list[tuple[str, str]] = copy(
        constants.CHOICES.CUSTOM_FORM_ITEM_TYPE)
    itemTypeChoices.insert(0, (None, "---------"))
    itemType: str = forms.ChoiceField(
        required=True,
        choices=itemTypeChoices,
        label="نوع الحقل",
        widget=forms.Select(
            attrs={
                'required': True,
                'class': form_classes,
            }
        ),
    )

    title: str = forms.CharField(
        required=False,
        label="السؤال",
        widget=forms.TextInput(
            attrs={
                'required': False,
                'class': form_classes,
                'placeholder': 'السؤال',
            }
        ),
    )

    description: str = forms.CharField(
        required=False,
        label="الوصف",
        widget=forms.TextInput(
            attrs={
                'required': False,
                'class': form_classes,
                'placeholder': 'الوصف',
            }
        ),
    )

    required: bool = forms.BooleanField(
        required=False,
        label="حقل مطلوب",
        widget=forms.CheckboxInput(
            attrs={
                "required": False,
                "class": "form-check-input check-box-ar-input",
            }
        ),
    )

    autofill: bool = forms.BooleanField(
        required=False,
        label="الملء التلقائي والتحقق من صحة الإدخال",
        widget=forms.CheckboxInput(
            attrs={
                "required": False,
                "class": "form-check-input check-box-ar-input",
            }
        ),
    )

    isHidden: bool = forms.BooleanField(
        required=False,
        label="إخفاء الحقل",
        widget=forms.CheckboxInput(
            attrs={
                "required": False,
                "disabled": True,
                "class": "form-check-input check-box-ar-input",
            }
        ),
    )

    headerImg: str = forms.ImageField(
        required=False,
        label="صورة العنوان",
        widget=forms.FileInput(
            attrs={
                "required": False,
                "class": form_classes,
                'accept': '.png, .jpeg, .jpg',
            }
        ),
    )

    file_types: list[tuple[str, str]] = [
        (".bmp, .dib, .gif, .heic, .heif, .jfif, .pjpeg, .jpeg, .pjp, .jpg, .png, .tiff, .tif, .ico, .webp", "صورة"),
        (".pdf", "PDF"),
        (".pdf, .bmp, .dib, .gif, .heic, .heif, .jfif, .pjpeg, .jpeg, .pjp, .jpg, .png, .tiff, .tif, .ico, .webp", "صورة/PDF"),
        (".docm, .dotm, .odt, .docx, .dotx, .text, .txt, .dot, .doc", "مستند"),
        (".xls, .xlsm, .xlsm, .xltm, .xltm, .ods, .xlsx, .xltx, .csv", "جدول بيانات"),
        (".3gp, .3g2, .avi, .m4v, .mp4, .mpg, .mpeg, .ogm, .ogv, .mov, .webm, .m4v, .mkv, .asx, .wm, .wmv, .wvx, .avi", "فيديو"),
        (".ppt, .pptm, .ppsm, .potm, .odp, .pptx, .ppsx, .potx", "عرض تقديمي"),
        (".flac, .mid, .mp3, .m4a, .opus, .ogg, .oga, .wav", "صوت"),
        (".*", "كل الملفات"),
    ]

    fileType: str = forms.ChoiceField(
        required=False,
        choices=file_types,
        label="نوع الملف",
        widget=TooltipSelect(
            tooltips={i[0]: i[0].replace(".", "*.") for i in file_types},
            attrs={
                'required': False,
                'class': form_classes,
            }
        ),
    )

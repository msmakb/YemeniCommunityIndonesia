from django import forms
from django.template.loader import render_to_string

from main import constants

from .models import Attachment, EmailBroadcast

form_classes: str = 'form-control shadow-sm rounded'


class EmailBroadcastForm(forms.ModelForm):
    to_choices: list[tuple[str, str]] = [
        ("ALL", "الكل"),
        ("MEMBERS", "الأعضاء فقط"),
        ("NON-MEMBERS", "غير الأعضاء فقط"),
        ("STUDENTS", "الطلاب فقط"),
    ]
    to = forms.ChoiceField(
        label="إرسال إلى",
        choices=to_choices,
        initial='ALL',
        widget=forms.Select(
            attrs={
                'required': True,
                'class': form_classes,
            }
        )
    )
    body = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'required': True,
                'class': form_classes,
                'rows': 20,
                'placeholder': 'محتوى البرودكاست',
            }
        ),
        initial='\n\n\n'+render_to_string(constants.TEMPLATES.EMAIL_FOOTER_TEMPLATE),
        label='محتوى البرودكاست',
    )
    
    class Meta:
        model = EmailBroadcast
        fields = [
            'subject',
            'body',
            'email_list',
        ]
        widgets = {
            'subject': forms.TextInput(
                attrs={
                    'required': True,
                    'class': form_classes,
                    'placeholder': 'الموضوع',
                }
            ),
            'email_list': forms.HiddenInput(
                attrs={
                    'required': True,
                }
            ),
        }
        labels = {
            'subject': 'الموضوع',
        }


class AttachmentForm(forms.ModelForm):
    
    class Meta:
        model = Attachment
        fields = [
            'file_name',
            'content',
            'mimetype',
            'email_broadcast',
        ]
        widgets = {
            'file_name': forms.TextInput(
                attrs={
                    'required': True,
                    'class': form_classes,
                    'placeholder': 'اسم الملف',
                }
            ),
            'content': forms.FileInput(
                attrs={
                    'required': False,
                    'class': form_classes,
                    'accept': '.avi, .jpeg, .jpg, .mp4, .mp3, ' 
                        + '.png, .pdf, .rar, .txt, .wav, '
                        + '.xls, .xlsx, .ppt, .pptx'
                }
            ),
            'mimetype': forms.Select(
                attrs={
                    'required': True,
                    'class': form_classes,
                }
            ),
            'email_broadcast': forms.HiddenInput(
                attrs={
                    'required': True,
                }
            ),
        }
        labels = {
            'file_name': 'اسم الملف',
            'content': 'الملف',
            'mimetype': 'نوع الملف',
        }


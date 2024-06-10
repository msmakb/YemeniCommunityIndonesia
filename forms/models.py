from typing import Any

from django.db import models

from main import constants
from main.models import BaseModel


class CustomFormItem(BaseModel):
    formId: str = models.CharField(max_length=255)
    index: int = models.SmallIntegerField(default=-1)
    itemId: str = models.CharField(max_length=10)
    itemType: str = models.CharField(
        max_length=15, choices=constants.CHOICES.CUSTOM_FORM_ITEM_TYPE)
    title: str = models.CharField(max_length=255)
    description: str = models.TextField(blank=True, null=True)
    itemData: dict[str, Any] = models.JSONField()


class CustomFormResponse(BaseModel):
    responseId: str = models.CharField(max_length=255)
    answers: dict[str, Any] = models.JSONField()

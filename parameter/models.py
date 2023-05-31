import logging

from django.db import models
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.core.validators import validate_email

from main.models import BaseModel
from main import constants

logger = logging.getLogger(constants.LOGGERS.MODELS)


class Parameter(BaseModel):
    """ 
    ---------------------------------------------------------
    #       There is no setters for parameter model         #
    #   Parameters can be set when the table is created     #
    #                see main.signals.py                    #
    #     And only can be modified via admin dashboard      #
    ---------------------------------------------------------
    """

    _name: str = models.CharField(max_length=50, editable=False,
                                  db_column='name', name='name')
    _value: str = models.CharField(max_length=50, db_column='value',
                                   name='value')
    _access_type: str = models.CharField(max_length=1, editable=False,
                                         db_column='access_type', name='access_type',
                                         choices=constants.CHOICES.ACCESS_TYPE,
                                         default=constants.ACCESS_TYPE.No_ACCESS)
    _parameter_type: str = models.CharField(max_length=1, editable=False,
                                            db_column='parameter_type', name='parameter_type',
                                            choices=constants.CHOICES.DATA_TYPE,
                                            default=constants.DATA_TYPE.STRING)
    _description: str = models.CharField(max_length=255, db_column='description',
                                         name='description', editable=False,
                                         null=True, blank=True)

    def __str__(self) -> str:
        name: str = self.name
        return name.replace('_', ' ').capitalize()
    
    @property
    def getDescription(self) -> str:
        if self.description.endswith("."):
            return self.description[:-1]
        return self.description

    @property
    def getValue(self) -> str:
        return self.value

    @property
    def getParameterType(self) -> str:
        return self.parameter_type

    @property
    def getInputType(self) -> str:
        match self.getParameterType:
            case constants.DATA_TYPE.INTEGER:
                return "number"
            case constants.DATA_TYPE.FLOAT:
                return "number"
            case constants.DATA_TYPE.BOOLEAN:
                return "checkbox"
            case constants.DATA_TYPE.EMAIL:
                return "email"
            case _:
                return "text"
    
    @property
    def getCheckboxValue(self) -> str:
        if self.getParameterType == constants.DATA_TYPE.BOOLEAN:
            true_con: tuple[bool, ...] = (
                self.getValue.lower() == 'yes',
                self.getValue.lower() == 'true',
                self.getValue == '1',
            )
            false_con: tuple[bool, ...] = (
                self.getValue.lower() == 'no',
                self.getValue.lower() == 'false',
                self.getValue == '0'
            )
            if any(true_con):
                return True
            elif any(false_con):
                return False
        return ""

    def clean(self) -> None:
        val: str = self.getValue
        match self.getParameterType:
            case constants.DATA_TYPE.INTEGER:
                try:
                    int(val)
                except ValueError:
                    raise ValidationError(
                        "Sorry, the value must be a integer.")
            case constants.DATA_TYPE.FLOAT:
                try:
                    float(val)
                except ValueError:
                    raise ValidationError("Sorry, the value must be a number.")
            case constants.DATA_TYPE.BOOLEAN:
                con: tuple[bool, ...] = (
                    val.lower() == 'yes',
                    val.lower() == 'no',
                    val.lower() == 'true',
                    val.lower() == 'false',
                    val == '1',
                    val == '0'
                )
                if not any(con):
                    raise ValidationError("Sorry, the value must be "
                                          + "('true' or 'false', 'yes' or 'no', '1' or '0')")
            case constants.DATA_TYPE.EMAIL:
                validate_email(val)

        return super().clean()

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        logger.info(f"Saving parameter '{self.name}' in cache")
        cache.set(self.name, self, constants.DEFAULT_CACHE_EXPIRE)

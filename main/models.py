from __future__ import annotations
import logging
from typing import Optional

from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.cache import cache

from . import constants

logger = logging.getLogger(constants.LOGGERS.MODELS)


class BaseModel(models.Model):

    class Meta:
        abstract = True

    id: int = models.AutoField(primary_key=True)
    created: timezone.datetime = models.DateTimeField(auto_now_add=True)
    updated: timezone.datetime = models.DateTimeField(auto_now=True)

    def setCreated(self, created: timezone.datetime) -> None:
        self.created = created
        self.save()

    def setUpdated(self, updated: timezone.datetime) -> None:
        self.updated = updated
        self.save()

    @classmethod
    def create(cls, *args, **kwargs) -> BaseModel:
        return cls.objects.create(*args, **kwargs)

    @classmethod
    def get(cls, *args, **kwargs) -> BaseModel | None:
        """
        This will return None if there are multiple objects returned.
        """
        try:
            obj: BaseModel = cls.objects.get(*args, **kwargs)
            return obj
        except cls.MultipleObjectsReturned:
            return None

    @classmethod
    def getAll(cls) -> QuerySet[BaseModel]:
        """
        Get all objects stored in the database.
        """
        return cls.objects.all()

    @classmethod
    def getAllOrdered(cls, order_by: str, reverse: Optional[bool] = False) -> QuerySet[BaseModel]:
        """
        Get all objects and order them.
        """
        if reverse:
            order_by = '-' + order_by
        return cls.objects.all().order_by(order_by)

    @classmethod
    def getLastInsertedObject(cls, queryset: Optional[QuerySet[BaseModel]] = None) -> BaseModel | None:
        """
        Get the last object from the model or queryset if it was declared.
        """
        query: QuerySet[BaseModel] = queryset
        if queryset is not None:
            if not isinstance(queryset, QuerySet) or not isinstance(queryset.first(), cls):
                raise NotImplementedError
        else:
            query = cls.objects.all()
        try:
            return query.order_by('-id')[0]
        except IndexError:
            return None

    @classmethod
    def filter(cls, *args, **kwargs) -> QuerySet[BaseModel]:
        return cls.objects.filter(*args, **kwargs)

    @classmethod
    def countAll(cls) -> int:
        """
        Count all objects.
        """
        return cls.objects.all().count()

    @classmethod
    def countFiltered(cls, *arg, **kwarg) -> int:
        """
        Count the filtered queryset.
        """
        return cls.objects.filter(*arg, **kwarg).count()

    @classmethod
    def orderFiltered(cls, order_by: str, *args, reverse=False, **kwargs) -> QuerySet[BaseModel]:
        """
        Order the filtered queryset.
        """
        if reverse:
            order_by = '-' + order_by
        return cls.objects.filter(*args, **kwargs).order_by(order_by)

    @classmethod
    def isExists(cls, *arg, **kwarg) -> bool:
        """
        Tre if there is an object in the filtered queryset.
        """
        return cls.objects.filter(*arg, **kwarg).exists()


class Client(BaseModel):

    class Meta:
        abstract = True

    user_agent: str = models.CharField(max_length=256, null=True, blank=True)
    ip: str = models.GenericIPAddressField()

    def setUserAgent(self, user_agent: str) -> None:
        self.user_agent = user_agent
        self.save()

    def setIp(self, ip: str) -> None:
        self.ip = ip
        self.save()


class BlockedClient(Client):

    block_type: str = models.CharField(max_length=1,
                                       choices=constants.CHOICES.BLOCK_TYPE)
    blocked_times: int = models.PositiveSmallIntegerField(default=1)

    def __str__(self) -> str:
        return f"IP: {self.ip} - User Agent: {self.user_agent}"

    def setBlockType(self, block_type: str) -> None:
        self.block_type = block_type
        self.save()

    def setBlockedTimes(self, blocked_times: int) -> None:
        self.blocked_times = blocked_times
        self.save()


class AuditEntry(Client):

    action: str = models.CharField(
        max_length=1, choices=constants.CHOICES.ACTION)
    username: str = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f'{self.action} - {self.username} - {self.ip}'

    @property
    def action_type(self) -> str:
        return constants.ACTION_STR[int(self.action)].replace('_', ' ').capitalize()
    
    @classmethod
    def getLastAuditEntry(self) -> QuerySet[AuditEntry]:
        result: QuerySet[AuditEntry] | None = cache.get(
            constants.CACHE.LAST_AUDIT_ENTRY_QUERYSET)
        if not result:
            from .parameters import getParameterValue
            logger.info("Fetching last audit entry queryset from database.")
            start_chunk_object_id: int = getParameterValue(
                constants.PARAMETERS.MAGIC_NUMBER)
            result = AuditEntry.filter(
                id__gte=start_chunk_object_id)
            cache.set(constants.CACHE.LAST_AUDIT_ENTRY_QUERYSET, result, 
                      constants.DEFAULT_CACHE_EXPIRE)
        
        return result

    def setAction(self, action: str) -> None:
        self.action = action
        self.save()

    def setUsername(self, username: str) -> None:
        self.username = username
        self.save()


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
    def getValue(self) -> str:
        return self.value

    @property
    def getParameterType(self) -> str:
        return self.parameter_type

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

        return super().clean()

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        logger.info(f"Saving parameter '{self.name}' in cache")
        cache.set(self.name, self, constants.DEFAULT_CACHE_EXPIRE)

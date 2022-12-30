import logging
from logging import Logger

from django.db.models.query import QuerySet
from django.utils import timezone

from . import constants
from .models import AuditEntry, Parameter
from .parameters import getParameterValue

logger: Logger = logging.getLogger(constants.LOGGERS.MAIN)


def setMagicNumber():
    """
    # ------------------------------------------------------------- #
    # This is the last object that is not included of the specified #
    # period of allowed logged in attempts reset                    #
    # Ex. if the parameter 'ALLOWED_LOGGED_IN_ATTEMPTS_RESET'       #
    # set to 7 days, the last object that will be reset, It will be #
    # saved in the in 'MAGIC_NUMBER' parameter, to make the search  #
    # in the table 'AuditEntry' faster and more scalable            #
    # ------------------------------------------------------------- #
    """
    logger.info('=========== CRON START SETTING MAGIC NUMBER ===========')
    magic_number: int = getParameterValue(constants.PARAMETERS.MAGIC_NUMBER)
    reset_days: int = getParameterValue(
        constants.PARAMETERS.ALLOWED_LOGGED_IN_ATTEMPTS_RESET)
    last_audit_entry: QuerySet[AuditEntry] = AuditEntry.filter(
        id__gte=magic_number,
        created__range=(timezone.now() - timezone.timedelta(days=reset_days),
                        timezone.now()))
    try:
        magic_number = last_audit_entry[0].id
    except IndexError:
        try:
            magic_number = AuditEntry.getLastInsertedObject().id
        except AttributeError:
            magic_number = 1

    # cleanup unsuspicious post requests
    normal_posts: QuerySet[AuditEntry] = AuditEntry.filter(
        id__lt=magic_number,
        action=constants.ACTION.NORMAL_POST)
    for post in normal_posts:
        post.delete()

    # This is the only time which a parameter updated in code
    pram = Parameter.get(name=constants.PARAMETERS.MAGIC_NUMBER)
    pram.value = magic_number  # NOQA
    pram.save()
    logger.info(f'Magic Number Updated to [{magic_number}].')
    logger.info('=========== CRON FINISH SETTING MAGIC NUMBER ===========')

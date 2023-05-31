from logging import Logger, getLogger

from main import constants

logger: Logger = getLogger(constants.LOGGERS.PARAMETER)

def createParameters(**kwargs):
    from .service import _saveDefaultParametersToDataBase
    _saveDefaultParametersToDataBase()
    logger.info("All default parameters was successfully created.")

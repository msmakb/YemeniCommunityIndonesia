from dataclasses import asdict
import logging as logging
from logging import Logger
from typing import Union

from django.core.cache import cache

from main.constants import DATA_TYPE, LOGGERS, DEFAULT_CACHE_EXPIRE

from .models import Parameter as _parameter
from .models import ImageParameter as _ImageParameter
from .default_parameters import _getDefaultParam

logger: Logger = logging.getLogger(LOGGERS.PARAMETER)


def _saveDefaultParametersToDataBase() -> None:
    # This executed when a parameter added after migrate
    for pram in _getDefaultParam():
        if pram.name == "TEST":
            continue
        if not _parameter.isExists(name=pram.name):
            logger.info(f"==== The default parameter {pram.name}"
                        + " added to the database. ====")
            logger.info("Parameter Row: " + str(asdict(pram)))
            _parameter.create(**asdict(pram))


def getParameterValue(key: str) -> Union[str, int, float, bool]:
    if not isinstance(key, str):
        raise ValueError("The key must be a string.")
    try:
        param: _parameter | None = cache.get(key)
        if not param:
            logger.info(
                f"Parameter '{key}' is not cached, trying to retrieve it form database")
            param = _parameter.get(name=key)
            cache.set(key, param, DEFAULT_CACHE_EXPIRE)
        match param.getParameterType:
            case DATA_TYPE.INTEGER:
                value: int = int(param.getValue)
                return value
            case DATA_TYPE.FLOAT:
                value: float = float(param.getValue)
                return value
            case DATA_TYPE.BOOLEAN:
                val: str = param.getValue
                true_con: tuple[bool, ...] = (
                    val.lower() == 'yes',
                    val.lower() == 'true',
                    val == '1',
                )
                false_con: tuple[bool, ...] = (
                    val.lower() == 'no',
                    val.lower() == 'false',
                    val == '0',
                )
                if any(true_con):
                    return True
                elif any(false_con):
                    return False
                else:
                    raise ValueError("Non boolean value")
            case DATA_TYPE.IMAGE_FILE:
                val: str = param.getValue
                if val == "None":
                    return ""
                img_url: _ImageParameter | None = cache.get(
                    f'IMAGE_PARAMETER:{val}')
                if not img_url:
                    img_url = _ImageParameter.get(pk=int(val))
                    cache.set(f'IMAGE_PARAMETER:{val}', img_url, None)
                return img_url.content.url
            case _:
                return param.getValue
    except _parameter.DoesNotExist:
        if key != "TEST":
            logger.warning(f"The parameter [{key}] "
                           + "dose not exist in database!")
        for pram in _getDefaultParam():
            if key == pram.name:
                match pram.parameter_type:
                    case DATA_TYPE.INTEGER:
                        value: int = int(pram.value)
                        return value
                    case DATA_TYPE.FLOAT:
                        value: float = float(pram.value)
                        return value
                    case DATA_TYPE.BOOLEAN:
                        val: str = pram.value
                        true_con: tuple[bool, ...] = (
                            val.lower() == 'yes',
                            val.lower() == 'true',
                            val == '1',
                        )
                        false_con: tuple[bool, ...] = (
                            val.lower() == 'no',
                            val.lower() == 'false',
                            val == '0'
                        )
                        if any(true_con):
                            return True
                        elif any(false_con):
                            return False
                        else:
                            raise ValueError
                    case DATA_TYPE.IMAGE_FILE:
                        if pram.value == "None":
                            return ""
                        img_url: _ImageParameter = _ImageParameter.get(
                            pk=int(pram.value))
                        return img_url.content.url
                    case _:
                        return pram.value
        raise KeyError("The parameter does not exist in the database "
                       + "nor the default parameters.")

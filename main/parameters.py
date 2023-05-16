from dataclasses import dataclass
import logging as logging
from logging import Logger
from typing import Union

from django.core.cache import cache

from .constants import ACCESS_TYPE, DATA_TYPE, LOGGERS, DEFAULT_CACHE_EXPIRE
from .models import Parameter as _parameter

logger: Logger = logging.getLogger(LOGGERS.MAIN)


@dataclass
class _DefaultParameter:
    name: str
    value: str
    access_type: str
    parameter_type: str
    description: str


def _getDefaultParam() -> list[_DefaultParameter]:
    default_parameters: list[_DefaultParameter] = list()
    default_parameters.append(
        _DefaultParameter(
            name="ALLOWED_LOGGED_IN_ATTEMPTS",
            value="5",
            description="Allowed login attempts before the user get blocked from the site. Note: IT MUST BE AN INTEGER.",
            access_type=ACCESS_TYPE.ADMIN_ACCESS,
            parameter_type=DATA_TYPE.INTEGER
        )
    )
    default_parameters.append(
        _DefaultParameter(
            name="ALLOWED_LOGGED_IN_ATTEMPTS_RESET",
            value="1",
            description="This is the period of resetting the failed login attempt in days.  Note: IT MUST BE AN INTEGER.",
            access_type=ACCESS_TYPE.ADMIN_ACCESS,
            parameter_type=DATA_TYPE.INTEGER
        )
    )
    default_parameters.append(
        _DefaultParameter(
            name="MAX_TEMPORARY_BLOCK",
            value="5",
            description="The number of temporary blocks of failing to login before getting blocked forever. Note: IT MUST BE AN INTEGER.",
            access_type=ACCESS_TYPE.ADMIN_ACCESS,
            parameter_type=DATA_TYPE.INTEGER
        )
    )
    default_parameters.append(
        _DefaultParameter(
            name="TEMPORARY_BLOCK_PERIOD",
            value="1",
            description="The period of temporary block in days. Note: IT MUST BE AN INTEGER.",
            access_type=ACCESS_TYPE.ADMIN_ACCESS,
            parameter_type=DATA_TYPE.INTEGER
        )
    )
    default_parameters.append(
        _DefaultParameter(
            name="TIME_OUT_PERIOD",
            value="1440",
            description="Specifies the number of minutes before the Session time-out when logged in. The default is 1440 minutes, which is one day. Note: IT MUST BE AN INTEGER.",
            access_type=ACCESS_TYPE.ADMIN_ACCESS,
            parameter_type=DATA_TYPE.INTEGER
        )
    )
    default_parameters.append(
        _DefaultParameter(
            name="BETWEEN_POST_REQUESTS_TIME",
            value="500",
            description="This is the milliseconds countdown before allowing the to do anther post request (1000 milliseconds = 1 second). Note: IT MUST BE AN INTEGER.",
            access_type=ACCESS_TYPE.ADMIN_ACCESS,
            parameter_type=DATA_TYPE.INTEGER
        )
    )
    default_parameters.append(
        _DefaultParameter(
            name="MAGIC_NUMBER",
            value="1",
            description="DO NOT CHANGE THIS. THIS CONTROLLED BY THE SYSTEM ONLY.",
            access_type=ACCESS_TYPE.No_ACCESS,
            parameter_type=DATA_TYPE.INTEGER
        )
    )
    default_parameters.append(
        _DefaultParameter(
            name="MEMBERSHIP_EXPIRE_PERIOD",
            value="2",
            description="The expired period of the membership in years.",
            access_type=ACCESS_TYPE.ADMIN_ACCESS,
            parameter_type=DATA_TYPE.INTEGER
        )
    )
    default_parameters.append(
        _DefaultParameter(
            name="THREE_CHARACTER_PREFIX_FOR_MEMBERSHIP",
            value="YEM",
            description="The first 3 characters membership number starts with. It must not be more than 3"
            + " characters. It can be less than 3 characters and it can be empty so the membership number will have digits only",
            access_type=ACCESS_TYPE.ADMIN_ACCESS,
            parameter_type=DATA_TYPE.STRING
        )
    )
    default_parameters.append(
        _DefaultParameter(
            name="MEMBER_FORM_POST_LIMIT",
            value="1",
            description="The member form post limit per device within the Allowed logged in attempts reset period.",
            access_type=ACCESS_TYPE.ADMIN_ACCESS,
            parameter_type=DATA_TYPE.INTEGER
        )
    )
    default_parameters.append(
        _DefaultParameter(
            name="IMAGE_MAX_SIZE",
            value="4",
            description="The image max size accepted to be upload in Megabytes (MB).",
            access_type=ACCESS_TYPE.ADMIN_ACCESS,
            parameter_type=DATA_TYPE.INTEGER
        )
    )
    default_parameters.append(
        _DefaultParameter(
            name="REMOVE_BG_API_KEY",
            value="None",
            description="Remove background API key.",
            access_type=ACCESS_TYPE.ADMIN_ACCESS,
            parameter_type=DATA_TYPE.STRING
        )
    )
    default_parameters.append(
        _DefaultParameter(
            name="PLACEHOLDER_EMAIL",
            value="placeholder@example.com",
            description="This ensures that the email is properly delivered and avoids potential issues with spam filters or email clients.",
            access_type=ACCESS_TYPE.ADMIN_ACCESS,
            parameter_type=DATA_TYPE.STRING
        )
    )
    default_parameters.append(
        _DefaultParameter(
            name="OPEN_MEMBER_REGISTRATION_FORM",
            value="YES",
            description="This for opening and closing the registration form for new members. The value must be 'YES' or 'NO'.",
            access_type=ACCESS_TYPE.ADMIN_ACCESS,
            parameter_type=DATA_TYPE.BOOLEAN
        )
    )
    default_parameters.append(
        _DefaultParameter(
            name="TEST",
            value="TEST_PARAMETER",
            description="Just for testing propose.",
            access_type=ACCESS_TYPE.No_ACCESS,
            parameter_type=DATA_TYPE.STRING
        )
    )
    return default_parameters


def _saveDefaultParametersToDataBase() -> None:
    # This executed one time only, when parameters table is created
    for pram in _getDefaultParam():
        if pram.name == "TEST":
            continue
        if not _parameter.isExists(name=pram.name):
            logger.info(f"The default parameter {pram.name}"
                        + " added to the database.")
            _parameter.create(
                name=pram.name,
                value=pram.value,
                description=pram.description,
                access_type=pram.access_type,
                parameter_type=pram.parameter_type,
            )


def getParameterValue(key: str) -> Union[str, int, float, bool]:
    if not isinstance(key, str):
        raise ValueError("The key must be a string.")
    try:
        param: _parameter | None = cache.get(key)
        if not param:
            logger.info(f"Parameter '{key}' is not cached, trying to retrieve it form database")
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
                    val == '0'
                )
                if any(true_con):
                    return True
                elif any(false_con):
                    return False
                else:
                    raise ValueError
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
                    case _:
                        return pram.value
        raise KeyError("The parameter does not exist in the database "
                       + "nor the default parameters.")

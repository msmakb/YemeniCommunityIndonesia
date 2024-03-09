from dataclasses import dataclass
import logging as logging

from main.constants import ACCESS_TYPE, DATA_TYPE


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
            parameter_type=DATA_TYPE.EMAIL
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
            name="MEMBERSHIP_TRANSFER_INFO_IMAGE",
            value="None",
            description="The image showing in the payment page for the members, displaying the bank account info to received membership payments. THIS IMAGE MUST BE 1150X270.",
            access_type=ACCESS_TYPE.ADMIN_ACCESS,
            parameter_type=DATA_TYPE.IMAGE_FILE
        )
    )
    default_parameters.append(
        _DefaultParameter(
            name="REQUEST_MAX_LIMIT_PER_SECOND",
            value="50",
            description="The requests count allowed per second.",
            access_type=ACCESS_TYPE.No_ACCESS,
            parameter_type=DATA_TYPE.INTEGER
        )
    )
    default_parameters.append(
        _DefaultParameter(
            name="DEFAULT_PAYMENT_ACCOUNT",
            value="0",
            description="Default payment account number.",
            access_type=ACCESS_TYPE.ADMIN_ACCESS,
            parameter_type=DATA_TYPE.STRING
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

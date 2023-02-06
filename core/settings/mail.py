from os import environ

MAILING_IS_ACTIVE = True

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = "smtp.gmail.com"

EMAIL_PORT = 587

EMAIL_USE_TLS = True

EMAIL_HOST_USER = "yemenicommunityindonesia@gmail.com"

EMAIL_HOST_PASSWORD = "vqxwfapbmvhgdujn"  # environ.get('EMAIL_HOST_PASSWORD')

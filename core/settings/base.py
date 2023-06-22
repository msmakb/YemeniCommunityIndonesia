# Application definition
INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # System apps
    'main.apps.MainConfig',
    'member.apps.MemberConfig',
    'broadcast.apps.BroadcastConfig',
    'parameter.apps.ParameterConfig',
    'monitor.apps.MonitorConfig',
    'company_user.apps.CompanyUserConfig',
    'payment.apps.PaymentConfig',

    # Third party apps
    'django_crontab',
    'django_filters',
    'dbbackup',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'company_user.middleware.CacheUserMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # System Middleware
    'main.middleware.AllowedClientMiddleware',
    'main.middleware.SiteUnderMaintenanceMiddleware',
    'main.middleware.LoginRequiredMiddleware',
    'company_user.middleware.AllowedUserMiddleware',
    'main.middleware.ErrorHandlerMiddleware',
]

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

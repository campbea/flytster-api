from .settings import *


EMAIL_HOST = "localhost"
EMAIL_PORT = "1025"
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

TWILIO_ACCOUNT_ID = os.getenv('TEST_TWILIO_ACCOUNT_ID')
TWILIO_API_TOKEN = os.getenv('TEST_TWILIO_API_TOKEN')
TWILIO_NUMBER = os.getenv('TEST_TWILIO_NUMBER')

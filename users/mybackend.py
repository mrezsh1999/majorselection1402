from django.contrib.auth.backends import ModelBackend
from users.models import User


class MobileBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        mobile = kwargs.get('mobile')
        try:
            User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            pass
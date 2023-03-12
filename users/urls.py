from rest_framework import routers
from users.api import UserViewSet

router = routers.SimpleRouter()
router.register(r'user', UserViewSet, 'user')
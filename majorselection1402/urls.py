"""majorselection1402 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from majorselection1402 import settings
from users.urls import router as users_router
from booklet_information.urls import router as booklet_information_router

urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'api/v1/', include(users_router.urls)),
    path(r'api/v1/', include(booklet_information_router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
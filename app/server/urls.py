"""
URL configuration for tg_bot_master project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
import os
from django.conf import settings
from django.contrib import admin
from django.http import FileResponse, Http404
from django.urls import path, include, re_path


def serve_react(request, path=''):
    index_file = os.path.join(getattr(settings, 'WHITENOISE_ROOT', ''), 'index.html')
    if not os.path.exists(index_file):
        raise Http404
    return FileResponse(open(index_file, 'rb'), content_type='text/html')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('apps.users.urls')),
    path('api/bots/', include('apps.bots.urls')),
    path('api/scenarios/', include('apps.scenarios.urls')),
    path('api/chats/', include('apps.chats.urls')),
    re_path(r'^.*$', serve_react),
]

"""teadiagnose URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from imgUp.views import uploadImg, main, getStart, showDemo, showHtml, showHistory, feedback
# from iBp.views import ibpinterface

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', getStart),
    path('demopage/', showDemo),
    path('uploadImg/', uploadImg, name='uploadImg'),
    path('showImg/', main),
    path('showHistory/', showHistory),
    # path('showImg/', feedback),
    path('descript/<str:f>/', showHtml),
    path('showImg/<str:f>/', main),
    # path('iBpInterface/', ibpinterface),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



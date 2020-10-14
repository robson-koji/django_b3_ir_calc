"""django_b3_ir_calc URL Configuration

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

from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from django.conf.urls.static import static

from report import urls
from report.views import StockPriceView

urlpatterns = [

    path('', include('file_upload.urls')),    

    path('admin/', admin.site.urls),

    path('report/', include('report.urls')),
    path('file_upload/', include('file_upload.urls')),

    url(r'^stock_quotes/$', StockPriceView.as_view(), name='stock_quotes'),

    url(r'^accounts/', include('allauth.urls')),


]


# For static development
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Upload files
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

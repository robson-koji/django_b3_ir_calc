from django.urls import path
from .views import documents_home, redirect_view, upload_endorse_file

urlpatterns = [
    path('', documents_home, name='documents_home'),
    path('open_file/', redirect_view, name='open-file'),

    path('upload_endorse_file/', upload_endorse_file, name='upload_endorse_file'),



]

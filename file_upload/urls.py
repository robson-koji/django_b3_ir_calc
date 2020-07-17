from django.urls import path
from .views import my_view, redirect_view, upload_endorse_file

urlpatterns = [
    path('', my_view, name='my-view'),
    path('open_file/', redirect_view, name='open-file'),

    path('upload_endorse_file/', upload_endorse_file, name='upload_endorse_file'),



]

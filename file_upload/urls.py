from django.urls import path
from .views import my_view, redirect_view

urlpatterns = [
    path('', my_view, name='my-view'),
    path('open_file/', redirect_view, name='open-file')

]

from django.urls import path
from .views import *

urlpatterns = [
    path('', documents_home, name='documents_home'),
    path('open_file/', redirect_view, name='open-file'),

    path('upload_endorse_file/', upload_endorse_file, name='upload_endorse_file'),
    path('merge_files/', MergeFiles.as_view(), name='merge_files'),
    path('delete_files/', DeleteFiles.as_view(), name='delete_files'),
]

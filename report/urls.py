from django.conf.urls import url
from report.views import HistoryView, PositionView


urlpatterns = [
    url(r'^history/$', HistoryView.as_view(), name='history'),
    url(r'^position/$', PositionView.as_view(), name='position')
]

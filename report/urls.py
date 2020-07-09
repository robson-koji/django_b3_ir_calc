from django.conf.urls import url
from report.views import HistoryView, PositionView, Endorse_11


urlpatterns = [
    url(r'^history/$', HistoryView.as_view(), name='history'),
    url(r'^position/$', PositionView.as_view(), name='position'),
    url(r'^endorse/$', Endorse_11.as_view(), name='position')
]

from django.conf.urls import url
from report.views import HistoryView, HistoryDetailView, PositionView, Endorse11Download, Endorse11View


urlpatterns = [
    url(r'^history/$', HistoryView.as_view(), name='history'),
    url(r'^history/(?P<stock>.*)$', HistoryDetailView.as_view(), name='history_detail'),
    url(r'^position/$', PositionView.as_view(), name='position'),
    url(r'^endorse_download/$', Endorse11Download.as_view(), name='endorse_dwl'),
    url(r'^endorse/$', Endorse11View.as_view(), name='endorse'),
    url(r'^tech_analysis/$', Endorse11View.as_view(), name='tech_analysis')


]

from django.conf.urls import url
from django.urls import path

from report.views import HistoryView, HistoryDetailView, PositionView, Endorse11Download, Endorse11View
from django.views.generic import TemplateView


urlpatterns = [
    url(r'^history/$', HistoryView.as_view(), name='history'),
    url(r'^history/(?P<stock>.*)$', HistoryDetailView.as_view(), name='history_detail'),
    url(r'^position/$', PositionView.as_view(), name='position'),
    url(r'^endorse_download/$', Endorse11Download.as_view(), name='endorse_dwl'),
    url(r'^endorse/$', Endorse11View.as_view(), name='endorse'),
    url(r'^tech_analysis/$', Endorse11View.as_view(), name='tech_analysis'),
    # path('indices/', TemplateView.as_view(template_name='report/indices.html')),
]

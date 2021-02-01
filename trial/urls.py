from django.conf.urls import url
from django.urls import path

from trial.views import *


urlpatterns = [
    path('', TrialView.as_view(), name='trial'),
    path('logout/', TrialLogoutView.as_view(), name='trial_logout'),
    # path('indices/', TemplateView.as_view(template_name='report/indices.html')),
]

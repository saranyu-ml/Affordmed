from django.urls import path
from .views import CreateShortURL, RedirectURL, URLStatsView, index

urlpatterns = [
    path('', index, name='index'),
    path('shorturls/', CreateShortURL.as_view(), name='create_short_url'),
    path('<str:short_code>/', RedirectURL.as_view(), name='redirect_url'),
    path('shorturls/<str:short_code>/', URLStatsView.as_view(), name='url_stats'),
]
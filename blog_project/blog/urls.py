from django.urls import path
from .views import *

app_name = 'blog_app'

urlpatterns = [
    path('blogger', BloggerView.as_view(), name="blogger"),
    path('tistory', TistoryView.as_view(), name="tistory"),
    path('blogger/upload', BloggerUploadView.as_view(), name="upload"),
    path('tistory/token', TistoryTokenView.as_view()),
    path('tistory/upload', TistoryUploadView.as_view()),
]
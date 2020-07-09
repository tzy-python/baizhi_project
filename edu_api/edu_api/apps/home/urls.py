from django.urls import path

from home import views

urlpatterns = [
    path("banner/",views.BannerListAPIView.as_view()),
    path("navu/",views.NavUpListAPIView.as_view()),
    path("navd/",views.NavDownListAPIView.as_view()),
]
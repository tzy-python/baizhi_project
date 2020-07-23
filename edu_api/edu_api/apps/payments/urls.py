from django.urls import path

from payments import views

urlpatterns = [
    path('alipay/',views.AliPayAPIView.as_view()),
    path('result/',views.AliPayResultAPIView.as_view()),
]
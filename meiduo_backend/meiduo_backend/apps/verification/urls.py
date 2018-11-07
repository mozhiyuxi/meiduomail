from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'image_codes/(?P<image_code_id>.+)/$', views.ImageCodeView.as_view()),
    url(r'sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SmsCodes.as_view()),
    url(r'accounts/(?P<account>\w{5,20})/sms/token/', views.SMSCodeTokenView.as_view()),
    url(r'sms_codes/$', views.SMSCodeByTokenView.as_view()),
]
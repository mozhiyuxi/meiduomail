from django.conf.urls import url

from rest_framework_jwt.views import obtain_jwt_token

from . import views

urlpatterns = [
    url(r'usernames/(?P<username>\w{5,20})/count/', views.UsernameCountView.as_view()),
    url(r'mobiles/(?P<mobile>1[345789]\d{9})/count/', views.MobileCountView.as_view()),
    url(r'^users/$', views.CreateUserView.as_view()),
    url(r'authorizations/$', obtain_jwt_token),
    url(r'accounts/(?P<account>\w{5,20})/password/token/$', views.PasswordTokenView.as_view()),
    url(r'users/(?P<pk>\d+)/password/$', views.ResetPasswordView.as_view()),
]
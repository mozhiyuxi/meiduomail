from django.conf.urls import url,include
from rest_framework.routers import DefaultRouter

from .views import AreasViewSet

router = DefaultRouter()
router.register(r'areas', AreasViewSet, base_name='areas')

urlpatterns = [
   # url(r'^', include(router.urls))
]

urlpatterns += router.urls
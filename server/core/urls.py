from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# router.register(r"example-path", ExampleView, basename="example-basename") Example View

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
]

from django.urls import path

from .views import PackageListView, PackageDetailView


urlpatterns = [
    path('', PackageListView.as_view(), name='package-list'),
    path('<int:pk>/', PackageDetailView.as_view(), name='package-detail'),
]

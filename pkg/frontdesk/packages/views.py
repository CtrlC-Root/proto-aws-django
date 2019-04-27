from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from .models import Carrier, Package


class PackageListView(ListView):
    model = Package


class PackageDetailView(DetailView):
    model = Package

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.http import HttpResponseRedirect

from .models import Carrier, Package
from .tasks import fetch_package_status


class PackageListView(ListView):
    model = Package


class PackageDetailView(DetailView):
    model = Package

    def post(self, *args, **kwargs):
        # retrieve the package and start the task
        package = self.get_object()
        task = fetch_package_status.delay(package.id)

        # wait a little bit for the task to complete in case it
        # doesn't take long so we can show the result right away
        task.get(timeout=5)

        # redirect back to the same page
        return HttpResponseRedirect(self.request.path_info)

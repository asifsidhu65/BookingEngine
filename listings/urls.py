from django.urls import path

from listings.views import FetchAvailableUnitsApiView

urlpatterns = [
    path('v1/units/', FetchAvailableUnitsApiView.as_view())
]
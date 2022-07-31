from django.urls import path
from .views import get_patients, get_surgery_avg_time

urlpatterns = [
    path("patients", get_patients),
    path("average_surgery_time", get_surgery_avg_time),
]

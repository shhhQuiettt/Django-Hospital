from django.views import generic
from .models import Patient, Surgery
from django.shortcuts import render
from django.db.models import Avg, F
from django.db.models.functions import ExtractSecond


def get_patients(request):
    rows = Patient.objects.all()
    query = rows.query

    return render(request, "hospital/index.html", {"query": query, "rows": rows})


def get_surgery_avg_time(request):
    # TODO: make it work
    rows = Surgery.objects.aggregate(
        avrage_time=Avg(
            ExtractSecond(F("start_endetime")) - ExtractSecond(F("d_datetime"))
        )
    )
    # query = rows.query
    query = None

    return render(
        request, "hospital/index.html", {"query": query, "rows": {rows["avrage_time"]}}
    )


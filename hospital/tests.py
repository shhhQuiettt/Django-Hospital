from hospital import queries
from hospital.models import Diagnosis, Doctor, Patient, Surgery
from hospital.utils import CustomTestCase
from datetime import datetime
from datetime import timedelta
from django.db.models import (
    Max,
    Avg,
    Min,
    Count,
    DurationField,
    ExpressionWrapper,
    fields,
    F,
)
from django.db import connection


class HospitalTests(CustomTestCase):
    fixtures = ["initial_data"]

    def test_all_patients(self):
        """A completed example. Change the firstmode argument of the assert,
        Patient.objects.all(), to make the test fail.
        """
        self.assertQuerysetEqual(
            Patient.objects.all(),
            queries.all_patients(),
        )

    def test_all_doctors(self):
        """Retrieve every doctor."""
        self.assertQuerysetEqual(
            Doctor.objects.all(),
            queries.all_doctors(),
        )

    def test_meredith_grey(self):
        """Retrieve only the doctor Meredith Grey."""
        self.assertQuerysetEqual(
            Doctor.objects.filter(first_name="Meredith", last_name="Grey"),
            queries.meredith_grey(),
        )

    def test_all_attendings(self):
        """Retrieve the doctors who are attendings."""
        self.assertQuerysetEqual(
            Doctor.objects.filter(position=Doctor.ATTENDING),
            queries.all_attendings(),
        )

    def test_deceased_patients(self):
        """Retrieve patients who died."""
        self.assertQuerysetEqual(
            Patient.objects.filter(survived=False),
            queries.deceased_patients(),
        )

    def test_patients_unknown_last_name(self):
        """Retrieve patients whose last name isn't known.."""
        self.assertQuerysetEqual(
            Patient.objects.filter(last_name=""),
            queries.patients_unknown_last_name(),
        )

    def test_procedure_contains_surgery_case_insensitive(self):
        """Working with field lookups.
        https://docs.djangoproject.com/en/3.1/ref/models/querysets/#field-lookups

        Retrieve surgeries in which the procedure includes the word 'surgery',
        ignoring case.
        """
        self.assertQuerysetEqual(
            Surgery.objects.filter(procedure__contains="surgery"),
            queries.procedure_contains_surgery_case_insensitive(),
        )

    def test_procedure_contains_surgery_case_sensitive(self):
        """Retrieve surgeries in which the procedure includes the word 'Surgery',
        case sensitive.
        """
        self.assertQuerysetEqual(
            Surgery.objects.filter(procedure__icontains="Surgery"),
            queries.procedure_contains_surgery_case_sensitive(),
        )

    def test_patients_with_certain_first_names(self):
        """Retrieve patients who have any of these names: Katie, Kevin, Rick."""
        self.assertQuerysetEqual(
            Patient.objects.filter(first_name__in=["Katie", "Kevin", "Rick"]),
            queries.patients_with_certain_first_names(),
        )

    def test_doctors_born_in_certain_years(self):
        """Retrieve doctors born in any of these years: 1954, 1973."""
        self.assertQuerysetEqual(
            Doctor.objects.filter(birth_year__in=[1954, 1973]),
            queries.doctors_born_in_certain_years(),
        )

    def test_interns_born_after_1978(self):
        """Retrieve doctors who are interns born after 1978."""
        self.assertQuerysetEqual(
            Doctor.objects.filter(birth_year__gt=1978, position="INT"),
            queries.interns_born_after_1978(),
        )

    def test_surgeries_on_10_apr_2005_starting_before_noon(self):
        """Retrieve surgeries that happened on 10 April 2005 and started before
        12 noon.
        """
        start_date = datetime(2005, 4, 10, 0, 0, 0)
        end_date = datetime(2005, 4, 10, 11, 59, 59)
        self.assertQuerysetEqual(
            Surgery.objects.filter(start_datetime__range=(start_date, end_date)),
            queries.surgeries_on_10_apr_2005_starting_before_noon(),
        )

    def test_baileys_surgeries(self):
        """Spanning relationships
        https://docs.djangoproject.com/en/3.1/topics/db/queries/#lookups-that-span-relationships

        Retrieve all of Dr Bailey's surgeries.
        """
        queryset = Surgery.objects.filter(doctors__last_name="Bailey")
        self.assertQuerysetEqual(
            queryset,
            queries.baileys_surgeries(),
        )

    def test_cardiothoracic_surgeries(self):
        """Retrieve all surgeries carried out by a cardiolog"""

        queryset = Surgery.objects.filter(doctors__speciality="CAR")
        self.assertQuerysetEqual(
            queryset,
            queries.cardiothoracic_surgeries(),
        )

    def test_shepherds_patients(self):
        """Retrieve patients treated by Dr Shepherd.

        Tip: patients can have >1 surgery.
        """

        queryset = Patient.objects.filter(
            surgery__doctors__last_name="Shepherd"
        ).distinct()
        self.assertQuerysetEqual(
            queryset,
            queries.shepherds_patients(),
        )

    def test_number_deceased_patients(self):
        """Counting, aggregating and annotating.

        How many patients died?
        """

        dead = Patient.objects.filter(survived=False).count()
        self.assertEqual(
            dead,
            queries.number_deceased_patients(),
        )

    def test_number_of_diagnoses_jerry_frost(self):
        """How many diagnoses were received by the patient Jerry Frost?"""

        number = Diagnosis.objects.filter(
            patient__first_name__exact="Jerry", patient__last_name="Frost"
        ).count()

        self.assertEqual(
            number,
            queries.number_of_diagnoses_jerry_frost(),
        )

    def test_earliest_birth_year_of_doctors(self):
        """The doctors' records contain birth years. What is the earliest birth year?"""
        query = Doctor.objects.aggregate(Min("birth_year"))
        self.assertEqual(
            query,
            queries.earliest_birth_year_of_doctors(),
        )

    def test_largest_number_of_diagnoses(self):
        """What is the largest number of diagnoses received by a patient?"""
        query = Patient.objects.annotate(num_diagnoses=Count("diagnosis")).aggregate(
            Max("num_diagnoses")
        )

        self.assertEqual(
            query,
            queries.largest_number_of_diagnoses(),
        )

    def test_average_duration_all_surgeries(self):
        """What is the average duration of all surgeries?

        Tip: if you're using SQLite, the default database, you'll need to use an
        ExpressionWrapper.
        """
        avg_time = Surgery.objects.annotate(
            duration=ExpressionWrapper(
                F("end_datetime") - F("start_datetime"),
                output_field=DurationField(),
            ),
        ).aggregate(Avg("duration"))

        self.assertEqual(
            avg_time,
            queries.average_duration_all_surgeries(),
        )

    def test_surgeries_longer_3hours(self):
        """Retrieve surgeries that were longer than 3 hours."""
        query = Surgery.objects.annotate(
            duration=ExpressionWrapper(
                F("end_datetime") - F("start_datetime"),
                output_field=DurationField(),
            ),
        ).filter(duration__gt=timedelta(hours=3))
        self.assertQuerysetEqual(
            query,
            queries.surgeries_longer_3hours(),
        )

import datetime
import uuid
from time import timezone

from django.db import models


# Create your models here.
class Institute(models.Model):
    serial = models.CharField(max_length=5, default="")
    name = models.CharField(max_length=30, default="")
    description = models.CharField(max_length=500, default="")
    address = models.CharField(max_length=200, default="")
    city = models.CharField(max_length=20, default="")
    fees = models.CharField(max_length=10, default="")
    mobile = models.CharField(max_length=15, default="")
    map = models.CharField(max_length=500, default="")
    category = models.CharField(max_length=20, default="")
    photo = models.ImageField(upload_to='institute_images')

    class Meta:
        db_table = "institute"

    def __str__(self):
        return self.name


class Registration(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    email = models.CharField(max_length=30)
    mobile = models.CharField(max_length=15)
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    zip = models.CharField(max_length=10)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE)
    fees = models.CharField(max_length=10)
    registration_id = models.CharField(max_length=100, unique=True, default="")
    txn_id = models.CharField(max_length=100, default="")
    txn_amount = models.CharField(max_length=10, default="")
    txn_date = models.CharField(max_length=20, default="")
    txn_status = models.CharField(max_length=100, default="")
    txn_msg = models.CharField(max_length=400, default="")

    class Meta:
        db_table = "registration"

    def __str__(self):
        return self.first_name + self.last_name


class Status(models.Model):
    registration_status = models.CharField(max_length=50)
    user = models.ForeignKey(Registration, on_delete=models.CASCADE)

    class Meta:
        db_table = "status"

    def __str__(self):
        return self.user.registration_id

class Contact(models.Model):
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    subject = models.CharField(max_length=100)
    message = models.CharField(max_length=500)

    class Meta:
        db_table = "contact"

    def __str__(self):
        return self.name





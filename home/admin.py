from django.contrib import admin

# Register your models here.
from .models import Institute, Registration, Status, Contact

admin.site.register(Institute)
admin.site.register(Registration)
admin.site.register(Status)
admin.site.register(Contact)
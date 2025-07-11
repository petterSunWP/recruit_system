from django.contrib import admin

# Register your models here.
from .models import (
    User, JobSeeker, Company,
    JobInfo, JobCategory, JobLocation,
    JobApplication
)

admin.site.register(User)
admin.site.register(JobSeeker)
admin.site.register(Company)
admin.site.register(JobInfo)
admin.site.register(JobCategory)
admin.site.register(JobLocation)
admin.site.register(JobApplication)


"""
URL configuration for car_rental_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from . import views
# 在 views.py 中

urlpatterns = [
    path("", views.index, name="index"),
    path("info/",views.jobseeker_info,name="jobseeker_info"),
    path('jobs/', views.jobseeker_jobs_view, name='jobseeker_jobs'),
    path('options/', views.job_options, name='job_options'),
    path('search-jobs/', views.search_jobs_api, name='search_jobs_api'),
    path('apply/', views.apply_job, name='apply_job'),
    path('my-applications/', views.get_applications, name='my_applications'),
    path('logout/', views.jobseeker_logout, name='jobseeker_logout'),
    path('messages/', views.jobseeker_messages, name='jobseeker_messages'),
]

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
    path("locations/", views.location_search, name='location_search'),
    path("Category/", views.category_search, name='category_search'),
    path("postJob/", views.post_job, name='post_job'),   
    path('jobs/', views.company_jobs, name='company_jobs'),
    path('jobs/<int:job_id>/toggle/', views.toggle_job_status, name='toggle_job_status'),
    path('jobs/<int:job_id>/', views.get_job_detail, name='get_job_detail'),
    path('jobs/<int:job_id>/edit/', views.edit_job, name='edit_job'),
    path('logout/', views.company_logout, name='company_logout'),
    path('applications/<int:job_id>/', views.job_applications, name='job_applications'),
    path('applications/<int:application_id>/schedule/', views.schedule_interview),
    path('update-application-status/', views.update_application_status),
]
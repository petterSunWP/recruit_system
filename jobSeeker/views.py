from django.shortcuts import render
import os
import time
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from core.models import JobSeeker, JobCategory, JobLocation, JobInfo, JobApplication
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.contrib.auth import logout
from django.shortcuts import redirect


# Create your views here.
def index(request):
   
    return render(request, "jobSeeker/index.html")


@csrf_exempt
@require_http_methods(["GET", "POST"])
def jobseeker_info(request):
    if request.method == 'GET':
        user_id = request.GET.get('user_id')
        if not user_id:
            return JsonResponse({'success': False, 'message': 'Missing user_id'}, status=400)

        try:
            seeker = JobSeeker.objects.get(user_id=user_id)
            return JsonResponse({
                'success': True,
                'name': seeker.name,
                'age': seeker.age,
                'university': seeker.university,
                'major': seeker.major,
                'cv_link': seeker.cv_link
            })
        except JobSeeker.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found'}, status=404)

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        name = request.POST.get('name')
        age = request.POST.get('age').strip()
        university = request.POST.get('university')
        major = request.POST.get('major')
        cv_file = request.FILES.get('cv')
        print(age,name,user_id,university,major,cv_file)


        try:
            seeker, created = JobSeeker.objects.get_or_create(
                user_id=user_id,
                defaults={
                    'name': name,
                    'age': int(age),
                    'university': university,
                    'major': major,
                    'cv_link': '',
                }
            )

            if not created:
                seeker.name = name
                seeker.age = int(age)
                seeker.university = university
                seeker.major = major

            if cv_file:
                subfolder = f'cv/user_{user_id}'
                ext = os.path.splitext(cv_file.name)[1]
                unique_filename = f'{int(time.time())}{ext}'
                path = os.path.join(subfolder, unique_filename)
                saved_path = default_storage.save(path, ContentFile(cv_file.read()))
                seeker.cv_link = default_storage.url(saved_path)
                print('[DEBUG] saved to:', saved_path)      
            seeker.save()
            return JsonResponse({'success': True, 'cv_link': seeker.cv_link})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

def jobseeker_jobs_view(request):
    user_id = request.GET.get('user_id')
    return render(request, 'jobseeker/jobs.html', {'user_id': user_id})



def job_options(request):
    categories = JobCategory.objects.all().values('id', 'name')
    locations = JobLocation.objects.all().values('id', 'name')
    return JsonResponse({
        'categories': list(categories),
        'locations': list(locations)
    })


def search_jobs_api(request):
    title = request.GET.get('title', '').strip()
    category_id = request.GET.get('category')
    location_id = request.GET.get('location')
    user_id = request.GET.get('user_id')

    if user_id and user_id.isdigit():
        user_id = int(user_id)
    else:
        user_id = None

    jobs = JobInfo.objects.select_related('category', 'location').filter(status='online')

    if title:
        jobs = jobs.filter(title__icontains=title)
    if category_id and category_id.isdigit():
        jobs = jobs.filter(category_id=int(category_id))
    if location_id and location_id.isdigit():
        jobs = jobs.filter(location_id=int(location_id))

    # ✅ 只查一次，获取该用户所有已投递 job_id
    applied_job_ids = set()
    if user_id:
        applied_job_ids = set(
            JobApplication.objects.filter(user_id=user_id).values_list('job_id', flat=True)
        )

    results = []
    for job in jobs:
        try:
            skills = json.loads(job.skills)
        except Exception:
            skills = []

        try:
            requirements = json.loads(job.requirements)
        except Exception:
            requirements = []

        results.append({
            'id': job.id,
            'title': job.title,
            'company_id': job.company_id,
            'category': job.category.name if job.category else '',
            'location': job.location.name if job.location else '',
            'hourly_wage': float(job.hourly_wage),
            'start_date': job.start_date.strftime('%Y-%m-%d'),
            'end_date': job.end_date.strftime('%Y-%m-%d'),
            'status': job.status,
            'skills': skills,
            'requirements': requirements,
            'description': job.description,
            'applied': job.id in applied_job_ids,  # ✅ 用集合判断效率极高
        })

    return JsonResponse({'jobs': results})




def apply_job(request):
    try:
        data = json.loads(request.body)
        job_id = data.get('job_id')
        user_id = data.get('user_id')  # 实际上传的是 user_id

        if not job_id or not user_id:
            return JsonResponse({'success': False, 'message': 'Missing job_id or user_id'}, status=400)

        # 查找 jobseeker_id
        try:
            jobseeker = JobSeeker.objects.get(user_id=user_id)
        except JobSeeker.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Jobseeker not found'}, status=404)

        jobseeker_id = jobseeker.id

        # 检查是否已投递过
        exists = JobApplication.objects.filter(job_id=job_id, jobseeker_id=jobseeker_id).exists()
        if exists:
            return JsonResponse({'success': False, 'message': 'You have already applied to this job.'})

        # 创建投递记录
        JobApplication.objects.create(
            user_id=user_id,
            job_id=job_id,
            jobseeker_id=jobseeker_id,
            applied_at=timezone.now(),
            status='pending',
        )

        return JsonResponse({'success': True, 'message': 'Application submitted.'})

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
    
    # views.py


def get_applications(request):
    user_id = request.GET.get('user_id')

    if not user_id or not user_id.isdigit():
        return JsonResponse({'success': False, 'message': 'Invalid user_id'}, status=400)

    user_id = int(user_id)

    # 查出该用户已投递的 job_id 列表
    applied_job_ids = JobApplication.objects.filter(user_id=user_id).values_list('job_id', flat=True)

    # 查出这些职位详情
    jobs = JobInfo.objects.filter(id__in=applied_job_ids).select_related('category', 'location')

    results = []
    for job in jobs:
        try:
            skills = json.loads(job.skills)
        except Exception:
            skills = []

        try:
            requirements = json.loads(job.requirements)
        except Exception:
            requirements = []

        results.append({
            'id': job.id,
            'title': job.title,
            'category': job.category.name if job.category else '',
            'location': job.location.name if job.location else '',
            'hourly_wage': float(job.hourly_wage),
            'start_date': job.start_date.strftime('%Y-%m-%d'),
            'end_date': job.end_date.strftime('%Y-%m-%d'),
            'skills': skills,
            'requirements': requirements,
            'description': job.description,
        })

    return JsonResponse({'jobs': results})


def jobseeker_logout(request):
    logout(request)
    return redirect('/')  # 或者跳转到你想去的首页

def jobseeker_messages(request):
    user_id = request.GET.get('user_id')
    if not user_id or not user_id.isdigit():
        return JsonResponse({'success': False, 'message': 'Missing user_id'}, status=400)

    applications = JobApplication.objects.filter(user_id=user_id).exclude(status='pending')

    data = []
    for app in applications:
        data.append({
            'status': app.status,
            'interview_time': app.interview_time.strftime('%Y-%m-%d %H:%M') if app.interview_time else '',
            'interview_note': app.interview_note,
        })

    return JsonResponse({'messages': data})



from django.shortcuts import render
from django.http import JsonResponse
from core.models import JobInfo, JobLocation, JobCategory, Company, JobApplication, JobSeeker
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_GET
from django.views.decorators.http import require_http_methods
from django.utils.dateparse import parse_date
from django.contrib.auth import logout
import json
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def index(request):
    
    return render(request, "company/index.html")


def location_search(request):
    query = request.GET.get('q', '')
    locations = JobLocation.objects.filter(name__icontains=query).values('id', 'name')[:20]
    data = [{'id': loc['id'], 'name': loc['name']} for loc in locations]
    return JsonResponse(data, safe=False)

def category_search(request):
    query = request.GET.get('q', '')
    category = JobCategory.objects.filter(name__icontains=query).values('id', 'name')[:20]
    data = [{'id': loc['id'], 'name': loc['name']} for loc in category]
    return JsonResponse(data, safe=False)




@csrf_exempt
@require_POST
def post_job(request):
    try:
        data = json.loads(request.body)

        user_id = data.get('user_id')
        title = data.get('title')
        description = data.get('description')
        location_id = data.get('location_id')
        category_id = data.get('category_id')
        hourly_wage = data.get('hourly_wage')
        start_date = parse_date(data.get('start_date'))
        end_date = parse_date(data.get('end_date'))
        skills = data.get('skills', [])
        requirements = data.get('requirements', [])

        # ✅ 校验必填字段
        if not all([user_id, title, location_id, category_id, start_date, end_date]):
            return JsonResponse({'success': False, 'message': 'Missing required fields.'})

        # ✅ 获取 company_id
        company = Company.objects.filter(user_id=user_id).first()
        if not company:
            return JsonResponse({'success': False, 'message': 'Company not found for user_id.'})

        # ✅ 创建 JobInfo
        JobInfo.objects.create(
            company_id=company.id,
            title=title,
            description=description,
            location_id=location_id,
            category_id=category_id,
            hourly_wage=hourly_wage,
            start_date=start_date,
            end_date=end_date,
            skills=json.dumps(skills),  # 存为 JSON 字符串
            requirements=json.dumps(requirements),
            status='offline',  # 初始状态设为 offline
        )

        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})

@require_GET
def company_jobs(request):
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')

    # 过滤职位
    jobs = JobInfo.objects.all()

    if search:
        jobs = jobs.filter(title__icontains=search)
    if status:
        jobs = jobs.filter(status=status)

    # 返回结果
    job_list = []
    for job in jobs.order_by('-created_at'):
        job_list.append({
            "id": job.id,  
            'title': job.title,
            'status': job.status,
            'location': job.location.name if job.location else 'N/A',
        })

    return JsonResponse({'jobs': job_list})

@require_POST
def toggle_job_status(request, job_id):
    try:
        job = JobInfo.objects.get(id=job_id)
        job.status = 'offline' if job.status == 'online' else 'online'
        job.save()
        return JsonResponse({'success': True, 'new_status': job.status})
    except JobInfo.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Job not found'}, status=404)
    
@require_GET
def get_job_detail(request, job_id):
    try:
        job = JobInfo.objects.get(id=job_id)
        return JsonResponse({
            'id': job.id,
            'title': job.title,
            'hourly_wage': str(job.hourly_wage),
            'start_date': job.start_date,
            'end_date': job.end_date,
            'location_id': job.location.id if job.location else None,
            'category_id': job.category.id if job.category else None,
            'description': job.description,
            'skills': json.loads(job.skills),
            'requirements': json.loads(job.requirements),
            'status': job.status
        })
    except JobInfo.DoesNotExist:
        return JsonResponse({'error': 'Job not found'}, status=404)



@csrf_exempt
@require_http_methods(["PUT"])
def edit_job(request, job_id):
    try:
        data = json.loads(request.body)

        # 1. 查找对应的 JobInfo 实例
        try:
            job = JobInfo.objects.get(id=job_id)
        except JobInfo.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Job not found'}, status=404)

        # 2. 收集并更新字段
        job.title = data.get('title', job.title)
        job.hourly_wage = data.get('hourly_wage', job.hourly_wage)
        job.start_date = data.get('start_date', job.start_date)
        job.end_date = data.get('end_date', job.end_date)
        job.description = data.get('description', job.description)

        # skills 和 requirements 是数组，需要序列化成 JSON 字符串
        job.skills = json.dumps(data.get('skills', []))
        job.requirements = json.dumps(data.get('requirements', []))

        location_id = data.get('location_id')
        if location_id:
            job.location = JobLocation.objects.get(id=location_id)

        category_id = data.get('category_id')
        if category_id:
            job.category = JobCategory.objects.get(id=category_id)


        # 3. 保存更新
        job.save()

        return JsonResponse({'success': True, 'message': 'Job updated successfully!'})

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)




@require_POST
def company_logout(request):
    logout(request)
    return JsonResponse({'success': True, 'redirect': '/'})  # 你可以跳转到首页或 /login/



def job_applications(request, job_id):
    if not job_id:
        return JsonResponse({'success': False, 'message': 'Missing job_id'}, status=400)

    applications = JobApplication.objects.filter(job_id=job_id)
    results = []

    for app in applications:
        seeker = JobSeeker.objects.filter(user_id=app.user_id).first()
        results.append({
            'application_id': app.id,
            'job_id': job_id,
            'name': seeker.name if seeker else '',
            'age': seeker.age if seeker else '',
            'university': seeker.university if seeker else '',
            'major': seeker.major if seeker else '',
            'cv_link': seeker.cv_link if seeker else '',
            'status': app.status,
            'interview_time': app.interview_time,
            'interview_note': app.interview_note,
        })

    return JsonResponse({'success': True, 'applications': results})




@csrf_exempt
def schedule_interview(request, application_id):
    if request.method == 'POST':
        try:
            app = JobApplication.objects.get(id=application_id)
            data = json.loads(request.body)
            app.status = 'interview'
            app.interview_time = data.get('interview_time')
            app.interview_note = data.get('interview_note')
            app.save()
            return JsonResponse({'success': True})
        except JobApplication.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Application not found'}, status=404)
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)



@csrf_exempt
def update_application_status(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            app_id = data.get('application_id')
            new_status = data.get('status')

            if not app_id or new_status not in ['pending', 'interview', 'rejected']:
                return JsonResponse({'success': False, 'message': 'Invalid data'}, status=400)

            app = JobApplication.objects.get(id=app_id)
            app.status = new_status
            app.save()

            return JsonResponse({'success': True})
        except JobApplication.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Application not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid method'}, status=405)


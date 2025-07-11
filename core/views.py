from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from core.models import User
import json
from django.http import JsonResponse

from django.http import JsonResponse
from django.db import IntegrityError
from django.contrib.auth.hashers import make_password
from django.contrib.auth import login
from .models import User
import json

from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt
import json
from core.models import User, Company  # ⚠️ 修改为你实际的导入路径

@csrf_exempt
def register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            role = data.get('role')
            company_name = data.get('company_name', '')
            address = data.get('address', '')

            # ✅ 1. 字段校验
            if not all([username, email, password, role]):
                return JsonResponse({'success': False, 'message': 'All fields are required.'})

            if role == 'company' and (not company_name or not address):
                return JsonResponse({'success': False, 'message': 'Company name and address are required.'})

            # ✅ 2. 唯一性校验
            if User.objects.filter(username=username).exists():
                return JsonResponse({'success': False, 'message': 'Username already exists.'})
            if User.objects.filter(email=email).exists():
                return JsonResponse({'success': False, 'message': 'Email already registered.'})

            # ✅ 3. 创建用户
            user = User.objects.create(
                username=username,
                password=make_password(password),
                email=email,
                is_jobseeker=(role == 'jobseeker'),
                is_company=(role == 'company'),
            )
            login(request, user)

            # ✅ 4. 如果是公司身份，保存公司信息
            if user.is_company:
                Company.objects.create(
                    user_id=user.id,  # 非外键关联
                    company_name=company_name,
                    address=address
                )

            # ✅ 5. 返回跳转地址
            if user.is_jobseeker:
                return JsonResponse({'success': True, 'redirect': f'/jobseeker/?user_id={user.id}&role=jobseeker'})
            elif user.is_company:
                return JsonResponse({'success': True, 'redirect': f'/company/?user_id={user.id}&role=company'})
            else:
                return JsonResponse({'success': True, 'redirect': '/'})


        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Registration failed: {str(e)}'})

    return  render(request, 'core/home.html')




from django.contrib.auth import authenticate, login
from django.http import JsonResponse
import json

def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        role = data.get('role')  # jobseeker or company

        user = authenticate(request, username=username, password=password)
        if user:
            if role == 'jobseeker' and user.is_jobseeker:
                login(request, user)
                return JsonResponse({
                    'success': True,
                    'redirect': f'/jobseeker/?user_id={user.id}&role=jobseeker'
                })
            elif role == 'company' and user.is_company:
                login(request, user)
                return JsonResponse({
                    'success': True,
                    'redirect': f'/company/?user_id={user.id}&role=company'
                })
            else:
                return JsonResponse({'success': False, 'message': 'Role mismatch'})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid credentials'})



from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    is_jobseeker = models.BooleanField(default=False)
    is_company = models.BooleanField(default=False)
    is_super_admin = models.BooleanField(default=False)
    email = models.EmailField(unique=True)

class JobSeeker(models.Model):
    user_id = models.IntegerField()  # 手动管理，不做外键
    name = models.CharField(max_length=255)
    age = models.PositiveIntegerField()
    university = models.CharField(max_length=255)   # 毕业院校
    major = models.CharField(max_length=255)        # 专业
    cv_link = models.URLField()


class Company(models.Model):
    user_id = models.IntegerField()  # 普通字段，不做外键
    company_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)

class JobCategory(models.Model):
    name = models.CharField(max_length=100)

class JobLocation(models.Model):
    name = models.CharField(max_length=100, unique=True)


class JobInfo(models.Model):
    company_id = models.IntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.ForeignKey('JobLocation', on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey('JobCategory', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    hourly_wage = models.DecimalField(max_digits=6, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    skills = models.TextField(help_text="存储 JSON 格式的字符串数组")
    requirements = models.TextField(help_text="岗位要求，存 JSON 数组")

    status = models.CharField(
        max_length=20,
        choices=[("offline", "Offline"), ("online", "Online")],
        default="offline"
    )

 


class JobApplication(models.Model):
    user_id = models.IntegerField()           # ✅ 谁投的（方便用户身份判断、权限校验）
    jobseeker_id = models.IntegerField()      # ✅ 对应简历（方便查简历详情）

    job_id = models.IntegerField()
    applied_at = models.DateTimeField(auto_now_add=True)

    status_choices = [
        ('pending', 'Pending'),
        ('interview', 'Interview Scheduled'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='pending')

    interview_time = models.DateTimeField(null=True, blank=True)
    interview_note = models.TextField(blank=True) # 补充说明、面试方式等


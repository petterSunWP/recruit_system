
from django.test import TestCase, Client
from core.models import Company, JobLocation, JobCategory, JobInfo
import json
from datetime import date

class CompanyViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.company = Company.objects.create(user_id=1, company_name="TestCo", address="123 Test St")
        self.location = JobLocation.objects.create(name="Wellington")
        self.category = JobCategory.objects.create(name="Engineering")

    def test_location_search(self):
        response = self.client.get('/company/locations/?q=well')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any("Wellington" in item['name'] for item in response.json()))

    def test_category_search(self):
        response = self.client.get('/company/Category/?q=Eng')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any("Engineering" in item['name'] for item in response.json()))

    def test_post_job_success(self):
        data = {
            "user_id": self.company.user_id,
            "title": "Software Engineer",
            "description": "Develop apps",
            "location_id": self.location.id,
            "category_id": self.category.id,
            "hourly_wage": 30,
            "start_date": "2025-08-01",
            "end_date": "2025-12-31",
            "skills": ["Python", "Django"],
            "requirements": ["Degree"]
        }
        response = self.client.post('/company/postJob/', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get("success"))

    def test_company_jobs_missing_user(self):
        response = self.client.get('/company/jobs/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json().get("success"))

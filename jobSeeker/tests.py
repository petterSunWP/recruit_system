
from django.test import TestCase, Client
from django.urls import reverse
from core.models import JobSeeker

class JobSeekerViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_id = 1
        self.seeker = JobSeeker.objects.create(
            user_id=self.user_id,
            name='John Doe',
            age=25,
            university='Test University',
            major='Computer Science',
            cv_link='http://example.com/cv.pdf'
        )

    def test_get_jobseeker_info_success(self):
        response = self.client.get('/jobseeker/info/', {'user_id': self.user_id})
        self.assertEqual(response.status_code, 200)
        self.assertIn('name', response.json())
        self.assertEqual(response.json()['name'], 'John Doe')

    def test_get_jobseeker_info_missing_user_id(self):
        response = self.client.get('/jobseeker/info/')
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])

    def test_get_jobseeker_info_not_found(self):
        response = self.client.get('/jobseeker/info/', {'user_id': 999})
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.json()['success'])

    def test_post_jobseeker_info_create(self):
        with open(__file__, 'rb') as fake_cv:
            response = self.client.post('/jobseeker/info/', {
                'user_id': 2,
                'name': 'Alice',
                'age': '22',
                'university': 'Another University',
                'major': 'Math',
                'cv': fake_cv,
            })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

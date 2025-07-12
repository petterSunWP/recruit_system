
from django.test import TestCase, Client
from core.models import User, Company

class RegisterViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_jobseeker_success(self):
        data = {
            'username': 'student1',
            'email': 'student1@example.com',
            'password': 'securepass123',
            'role': 'jobseeker'
        }
        response = self.client.post('/register/', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get('success'))
        self.assertIn('/jobseeker/', response.json().get('redirect', ''))

    def test_register_company_success(self):
        data = {
            'username': 'company1',
            'email': 'company1@example.com',
            'password': 'securepass123',
            'role': 'company',
            'company_name': 'TechCorp',
            'address': '123 Tech Street'
        }
        response = self.client.post('/register/', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get('success'))
        self.assertIn('/company/', response.json().get('redirect', ''))

    def test_register_missing_fields(self):
        data = {'username': 'incomplete'}
        response = self.client.post('/register/', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json().get('success'))
        self.assertIn('All fields are required.', response.json().get('message', ''))

    def test_register_duplicate_username(self):
        User.objects.create(username='takenuser', email='taken@example.com', password='hashed')
        data = {
            'username': 'takenuser',
            'email': 'new@example.com',
            'password': 'securepass',
            'role': 'jobseeker'
        }
        response = self.client.post('/register/', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json().get('success'))
        self.assertIn('Username already exists', response.json().get('message', ''))

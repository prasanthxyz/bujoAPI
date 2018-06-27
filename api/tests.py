from django.test import TestCase
from models import Entry
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from django.core.urlresolvers import reverse


class ModelTestCase(TestCase):
    """This class defines the test suite for the entry model."""

    def setUp(self):
        """Define the test client and other test variables."""
        self.entry_text = "Write code for BuJo API"
        self.user = User.objects.create_user(username='john', password='john')
        self.entry = Entry(text=self.entry_text, user=self.user)

    def test_model_can_create_an_entry(self):
        """Test the entry model can create an entry."""
        old_count = Entry.objects.count()
        self.entry.save()
        new_count = Entry.objects.count()
        self.assertNotEqual(old_count, new_count)


class ViewTestCase(TestCase):
    """Test suite for the api views."""

    def setUp(self):
        """Define the test client and other test variables."""
        self.client = APIClient()
        self.user = User.objects.create_user(username='john', password='john')
        self.entry_data = {'text': 'Write code for BuJo API'}

    def post(self):
        self.response = self.client.post(
            reverse('create'),
            self.entry_data,
            format="json")

    def test_api_can_create_an_entry(self):
        """Test the api has bucket creation capability."""
        self.client.login(username='john', password='john')
        self.post()
        self.client.logout()
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)
    
    def test_unauth_api_cannot_create_entry(self):
        """Test the api supports only authenticated users."""
        self.post()
        self.assertEqual(self.response.status_code, status.HTTP_401_UNAUTHORIZED)

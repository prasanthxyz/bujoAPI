from django.test import TestCase
from models import Entry
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from django.core.urlresolvers import reverse
from rest_framework.authtoken.models import Token


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

    def create_authenticated_entry(self):
        self.client.login(username='john', password='john')
        self.post()
        self.client.logout()

    def test_api_can_create_an_entry(self):
        """Test the api has entry creation capability."""
        self.create_authenticated_entry()
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)
    
    def test_unauth_api_cannot_create_entry(self):
        """Test the api supports only authenticated users."""
        self.post()
        self.assertEqual(self.response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_api_can_get_an_entry(self):
        """Test the api can get a given entry."""
        self.create_authenticated_entry()
        entry = Entry.objects.get()
        response = self.client.get(
            reverse('details',
            kwargs={'pk': entry.id}), format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, entry)

    def test_api_can_update_entry(self):
        """Test the api can update a given entry."""
        self.create_authenticated_entry()
        change_entry = {'text': 'Changed Entry'}
        entry = Entry.objects.get()

        res = self.client.put(
            reverse('details', kwargs={'pk': entry.id}),
            change_entry, format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_api_can_delete_entry(self):
        """Test the api can delete an entry."""
        self.create_authenticated_entry()
        entry = Entry.objects.get()
        response = self.client.delete(
            reverse('details', kwargs={'pk': entry.id}),
            format='json',
            follow=True)

        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEquals(Entry.objects.count(), 0)


class AuthTestCase(TestCase):
    """ Test suite for authentication """
    def setUp(self):
        self.client = APIClient()

    def test_user_gets_auth_token(self):
        old_token_count = Token.objects.count()
        User.objects.create_user(username='john', password='john')
        new_token_count = Token.objects.count()
        self.assertNotEqual(old_token_count, new_token_count)

    def test_user_auth_token(self):
        User.objects.create_user(username='john', password='john')

        # missing fields
        response = self.client.post(reverse('auth_token'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # wrong password
        response = self.client.post(
            reverse('auth_token'),
            { 'username': 'john', 'password': 'wrong' }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # success case
        response = self.client.post(
            reverse('auth_token'),
            { 'username': 'john', 'password': 'john' }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['token']), 40)
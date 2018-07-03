""" Entry App Tests """

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from api.models import Entry


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
        self.response = ''

    def login(self):
        """ Log in with valid credentials """
        self.client.login(username='john', password='john')

    def logout(self):
        """ Log out """
        self.client.logout()

    def post(self):
        """ Post data to the create entry endpoint """
        self.response = self.client.post(
            reverse('entry-list'),
            self.entry_data,
            format="json")

    def create_authenticated_entry(self):
        """ Create an entry after authentication """
        self.login()
        self.post()
        self.logout()

    def update_entry(self, entry_id):
        """ Update the entry with entry_id """
        change_entry = {'text': 'Changed Entry'}
        response = self.client.put(
            reverse('entry-detail', kwargs={'pk': entry_id}),
            change_entry, format='json'
        )
        return response

    def test_api_can_create_an_entry(self):
        """Test the api has entry creation capability."""
        self.create_authenticated_entry()
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)

    def test_api_can_get_all_entries(self):
        """Test the api can get all entries."""
        self.create_authenticated_entry()
        self.create_authenticated_entry()

        self.login()
        response = self.client.get(reverse('entry-list'), format="json")
        self.logout()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_api_can_get_an_entry(self):
        """Test the api can get a given entry."""
        self.create_authenticated_entry()
        entry = Entry.objects.get()
        self.login()
        response = self.client.get(
            reverse('entry-detail', kwargs={'pk': entry.id}),
            format="json")
        self.logout()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, entry)

    def test_api_can_update_entry(self):
        """Test the api can update a given entry."""
        self.create_authenticated_entry()
        entry = Entry.objects.get()

        self.login()
        response = self.update_entry(entry.id)
        self.logout()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_api_can_delete_entry(self):
        """Test the api can delete an entry."""
        self.create_authenticated_entry()
        entry = Entry.objects.get()

        self.login()
        response = self.client.delete(
            reverse('entry-detail', kwargs={'pk': entry.id}),
            format='json',
            follow=True)
        self.logout()

        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEquals(Entry.objects.count(), 0)

    def test_unauth_api_not_crud_entry(self):
        """ Test the api won't allow unauthenticated users to post/get/put/delete """
        # create
        self.post()
        self.assertEqual(self.response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.create_authenticated_entry()
        entry = Entry.objects.get()
        self.create_authenticated_entry()

        # read
        response = self.client.get(reverse('entry-list'), format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(
            reverse('entry-detail', kwargs={'pk': entry.id}),
            format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # update
        response = self.update_entry(entry.id)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # delete
        response = self.client.delete(
            reverse('entry-detail', kwargs={'pk': entry.id}),
            format='json',
            follow=True)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthTestCase(TestCase):
    """ Test suite for authentication """
    def setUp(self):
        self.client = APIClient()

    def test_user_gets_auth_token(self):
        """ Test an auth token is generated when a user is created """
        old_token_count = Token.objects.count()
        User.objects.create_user(username='john', password='john')
        new_token_count = Token.objects.count()
        self.assertNotEqual(old_token_count, new_token_count)

    def test_user_auth_token(self):
        """ Test the user gets auth token only for valid credentials """
        User.objects.create_user(username='john', password='john')

        # missing fields
        response = self.client.post(reverse('auth_token'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # wrong password
        response = self.client.post(
            reverse('auth_token'),
            {'username': 'john', 'password': 'wrong'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # success case
        response = self.client.post(
            reverse('auth_token'),
            {'username': 'john', 'password': 'john'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['token']), 40)

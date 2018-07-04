""" Entry App Tests """

from datetime import timedelta
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.timezone import now
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

    def test_user_registration(self):
        # success case
        response = self.client.post(
            reverse('auth_registration'),
            {'username': 'john', 'password': 'john'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)

        # existing username case
        response = self.client.post(
            reverse('auth_registration'),
            {'username': 'john', 'password': 'something'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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


class EntryQueryTestCase(TestCase):
    """ Test suite for authentication """
    def setUp(self):
        self.client = APIClient()

        # create two users
        self.user_john = User.objects.create_user(username='john', password='john')
        self.user_francis = User.objects.create_user(username='francis', password='francis')

        self.current_time = now()
        self.yesterday = self.current_time - timedelta(days=1)
        self.two_days_ago = self.current_time - timedelta(days=2)

        # create 3 entries each with set timestamps
        entry = Entry.objects.create(text="Entry 1", user=self.user_john)
        entry.date_created = self.yesterday
        entry.save()
        entry = Entry.objects.create(text="Entry 2", user=self.user_john)
        entry.date_created = self.yesterday
        entry.save()
        entry = Entry.objects.create(text="Entry 3", user=self.user_john)

        entry = Entry.objects.create(text="Entry 1", user=self.user_francis)
        entry.date_created = self.yesterday
        entry.save()
        entry = Entry.objects.create(text="Entry 2", user=self.user_francis)
        entry = Entry.objects.create(text="Entry 3", user=self.user_francis)

    def test_api_gets_day_entries(self):
        """ Testing the get_day_entries api """
        # unauthorized request
        response = self.client.get(reverse('entry-get-day-entries'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # testing responses for user 1
        self.client.login(username='john', password='john')
        response = self.client.get(reverse('entry-get-day-entries'))
        self.assertIsNotNone(response.data)
        self.assertEqual(len(response.data), 1)
        entry_names = map(lambda entry: entry['text'], response.data)
        self.assertIn('Entry 3', entry_names)

        response = self.client.get(reverse('entry-get-day-entries') + '?day=' + str(self.yesterday))
        self.assertIsNotNone(response.data)
        self.assertEqual(len(response.data), 2)
        entry_names = map(lambda entry: entry['text'], response.data)
        self.assertIn('Entry 1', entry_names)
        self.assertIn('Entry 2', entry_names)

        response = self.client.get(reverse('entry-get-day-entries') + '?day=' + str(self.two_days_ago))
        self.assertIsNotNone(response.data)
        self.assertEqual(len(response.data), 0)

        self.client.logout()

        # testing responses for user 2
        self.client.login(username='francis', password='francis')
        response = self.client.get(reverse('entry-get-day-entries'))
        self.assertIsNotNone(response.data)
        self.assertEqual(len(response.data), 2)
        entry_names = map(lambda entry: entry['text'], response.data)
        self.assertIn('Entry 2', entry_names)
        self.assertIn('Entry 3', entry_names)

        response = self.client.get(reverse('entry-get-day-entries') + '?day=' + str(self.yesterday))
        self.assertIsNotNone(response.data)
        self.assertEqual(len(response.data), 1)
        entry_names = map(lambda entry: entry['text'], response.data)
        self.assertIn('Entry 1', entry_names)

        response = self.client.get(reverse('entry-get-day-entries') + '?day=' + str(self.two_days_ago))
        self.assertIsNotNone(response.data)
        self.assertEqual(len(response.data), 0)

        self.client.logout()

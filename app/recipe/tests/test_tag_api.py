"""
Test for tag API.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

from core.models import (
    Tag,
    Recipe,
)

from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')

def detail_url(tag_id):
    """Create and return a tag detail url."""
    return reverse('recipe:tag-detail', args=[tag_id])

def create_user(email='test@example.com', password='testpass123'):
    """Creata and return a user."""
    return get_user_model().objects.create_user(email=email, password=password)

class PublicTagAPITests(TestCase):
    """Test unauthenticated API requests."""
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_requied(self):
        """Test auth is required for retrieving tags."""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateTagAPITests(TestCase):
    """Test authenticated API requests."""
    def setUp(self) -> None:
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_tags(self):
        """Test list tags."""
        Tag.objects.create(user=self.user, name="Vinh")
        Tag.objects.create(user=self.user, name='Zico')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_by_user(self):
        """Test list of tags is limited to authenticated user."""
        another_user = create_user(email='another@example.com', password='anotherpass123')
        Tag.objects.create(user=another_user, name='Hello')
        tag = Tag.objects.create(user=self.user, name='Hi')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tag(self):
        """Test update a tag."""
        tag = Tag.objects.create(user=self.user, name='OMG')

        payload = {
            'name': "OMG!!!",
        }
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """Test delete a tag."""
        tag = Tag.objects.create(user=self.user, name='Delete me')

        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

    def test_filter_tags_assigned_to_recipes(self):
        """Test listing tags to those assigned to recipes."""
        tag1 = Tag.objects.create(user=self.user, name='Breakfast')
        tag2 = Tag.objects.create(user=self.user, name='Lunch')
        recipe = Recipe.objects.create(
            title='Green Eggs on Toast',
            time_minutes=10,
            price=Decimal('5.55'),
            user=self.user,
        )

        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)

        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_tags_unique(self):
        """Test filtered tags returns a unique list."""
        tag = Tag.objects.create(user=self.user, name="Dinner")
        Tag.objects.create(user=self.user, name='Midnight')
        recipe1 = Recipe.objects.create(
            title='Eggs Fried',
            time_minutes=10,
            price=Decimal('2.00'),
            user=self.user
        )
        recipe2 = Recipe.objects.create(
            title='Eggs Herbs',
            time_minutes=10,
            price=Decimal('2.00'),
            user=self.user
        )

        recipe1.tags.add(tag)
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)




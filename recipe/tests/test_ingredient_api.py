from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe

from recipe.serializers import IngredientSerializer


INGREDIENT_URL = reverse('recipe:ingredient-list')


class PublicIngredientApiTests(TestCase):
    """Test the Public Ingredient API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Login is always required to access this endpoint"""
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTests(TestCase):
    """Test the private ingredient API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """Test retrieving a list of ingredients"""
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Salt')

        res = self.client.get(INGREDIENT_URL)
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that ingredients for the authenticated users are returned"""
        user2 = get_user_model().objects.create_user(
            'test2@test.com',
            'testpass'
        )
        Ingredient.objects.create(user=user2, name="Vinegar")
        ingredient = Ingredient.objects.create(user=self.user, name='Tumeric')

        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient_successful(self):
        """Test creating an ingredient is successful"""
        payload = {'name': 'Cabbage'}
        self.client.post(INGREDIENT_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """Test creating an ingredient with invalid payload fails"""
        payload = {'name': ''}
        res = self.client.post(INGREDIENT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_recipes(self):
        """Test filtering ingredients by thos assigned to recipes"""
        ingredient1 = Ingredient.objects.create(
            user=self.user, name='Apples'
        )
        ingredient2 = Ingredient.objects.create(
            user=self.user, name='Turkey'
        )
        recipe = Recipe.objects.create(
            title='Apple crumble',
            time_minutes=5,
            price=5.00,
            user=self.user
        )
        recipe.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENT_URL, {'assigned_only': 1})
        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_ingredient_assinged_unique(self):
        """Test filtering ingredients by assinged returns unique items"""
        ingredient = Ingredient.objects.create(
            user=self.user, name='Eggs'
        )
        Ingredient.objects.create(user=self.user, name='Cheese')
        recipe1 = Recipe.objects.create(
            title='Egges bennedict',
            time_minutes=5,
            price=5.00,
            user=self.user
        )
        recipe1.ingredients.add(ingredient)
        recipe2 = Recipe.objects.create(
            title='ACoriander eggs on a toast',
            time_minutes=5,
            price=5.00,
            user=self.user
        )
        recipe2.ingredients.add(ingredient)
        res = self.client.get(INGREDIENT_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
import json

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Recipe

class RecipeModelTests(TestCase):
    def test_is_viewable_by(self):
        user = get_user_model().objects.create(username="testuser")
        user.set_password('password2026')
        user.save()
        recipe = Recipe(is_public=False, method="test", user_id=user.id)
        recipe.save()
        self.assertIs(recipe.is_viewable_by(user), True)
        user_two = get_user_model().objects.create(username='two')
        user_two.save()
        self.assertIs(recipe.is_viewable_by(user_two), False)
        recipe.is_public = True
        self.assertIs(recipe.is_viewable_by(user_two), True)

class RecipePublicIndexViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(username="testuser", password="password2026")
        self.user.set_password('password2026')
        self.user.save()

    def test_logged_out_sees_public(self):
        # setup
        recipe = Recipe(name="Test Recipe", method="test", is_public=False, user_id=self.user.id)
        recipe.save()
        user_two = get_user_model().objects.create(username="testuserTwo")
        user_two.set_password('password2026')
        user_two.save()
        recipe_two = Recipe(name="User Two Recipe", method="test", is_public=True, user_id=user_two.id)
        recipe_two.save()

        response = self.client.get(reverse("recipes:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "User Two Recipe")
        self.assertNotContains(response, "Test Recipe")
        self.assertQuerySetEqual(response.context["recipe_list"], [recipe_two])

    def test_see_public_recipes(self):
        self.client.login(username="testuser", password="password2026")
        response = self.client.get(reverse("recipes:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No recipes found.")
        self.assertQuerySetEqual(response.context["recipe_list"], [])

        # setup
        recipe = Recipe(name="Test Recipe", method="test", is_public=False, user_id=self.user.id)
        recipe.save()
        user_two = get_user_model().objects.create(username="testuserTwo")
        user_two.set_password('password2026')
        user_two.save()
        recipe_two = Recipe(name="User Two Recipe", method="test", is_public=True, user_id=user_two.id)
        recipe_two.save()

        response = self.client.get(reverse("recipes:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "User Two Recipe")
        self.assertNotContains(response, "Test Recipe")
        self.assertQuerySetEqual(response.context["recipe_list"], [recipe_two])

        recipe.is_public = True
        recipe.save()
        response = self.client.get(reverse("recipes:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "User Two Recipe")
        self.assertContains(response, "Test Recipe")
        self.assertQuerySetEqual(response.context["recipe_list"], [recipe, recipe_two], ordered=False)

class RecipeIndexViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(username="testuser", password="password2026")
        self.user.set_password('password2026')
        self.user.save()

    def test_see_no_user_recipes(self):
        # not logged in
        response = self.client.get(reverse("recipes:my_recipes"))
        self.assertEqual(response.status_code, 302) # redirect to login

        # logged in no recipes created
        self.client.login(username="testuser", password="password2026")
        response = self.client.get(reverse("recipes:my_recipes"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No recipes found.")
        self.assertQuerySetEqual(response.context["recipe_list"], [])

    def test_see_user_recipes(self):
        self.client.login(username="testuser", password="password2026")
        recipe = Recipe(name="Test Recipe", method="test", is_public=False, user_id=self.user.id)
        recipe.save()
        response = self.client.get(reverse("recipes:my_recipes"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Recipe")
        self.assertQuerySetEqual(response.context["recipe_list"], [recipe])

class RecipeDetailViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(username="testuser")
        self.user.set_password('password2026')
        self.user.save()
        self.recipe = Recipe(name="Test Recipe", method="test", is_public=False, user_id=self.user.id)
        self.recipe.save()

    def test_user_sees_recipe(self):
        self.client.login(username="testuser", password="password2026")
        response = self.client.get(reverse('recipes:detail', kwargs={'uuid': self.recipe.uuid}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Recipe')
        self.assertEqual(response.context["recipe"], self.recipe)

    def test_other_user_cant_see_recipe(self):
        user_two = get_user_model().objects.create(username="testuserTwo")
        user_two.set_password('password2026')
        user_two.save()
        self.client.login(username="testuserTwo", password="password2026")
        response = self.client.get(reverse('recipes:detail', kwargs={'uuid': self.recipe.uuid}))
        self.assertEqual(response.status_code, 404)

    def test_other_user_can_see_public_recipe(self):
        self.recipe.is_public = True
        self.recipe.save()
        user_two = get_user_model().objects.create(username="testuserTwo")
        user_two.set_password('password2026')
        user_two.save()
        self.client.login(username="testuserTwo", password="password2026")
        response = self.client.get(reverse('recipes:detail', kwargs={'uuid': self.recipe.uuid}))
        self.assertEqual(response.status_code, 200)

    def test_public_cant_see_recipe(self):
        response = self.client.get(reverse('recipes:detail', kwargs={'uuid': self.recipe.uuid}))
        self.assertEqual(response.status_code, 302) # redirect to login

    def test_public_can_see_public_recipe(self):
        self.recipe.is_public = True
        self.recipe.save()
        response = self.client.get(reverse('recipes:detail', kwargs={'uuid': self.recipe.uuid}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Recipe')
        self.assertEqual(response.context["recipe"], self.recipe)


class RecipeUpdateViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(username="testuser")
        self.user.set_password('password2026')
        self.user.save()
        self.recipe = Recipe(name="Test Recipe", method="test", is_public=False, user_id=self.user.id)
        self.recipe.save()

    def test_user_can_edit_recipe(self):
        self.client.login(username="testuser", password="password2026")
        response = self.client.get(reverse('recipes:update', kwargs={'uuid': self.recipe.uuid}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Recipe')
        self.assertEqual(response.context["recipe"], self.recipe)

    def test_other_user_cant_edit_recipe(self):
        user_two = get_user_model().objects.create(username="testuserTwo")
        user_two.set_password('password2026')
        user_two.save()
        self.client.login(username="testuserTwo", password="password2026")
        response = self.client.get(reverse('recipes:update', kwargs={'uuid': self.recipe.uuid}))
        self.assertEqual(response.status_code, 404)

    def test_public_cant_edit_recipe(self):
        response = self.client.get(reverse('recipes:update', kwargs={'uuid': self.recipe.uuid}))
        self.assertEqual(response.status_code, 302) # Redirecto to login

class RecipeDeleteViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(username="testuser")
        self.user.set_password('password2026')
        self.user.save()
        self.recipe = Recipe(name="Test Recipe", method="test", is_public=False, user_id=self.user.id)
        self.recipe.save()

    def test_user_can_delete_recipe(self):
        self.client.login(username="testuser", password="password2026")
        response = self.client.get(reverse('recipes:delete', kwargs={'uuid': self.recipe.uuid}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Delete Test Recipe')
        self.assertEqual(response.context["recipe"], self.recipe)

    def test_other_user_cant_delete_recipe(self):
        user_two = get_user_model().objects.create(username="testuserTwo")
        user_two.set_password('password2026')
        user_two.save()
        self.client.login(username="testuserTwo", password="password2026")
        response = self.client.get(reverse('recipes:delete', kwargs={'uuid': self.recipe.uuid}))
        self.assertEqual(response.status_code, 404)

    def test_public_cant_delete_recipe(self):
        response = self.client.get(reverse('recipes:delete', kwargs={'uuid': self.recipe.uuid}))
        self.assertEqual(response.status_code, 302) # Redirecto to login

class ConvertQuantitiesTest(TestCase):
    def test_metric_to_us_customary(self):
        path = reverse("recipes:convert_quantities")
        data = {
            "convert_to": "us_customary",
            "ingredients": [
                {
                    "id": 1,
                    "quantity": "200.00",
                    "unit": "g"
                },
                {
                    "id": 2,
                    "quantity": "1.00",
                    "unit": "kg"
                },
                {
                    "id": 3,
                    "quantity": "2.00",
                    "unit": "none"
                },
                {
                    "id": 4,
                    "quantity": "1.50",
                    "unit": "cup"
                }
            ]
        }
        response = self.client.post(path, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, [
            {
                "id": 1,
                "quantity": 7.05,
                "unit": "oz"
            },
            {
                "id": 2,
                "quantity": 2.2,
                "unit": "lb"
            },
            {
                "id": 3,
                "quantity": 2,
                "unit": "none"
            },
            {
                "id": 4,
                "quantity": "1 1/2",
                "unit": "cup"
            }
        ])

    def test_us_customary_to_metric(self):
        path = reverse("recipes:convert_quantities")
        data = {
            "convert_to": "metric",
            "ingredients": [
                {
                    "id": 1,
                    "quantity": "2.00",
                    "unit": "oz"
                },
                {
                    "id": 2,
                    "quantity": "1.00",
                    "unit": "lb"
                },
                {
                    "id": 3,
                    "quantity": "2.00",
                    "unit": "none"
                },
                {
                    "id": 3,
                    "quantity": "1.5",
                    "unit": "cup"
                }
            ]
        }
        response = self.client.post(path, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, [
            {
                "id": 1,
                "quantity": 56.7,
                "unit": "g"
            },
            {
                "id": 2,
                "quantity": 0.45,
                "unit": "kg"
            },
            {
                "id": 3,
                "quantity": 2,
                "unit": "none"
            },
            {
                "id": 3,
                "quantity": "1 1/2",
                "unit": "cup"
            }
        ])
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Recipe

class RecipeModelTests(TestCase):
    def test_is_viewable_by(self):
        user = User.objects.create_user(username="testuser", password="password2026")
        user.save()
        recipe = Recipe(is_public=False, user_id=user.id)
        recipe.save()
        self.assertIs(recipe.is_viewable_by(user), True)
        user_two = User(username='two')
        user_two.save()
        self.assertIs(recipe.is_viewable_by(user_two), False)
        recipe.is_public = True
        self.assertIs(recipe.is_viewable_by(user_two), True)

class RecipePublicIndexViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password2026")

    def test_logged_out_sees_public(self):
        # setup
        recipe = Recipe(name="Test Recipe", is_public=False, user_id=self.user.id)
        recipe.save()
        user_two = User.objects.create_user(username="testuserTwo", password="password2026")
        recipe_two = Recipe(name="User Two Recipe", is_public=True, user_id=user_two.id)
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
        recipe = Recipe(name="Test Recipe", is_public=False, user_id=self.user.id)
        recipe.save()
        user_two = User.objects.create_user(username="testuserTwo", password="password2026")
        recipe_two = Recipe(name="User Two Recipe", is_public=True, user_id=user_two.id)
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
        self.user = User.objects.create_user(username="testuser", password="password2026")

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
        recipe = Recipe(name="Test Recipe", is_public=False, user_id=self.user.id)
        recipe.save()
        response = self.client.get(reverse("recipes:my_recipes"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Recipe")
        self.assertQuerySetEqual(response.context["recipe_list"], [recipe])

class RecipeDetailViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password2026")
        self.recipe = Recipe(name="Test Recipe", is_public=False, user_id=self.user.id)
        self.recipe.save()

    def test_user_sees_recipe(self):
        self.client.login(username="testuser", password="password2026")
        response = self.client.get(reverse('recipes:detail', kwargs={'uuid': self.recipe.uuid}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Recipe')
        self.assertEqual(response.context["recipe"], self.recipe)

    def test_other_user_cant_see_recipe(self):
        user_two = User.objects.create_user(username="testuserTwo", password="password2026")
        user_two.save()
        self.client.login(username="testuserTwo", password="password2026")
        response = self.client.get(reverse('recipes:detail', kwargs={'uuid': self.recipe.uuid}))
        self.assertEqual(response.status_code, 404)

    def test_public_cant_see_recipe(self):
        response = self.client.get(reverse('recipes:detail', kwargs={'uuid': self.recipe.uuid}))
        self.assertEqual(response.status_code, 404)

    def test_public_can_see_public_recipe(self):
        self.recipe.is_public = True
        self.recipe.save()
        response = self.client.get(reverse('recipes:detail', kwargs={'uuid': self.recipe.uuid}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Recipe')
        self.assertEqual(response.context["recipe"], self.recipe)


class RecipeUpdateViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password2026")
        self.recipe = Recipe(name="Test Recipe", is_public=False, user_id=self.user.id)
        self.recipe.save()

    def test_user_can_edit_recipe(self):
        self.client.login(username="testuser", password="password2026")
        response = self.client.get(reverse('recipes:update', kwargs={'uuid': self.recipe.uuid}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Recipe')
        self.assertEqual(response.context["recipe"], self.recipe)

    def test_other_user_cant_edit_recipe(self):
        user_two = User.objects.create_user(username="testuserTwo", password="password2026")
        user_two.save()
        self.client.login(username="testuserTwo", password="password2026")
        response = self.client.get(reverse('recipes:update', kwargs={'uuid': self.recipe.uuid}))
        self.assertEqual(response.status_code, 404)

    def test_public_cant_edit_recipe(self):
        response = self.client.get(reverse('recipes:update', kwargs={'uuid': self.recipe.uuid}))
        self.assertEqual(response.status_code, 302) # Redirecto to login
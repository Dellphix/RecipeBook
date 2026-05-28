from django.contrib.auth.models import User
from django.db.models.sql import query
from django.test import TestCase
from django.urls import reverse

from .models import Invitation

class InvitationModelTests(TestCase):
    def setUp(self):
        self.invitation = Invitation()
        self.invitation.save()

    def test_is_viewable_when_unused(self):
        response = self.client.get(reverse("invitation", kwargs={'code': self.invitation.code.hex}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You are cordially invited to use this Recipe Book.")

    def test_is_not_viewable_when_used(self):
        user = User()
        user.save()
        self.invitation.user_id = user.id
        self.invitation.save()

        response = self.client.get(reverse("invitation", kwargs={'code': self.invitation.code.hex}))
        self.assertEqual(response.status_code, 404)

    def test_links_user_when_used(self):
        invite_path = reverse("invitation", kwargs={'code': self.invitation.code.hex})
        data = {"username": "invited_user", "password1": "testpassword", "password2": "testpassword"}
        self.client.post(invite_path, data=data)

        user = User.objects.filter(username="invited_user")[0]
        self.assertIsNotNone(user)
        self.invitation.refresh_from_db()
        self.assertEqual(self.invitation.user_id, user.id)
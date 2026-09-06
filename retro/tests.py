from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from retro.models import Project


class HomeViewTests(TestCase):
    def test_home_returns_200(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)


class ProjectTokenTests(TestCase):
    def test_token_auto_populated_on_save(self):
        project = Project.objects.create(name="Team A")
        self.assertTrue(project.token)

    def test_tokens_differ_between_projects(self):
        first = Project.objects.create(name="Team A")
        second = Project.objects.create(name="Team B")
        self.assertNotEqual(first.token, second.token)

    def test_duplicate_token_raises_integrity_error(self):
        existing = Project.objects.create(name="Team A")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Project.objects.create(name="Team B", token=existing.token)

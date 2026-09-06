import secrets

from django.db import models


def generate_token():
    """Return an unguessable, URL-safe token with at least 128 bits of entropy."""
    return secrets.token_urlsafe(16)


class Project(models.Model):
    name = models.CharField(max_length=200)
    token = models.CharField(max_length=32, unique=True, default=generate_token)

    def __str__(self):
        return self.name

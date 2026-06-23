# PATH: Ztech/newsletter/models.py

from django.db import models


class Subscriber(models.Model):
    email       = models.EmailField(unique=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    is_active   = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.email
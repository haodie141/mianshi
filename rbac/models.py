from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    plan = models.CharField(max_length=10, default="free")  # free / pro
    roles = models.ManyToManyField("Role", blank=True)

class Permission(models.Model):
    code = models.CharField(max_length=100, unique=True)   # 权限代号
    name = models.CharField(max_length=255)                # 人类可读

    def __str__(self):
        return f"{self.name}({self.code})"

class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    permissions = models.ManyToManyField(Permission, blank=True)

    def __str__(self):
        return self.name
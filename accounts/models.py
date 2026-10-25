from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        EMPLOYEE = "employee", "Employee"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.EMPLOYEE,
    )

    def get_initials(self):
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        return self.username[:2].upper()

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_employee(self):
        return self.role == self.Role.EMPLOYEE

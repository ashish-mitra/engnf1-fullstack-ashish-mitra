from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):

    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):

        if not email:
            raise ValueError("Email is required")

        email = email.strip().lower()

        name = extra_fields.get("name")

        if not name:
            raise ValueError("Name is required")

        # Normal users cannot create ADMIN accounts.
        requested_role = extra_fields.pop(
            "role",
            "USER"
        )

        if requested_role != "USER":
            raise ValueError("Use create_superuser for ADMIN accounts")

        user = self.model(
            email=email,
            role="USER",
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):

        if not email:
            raise ValueError("Email is required")

        email = email.strip().lower()

        extra_fields.setdefault("role", "ADMIN")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("role") != "ADMIN":
            raise ValueError("Superuser must have ADMIN role")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_admin_user(
            email,
            password,
            **extra_fields
        )

    def create_admin_user(self, email, password, **extra_fields):

        name = extra_fields.get("name")

        if not name:
            raise ValueError("Name is required")

        user = self.model(
            email=email,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

class User(AbstractUser):

    class Role(models.TextChoices):
        USER = "USER", "User"
        ADMIN = "ADMIN", "Admin"

    username = None

    name = models.CharField(max_length=50)

    email = models.EmailField(
        max_length=254,
        unique=True
    )

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER
    )

    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return self.email
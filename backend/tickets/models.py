from django.db import models
from django.conf import settings


class Ticket(models.Model):

    class Category(models.TextChoices):
        BILLING = "BILLING", "Billing"
        BUG = "BUG", "Bug"
        FEATURE_REQUEST = "FEATURE_REQUEST", "Feature Request"
        LOGIN = "LOGIN", "Login"
        DELIVERY = "DELIVERY", "Delivery"

    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"
        URGENT = "URGENT", "Urgent"

    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        RESOLVED = "RESOLVED", "Resolved"
        CLOSED = "CLOSED", "Closed"

    external_id = models.CharField(
        max_length=100,
        unique=True
    )

    subject = models.CharField(
        max_length=150
    )

    body = models.TextField()

    auto_category = models.CharField(
        max_length=20,
        choices=Category.choices
    )

    category = models.CharField(
        max_length=20,
        choices=Category.choices
    )

    is_human_override = models.BooleanField(
        default=False
    )

    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )

    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.OPEN
    )

    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets"
    )

    is_reviewed = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["category"]),
            models.Index(fields=["priority"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.external_id} - {self.subject}"


class TicketEvent(models.Model):

    class Field(models.TextChoices):
        CATEGORY = "category", "Category"
        PRIORITY = "priority", "Priority"
        STATUS = "status", "Status"
        ASSIGNEE_ID = "assigneeId", "Assignee"

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="events"
    )

    field = models.CharField(
        max_length=20,
        choices=Field.choices
    )

    old_value = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    new_value = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    actor = models.CharField(
        max_length=254
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["created_at"]

        indexes = [
            models.Index(
                fields=["ticket", "created_at"]
            ),
        ]

    def __str__(self):
        return f"Ticket {self.ticket_id}: {self.field}"
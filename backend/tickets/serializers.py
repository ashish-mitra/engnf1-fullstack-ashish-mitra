from rest_framework import serializers
from .models import Ticket, TicketEvent


class TicketImportItemSerializer(serializers.Serializer):

    externalId = serializers.CharField(
        max_length=100,
        trim_whitespace=True
    )

    subject = serializers.CharField(
        min_length=3,
        max_length=150,
        trim_whitespace=True
    )

    body = serializers.CharField(
        min_length=5,
        max_length=2000,
        trim_whitespace=True
    )


class TicketImportSerializer(serializers.Serializer):

    tickets = TicketImportItemSerializer(
        many=True,
        allow_empty=False
    )

class TicketSerializer(serializers.ModelSerializer):

    externalId = serializers.CharField(
        source="external_id",
        read_only=True
    )

    autoCategory = serializers.CharField(
        source="auto_category",
        read_only=True
    )

    isHumanOverride = serializers.BooleanField(
        source="is_human_override",
        read_only=True
    )

    assigneeId = serializers.IntegerField(
        source="assignee_id",
        read_only=True,
        allow_null=True
    )

    isReviewed = serializers.BooleanField(
        source="is_reviewed",
        read_only=True
    )

    createdAt = serializers.DateTimeField(
        source="created_at",
        read_only=True
    )

    updatedAt = serializers.DateTimeField(
        source="updated_at",
        read_only=True
    )

    class Meta:
        model = Ticket

        fields = [
            "id",
            "externalId",
            "subject",
            "body",
            "autoCategory",
            "category",
            "isHumanOverride",
            "priority",
            "status",
            "assigneeId",
            "isReviewed",
            "createdAt",
            "updatedAt"
        ]

class TicketEventSerializer(serializers.ModelSerializer):

    ticketId = serializers.IntegerField(
        source="ticket_id",
        read_only=True
    )

    oldValue = serializers.CharField(
        source="old_value",
        read_only=True,
        allow_null=True
    )

    newValue = serializers.CharField(
        source="new_value",
        read_only=True,
        allow_null=True
    )

    createdAt = serializers.DateTimeField(
        source="created_at",
        read_only=True
    )

    class Meta:
        model = TicketEvent

        fields = [
            "id",
            "ticketId",
            "field",
            "oldValue",
            "newValue",
            "actor",
            "createdAt"
        ]

        read_only_fields = [
            "id",
            "ticketId",
            "field",
            "oldValue",
            "newValue",
            "actor",
            "createdAt"
        ]